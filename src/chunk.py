"""Milestone 3 — structure-aware chunking.

Per planning.md: split on the natural semantic boundary of each document type rather
than a fixed character window.

  * Review pages (rmp_*.txt): one "profile" chunk (overall ratings + tags) plus one
    chunk per student review. The profile chunk keeps the "would take again %" metric
    in the corpus — needed so evaluation question 5 has retrievable data even though
    answering it requires aggregation across all professors.
  * Forum threads (reddit_*.txt): one chunk for the original post, plus one chunk per
    top-level comment grouped with its nested replies.

Every chunk gets a "[Professor | Course | Source]" context header prepended so it is
self-contained, and carries metadata (source, doc_type, chunk_type, professor, course,
chunk_index). No character overlap. Long chunks are split at sentence boundaries to
respect the ~800-char cap.
"""

from __future__ import annotations

import re

from .ingest import load_documents

MAX_CHARS = 800

# --- Review-page patterns ---
_PROFESSOR = re.compile(r"^Professor\s+(.+?)\s*$", re.MULTILINE)
_STATS = re.compile(
    r"Overall Quality:\s*([\d.]+)\s*/\s*5\s+"
    r"Would take again:\s*(\d+)%\s+"
    r"Level of Difficulty:\s*([\d.]+)"
)
_TAGS = re.compile(r"---\s*Top Tags\s*---\s*\n(.+)")
# CS 201 - Data Structures   |   Quality: 5.0   Difficulty: 4.0   |   Mar 2024
_REVIEW_HEADER = re.compile(
    r"^(CS\s*\d+)\s*-\s*(.+?)\s*\|\s*Quality:\s*([\d.]+)\s+Difficulty:\s*([\d.]+)\s*\|\s*(.+?)\s*$",
    re.MULTILINE,
)

# --- Forum-thread patterns ---
_POSTED_BY = re.compile(r"^r/(\w+)\s*[•·]\s*Posted by\s+(u/[\w-]+)", re.MULTILINE)
# matches both top-level "▲ 96  u/foo  • ..." and nested "↳ ▲ 24  u/bar (OP)  • ..."
_COMMENT = re.compile(
    r"^(?P<indent>\s*)(?P<reply>↳\s*)?▲\s*\d+\s+(?P<author>u/[\w-]+)(?:\s*\(OP\))?\s*[•·]"
)


def _split_with_cap(header: str, body: str, cap: int = MAX_CHARS) -> list[str]:
    """Return one chunk if header+body fits cap, else split body at sentence ends."""
    body = body.strip()
    full = f"{header}\n{body}"
    if len(full) <= cap:
        return [full]
    sentences = re.split(r"(?<=[.!?])\s+", body)
    chunks, current = [], ""
    for sent in sentences:
        candidate = f"{current} {sent}".strip()
        if len(header) + 1 + len(candidate) > cap and current:
            chunks.append(f"{header}\n{current.strip()}")
            current = sent
        else:
            current = candidate
    if current.strip():
        chunks.append(f"{header}\n{current.strip()}")
    return chunks


def _chunk_review_page(doc: dict) -> list[dict]:
    text, source = doc["text"], doc["source"]
    prof_m = _PROFESSOR.search(text)
    professor = prof_m.group(1).strip() if prof_m else ""

    # Course label comes from the first review header on the page.
    first = _REVIEW_HEADER.search(text)
    course = f"{first.group(1)} {first.group(2)}".strip() if first else ""
    header_label = f"Prof. {professor} | {course} | RateMyProfessors"

    chunks: list[dict] = []

    # 1) Profile chunk — overall ratings + tags (keeps "would take again %" retrievable).
    stats = _STATS.search(text)
    tags_m = _TAGS.search(text)
    if stats:
        tags = ""
        if tags_m:
            tags = ", ".join(t.strip() for t in re.split(r"[•·]", tags_m.group(1)) if t.strip())
        profile = (
            f"Overall quality {stats.group(1)}/5. "
            f"Would take again: {stats.group(2)}%. "
            f"Difficulty {stats.group(3)}/5."
        )
        if tags:
            profile += f" Common student tags: {tags}."
        chunks.append(
            {
                "text": f"[{header_label} profile]\n{profile}",
                "metadata": {
                    "source": source, "doc_type": "review_page", "chunk_type": "profile",
                    "professor": professor, "course": course, "extra": "overall ratings",
                },
            }
        )

    # 2) One chunk per student review.
    matches = list(_REVIEW_HEADER.finditer(text))
    for i, m in enumerate(matches):
        body_start = m.end()
        body_end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[body_start:body_end].strip()
        if not body:
            continue
        date = m.group(5).strip()
        rh = (
            f"[{header_label} review · {date} · "
            f"quality {m.group(3)}/5, difficulty {m.group(4)}/5]"
        )
        for piece in _split_with_cap(rh, body):
            chunks.append(
                {
                    "text": piece,
                    "metadata": {
                        "source": source, "doc_type": "review_page", "chunk_type": "review",
                        "professor": professor, "course": course, "extra": date,
                    },
                }
            )
    return chunks


def _chunk_forum_thread(doc: dict) -> list[dict]:
    text, source = doc["text"], doc["source"]
    posted = _POSTED_BY.search(text)
    author_op = posted.group(2) if posted else ""

    lines = text.splitlines()
    comment_starts = [i for i, ln in enumerate(lines) if _COMMENT.match(ln)]

    # Title + body = everything before the first comment (minus the "Posted by" line).
    head_end = comment_starts[0] if comment_starts else len(lines)
    head_lines = [ln for ln in lines[:head_end] if not _POSTED_BY.match(ln)]
    head_text = "\n".join(head_lines).strip()
    title = head_text.splitlines()[0].strip() if head_text else source
    label = f"r/LakemontU thread: \"{title}\""

    chunks: list[dict] = []

    # 1) Original post chunk.
    if head_text:
        for piece in _split_with_cap(f"[{label} | original post by {author_op}]", head_text):
            chunks.append(
                {
                    "text": piece,
                    "metadata": {
                        "source": source, "doc_type": "forum_thread", "chunk_type": "post",
                        "professor": "", "course": "", "extra": title,
                    },
                }
            )

    # 2) Group each top-level comment with its nested replies into one chunk.
    # Each block's first line is the "▲ <votes> u/<author> • <when>" chrome line — we
    # drop it (the chunk header already names the author) and keep only the comment text.
    def _block_text(start: int, end: int) -> str:
        return "\n".join(lines[start + 1:end]).strip()

    groups: list[dict] = []  # {author, parts: [str]}
    for idx, start in enumerate(comment_starts):
        end = comment_starts[idx + 1] if idx + 1 < len(comment_starts) else len(lines)
        m = _COMMENT.match(lines[start])
        body = _block_text(start, end)
        if m.group("reply") and groups:
            groups[-1]["parts"].append(f"↳ reply ({m.group('author')}): {body}")
        else:
            groups.append({"author": m.group("author"), "parts": [body]})

    for group in groups:
        body = "\n\n".join(group["parts"])
        for piece in _split_with_cap(f"[{label} | reply by {group['author']}]", body):
            chunks.append(
                {
                    "text": piece,
                    "metadata": {
                        "source": source, "doc_type": "forum_thread", "chunk_type": "comment",
                        "professor": "", "course": "", "extra": group["author"],
                    },
                }
            )
    return chunks


def chunk_document(doc: dict) -> list[dict]:
    """Dispatch on document type (detected from filename prefix)."""
    if doc["source"].startswith("reddit_"):
        return _chunk_forum_thread(doc)
    return _chunk_review_page(doc)


def chunk_corpus(docs: list[dict] | None = None) -> list[dict]:
    """Load (if needed) and chunk all documents, assigning stable ids + chunk_index."""
    if docs is None:
        docs = load_documents()
    all_chunks: list[dict] = []
    for doc in docs:
        for i, chunk in enumerate(chunk_document(doc)):
            chunk["metadata"]["chunk_index"] = i
            chunk["id"] = f"{doc['source']}::{i}"
            all_chunks.append(chunk)
    return all_chunks


if __name__ == "__main__":
    import random

    chunks = chunk_corpus()
    print(f"Total chunks: {len(chunks)}\n")

    by_type: dict[str, int] = {}
    for c in chunks:
        by_type[c["metadata"]["chunk_type"]] = by_type.get(c["metadata"]["chunk_type"], 0) + 1
    print("By chunk type:", by_type)
    lengths = [len(c["text"]) for c in chunks]
    print(f"Chunk length chars: min {min(lengths)}, max {max(lengths)}, "
          f"avg {sum(lengths)//len(lengths)}\n")

    random.seed(7)
    print("===== 5 RANDOM CHUNKS =====")
    for c in random.sample(chunks, 5):
        print(f"\n--- id={c['id']}  type={c['metadata']['chunk_type']}  "
              f"({len(c['text'])} chars) ---")
        print(c["text"])

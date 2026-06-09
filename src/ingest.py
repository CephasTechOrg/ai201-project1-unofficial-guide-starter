"""Milestone 3 — document ingestion: load raw files and strip boilerplate.

Implements the Documents + Chunking Strategy spec from planning.md. Cleaning removes
the web boilerplate present in our sources (nav bars, cookie notices, engagement
counters, footers, Reddit chrome) while *preserving* the structural markers the
chunker relies on (professor/stats headers, the STUDENT REVIEWS divider, review
header lines, Reddit comment author lines).
"""

from __future__ import annotations

import html
import re
from pathlib import Path

RAW_DIR = Path(__file__).resolve().parent.parent / "documents" / "raw"

# Line-level boilerplate. A line is dropped if any pattern matches (search, not
# fullmatch) — these target site chrome, not content. Structural markers used by
# the chunker (Professor, Overall Quality, --- Top Tags ---, STUDENT REVIEWS,
# review headers, Reddit "Posted by" / "▲ <votes> u/<author>" lines) are NOT here.
_BOILERPLATE = [
    r"^RateMyProfessors\.com",                 # top nav
    r"^\[Skip to main content\]",              # skip-link + cookie notice line
    r"Rate Professor .*\]",                    # [ ★ Rate ... ] [ Compare ] action bar
    r"Helpful \(\d+\)",                        # 👍 Helpful (42)  👎 Not helpful (3) | Reply | Share
    r"^\[ Load more reviews \]",               # pagination / "Submit a Correction"
    r"^Footer:",                               # RMP footer
    r"^Was this page helpful\?",               # RMP engagement footer
    r"Download our app",
    r"^Upvote \d+\s*[•·]\s*Downvote",          # Reddit vote bar
    r"^\[ View \d+ more comments \]",          # Reddit pagination
    r"Comments are locked",                    # Reddit archived notice
    r"^About\s*[•·]\s*Help",                   # Reddit footer
    r"©\s*\d{4}",                              # copyright lines (both sources)
    r"^[─—-]{3,}$",                            # horizontal separators
]
_BOILERPLATE_RE = [re.compile(p) for p in _BOILERPLATE]


def clean_document(text: str) -> str:
    """Strip boilerplate and decode HTML entities, preserving content + structure."""
    text = html.unescape(text)  # &amp; -> &, &#39; -> '
    kept: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if any(rx.search(stripped) for rx in _BOILERPLATE_RE):
            continue
        kept.append(line.rstrip())
    cleaned = "\n".join(kept)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)  # collapse blank-line runs
    return cleaned.strip()


def load_documents(raw_dir: Path | str = RAW_DIR) -> list[dict]:
    """Load every .txt in raw_dir, returning {source, raw, text} dicts (text = cleaned)."""
    raw_dir = Path(raw_dir)
    docs = []
    for path in sorted(raw_dir.glob("*.txt")):
        raw = path.read_text(encoding="utf-8")
        docs.append({"source": path.name, "raw": raw, "text": clean_document(raw)})
    if not docs:
        raise FileNotFoundError(f"No .txt documents found in {raw_dir}")
    return docs


if __name__ == "__main__":
    docs = load_documents()
    print(f"Loaded {len(docs)} documents from {RAW_DIR}\n")
    sample = docs[0]
    print(f"===== CLEANED PREVIEW: {sample['source']} =====")
    print(f"(raw {len(sample['raw'])} chars -> cleaned {len(sample['text'])} chars)\n")
    print(sample["text"])

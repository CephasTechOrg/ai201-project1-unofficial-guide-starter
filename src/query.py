"""Milestone 5 — end-to-end query orchestration: retrieve -> generate -> attribute.

`ask()` is the single entry point used by the interface (app.py) and the evaluation
script. It guarantees source attribution programmatically: the `sources` list is built
from the retrieved chunks' metadata, never from the model's output.
"""

from __future__ import annotations

from .generate import REFUSAL, generate_answer
from .vectorstore import retrieve


def _source_label(meta: dict) -> str:
    """Human-readable source label from a chunk's metadata."""
    if meta.get("professor"):
        course = f" — {meta['course']}" if meta.get("course") else ""
        return f"{meta['source']} (Prof. {meta['professor']}{course})"
    if meta.get("extra"):  # forum thread: extra holds the thread title or author
        return f"{meta['source']} ({meta['extra']})"
    return meta["source"]


def ask(question: str, k: int = 5) -> dict:
    """Answer a question with grounded generation and programmatic source attribution.

    Returns {"answer", "sources", "chunks"}:
      - answer:  the LLM's grounded response (or the refusal sentence)
      - sources: de-duplicated source labels from the retrieved chunks (order preserved)
      - chunks:  the raw retrieved chunks (with distances) for inspection/evaluation
    """
    chunks = retrieve(question, k=k)
    answer = generate_answer(question, chunks)

    # Only attribute sources when the system actually answered.
    sources: list[str] = []
    if answer.strip() != REFUSAL:
        seen = set()
        for c in chunks:
            label = _source_label(c["metadata"])
            if label not in seen:
                seen.add(label)
                sources.append(label)

    return {"answer": answer, "sources": sources, "chunks": chunks}


if __name__ == "__main__":
    import sys

    q = " ".join(sys.argv[1:]) or "What do students say about Professor Marsh's exams?"
    result = ask(q)
    print(f"Q: {q}\n")
    print(f"ANSWER:\n{result['answer']}\n")
    print("SOURCES:")
    for s in result["sources"]:
        print(f"  • {s}")
    if not result["sources"]:
        print("  (none — system declined to answer)")

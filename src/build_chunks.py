"""Build the chunk corpus and write it to data/chunks.json.

Run: python -m src.build_chunks
This is the hand-off artifact between Milestone 3 (chunking) and Milestone 4 (embedding).
"""

from __future__ import annotations

import json
from pathlib import Path

from .chunk import chunk_corpus

OUT_PATH = Path(__file__).resolve().parent.parent / "data" / "chunks.json"


def main() -> None:
    chunks = chunk_corpus()
    OUT_PATH.parent.mkdir(exist_ok=True)
    OUT_PATH.write_text(json.dumps(chunks, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {len(chunks)} chunks to {OUT_PATH.relative_to(OUT_PATH.parent.parent)}")


if __name__ == "__main__":
    main()

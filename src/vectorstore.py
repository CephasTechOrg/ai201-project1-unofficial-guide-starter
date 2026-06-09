"""Milestone 4 — embedding + vector store + retrieval.

Embeds each chunk with all-MiniLM-L6-v2 (sentence-transformers) and stores it in a
persistent ChromaDB collection along with its metadata. Retrieval embeds the query with
the same model and returns the top-k chunks by cosine distance (lower = more similar).

Build the index:   python -m src.vectorstore --build
Test retrieval:     python -m src.vectorstore
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

ROOT = Path(__file__).resolve().parent.parent
CHUNKS_PATH = ROOT / "data" / "chunks.json"
CHROMA_PATH = ROOT / "chroma_db"
COLLECTION_NAME = "unofficial_guide"
MODEL_NAME = "all-MiniLM-L6-v2"

_model: SentenceTransformer | None = None


def get_model() -> SentenceTransformer:
    """Load the embedding model once and reuse it."""
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def load_chunks() -> list[dict]:
    if not CHUNKS_PATH.exists():
        raise FileNotFoundError(
            f"{CHUNKS_PATH} not found — run `python -m src.build_chunks` first."
        )
    return json.loads(CHUNKS_PATH.read_text(encoding="utf-8"))


def build_index(reset: bool = True) -> chromadb.api.models.Collection.Collection:
    """Embed all chunks and (re)load them into ChromaDB. Cosine distance space."""
    chunks = load_chunks()
    client = chromadb.PersistentClient(path=str(CHROMA_PATH))
    if reset:
        try:
            client.delete_collection(COLLECTION_NAME)
        except Exception:
            pass  # collection didn't exist yet
    collection = client.get_or_create_collection(
        COLLECTION_NAME, metadata={"hnsw:space": "cosine"}
    )
    texts = [c["text"] for c in chunks]
    print(f"Embedding {len(texts)} chunks with {MODEL_NAME} ...")
    embeddings = get_model().encode(
        texts, show_progress_bar=True, normalize_embeddings=True
    ).tolist()
    collection.add(
        ids=[c["id"] for c in chunks],
        documents=texts,
        embeddings=embeddings,
        metadatas=[c["metadata"] for c in chunks],
    )
    print(f"Indexed {collection.count()} chunks into {CHROMA_PATH.name}/")
    return collection


def get_collection() -> chromadb.api.models.Collection.Collection:
    client = chromadb.PersistentClient(path=str(CHROMA_PATH))
    return client.get_collection(COLLECTION_NAME)


def retrieve(query: str, k: int = 5, collection=None) -> list[dict]:
    """Return the top-k chunks for a query as {id, text, metadata, distance} dicts."""
    collection = collection or get_collection()
    q_emb = get_model().encode([query], normalize_embeddings=True).tolist()
    res = collection.query(query_embeddings=q_emb, n_results=k)
    return [
        {"id": _id, "text": doc, "metadata": meta, "distance": dist}
        for _id, doc, meta, dist in zip(
            res["ids"][0], res["documents"][0], res["metadatas"][0], res["distances"][0]
        )
    ]


# The 5 evaluation questions from planning.md (q5 is the designed failure case).
EVAL_QUERIES = [
    "What do students say about Professor Marsh's exams in CS 201?",
    "Which CS professor is best for someone who has never programmed before?",
    "How should I prepare for CS 310 Algorithms with Professor Patel?",
    "Which two CS classes should I avoid taking in the same semester?",
    'Which CS professor has the highest "would take again" rating?',
]


def _demo_retrieval(queries: list[str], k: int = 5) -> None:
    collection = get_collection()
    for q in queries:
        print("\n" + "=" * 80)
        print(f"QUERY: {q}")
        print("=" * 80)
        for i, hit in enumerate(retrieve(q, k=k, collection=collection), 1):
            m = hit["metadata"]
            tag = m.get("professor") or m.get("extra") or m["source"]
            preview = hit["text"].split("\n", 1)[-1][:160].replace("\n", " ")
            print(f"  {i}. dist={hit['distance']:.3f}  [{m['chunk_type']}] "
                  f"{tag} ({m['source']})")
            print(f"     {preview}...")


if __name__ == "__main__":
    if "--build" in sys.argv:
        build_index()
    else:
        _demo_retrieval(EVAL_QUERIES)

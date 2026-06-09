"""Milestone 5 — grounded answer generation with Groq.

Grounding is enforced two ways:
  1. A strict system prompt that tells the model to answer ONLY from the supplied
     context and to refuse with a fixed sentence when the context is insufficient.
  2. The context is the *only* source of facts in the prompt — retrieved chunks are
     numbered and labeled with their source filename so answers stay traceable.

Source attribution itself is NOT left to the model — it is appended programmatically
from the retrieved chunks' metadata in query.py.
"""

from __future__ import annotations

import os

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

MODEL = "llama-3.3-70b-versatile"
REFUSAL = "I don't have enough information on that."

SYSTEM_PROMPT = (
    "You are The Unofficial Guide, an assistant that answers questions about student "
    "reviews of Computer Science professors at Lakemont University.\n\n"
    "Follow these rules strictly:\n"
    "1. Answer using ONLY the information in the CONTEXT below. Do not use any outside "
    "or general knowledge about these professors, courses, or universities.\n"
    f"2. If the CONTEXT does not contain enough information to answer, reply with exactly "
    f'this sentence and nothing else: "{REFUSAL}"\n'
    "3. Every fact in your answer must be traceable to the CONTEXT. Do not invent "
    "professor names, ratings, or course details that are not present.\n"
    "4. Be concise and specific. Refer to professors and courses by the names and "
    "numbers used in the CONTEXT.\n"
    "5. Do not list sources yourself — the system appends them automatically."
)

_client: Groq | None = None


def get_client() -> Groq:
    global _client
    if _client is None:
        key = os.environ.get("GROQ_API_KEY")
        if not key or key == "your_key_here":
            raise RuntimeError(
                "GROQ_API_KEY is not set. Copy .env.example to .env and add your key "
                "from https://console.groq.com"
            )
        _client = Groq(api_key=key)
    return _client


def build_context(chunks: list[dict]) -> str:
    """Render retrieved chunks as a numbered, source-labeled context block."""
    blocks = []
    for i, c in enumerate(chunks, 1):
        blocks.append(f"[{i}] (source: {c['metadata']['source']})\n{c['text']}")
    return "\n\n".join(blocks)


def generate_answer(question: str, chunks: list[dict], temperature: float = 0.1) -> str:
    """Generate a grounded answer from the retrieved chunks."""
    if not chunks:
        return REFUSAL
    context = build_context(chunks)
    user_msg = (
        f"CONTEXT:\n{context}\n\n"
        f"QUESTION: {question}\n\n"
        "Answer using only the CONTEXT above."
    )
    resp = get_client().chat.completions.create(
        model=MODEL,
        temperature=temperature,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
        ],
    )
    return resp.choices[0].message.content.strip()

"""Milestone 5 — Gradio query interface for The Unofficial Guide.

Run:  python app.py    then open http://localhost:7860

Input:  a plain-language question about Lakemont CS professors.
Output: a grounded answer (from retrieved reviews only) plus the source documents it
        drew from and the retrieved chunks with their distance scores.
"""

import gradio as gr

from src.query import ask

EXAMPLES = [
    "What do students say about Professor Marsh's exams in CS 201?",
    "Which CS professor is best for someone who has never programmed before?",
    "How should I prepare for CS 310 Algorithms with Professor Patel?",
    "Which two CS classes should I avoid taking in the same semester?",
    "What is the parking like near the CS building?",  # out-of-scope -> should refuse
]


def handle_query(question: str):
    if not question or not question.strip():
        return "Please enter a question.", "", ""
    result = ask(question)
    sources = "\n".join(f"• {s}" for s in result["sources"]) or "(none — system declined)"
    retrieved = "\n".join(
        f"[{i}] dist={c['distance']:.3f}  {c['metadata']['source']}\n    "
        f"{c['text'].splitlines()[-1][:140]}..."
        for i, c in enumerate(result["chunks"], 1)
    )
    return result["answer"], sources, retrieved


with gr.Blocks(title="The Unofficial Guide") as demo:
    gr.Markdown(
        "# 🎓 The Unofficial Guide\n"
        "Ask about CS professors at Lakemont University. Answers are grounded **only** in "
        "collected student reviews and forum threads, with sources cited."
    )
    inp = gr.Textbox(label="Your question", placeholder="e.g. How are Professor Tanaka's exams?")
    btn = gr.Button("Ask", variant="primary")
    answer = gr.Textbox(label="Answer", lines=6)
    sources = gr.Textbox(label="Sources (cited from retrieved documents)", lines=4)
    retrieved = gr.Textbox(label="Retrieved chunks (with distance scores)", lines=8)
    gr.Examples(EXAMPLES, inputs=inp)

    btn.click(handle_query, inputs=inp, outputs=[answer, sources, retrieved])
    inp.submit(handle_query, inputs=inp, outputs=[answer, sources, retrieved])


if __name__ == "__main__":
    demo.launch()

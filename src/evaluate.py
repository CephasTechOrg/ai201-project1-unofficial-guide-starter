"""Milestone 6 — run the 5 evaluation questions (plus an out-of-scope query) end-to-end.

Run:  python -m src.evaluate
Prints each question, its expected answer, the system's actual answer, cited sources, and
the retrieved chunks with distances — the raw material for the README evaluation report.
"""

from __future__ import annotations

from .query import ask

# (question, expected answer) from planning.md
EVAL = [
    (
        "What do students say about Professor Marsh's exams in CS 201?",
        "Exams come from the lecture slides, not the textbook; midterms are curved but "
        "the final is not; keeping up / attendance matters more than the readings.",
    ),
    (
        "Which CS professor is best for someone who has never programmed before?",
        "Professor Okonkwo (CS 101) — beginner-friendly, patient, clear rubrics.",
    ),
    (
        "How should I prepare for CS 310 Algorithms with Professor Patel?",
        "Do every practice problem (exams are variations); take Discrete (Bello, CS 210) "
        "first for proof skills; form a study group; expect disorganization but a generous curve.",
    ),
    (
        "Which two CS classes should I avoid taking in the same semester?",
        "Operating Systems (Lindqvist, CS 340) and Machine Learning (Tanaka, CS 420) — "
        "both ~20 hrs/week.",
    ),
    (
        'Which CS professor has the highest "would take again" rating?',
        "Okonkwo, 94% (DESIGNED FAILURE — needs aggregation across all 10 profiles).",
    ),
]

OUT_OF_SCOPE = "What is the parking like near the CS building?"


def _report(question: str, expected: str | None) -> None:
    result = ask(question)
    print("\n" + "=" * 88)
    print(f"Q: {question}")
    if expected:
        print(f"\nEXPECTED: {expected}")
    print(f"\nSYSTEM ANSWER:\n{result['answer']}")
    print("\nSOURCES:")
    for s in result["sources"] or ["(none — declined)"]:
        print(f"  • {s}")
    print("\nRETRIEVED CHUNKS:")
    for i, c in enumerate(result["chunks"], 1):
        print(f"  [{i}] dist={c['distance']:.3f}  {c['id']}")


if __name__ == "__main__":
    for q, exp in EVAL:
        _report(q, exp)
    print("\n\n########## OUT-OF-SCOPE (should refuse) ##########")
    _report(OUT_OF_SCOPE, "N/A — not covered by any document; system should decline.")

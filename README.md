# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

**Student reviews of Computer Science professors at Lakemont University.** This system makes the
real, student-to-student knowledge about CS courses searchable — teaching style, exam difficulty,
workload, grading leniency, and which professors to take (or avoid) for a given course. Official
course catalogs list a class's topics and credits but never tell you that Patel's exams are
all proofs, that Okonkwo is the right first class for a non-coder, or that you shouldn't stack
OS and ML in the same semester. That knowledge lives in scattered reviews and forum threads,
is hard to search across, and is exactly what a grounded RAG system can surface.

> Corpus note: documents are *synthetic* samples modeled on Rate My Professors pages and Reddit
> threads (a fictional university avoids publishing negative claims about real professors, and
> real RMP/Reddit content blocks scraping). The pipeline is source-agnostic — real `.txt`/PDF
> files can be dropped into `documents/raw/` later. See [`documents/SOURCES.md`](documents/SOURCES.md).

---

## Document Sources

12 documents in two formats (review pages + forum threads) for structural variety. Full index
with notes: [`documents/SOURCES.md`](documents/SOURCES.md).

| #  | Source                                              | Type          | File path                                         |
|----|-----------------------------------------------------|---------------|---------------------------------------------------|
| 1  | RateMyProfessors — Prof. Elena Marsh (CS 201)       | Review page   | `documents/raw/rmp_marsh_cs201.txt`               |
| 2  | RateMyProfessors — Prof. David Okonkwo (CS 101)     | Review page   | `documents/raw/rmp_okonkwo_cs101.txt`             |
| 3  | RateMyProfessors — Prof. Rajesh Patel (CS 310)      | Review page   | `documents/raw/rmp_patel_cs310.txt`               |
| 4  | RateMyProfessors — Prof. Sarah Lindqvist (CS 340)   | Review page   | `documents/raw/rmp_lindqvist_cs340.txt`           |
| 5  | RateMyProfessors — Prof. Michael Brennan (CS 325)   | Review page   | `documents/raw/rmp_brennan_cs325.txt`             |
| 6  | RateMyProfessors — Prof. Yuki Tanaka (CS 420)       | Review page   | `documents/raw/rmp_tanaka_cs420.txt`              |
| 7  | RateMyProfessors — Prof. Carla Mendez (CS 230)      | Review page   | `documents/raw/rmp_mendez_cs230.txt`              |
| 8  | RateMyProfessors — Prof. Thomas Reed (CS 250)       | Review page   | `documents/raw/rmp_reed_cs250.txt`                |
| 9  | RateMyProfessors — Prof. Aisha Bello (CS 210)       | Review page   | `documents/raw/rmp_bello_cs210.txt`               |
| 10 | RateMyProfessors — Prof. Gregory Halvorsen (CS 350) | Review page   | `documents/raw/rmp_halvorsen_cs350.txt`           |
| 11 | r/LakemontU — "Best CS electives senior year?"      | Reddit thread | `documents/raw/reddit_cs_electives_thread.txt`    |
| 12 | r/LakemontU — "Is Patel as bad as people say?"      | Reddit thread | `documents/raw/reddit_algorithms_prof_thread.txt` |

---

## Chunking Strategy

<!-- Describe your chunking approach with enough specificity that someone else could reproduce it.
     Include:
     - Chunk size (characters or tokens) and why that size fits your documents
     - Overlap size and why (or why not) you used overlap
     - Any preprocessing you did before chunking (e.g., stripping HTML, removing headers)
     - What your final chunk count was across all documents -->

**Chunk size:**

**Overlap:**

**Why these choices fit your documents:**

**Final chunk count:**

---

## Embedding Model

<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->

**Model used:**

**Production tradeoff reflection:**

---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction:**

**How source attribution is surfaced in the response:**

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

<!-- Identify at least one question where retrieval or generation did not work as expected.
     Write a specific explanation of *why* it failed, tied to a part of the pipeline.

     "The answer was wrong" is not an explanation.

     "The relevant information was split across a chunk boundary, so retrieval returned
     only half the context — the model didn't have enough to answer correctly" is an explanation.

     "The embedding model treated the professor's nickname as out-of-vocabulary and returned
     results from an unrelated review" is an explanation. -->

**Question that failed:**

**What the system returned:**

**Root cause (tied to a specific pipeline stage):**

**What you would change to fix it:**

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:**

**One way your implementation diverged from the spec, and why:**

---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you
     change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->

**Instance 1**

- *What I gave the AI:*
- *What it produced:*
- *What I changed or overrode:*

**Instance 2**

- *What I gave the AI:*
- *What it produced:*
- *What I changed or overrode:*

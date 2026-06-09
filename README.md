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

We use **structure-aware chunking** rather than a fixed-character split: the chunker splits each
document on its natural semantic boundary. Implemented in [`src/chunk.py`](src/chunk.py).

- **Review pages** → one "profile" chunk (overall quality, *would-take-again %*, difficulty,
  tags) plus **one chunk per student review**.
- **Forum threads** → one chunk for the original post, plus **one chunk per top-level comment
  grouped with its nested replies**.

**Preprocessing before chunking** ([`src/ingest.py`](src/ingest.py)): strip site boilerplate
(RMP nav bar, cookie notice, `[ ★ Rate … ]` action bar, `👍 Helpful (n)` counters, "Load more",
footer; Reddit vote bars, "View N more comments", archived notice, footer, separators) and decode
HTML entities. A `[Professor | Course | Source]` context header is then prepended to every chunk.

**Chunk size:** one review/comment per chunk — typically 250–550 characters, with a hard cap of
**~800 characters** (longer comments are split at sentence boundaries). Measured range across the
corpus: 226–604 chars, average 372.

**Overlap:** **none (0 characters).** Each review/comment is an independent opinion, so overlap
would bleed one student's words into a neighbor's chunk. Standalone retrievability is achieved
instead by the prepended context header — overlap matters when splitting *continuous prose* where
a fact straddles a boundary, which is not our situation.

**Why these choices fit our documents:** the corpus is dominated by short, opinion-dense reviews
where the key fact lives in a single 2–5 sentence unit. A fixed 500-char split would cut reviews
mid-sentence and merge two unrelated students into one embedding; whole-document chunks would
average four topics into one vector that matches no specific query well. One review per chunk +
the header keeps each chunk to one coherent, attributable thought.

**Final chunk count:** **61 chunks** (10 profiles, 40 reviews, 2 posts, 9 comments) from 12
documents — inside the healthy 50–2,000 range.

### Sample chunks (5 labeled, with source)

```
[1] source: rmp_marsh_cs201.txt
[Prof. Elena Marsh | CS 201 Data Structures | RateMyProfessors review · Mar 2024 · quality 5.0/5, difficulty 4.0/5]
Marsh is hard but genuinely one of the best professors in the CS department. Her exams come
straight from the lecture slides, not the textbook... Midterms are curved, the final is not.

[2] source: rmp_okonkwo_cs101.txt  (profile chunk — keeps the would-take-again metric)
[Prof. David Okonkwo | CS 101 Intro to Programming | RateMyProfessors profile]
Overall quality 4.7/5. Would take again: 94%. Difficulty 2.1/5. Common student tags: CARING,
BEGINNER FRIENDLY, CLEAR GRADING CRITERIA, INSPIRATIONAL, GIVES GOOD FEEDBACK.

[3] source: rmp_tanaka_cs420.txt
[Prof. Yuki Tanaka | CS 420 Machine Learning | RateMyProfessors review · May 2023 · quality 3.5/5, difficulty 5.0/5]
Brilliant but assumes a lot. If you haven't taken a probability course you'll struggle with the
Bayesian material. The reading load (2-3 papers a week) is no joke.

[4] source: reddit_cs_electives_thread.txt  (comment chunk)
[r/LakemontU thread: "Best CS electives to take senior year?" | reply by u/lurker2021]
Avoid stacking 340 (OS, Lindqvist) and 420 (ML, Tanaka) together unless you hate sleep. Both are
20-hour-a-week classes.

[5] source: reddit_algorithms_prof_thread.txt  (comment + nested reply grouped)
[r/LakemontU thread: "CS 310 Algorithms — is Patel really as bad as people say?" | reply by u/survived_310]
Patel is brilliant but disorganized... If you do every practice problem he posts, the exams are
variations of those. Don't wait, just go in prepared.
↳ reply (u/needto_grad): The "syllabus is fiction" line is sending me. Ok, doing the practice problems religiously.
```

---

## Embedding Model

**Model used:** `all-MiniLM-L6-v2` via `sentence-transformers`, stored in **ChromaDB** with
cosine distance ([`src/vectorstore.py`](src/vectorstore.py)). It runs locally with no API key or
rate limits, produces 384-dim vectors, and handles ~256 tokens per input — our header-plus-review
chunks fit comfortably. Retrieval uses **top-k = 5**.

**Production tradeoff reflection:** if deployed for real users with cost no object, I'd weigh:
- **Accuracy on domain text** — a larger model (`all-mpnet-base-v2`, or a hosted OpenAI/Cohere
  embedding) distinguishes near-synonyms like "curved" vs "lenient grading" better, at higher
  latency and (for hosted) per-query cost.
- **Context length** — MiniLM's ~256-token cap is fine for short reviews but would truncate
  long syllabi or guides; a long-context model matters if documents grow.
- **Multilingual support** — MiniLM is English-centric; multilingual reviews would need a model
  like `paraphrase-multilingual-MiniLM`.
- **Local vs. API** — local keeps potentially sensitive student reviews private and removes rate
  limits/cost, at a lower accuracy ceiling. For this domain I'd lean local even in production,
  largely for privacy.

### Retrieval test results (top results, cosine distance — lower is better)

| Query | Top chunk | Distance | Why it's relevant |
|-------|-----------|----------|-------------------|
| "…Professor Marsh's exams in CS 201?" | Marsh CS 201 review | **0.339** | Directly states exams come from lecture slides, midterms curved |
| "…best for someone who has never programmed before?" | Okonkwo CS 101 review (top 3 all Okonkwo) | **0.367** | "If you have never written a line of code… take CS 101 with Okonkwo" |
| "…prepare for CS 310 Algorithms with Patel?" | Algorithms thread comment | **0.192** | All 5 hits from the Patel thread — study group, practice problems, take Discrete first |

All top results are well below the 0.5 relevance threshold. (By contrast, the out-of-scope
"parking" query's best match is 0.768 — correctly far above threshold.)

---

## Grounded Generation

The generator is Groq's `llama-3.3-70b-versatile` ([`src/generate.py`](src/generate.py)), called
at temperature 0.1. Grounding is enforced two ways:

**1. System prompt instruction** (verbatim, abbreviated):
> "Answer using ONLY the information in the CONTEXT below. Do not use any outside or general
> knowledge about these professors, courses, or universities. If the CONTEXT does not contain
> enough information to answer, reply with exactly this sentence and nothing else: *'I don't have
> enough information on that.'* Every fact in your answer must be traceable to the CONTEXT. Do not
> invent professor names, ratings, or course details that are not present."

**2. Structural choices:** the retrieved chunks are the *only* facts placed in the prompt. They
are numbered and labeled with their source filename (`[1] (source: rmp_marsh_cs201.txt) …`). If
retrieval returns nothing, the code short-circuits to the refusal before any model call.

**How source attribution is surfaced:** attribution is **not** left to the model — it is appended
programmatically in [`src/query.py`](src/query.py) from the retrieved chunks' metadata
(`source` + `professor`/`course` or thread title). The model is explicitly told *not* to list
sources itself. When the model returns the refusal sentence, the source list is suppressed (an
"I don't know" answer has no sources to cite).

### Example responses (with source attribution)

**In-scope #1 — "What do students say about Professor Marsh's exams in CS 201?"**
> Students say Professor Marsh's exams in CS 201 come straight from the lecture slides, not the
> textbook. Midterms are curved, but the final is not.
> **Sources:** `rmp_marsh_cs201.txt (Prof. Elena Marsh — CS 201 Data Structures)`

**In-scope #2 — "Which two CS classes should I avoid taking in the same semester?"**
> You should avoid taking CS 340 (OS, Lindqvist) and CS 420 (ML, Tanaka) in the same semester.
> **Sources:** `reddit_cs_electives_thread.txt (u/lurker2021)` and others from that thread.

**Out-of-scope — "What is the parking like near the CS building?"**
> I don't have enough information on that.
> **Sources:** (none — the system declined; no document covers parking, best match distance 0.768)

---

## Query Interface

A **Gradio web app** ([`app.py`](app.py)) — a single page; there is no separate backend to start,
the app loads retrieval + generation in-process.

**Input field:**
- *Your question* (textbox) — a plain-language question about Lakemont CS professors.

**Output fields:**
- *Answer* — the grounded response (or the refusal sentence).
- *Sources* — the document(s) the answer drew from, cited from metadata.
- *Retrieved chunks* — the top-5 chunks with cosine distance scores, for transparency.

**Sample interaction transcript:**
```
Your question:  Which two CS classes should I avoid taking in the same semester?

Answer:         You should avoid taking CS 340 (OS, Lindqvist) and CS 420 (ML, Tanaka)
                in the same semester.

Sources:        • reddit_cs_electives_thread.txt (u/lurker2021)
                • reddit_cs_electives_thread.txt (u/ml_or_bust)

Retrieved:      [1] dist=0.403  reddit_cs_electives_thread.txt::5
                    Avoid stacking 340 (OS, Lindqvist) and 420 (ML, Tanaka)...
                [2] dist=0.439  reddit_cs_electives_thread.txt::2 ...
```

### Running the system

```bash
# one-time setup
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env            # then put your Groq API key in .env

# build the index (run once, or after changing documents)
python -m src.build_chunks      # documents -> data/chunks.json
python -m src.vectorstore --build   # chunks -> ChromaDB

# launch the app  (open http://localhost:7860)
python app.py
```

---

## Evaluation Report

Run with `python -m src.evaluate`. Results below are the actual system output.

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | What do students say about Professor Marsh's exams in CS 201? | Exams from lecture slides not textbook; midterms curved, final not; attendance matters | "Exams come straight from the lecture slides, not the textbook. Midterms are curved, but the final is not." | Relevant (top dist 0.339) | **Accurate** |
| 2 | Which professor is best for someone who has never programmed before? | Okonkwo (CS 101) — beginner-friendly, patient, clear rubrics | "Prof. David Okonkwo is the best… great for beginners, slows down, gentle pace, transparent grading." | Relevant (top 3 all Okonkwo, 0.367) | **Accurate** |
| 3 | How should I prepare for CS 310 Algorithms with Patel? | Practice problems; take Discrete first; study group; expect disorganization but a curve | "Form a study group, do every practice problem… a foundation in proofs from Discrete (CS 210) helps… expect disorganization but use the generous curve." | Relevant (all 5 from Patel thread, 0.192) | **Accurate** |
| 4 | Which two CS classes should I avoid taking the same semester? | OS (340, Lindqvist) and ML (420, Tanaka) — both ~20 hrs/week | "Avoid taking CS 340 (OS, Lindqvist) and CS 420 (ML, Tanaka) in the same semester." | Relevant (top dist 0.403) | **Accurate** |
| 5 | Which professor has the highest "would take again" rating? | Okonkwo, 94% | "Prof. Michael Brennan has the highest… at 68%." | **Partially relevant** — retrieved only Patel (51%) & Brennan (68%) profiles; Okonkwo's 94% not retrieved | **Inaccurate** (see Failure Case) |

**Summary:** 4/5 accurate and grounded; Q5 inaccurate by design (the planned failure case).

---

## Failure Case Analysis

**Question that failed:** Q5 — *"Which CS professor has the highest 'would take again' rating?"*

**What the system returned:** "Prof. Michael Brennan has the highest 'would take again' rating at
68%." This is **wrong** — the correct answer is Okonkwo at 94%.

**Root cause (tied to the retrieval stage):** this is an *aggregation/ranking* question — it
requires comparing the would-take-again value across **all 10** professor profile chunks. But
semantic retrieval returns only the top-k chunks most textually *similar* to the query, not a
global maximum. At k=5 the retriever surfaced two profile chunks (Patel 51%, Brennan 68%) plus
three loosely-related electives comments; **Okonkwo's 94% profile was never retrieved.** The LLM
then did exactly what it was told — it grounded its answer in the supplied context and correctly
picked the max of what it could see (Brennan, 68%). So this is *not* a hallucination (68% is
Brennan's real number) and *not* a generation bug — it is an inherent limitation of
retrieval-only RAG: **it does similarity search, not aggregation.**

**What I would change to fix it:** (a) detect superlative/aggregation queries ("highest",
"most", "how many") and route them to a metadata query over *all* profiles instead of top-k
semantic search; or (b) raise k high enough to include every profile chunk for this query class;
or (c) precompute a small structured table of per-professor stats and let the model read the
whole table for ranking questions. Each trades simplicity for coverage on this query type.

---

## Spec Reflection

**One way the spec helped you during implementation:** Deciding the chunking strategy in
`planning.md` *before* writing code meant the chunker had one clear target — "one review/comment
per chunk, with a `[Professor | Course | Source]` header, no overlap." Because the decision and
its reasoning were already written down, implementation was a direct translation rather than a
series of guesses, and I could tell immediately whether the generated code matched the plan.

**One way your implementation diverged from the spec, and why:** The spec described "one chunk
per student review," but during implementation I added a separate **profile chunk** per professor
holding the overall ratings (including the would-take-again %). Pure review chunks would have
thrown those numbers away entirely, leaving evaluation question 5 not just hard but *impossible*
(the data wouldn't exist in the index). Adding the profile chunk keeps the metric retrievable, so
Q5 fails for the *right* reason — aggregation, not missing data. I also added a comment-cleanup
step (stripping Reddit vote lines) that the spec didn't anticipate, discovered by inspecting
sample chunks.

---

## AI Usage

I used **Claude (Claude Code)** throughout, in the way the milestones intend: I made the design
decisions and directed the work; Claude generated and refined the implementation under that
direction, and I reviewed and corrected its output.

**Instance 1 — chunking pipeline**

- *What I gave the AI:* my `planning.md` Chunking Strategy section and the document descriptions,
  and a choice between fixed-size, whole-document, and structure-aware chunking.
- *What it produced:* I chose structure-aware; Claude implemented `clean_document()` and
  `chunk_document()` in `src/`, then printed 5 sample chunks and the total count for inspection.
- *What I changed or overrode:* on reviewing the samples I saw the comment chunks still contained
  the Reddit vote line (`▲ 40  u/justpassing  •  7 mo. ago`). I directed it to strip that chrome,
  and it refactored the forum parser so each comment chunk holds only the comment text under its
  header.

**Instance 2 — grounded generation**

- *What I gave the AI:* the grounding requirement — answer from retrieved context only, refuse
  with a fixed sentence when context is insufficient — and the rule that source attribution must
  be programmatic, not produced by the model.
- *What it produced:* the strict system prompt in `src/generate.py` and the `ask()` orchestration
  in `src/query.py` that builds the source list from chunk metadata.
- *What I changed or overrode:* I confirmed the system prompt *enforces* grounding (fixed refusal
  sentence, "do not invent" rules) rather than merely suggesting it, and that the model is told
  **not** to list sources so attribution can't drift from what was actually retrieved.

**Instance 3 — process / version control**

- *What I gave the AI:* direction on how to handle git.
- *What it produced:* it had committed a milestone for me.
- *What I changed or overrode:* I had it **reverse** the commit (`git reset --soft`, local-only)
  and instructed it never to commit on my behalf — I manage all commits myself.

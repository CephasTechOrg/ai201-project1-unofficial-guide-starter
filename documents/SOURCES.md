# Document Sources — The Unofficial Guide

**Domain:** Student reviews of Computer Science professors at Lakemont University (fictional).

> ⚠️ **Note on the corpus:** These are *synthetic* documents generated to resemble real
> Rate My Professors review pages and Reddit threads. They were authored for this project
> because (a) real RMP/Reddit content is JavaScript-rendered and blocks scraping, and
> (b) using a fictional university avoids publishing negative claims about real professors.
> The structure, noise (nav menus, cookie banners, footers), and writing style mirror real
> sources so the ingestion/cleaning pipeline is realistic. Swap in real `.txt`/PDF documents
> later by dropping them in `documents/raw/` — the pipeline is source-agnostic.

| #  | Source (simulated)                              | Type                | File path                                          |
|----|-------------------------------------------------|---------------------|----------------------------------------------------|
| 1  | RateMyProfessors — Prof. Elena Marsh (CS 201)   | Review page         | `documents/raw/rmp_marsh_cs201.txt`                |
| 2  | RateMyProfessors — Prof. David Okonkwo (CS 101) | Review page         | `documents/raw/rmp_okonkwo_cs101.txt`              |
| 3  | RateMyProfessors — Prof. Rajesh Patel (CS 310)  | Review page         | `documents/raw/rmp_patel_cs310.txt`                |
| 4  | RateMyProfessors — Prof. Sarah Lindqvist (CS 340)| Review page        | `documents/raw/rmp_lindqvist_cs340.txt`            |
| 5  | RateMyProfessors — Prof. Michael Brennan (CS 325)| Review page        | `documents/raw/rmp_brennan_cs325.txt`              |
| 6  | RateMyProfessors — Prof. Yuki Tanaka (CS 420)   | Review page         | `documents/raw/rmp_tanaka_cs420.txt`               |
| 7  | RateMyProfessors — Prof. Carla Mendez (CS 230)  | Review page         | `documents/raw/rmp_mendez_cs230.txt`               |
| 8  | RateMyProfessors — Prof. Thomas Reed (CS 250)   | Review page         | `documents/raw/rmp_reed_cs250.txt`                 |
| 9  | RateMyProfessors — Prof. Aisha Bello (CS 210)   | Review page         | `documents/raw/rmp_bello_cs210.txt`                |
| 10 | RateMyProfessors — Prof. Gregory Halvorsen (CS 350)| Review page      | `documents/raw/rmp_halvorsen_cs350.txt`            |
| 11 | r/LakemontU — "Best CS electives senior year?"  | Reddit thread       | `documents/raw/reddit_cs_electives_thread.txt`     |
| 12 | r/LakemontU — "Is Patel as bad as people say?"  | Reddit thread       | `documents/raw/reddit_algorithms_prof_thread.txt`  |

## Structural variety (matters for chunking decisions in Milestone 2)

- **Review pages (1–10):** each holds 4 short, self-contained student reviews (2–5 sentences)
  tagged with course number, quality/difficulty scores, and date. Opinion-dense; key facts
  concentrated per review. Wrapped in nav/cookie/footer boilerplate that must be cleaned.
- **Reddit threads (11–12):** longer, nested back-and-forth where a single answer can span an
  original comment plus replies. Facts are spread across a conversation, not concentrated.

These two shapes argue for review-aware chunking (split on the review/comment boundary) rather
than a blind fixed-character split — to be specified in `planning.md`.

## Candidate questions this corpus can answer

1. What do students say about Professor Marsh's exams in CS 201?
2. Which CS professor is best for someone who has never coded before?
3. Is CS 310 Algorithms with Patel survivable, and how do students recommend preparing?
4. Which class has the heaviest workload, and which two should you avoid taking together?
5. Which professor gives the most useful feedback on assignments?

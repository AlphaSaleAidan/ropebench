# Self-improvement journal

Autonomous R&D session started 2026-07-04. Goal: keep testing and improving the
Jumping Rope theory + RopeBench, generate independent sub-theories, harden with
massive repetition, upgrade docs/visuals. Each entry: what was tried, what the
numbers said, what shipped.

## Core theory (as upgraded)
Externalized, dense, *structured* session memory with a retrieval tier beats
replaying the transcript: it fits when the transcript doesn't, it costs far
less, and it destroys the summarization every framework ships — at a small,
honest accuracy cost vs the (often-impossible) full-transcript oracle.

## Independent sub-theories to test
- T1: memory-hierarchy value grows super-linearly with session length
- T2: notation density has a floor — past X% compression, recall degrades
- T3: structured state (rope sections) beats flat dense text for a reader
- T4: retrieval quality sets the optimal rope budget
- T5: recency/section ordering affects recall
- T6: model capability × retrieval — stronger models exploit the vault more

## Log

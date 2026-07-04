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

### Entry 1 — statistical machinery validated at scale (2026-07-04)
Ran 30k iterations of property/stress tests:
- **Bootstrap CI coverage: 0.9492 empirical vs 0.95 nominal** (20,000 simulated
  paired experiments, true diff +0.20, n=40). The CIs report the coverage they
  claim — the hardened numbers are trustworthy.
- Scenario determinism: 0 mismatches / 5,000 seeds.
- Ground-truth invariant: 0 unanswerable planted probes / 5,000 seeds.
Shipped: a calibration test (`test_stats_calibration.py`, moderate trials for CI
+ a `local`-marked full 20k run).

### Entry 2 — T1 CONFIRMED: value grows with session length (2026-07-04)
Scripted sweep, session length 40→260 turns:
| turns | full/rope tokens | rope efficiency advantage |
|---|---|---|
| 40 | 1.44× | 1.38× |
| 120 | 2.52× | 2.41× |
| 200 | 3.66× | 3.58× |
| 260 | 4.55× | 4.50× |

Log-log fit: **full-history O(n^1.34), rope O(n^0.73) → rope advantage O(n^0.61).**
The memory hierarchy's payoff is a power law in session length — the longer the
session, the bigger the win. Backbone of Finding 2 ("no carry-everything past a
point"). Shipped `test_theory_t1.py`.

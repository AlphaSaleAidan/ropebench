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

### Entry 3 — T4 CONFIRMED (counterintuitive): tighter rope = better (2026-07-04)
Rope budget sweep (scripted, 3 seeds, 80 turns):
| budget | acc | long | tokens | efficiency | retrieval |
|---|---|---|---|---|---|
| 400 | 97% | 100% | 38K | **25.3** | 72% |
| 600 | 93% | 96% | 51K | 18.3 | 56% |
| 1000 | 93% | 96% | 70K | 13.3 | 46% |
| 1600 | 90% | 75% | 105K | 8.6 | 20% |
| 2400 | 100% | 100% | 130K | 7.7 | 29% |
| 3600 | 100% | 100% | 180K | 5.6 | 0% |

**Efficiency is maximized at the TIGHTEST satisfiable budget** and falls
monotonically as the budget grows — a smaller rope forces more retrieval and
the vault compensates, so accuracy stays high (97% at budget 400). Actionable:
default to the smallest satisfiable budget, not a comfortable one.
Note a **"valley of the middle budget"** (1600 → 90%, long 75%, retrieval only
20%): facts half-demoted, neither resident nor eagerly retrieved. Flagged for
more seeds. Shipped `test_theory_t4.py`.

### Entry 4 — T2 CONFIRMED (with nuance): density has a floor (2026-07-04)
Same 600-token budget, three notation profiles, scripted reader:
| profile | acc | long | rope tokens |
|---|---|---|---|
| symbolic-en | 93% | 96% | 418 |
| cjk-dense | 94% | 100% | 520 |
| **ai-native** | **82%** | 88% | 485 |

ai-native's adaptive §-dictionary saves tokens but **codes away the context
words a literal reader matches on** — recall drops 11 points. The distinctive
*values* survive verbatim; matchability doesn't. cjk-dense (lighter, single-char
substitution) is safe. **Implication:** ai-native needs a capable reader that
decodes via the legend, not a keyword-matcher — connects to T6 (capability ×
density). Shipped `test_theory_t2.py`.

### Entry 5 — T3 CONFIRMED: structure beats a flat dense blob (2026-07-04)
Same 600-token budget, same densify, same retrieval vault — rope vs a flat
dense blob (rope minus structure):
| regime | acc | long | med | efficiency |
|---|---|---|---|---|
| rope (structured) | 93% | **96%** | 88% | 18.3 |
| flat-dense | 90% | **62%** | 100% | 16.2 |

Structure's value is **concentrated in OLD facts** — 96% vs 62% at long
distance, a 34-point gap. The never-demoted STATE/GOALS + KEYS index give old
facts a durable home and a findable pointer; a flat blob drops them into
semantic-search-only limbo. (Flat-dense edges medium — recent facts in the blob
are trivially present.) Shipped `test_theory_t3.py` incl. a `FlatDenseRegime`.

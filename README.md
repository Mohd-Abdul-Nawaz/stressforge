# StressForge

**Differential stress-tester** for puzzle solutions: run your fast candidate against a slow-but-obviously-correct brute-force oracle on hundreds of seeded random inputs. First mismatch is printed with its seed so anyone can reproduce it.

Built by **Mohd Abdul Nawaz** · Python · MIT

## Why this exists

Sample tests lie. Hidden edge cases — all-negative arrays, ties, overflow, off-by-one windows — only surface under randomized differential testing. StressForge is the standard competitive-programming loop, packaged as a reusable CLI:

```
candidate (fast)  ─┐
                   ├─► same random input ─► diff outputs
oracle (brute)    ─┘                              │ mismatch? save seed + input
```

## Quickstart

```bash
pip install -e .

# correct Kadane vs O(n^2) oracle — 200 random cases
python -m stressforge examples/max-subarray/fast.py examples/max-subarray/oracle.py

# buggy variant (fails all-negative arrays) — exposes a counterexample in seconds
python -m stressforge examples/max-subarray/fast_bug.py examples/max-subarray/oracle.py

# more cases, custom generator
python -m stressforge fast.py oracle.py --generator max-subarray --cases 1000
```

Success:

```
generator: max-subarray  cases: 200
result: 200/200 matched — no differences found
```

Mismatch:

```
result: MISMATCH on case #7 (seed=7)
--- input ---
5
-3 -8 -2 -9 -5
--- fast output ---
0
--- oracle output ---
-2
reproduce: seed=7 generator=max-subarray
```

## Writing your own check

1. Write `oracle.py` — brute force, clarity over speed.
2. Write `fast.py` — your optimized solution (same stdin/stdout contract).
3. Add a generator in `stressforge/generators.py`: a function `(seed) -> (seed, input_text)` using `random.Random(seed)`.
4. Run `stressforge fast.py oracle.py --generator <name> --cases 500`.

Comparison is whitespace-insensitive (`normalize`), per-case timeouts default to 5 s, and `--continue-all` runs every case instead of stopping at the first mismatch.

## Testing

```bash
python -m unittest discover -s tests -v
```

Covers: correct solution matches oracle across 30 cases, buggy solution is exposed with a reproducing seed, missing-file and bad-argument errors.

## Layout

```
StressForge/
  stressforge/        # engine.py, generators.py, cli.py
  examples/max-subarray/  # fast.py, fast_bug.py, oracle.py
  tests/test_stress.py
  .github/workflows/ci.yml
```

## Skills demonstrated

Differential testing, oracle design, seeded reproducible randomness, subprocess isolation — the debugging half of **Puzzle Solver (Coding)** work: turning "works on samples" into "provably matches brute force on 1000 random cases".

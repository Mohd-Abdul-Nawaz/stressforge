"""Command-line interface for StressForge."""

from __future__ import annotations

import argparse
from pathlib import Path

from . import __version__
from .engine import stress
from .generators import GENERATORS


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="stressforge", description="Differential stress-tester: fast solution vs brute-force oracle."
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("fast", type=Path, help="candidate solution (.py)")
    parser.add_argument("oracle", type=Path, help="brute-force oracle (.py)")
    parser.add_argument("--generator", default="max-subarray", choices=sorted(GENERATORS),
                        help="random input generator")
    parser.add_argument("--cases", type=int, default=200, help="number of random cases")
    parser.add_argument("--timeout", type=float, default=5.0, help="per-case timeout in seconds")
    parser.add_argument("--continue-all", action="store_true",
                        help="run all cases instead of stopping at first mismatch")
    return parser


def main(argv: list | None = None) -> int:
    args = build_parser().parse_args(argv)
    generate = GENERATORS[args.generator]
    report = stress(
        args.fast, args.oracle, generate,
        cases=args.cases, timeout_s=args.timeout,
        stop_on_first=not args.continue_all,
    )
    print(f"generator: {args.generator}  cases: {args.cases}")
    print(f"fast:   {args.fast}")
    print(f"oracle: {args.oracle}")
    print(f"max time: fast {report.max_fast_ms:.1f} ms | oracle {report.max_oracle_ms:.1f} ms")
    if report.mismatches == 0:
        print(f"result: {report.total}/{report.total} matched — no differences found")
        return 0
    fail = report.first_failure
    print(f"result: MISMATCH on case #{fail.index} (seed={fail.seed})")
    print("--- input ---")
    print(fail.input_text, end="" if fail.input_text.endswith("\n") else "\n")
    print("--- fast output ---")
    print(fail.fast_stdout or "(empty)")
    print("--- oracle output ---")
    print(fail.oracle_stdout or "(empty)")
    if fail.stderr:
        print(f"--- stderr ---\n{fail.stderr}")
    print(f"reproduce: seed={fail.seed} generator={args.generator}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

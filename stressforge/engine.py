"""Core differential-testing engine: run two programs on random inputs, diff outputs."""

from __future__ import annotations

import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path


class StressError(RuntimeError):
    """Raised for unusable solutions (missing file, crash, timeout on every case)."""


@dataclass(frozen=True)
class CaseOutcome:
    index: int
    seed: int
    input_text: str
    fast_stdout: str
    oracle_stdout: str
    match: bool
    fast_ms: float
    oracle_ms: float
    stderr: str = ""


@dataclass(frozen=True)
class StressReport:
    total: int
    mismatches: int
    first_failure: CaseOutcome | None
    max_fast_ms: float
    max_oracle_ms: float


def run_program(command: list, stdin_text: str, timeout_s: float) -> tuple:
    """Run one program; return (returncode, stdout, stderr, elapsed_ms, timed_out)."""
    start = time.perf_counter()
    try:
        proc = subprocess.run(
            command,
            input=stdin_text,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout_s,
        )
    except subprocess.TimeoutExpired as exc:
        elapsed = (time.perf_counter() - start) * 1000.0
        partial = exc.stdout.decode() if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        return -1, partial or "", "timed out", elapsed, True
    elapsed = (time.perf_counter() - start) * 1000.0
    return proc.returncode, proc.stdout or "", proc.stderr or "", elapsed, False


def command_for(solution: str | Path) -> list:
    path = Path(solution)
    if not path.is_file():
        raise StressError(f"solution not found: {path}")
    if path.suffix.lower() == ".py":
        return [sys.executable, str(path.resolve())]
    raise StressError(f"only .py solutions supported, got {path.suffix!r}")


def normalize(text: str) -> str:
    return " ".join(text.split())


def stress(
    fast: str | Path,
    oracle: str | Path,
    generate,
    *,
    cases: int = 200,
    timeout_s: float = 5.0,
    stop_on_first: bool = True,
) -> StressReport:
    """Run `cases` random inputs through both programs and compare normalized output."""
    fast_cmd = command_for(fast)
    oracle_cmd = command_for(oracle)
    if cases <= 0:
        raise StressError("cases must be positive")

    mismatches = 0
    first_failure = None
    max_fast = 0.0
    max_oracle = 0.0

    for i in range(cases):
        seed, input_text = generate(i)
        code_f, out_f, err_f, ms_f, to_f = run_program(fast_cmd, input_text, timeout_s)
        code_o, out_o, err_o, ms_o, to_o = run_program(oracle_cmd, input_text, timeout_s)
        max_fast = max(max_fast, ms_f)
        max_oracle = max(max_oracle, ms_o)

        if to_f or to_o or code_f != 0 or code_o != 0:
            detail = err_f.strip() or err_o.strip() or f"exit fast={code_f} oracle={code_o}"
            outcome = CaseOutcome(i, seed, input_text, out_f, out_o, False, ms_f, ms_o, detail)
            mismatches += 1
            if first_failure is None:
                first_failure = outcome
            if stop_on_first:
                break
            continue

        match = normalize(out_f) == normalize(out_o)
        if not match:
            mismatches += 1
            outcome = CaseOutcome(i, seed, input_text, out_f, out_o, False, ms_f, ms_o)
            if first_failure is None:
                first_failure = outcome
            if stop_on_first:
                break

    return StressReport(cases, mismatches, first_failure, max_fast, max_oracle)

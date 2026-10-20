"""StressForge engine tests — no subprocess randomness beyond tiny local programs."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from stressforge.engine import StressError, normalize, stress
from stressforge.generators import GENERATORS

EXAMPLES = REPO / "examples" / "max-subarray"


class NormalizeTests(unittest.TestCase):
    def test_whitespace_insensitive(self):
        self.assertEqual(normalize("1 2\n3\n"), normalize("1  2  3"))

    def test_detects_difference(self):
        self.assertNotEqual(normalize("5"), normalize("6"))


class StressTests(unittest.TestCase):
    def test_correct_fast_matches_oracle(self):
        report = stress(
            EXAMPLES / "fast.py", EXAMPLES / "oracle.py",
            GENERATORS["max-subarray"], cases=30,
        )
        self.assertEqual(report.mismatches, 0)
        self.assertIsNone(report.first_failure)

    def test_buggy_fast_is_exposed_with_repro_seed(self):
        report = stress(
            EXAMPLES / "fast_bug.py", EXAMPLES / "oracle.py",
            GENERATORS["max-subarray"], cases=200,
        )
        self.assertGreater(report.mismatches, 0)
        self.assertIsNotNone(report.first_failure)
        # The saved seed must reproduce the exact input.
        seed, again = GENERATORS["max-subarray"](report.first_failure.seed)
        self.assertEqual(again, report.first_failure.input_text)

    def test_missing_solution_raises(self):
        with self.assertRaises(StressError):
            stress(REPO / "nope.py", EXAMPLES / "oracle.py",
                   GENERATORS["max-subarray"], cases=2)

    def test_nonpositive_cases_rejected(self):
        with self.assertRaises(StressError):
            stress(EXAMPLES / "fast.py", EXAMPLES / "oracle.py",
                   GENERATORS["max-subarray"], cases=0)


if __name__ == "__main__":
    unittest.main()

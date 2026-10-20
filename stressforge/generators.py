"""Seeded random input generators for bundled examples."""

from __future__ import annotations

import random


def max_subarray(seed: int, *, n_min: int = 1, n_max: int = 30) -> tuple:
    rng = random.Random(seed)
    n = rng.randint(n_min, n_max)
    arr = [rng.randint(-10, 10) for _ in range(n)]
    return seed, f"{n}\n{' '.join(map(str, arr))}\n"


GENERATORS = {"max-subarray": max_subarray}

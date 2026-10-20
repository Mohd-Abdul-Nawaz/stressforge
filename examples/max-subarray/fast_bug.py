"""Buggy candidate: resets to 0 on negatives — fails all-negative arrays."""
import sys


def main() -> None:
    data = list(map(int, sys.stdin.read().split()))
    if not data:
        return
    arr = data[1:1 + data[0]]
    best = cur = 0
    for x in arr:
        cur = max(0, cur + x)
        best = max(best, cur)
    print(best)


if __name__ == "__main__":
    main()

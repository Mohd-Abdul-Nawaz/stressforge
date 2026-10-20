"""Kadane's algorithm: O(n) candidate for max-subarray."""
import sys


def main() -> None:
    data = list(map(int, sys.stdin.read().split()))
    if not data:
        return
    arr = data[1:1 + data[0]]
    best = cur = arr[0]
    for x in arr[1:]:
        cur = max(x, cur + x)
        best = max(best, cur)
    print(best)


if __name__ == "__main__":
    main()

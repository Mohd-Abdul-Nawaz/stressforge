"""Brute-force oracle for max-subarray: O(n^2), obviously correct."""
import sys


def main() -> None:
    data = list(map(int, sys.stdin.read().split()))
    if not data:
        return
    arr = data[1:1 + data[0]]
    best = arr[0]
    for i in range(len(arr)):
        total = 0
        for j in range(i, len(arr)):
            total += arr[j]
            best = max(best, total)
    print(best)


if __name__ == "__main__":
    main()

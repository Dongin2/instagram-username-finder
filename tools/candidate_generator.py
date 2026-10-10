"""Generate four-character Instagram username candidates without network requests.

Usage:
    python tools/candidate_generator.py --count 100 --start 0
    python tools/candidate_generator.py --count 100 --start 100 --output candidates.csv

Review candidates manually in Instagram's username-change screen.
A missing public profile does NOT establish registration availability.
"""
import argparse
import csv
import itertools
from pathlib import Path

LETTERS = "abcdefghijklmnopqrstuvwxyz"
DIGITS = "0123456789"
# Interleave letter/digit patterns so generated names are not all alike.
PATTERNS = ("LLDD", "LDLD", "DLLD", "LDDL", "DDLL", "DLDL",
            "LLLD", "LLDL", "LDLL", "DLLL", "LDDD", "DLDD", "DDLD", "DDDL")


def candidates():
    for pattern in PATTERNS:
        alphabets = [LETTERS if c == "L" else DIGITS for c in pattern]
        for parts in itertools.product(*alphabets):
            yield "".join(parts)


def main():
    parser = argparse.ArgumentParser(description="Offline 4-character username candidates")
    parser.add_argument("--count", type=int, default=100)
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--output", default="data/candidates.csv")
    args = parser.parse_args()
    if args.count < 1 or args.start < 0 or args.count > 10000:
        parser.error("count must be 1..10000 and start must be >= 0")
    from itertools import islice
    selected = list(islice(candidates(), args.start, args.start + args.count))
    target = Path(args.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["username", "manual_status", "notes"])
        writer.writerows((name, "unchecked", "") for name in selected)
    print(f"Saved {len(selected)} offline candidates to {target}")
    print("Check in Instagram manually; no username is verified available.")


if __name__ == "__main__":
    main()

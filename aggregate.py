#!/usr/bin/env python3
"""
GRC Proposal #2 — Aggregated Restitution List Generator

Fetches authoritative payout data from each case repository and produces
restitution_aggregated.csv with one row per unique address, amounts summed
across all sources.

Deduplication design:
  - source_overrides.json (gonka_248_and_250_-epoch_loss) is the single
    authoritative layer for epochs 248-252. Only rows with status=package_payout
    are included; external_proposed rows are already covered by another source
    and excluded to avoid double-counting.
  - Case 2 (GRC-e247-preserver-audit) is an external source that the epoch-loss
    repo treats as already-paid. It is loaded separately from its own repo.
  - Case 3a (consensus_failure_restriction) covers epoch 249 only (248 and 250
    removed from that package). It is loaded separately from its own repo.
  - Case 4 (GRC-e254-api-issue) covers epoch 254 and is loaded from its own repo.

Sources:
  Case2    github.com/gonkalabs/GRC-e247-preserver-audit
           output/issue2_per_participant.csv | addr: participant_address | amt: total_lost_gonka

  Case3a   github.com/huxuxuya/-consensus_failure_restriction
           artifacts/compensation_calculation.csv | addr: address | amt: compensation_gnk
           (epoch 249 only — 248 and 250 excluded from this package)

  Case3b   github.com/huxuxuya/gonka_248_and_250_-epoch_loss
  Case3c   docs/source_overrides.json | filter: status=package_payout
  Case3d   sources: epoch-248-compensation-package (248),
                    epoch-250-compensation-package (250),
                    grc-e247-preserver-audit-remaining (249/251/252)

  Case4    github.com/votkon/GRC-e254-api-issue
           compensation.csv | addr: address | amt: compensation_gonka
"""

import csv
import io
import json
import urllib.request
from collections import defaultdict

SOURCE_OVERRIDES_URL = (
    "https://raw.githubusercontent.com/huxuxuya/gonka_248_and_250_-epoch_loss"
    "/main/docs/source_overrides.json"
)

CSV_SOURCES = {
    "Case2": (
        "https://raw.githubusercontent.com/gonkalabs/GRC-e247-preserver-audit"
        "/main/output/issue2_per_participant.csv",
        "participant_address",
        "total_lost_gonka",
    ),
    "Case3a": (
        "https://raw.githubusercontent.com/huxuxuya/-consensus_failure_restriction"
        "/main/artifacts/compensation_calculation.csv",
        "address",
        "compensation_gnk",
    ),
    "Case4": (
        "https://raw.githubusercontent.com/votkon/GRC-e254-api-issue"
        "/main/compensation.csv",
        "address",
        "compensation_gonka",
    ),
}

# Map source_overrides source names to case labels
OVERRIDE_SOURCE_LABELS = {
    "epoch-248-compensation-package": "Case3b_248",
    "epoch-250-compensation-package": "Case3c_250",
    "grc-e247-preserver-audit-remaining": "Case3d_remaining",
}


def fetch_csv(url: str) -> list[dict]:
    with urllib.request.urlopen(url) as resp:
        return list(csv.DictReader(io.TextIOWrapper(resp, encoding="utf-8")))


def fetch_json(url: str):
    with urllib.request.urlopen(url) as resp:
        return json.load(resp)


def main():
    totals: dict[str, float] = defaultdict(float)
    case_tags: dict[str, list[str]] = defaultdict(list)

    # Load CSV-based sources
    for case_name, (url, addr_col, amt_col) in CSV_SOURCES.items():
        print(f"Fetching {case_name} ...")
        rows = fetch_csv(url)
        count = 0
        for row in rows:
            amount = float(row[amt_col])
            if amount <= 0:
                continue
            addr = row[addr_col].strip()
            totals[addr] += amount
            if case_name not in case_tags[addr]:
                case_tags[addr].append(case_name)
            count += 1
        print(f"  {count} non-zero entries")

    # Load source_overrides.json — package_payout entries only
    print("Fetching source_overrides.json ...")
    overrides = fetch_json(SOURCE_OVERRIDES_URL)
    package_entries = [o for o in overrides if o["status"] == "package_payout"]
    counts: dict[str, int] = defaultdict(int)
    for o in package_entries:
        src = o["source"]
        if src not in OVERRIDE_SOURCE_LABELS:
            continue
        amount = float(o["source_compensation_gnk"])
        if amount <= 0:
            continue
        addr = o["address"].strip()
        label = OVERRIDE_SOURCE_LABELS[src]
        totals[addr] += amount
        if label not in case_tags[addr]:
            case_tags[addr].append(label)
        counts[src] += 1
    for src, label in OVERRIDE_SOURCE_LABELS.items():
        src_total = sum(
            float(o["source_compensation_gnk"])
            for o in package_entries
            if o["source"] == src and float(o["source_compensation_gnk"]) > 0
        )
        print(f"  {label}: {counts[src]} entries, {src_total:.6f} GNK")

    sorted_addresses = sorted(totals.items(), key=lambda x: x[1], reverse=True)
    grand_total = sum(v for _, v in sorted_addresses)

    output_path = "restitution_aggregated.csv"
    with open(output_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["address", "total_gnk", "cases"])
        for addr, total in sorted_addresses:
            writer.writerow([addr, f"{total:.6f}", ",".join(case_tags[addr])])

    print(f"\nWrote {len(sorted_addresses)} addresses to {output_path}")
    print(f"Grand total: {grand_total:.6f} GNK")


if __name__ == "__main__":
    main()

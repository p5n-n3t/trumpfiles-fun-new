#!/usr/bin/env python3
"""Validate source-recovery results against their deterministic packet."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "data/neon-workbench/external/people-enrichment-2026-10-25/source-recovery"


def rows(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def valid_url(value: object) -> bool:
    if not isinstance(value, str):
        return False
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--packet", required=True)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    input_path = BASE / "packets" / args.packet
    output_path = BASE / "results" / args.packet
    expected = {row["entry_number"] for row in rows(input_path)}
    findings = []
    observed = set()
    for index, row in enumerate(rows(output_path), 1):
        number = row.get("entry_number")
        label = f"{args.packet}:{index}"
        if not isinstance(number, int) or number not in expected:
            findings.append(f"{label}: outside or invalid entry")
            continue
        if number in observed:
            findings.append(f"{label}: duplicate entry")
            continue
        observed.add(number)
        status = row.get("status")
        sources = row.get("sources")
        if status not in {"source_found", "no_credible_source"}:
            findings.append(f"{label}: invalid status")
        if not isinstance(sources, list) or len(sources) > 2:
            findings.append(f"{label}: sources must be a list of up to two")
            continue
        if status == "source_found" and not sources:
            findings.append(f"{label}: source_found without source")
        if status == "no_credible_source" and sources:
            findings.append(f"{label}: no_credible_source carries source")
        if not isinstance(row.get("reason"), str) or not row["reason"].strip():
            findings.append(f"{label}: missing reason")
        for source in sources:
            if not isinstance(source, dict) or not valid_url(source.get("url")):
                findings.append(f"{label}: invalid source URL")
    if observed != expected:
        findings.append(f"{args.packet}: missing {len(expected - observed)} entries")
    result = {"status": "PASS" if not findings else "FAIL", "expected": len(expected), "observed": len(observed), "findings": findings}
    report = args.report or BASE / "results" / (args.packet.removesuffix(".jsonl") + "-validation.json")
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if not findings else 1


if __name__ == "__main__":
    raise SystemExit(main())

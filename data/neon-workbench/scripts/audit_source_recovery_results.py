#!/usr/bin/env python3
"""Audit source-recovery packet coverage and source-result quality signals."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "data/neon-workbench/external/people-enrichment-2026-10-25/source-recovery"
REPORT = ROOT / "data/neon-workbench/reports/source_recovery_audit_2026-10-25.json"


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> int:
    manifest = json.loads((BASE / "manifest.json").read_text(encoding="utf-8"))
    expected = {Path(packet["file"]).name for packet in manifest["packets"]}
    result_paths = sorted((BASE / "results").glob("source-recovery-*.jsonl"))
    observed = {path.name for path in result_paths}
    statuses = Counter()
    publishers = Counter()
    concerns: list[dict] = []
    for path in result_paths:
        for line_number, row in enumerate(read_jsonl(path), 1):
            statuses[row.get("status", "missing")] += 1
            if row.get("status") == "source_found":
                for source in row.get("sources", []):
                    publisher = str(source.get("publisher") or "unknown").strip()
                    publishers[publisher] += 1
                    parsed = urlparse(str(source.get("url") or ""))
                    if parsed.scheme != "https" or not parsed.netloc:
                        concerns.append({"file": path.name, "line": line_number, "entry_number": row.get("entry_number"), "issue": "non_https_or_invalid_url"})
                    if not str(source.get("title") or "").strip():
                        concerns.append({"file": path.name, "line": line_number, "entry_number": row.get("entry_number"), "issue": "missing_source_title"})
            if row.get("status") == "no_credible_source" and len(str(row.get("reason") or "").strip()) < 16:
                concerns.append({"file": path.name, "line": line_number, "entry_number": row.get("entry_number"), "issue": "thin_no_source_reason"})
    report = {
        "scope": "result-file audit only; no data is changed",
        "expected_packets": len(expected),
        "completed_packets": len(observed),
        "remaining_packets": sorted(expected - observed),
        "terminal_rows": sum(statuses.values()),
        "status_counts": dict(sorted(statuses.items())),
        "top_publishers": publishers.most_common(25),
        "concerns": concerns,
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "concerns"}, indent=2))
    print(f"concerns={len(concerns)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

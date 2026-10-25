#!/usr/bin/env python3
"""Partition people-enrichment inputs by whether they contain an evidence URL."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
INPUT_ROOT = ROOT / "data/neon-workbench/external/people-enrichment-2026-10-25"
OUT_ROOT = INPUT_ROOT / "evidence-partitions"
URL = re.compile(r"https?://", re.I)


def main() -> int:
    supported: list[dict] = []
    recovery: list[dict] = []
    for path in sorted((INPUT_ROOT / "packets").glob("people-*.jsonl")):
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            target = supported if URL.search(json.dumps([row.get("sources"), row.get("fact_check_sources")])) else recovery
            target.append(row)
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    result = {}
    for name, rows in (("url-supported", supported), ("source-recovery", recovery)):
        directory = OUT_ROOT / name
        directory.mkdir(exist_ok=True)
        manifest = []
        for offset in range(0, len(rows), 100):
            packet = rows[offset:offset + 100]
            filename = f"{name}-{offset // 100 + 1:03d}.jsonl"
            path = directory / filename
            path.write_text("\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in packet) + "\n", encoding="utf-8")
            manifest.append({
                "file": filename,
                "count": len(packet),
                "entry_range": [packet[0]["entry_number"], packet[-1]["entry_number"]],
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            })
        (directory / "manifest.json").write_text(json.dumps({"records": len(rows), "packets": manifest}, indent=2) + "\n", encoding="utf-8")
        result[name] = {"records": len(rows), "packets": len(manifest)}
    (OUT_ROOT / "summary.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

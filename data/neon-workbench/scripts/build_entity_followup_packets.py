#!/usr/bin/env python3
"""Build entity-extraction packets from validated source-recovery results."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "data/neon-workbench/external/people-enrichment-2026-10-25/source-recovery"
OUT = BASE / "entity-inputs"


def rows(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    built = []
    for result_path in sorted((BASE / "results").glob("source-recovery-*.jsonl")):
        packet_path = BASE / "packets" / result_path.name
        if not packet_path.exists():
            raise SystemExit(f"missing original packet for {result_path.name}")
        source_rows = {row["entry_number"]: row for row in rows(result_path)}
        packet_rows = rows(packet_path)
        if set(source_rows) != {row["entry_number"] for row in packet_rows}:
            raise SystemExit(f"coverage mismatch: {result_path.name}")
        out_rows = []
        for record in packet_rows:
            research = source_rows[record["entry_number"]]
            out_rows.append({
                "entry_number": record["entry_number"],
                "title": record.get("title"),
                "synopsis": record.get("synopsis"),
                "date_start": record.get("date_start"),
                "research_status": research.get("status"),
                "supported_event_claim": research.get("supported_event_claim"),
                "sources": research.get("sources", []),
                "research_reason": research.get("reason"),
            })
        target = OUT / result_path.name
        target.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in out_rows), encoding="utf-8")
        built.append(target.name)
    manifest = {"packets": built, "count": len(built), "instruction": "Extract people/organizations only from supplied fields and recovered URLs; never browse or infer."}
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

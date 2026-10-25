#!/usr/bin/env python3
"""Summarize offline people/entity enrichment coverage without touching canonical data."""

from __future__ import annotations

import json
import sqlite3
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
WORK = ROOT / "data/neon-workbench/external/people-enrichment-2026-10-25"
DB = ROOT / "data/neon-workbench/working/schema_v2_entity_enrichment_staged.sqlite"
REPORT = ROOT / "data/neon-workbench/reports/entity_enrichment_coverage_2026-10-25.json"


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> int:
    manifest = json.loads((WORK / "manifest.json").read_text(encoding="utf-8"))
    all_entry_ids = {
        row["entry_number"]
        for packet in manifest["packets"]
        for row in read_jsonl(WORK / packet["file"])
    }
    original_files = sorted((WORK / "results").glob("people-*.jsonl"))
    original_rows = [row for path in original_files for row in read_jsonl(path)]
    original_counts = Counter(row["status"] for row in original_rows)

    recovery_root = WORK / "source-recovery"
    recovery_manifest = json.loads((recovery_root / "manifest.json").read_text(encoding="utf-8"))
    recovery_entry_ids = {
        row["entry_number"]
        for packet in recovery_manifest["packets"]
        for row in read_jsonl(recovery_root / packet["file"])
    }
    recovery_files = sorted((recovery_root / "results").glob("source-recovery-*.jsonl"))
    recovery_rows = [row for path in recovery_files for row in read_jsonl(path)]
    recovery_counts = Counter(row["status"] for row in recovery_rows)

    entity_files = sorted((recovery_root / "entity-results").glob("source-recovery-*.jsonl"))
    entity_rows = [row for path in entity_files for row in read_jsonl(path)]
    entity_counts = Counter(row["status"] for row in entity_rows)

    conn = sqlite3.connect(DB)
    try:
        proposed_entries, proposed_links = conn.execute(
            "SELECT count(DISTINCT entry_number), count(*) FROM proposed_entry_entities"
        ).fetchone()
        kind_rows = conn.execute(
            "SELECT entity_kind, count(*) FROM proposed_entry_entities GROUP BY entity_kind ORDER BY entity_kind"
        ).fetchall()
    finally:
        conn.close()

    report = {
        "scope": "offline proposal lane only; frozen/canonical/Neon/live Neo4j unchanged",
        "legacy_blank_people_tag_entries": len(all_entry_ids),
        "original_packet_results": {
            "packets": len(original_files),
            "entries_terminally_classified": len(original_rows),
            "status_counts": dict(sorted(original_counts.items())),
            "entries_not_yet_classified": len(all_entry_ids - {row["entry_number"] for row in original_rows}),
        },
        "source_recovery": {
            "eligible_entries": len(recovery_entry_ids),
            "packets_completed": len(recovery_files),
            "entries_terminally_researched": len(recovery_rows),
            "status_counts": dict(sorted(recovery_counts.items())),
            "entity_followups_completed": len(entity_files),
            "entity_followup_entries": len(entity_rows),
            "entity_status_counts": dict(sorted(entity_counts.items())),
        },
        "proposed_relationships": {
            "entries_with_at_least_one_link": proposed_entries,
            "links": proposed_links,
            "by_kind": dict(kind_rows),
        },
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

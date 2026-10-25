#!/usr/bin/env python3
"""Build deterministic, disjoint packets for source-backed people enrichment.

The packets contain only entries whose legacy people_tags are blank.  They are
proposal inputs: workers return a separate overlay and must not alter any
catalogue record or assign relationships without a source URL and evidence.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_DB = ROOT / "data/neon-workbench/working/schema_v2_entity_enrichment_staged.sqlite"
DEFAULT_OUT = ROOT / "data/neon-workbench/external/people-enrichment-2026-10-25"
INSTRUCTIONS = """For each entry, identify only named people and organizations explicitly involved in the documented event. Do not infer a person from an office, a family relationship, a party, a location, a pronoun, or a source byline. Every proposed person/entity link must cite one of the supplied source URLs and a short evidence claim. Use roles only: subject, actor, official, target, mentioned. If the record/source does not identify a person, return an empty list and explain why. Do not change canonical records, assign new entry numbers, or create live database/Neo4j data."""


def json_value(value: str | None) -> object:
    if not value:
        return []
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return []


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--packet-size", type=int, default=100)
    args = parser.parse_args()
    if args.packet_size < 1 or args.packet_size > 250:
        raise SystemExit("packet size must be in 1..250")
    args.out.mkdir(parents=True, exist_ok=True)
    packets_dir = args.out / "packets"
    packets_dir.mkdir(exist_ok=True)
    conn = sqlite3.connect(f"file:{args.db}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            """SELECT entry_number,title,date_start,date_end,synopsis,rationale,category,subcategory,
                      keywords,sources,fact_check_sources,people_tags
                 FROM trump_entries
                WHERE people_tags IS NULL OR trim(people_tags) IN ('','[]','null')
                ORDER BY entry_number"""
        ).fetchall()
    finally:
        conn.close()
    manifest = {"run_id": "people-enrichment-2026-10-25", "packet_size": args.packet_size, "record_count": len(rows), "instructions": INSTRUCTIONS, "packets": []}
    for start in range(0, len(rows), args.packet_size):
        chunk = rows[start:start + args.packet_size]
        name = f"people-{start // args.packet_size + 1:03d}.jsonl"
        path = packets_dir / name
        lines = []
        for row in chunk:
            record = {key: row[key] for key in ("entry_number","title","date_start","date_end","synopsis","rationale","category","subcategory")}
            record["keywords"] = json_value(row["keywords"])
            record["sources"] = json_value(row["sources"])
            record["fact_check_sources"] = json_value(row["fact_check_sources"])
            lines.append(json.dumps(record, ensure_ascii=False, separators=(",", ":")))
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        manifest["packets"].append({"file": str(path.relative_to(args.out)), "count": len(chunk), "entry_range": [chunk[0]["entry_number"], chunk[-1]["entry_number"]], "sha256": digest})
    (args.out / "INSTRUCTIONS.md").write_text(f"# People and organization enrichment\n\n{INSTRUCTIONS}\n", encoding="utf-8")
    (args.out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "ok", "records": len(rows), "packets": len(manifest["packets"]), "out": str(args.out)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

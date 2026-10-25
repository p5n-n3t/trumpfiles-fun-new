#!/usr/bin/env python3
"""Create focused research packets for blank-tag entries lacking a usable URL."""

from __future__ import annotations

import hashlib
import json
import re
import sqlite3
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
DB = ROOT / "data/neon-workbench/working/schema_v2_entity_enrichment_staged.sqlite"
OUT = ROOT / "data/neon-workbench/external/people-enrichment-2026-10-25/source-recovery"
URL = re.compile(r"https?://", re.I)


def parse(value: str | None) -> object:
    try:
        return json.loads(value) if value else []
    except json.JSONDecodeError:
        return []


def has_url(*values: object) -> bool:
    return bool(URL.search(json.dumps(values, ensure_ascii=False)))


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    packets = OUT / "packets"
    packets.mkdir(exist_ok=True)
    conn = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    try:
        source = conn.execute(
            """SELECT entry_number,title,date_start,date_end,synopsis,rationale,category,subcategory,
                      keywords,suggested_source_query,entry_links,fact_check,fact_check_sources,sources
                 FROM trump_entries
                WHERE people_tags IS NULL OR trim(people_tags) IN ('','[]','null')
                ORDER BY entry_number"""
        ).fetchall()
    finally:
        conn.close()
    rows = []
    for record in source:
        if has_url(record["sources"], record["fact_check_sources"]):
            continue
        rows.append({
            "entry_number": record["entry_number"],
            "title": record["title"],
            "date_start": record["date_start"],
            "date_end": record["date_end"],
            "synopsis": record["synopsis"],
            "rationale": record["rationale"],
            "category": record["category"],
            "subcategory": record["subcategory"],
            "keywords": parse(record["keywords"]),
            "suggested_source_query": record["suggested_source_query"],
            "entry_links": parse(record["entry_links"]),
            "fact_check": record["fact_check"],
            "fact_check_sources": parse(record["fact_check_sources"]),
            "legacy_sources": parse(record["sources"]),
        })
    manifest = {"run_id": "people-source-recovery-2026-10-25", "records": len(rows), "packets": []}
    for offset in range(0, len(rows), 25):
        chunk = rows[offset:offset + 25]
        name = f"source-recovery-{offset // 25 + 1:03d}.jsonl"
        path = packets / name
        path.write_text("\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in chunk) + "\n", encoding="utf-8")
        manifest["packets"].append({
            "file": f"packets/{name}", "count": len(chunk),
            "entry_range": [chunk[0]["entry_number"], chunk[-1]["entry_number"]],
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        })
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    (OUT / "INSTRUCTIONS.md").write_text(
        "# Source recovery\n\n"
        "For each assigned record, locate at most two credible original or high-quality secondary sources for the central event. "
        "Search with title, date, named people, keywords, and suggested source query. Return one terminal JSONL object per entry: "
        "entry_number, status (source_found or no_credible_source), sources (URL/title/publisher/date/confidence), "
        "supported_event_claim, and reason. Do not draft new entry text, infer wrongdoing, or change any database. "
        "A search-results URL is never a source.\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": "ok", "records": len(rows), "packets": len(manifest["packets"])}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

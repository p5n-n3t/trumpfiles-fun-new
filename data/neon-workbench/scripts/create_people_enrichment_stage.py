#!/usr/bin/env python3
"""Create an offline, evidence-ready entity-enrichment SQLite stage.

The frozen export and existing graph stage remain read-only inputs.  This
script copies the graph stage, adds the minimal v2 relationship fields, and
records only schema/metadata changes.  It never guesses people or writes Neon.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sqlite3
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_SOURCE = ROOT / "data/neon-workbench/working/schema_v2_graph_staged.sqlite"
DEFAULT_TARGET = ROOT / "data/neon-workbench/working/schema_v2_entity_enrichment_staged.sqlite"
DEFAULT_REPORT = ROOT / "data/neon-workbench/reports/entity_enrichment_stage_2026-10-25.json"


def has_column(conn: sqlite3.Connection, table: str, column: str) -> bool:
    return any(row[1] == column for row in conn.execute(f"PRAGMA table_info({table})"))


def add_tag_column(conn: sqlite3.Connection, column: str) -> None:
    if not has_column(conn, "trump_entries", column):
        conn.execute(f"ALTER TABLE trump_entries ADD COLUMN {column} TEXT NOT NULL DEFAULT '[]'")


def add_link_column(conn: sqlite3.Connection, column: str, definition: str) -> None:
    if not has_column(conn, "entity_entry_links", column):
        conn.execute(f"ALTER TABLE entity_entry_links ADD COLUMN {column} {definition}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--target", type=Path, default=DEFAULT_TARGET)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()

    if not args.source.exists():
        raise SystemExit(f"source database is missing: {args.source}")
    args.target.parent.mkdir(parents=True, exist_ok=True)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.target.with_name(f".{args.target.name}.tmp-{os.getpid()}")
    if temporary.exists():
        temporary.unlink()

    before = args.source.stat()
    source = sqlite3.connect(f"file:{args.source}?mode=ro", uri=True)
    target = sqlite3.connect(temporary)
    try:
        source.backup(target)
        source.close()
        target.execute("PRAGMA foreign_keys = ON")
        for column in ("organization_tags", "location_tags", "topic_tags"):
            add_tag_column(target, column)
        # Additive compatibility: old graph links remain valid, while newly
        # reviewed links can carry a directly inspectable source trail.
        add_link_column(target, "claim_text", "TEXT")
        add_link_column(target, "source_url", "TEXT")
        add_link_column(target, "provenance_type", "TEXT")
        target.executescript(
            """
            CREATE TABLE IF NOT EXISTS entity_entry_evidence (
              evidence_id TEXT PRIMARY KEY,
              entity_id TEXT NOT NULL,
              entry_number INTEGER NOT NULL,
              role TEXT NOT NULL CHECK (role IN ('subject','actor','official','target','mentioned')),
              source_url TEXT NOT NULL,
              evidence_claim TEXT NOT NULL,
              confidence REAL NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
              extraction_method TEXT NOT NULL CHECK (extraction_method IN ('human','model','imported')),
              review_status TEXT NOT NULL CHECK (review_status IN ('proposed','reviewed','accepted','rejected')),
              created_at TEXT NOT NULL,
              UNIQUE(entity_id, entry_number, role, source_url, evidence_claim)
            );
            CREATE INDEX IF NOT EXISTS idx_entity_evidence_entry ON entity_entry_evidence(entry_number);
            CREATE INDEX IF NOT EXISTS idx_entity_evidence_entity ON entity_entry_evidence(entity_id);
            """
        )
        target.execute(
            """CREATE TABLE IF NOT EXISTS entity_enrichment_runs (
              run_id TEXT PRIMARY KEY,
              input_source TEXT NOT NULL,
              record_count INTEGER NOT NULL,
              instructions_version TEXT NOT NULL,
              status TEXT NOT NULL,
              created_at TEXT NOT NULL
            )"""
        )
        target.commit()
        target.execute("PRAGMA foreign_key_check")
        target.commit()
    finally:
        target.close()
        source.close()

    after = args.source.stat()
    source_unchanged = before.st_mtime_ns == after.st_mtime_ns and before.st_size == after.st_size
    if not source_unchanged:
        temporary.unlink(missing_ok=True)
        raise SystemExit("source changed while staging; refusing to replace target")
    os.replace(temporary, args.target)
    db = sqlite3.connect(f"file:{args.target}?mode=ro", uri=True)
    try:
        report = {
            "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
            "offline_only": True,
            "source": str(args.source),
            "target": str(args.target),
            "source_unchanged": source_unchanged,
            "entries": db.execute("SELECT count(*) FROM trump_entries").fetchone()[0],
            "empty_people_tags": db.execute("SELECT count(*) FROM trump_entries WHERE people_tags IS NULL OR trim(people_tags) IN ('','[]','null')").fetchone()[0],
            "entity_entry_links": db.execute("SELECT count(*) FROM entity_entry_links").fetchone()[0],
            "entity_entry_evidence_rows": db.execute("SELECT count(*) FROM entity_entry_evidence").fetchone()[0],
            "status": "ok",
        }
    finally:
        db.close()
    args.report.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

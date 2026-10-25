#!/usr/bin/env python3
"""Load validated proposal records into the offline candidate staging table."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
DB = ROOT / "data/neon-workbench/working/schema_v2_entity_enrichment_staged.sqlite"
INPUT = ROOT / "data/neon-workbench/external/enrichment-discovery-2026-10-24/trumpfile/recovered-entry-drafts/standardized/standardized-proposals.jsonl"
RUN_ID = "trumpfile-second-pass-recovery-2026-10-25"


def main() -> int:
    rows = [json.loads(line) for line in INPUT.read_text(encoding="utf-8").splitlines() if line.strip()]
    conn = sqlite3.connect(DB)
    try:
        conn.execute("BEGIN IMMEDIATE")
        conn.execute("DELETE FROM staged_candidates WHERE run_id = ?", (RUN_ID,))
        for row in rows:
            metadata = row["proposal_metadata"]
            enrichment = row["enrichment"]
            review_status = {
                "new_candidate": "proposed_new",
                "expand_existing": "proposed_expand",
                "probable_duplicate_existing": "probable_duplicate",
            }[metadata["reconciliation_disposition"]]
            notes = json.dumps({
                "trumpfile_post_id": metadata["trumpfile_post_id"],
                "existing_entry_numbers": metadata["existing_entry_numbers"],
                "proposal_only": True,
                "contract_event_id": enrichment["identity"]["event_id"],
                "full_contract_path": str(INPUT.relative_to(ROOT)),
            }, separators=(",", ":"))
            conn.execute(
                """INSERT INTO staged_candidates
                   (id,run_id,entry_number,title,date_start,date_end,synopsis,category,subcategory,
                    evidence_class,source_urls,scores,review_status,reviewer_notes,created_at,published_at)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    enrichment["identity"]["event_id"], RUN_ID, None, enrichment["title"],
                    enrichment["dates"]["start"], enrichment["dates"]["end"],
                    enrichment["summaries"]["short"], enrichment["taxonomy"]["category"],
                    enrichment["taxonomy"]["subcategory"], "source-backed-recovery",
                    json.dumps(enrichment["sources"], separators=(",", ":")),
                    json.dumps(enrichment["metrics"], separators=(",", ":")), review_status, notes,
                    enrichment["provenance"]["enriched_at"], None,
                ),
            )
        conn.execute(
            """INSERT OR REPLACE INTO entity_enrichment_runs
               (run_id,input_source,record_count,instructions_version,status,created_at)
               VALUES (?,?,?,?,?,?)""",
            (RUN_ID, str(INPUT.relative_to(ROOT)), len(rows), "2026-10-25.1", "proposal_only", "2026-10-25T00:00:00Z"),
        )
        conn.commit()
        count = conn.execute("SELECT count(*) FROM staged_candidates WHERE run_id = ?", (RUN_ID,)).fetchone()[0]
        statuses = dict(conn.execute("SELECT review_status,count(*) FROM staged_candidates WHERE run_id = ? GROUP BY review_status", (RUN_ID,)))
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
    if count != len(rows):
        raise SystemExit(f"staging count mismatch: {count} != {len(rows)}")
    print(json.dumps({"status": "ok", "run_id": RUN_ID, "records": count, "review_statuses": statuses}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

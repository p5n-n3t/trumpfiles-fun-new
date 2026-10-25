#!/usr/bin/env python3
"""Stage validated people and organization proposals in the offline SQLite copy."""

from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
WORK_ROOT = ROOT / "data/neon-workbench/external/people-enrichment-2026-10-25"
DB = ROOT / "data/neon-workbench/working/schema_v2_entity_enrichment_staged.sqlite"
ROLES = {"subject", "actor", "official", "target", "mentioned"}
ENTITY_TYPES = {"organization", "agency", "company", "country", "media", "other"}


def jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def urls(value: object) -> set[str]:
    if isinstance(value, str):
        return {value} if value.startswith(("http://", "https://")) else set()
    if isinstance(value, list):
        return set().union(*(urls(item) for item in value)) if value else set()
    if isinstance(value, dict):
        return set().union(*(urls(item) for item in value.values())) if value else set()
    return set()


def proposal_id(entry: int, kind: str, name: str, role: str, source_url: str, claim: str) -> str:
    text = "|".join((str(entry), kind, name, role, source_url, claim))
    return "pep_" + hashlib.sha256(text.encode()).hexdigest()[:24]


def main() -> int:
    manifest = json.loads((WORK_ROOT / "manifest.json").read_text(encoding="utf-8"))
    inputs = {}
    for packet in manifest["packets"]:
        path = WORK_ROOT / packet["file"]
        inputs[path.name] = {row["entry_number"]: urls(row) for row in jsonl(path)}
    result_paths = sorted((WORK_ROOT / "results").glob("people-*.jsonl"))

    # Follow-up entity work may use a URL recovered in a separate, validated
    # source-recovery packet. Build its permitted URL set from that terminal
    # output rather than accepting any arbitrary worker-supplied URL.
    recovery_root = WORK_ROOT / "source-recovery"
    recovery_manifest_path = recovery_root / "manifest.json"
    followup_paths = sorted((recovery_root / "entity-results").glob("source-recovery-*.jsonl"))
    if followup_paths:
        recovery_manifest = json.loads(recovery_manifest_path.read_text(encoding="utf-8"))
        recovery_inputs = {
            Path(packet["file"]).name: {row["entry_number"] for row in jsonl(recovery_root / packet["file"])}
            for packet in recovery_manifest["packets"]
        }
        for result_path in followup_paths:
            recovered_path = recovery_root / "results" / result_path.name
            if not recovered_path.exists():
                raise SystemExit(f"missing recovered-source file for {result_path.name}")
            expected_ids = recovery_inputs.get(result_path.name)
            recovered_rows = jsonl(recovered_path)
            if expected_ids is None or {row.get("entry_number") for row in recovered_rows} != expected_ids:
                raise SystemExit(f"recovered-source coverage mismatch for {result_path.name}")
            inputs[result_path.name] = {
                row["entry_number"]: urls(row.get("sources")) if row.get("status") == "source_found" else set()
                for row in recovered_rows
            }
        result_paths.extend(followup_paths)
    if not result_paths:
        raise SystemExit("no worker result files found")
    rows = []
    for result_path in result_paths:
        expected = inputs.get(result_path.name)
        if expected is None:
            raise SystemExit(f"no matching input packet for {result_path.name}")
        observed = set()
        for record in jsonl(result_path):
            number = record.get("entry_number")
            if not isinstance(number, int) or number not in expected or number in observed:
                raise SystemExit(f"{result_path.name}: invalid or duplicate entry number")
            observed.add(number)
            status = record.get("status")
            people = record.get("people")
            organizations = record.get("organizations")
            if status not in {"enriched", "no_supported_people", "needs_source"} or not isinstance(people, list) or not isinstance(organizations, list):
                raise SystemExit(f"{result_path.name}:{number}: malformed result")
            for kind, items in (("person", people), ("organization", organizations)):
                for item in items:
                    role = item.get("role") if kind == "person" else "mentioned"
                    entity_type = "person" if kind == "person" else item.get("entity_type")
                    if not isinstance(item.get("name"), str) or not item["name"].strip() or role not in ROLES or (kind == "organization" and entity_type not in ENTITY_TYPES):
                        raise SystemExit(f"{result_path.name}:{number}: invalid {kind}")
                    source_url = item.get("source_url")
                    claim = item.get("evidence_claim")
                    confidence = item.get("confidence")
                    if source_url not in expected[number] or not isinstance(claim, str) or not claim.strip() or not isinstance(confidence, (int, float)) or not 0 <= confidence <= 1:
                        raise SystemExit(f"{result_path.name}:{number}: unsupported {kind} evidence")
                    rows.append((proposal_id(number, kind, item["name"], role, source_url, claim), result_path.name, number, kind, item["name"].strip(), entity_type, role, source_url, claim.strip(), float(confidence), "proposed", "model", "2026-10-25T00:00:00Z"))
        if observed != set(expected):
            raise SystemExit(f"{result_path.name}: coverage mismatch")
    conn = sqlite3.connect(DB)
    try:
        conn.execute("BEGIN IMMEDIATE")
        conn.execute(
            """CREATE TABLE IF NOT EXISTS proposed_entry_entities (
                 proposal_id TEXT PRIMARY KEY,
                 packet_name TEXT NOT NULL,
                 entry_number INTEGER NOT NULL,
                 entity_kind TEXT NOT NULL CHECK (entity_kind IN ('person','organization')),
                 name TEXT NOT NULL,
                 entity_type TEXT NOT NULL,
                 role TEXT NOT NULL,
                 source_url TEXT NOT NULL,
                 evidence_claim TEXT NOT NULL,
                 confidence REAL NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
                 review_status TEXT NOT NULL CHECK (review_status IN ('proposed','accepted','rejected')),
                 extraction_method TEXT NOT NULL,
                 created_at TEXT NOT NULL,
                 UNIQUE(entry_number, entity_kind, name, role, source_url, evidence_claim)
               )"""
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_proposed_entities_entry ON proposed_entry_entities(entry_number)")
        packets = sorted({row[1] for row in rows})
        for packet in packets:
            conn.execute("DELETE FROM proposed_entry_entities WHERE packet_name = ?", (packet,))
        conn.executemany(
            """INSERT INTO proposed_entry_entities
               (proposal_id,packet_name,entry_number,entity_kind,name,entity_type,role,source_url,evidence_claim,confidence,review_status,extraction_method,created_at)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            rows,
        )
        conn.commit()
        count = conn.execute("SELECT count(*) FROM proposed_entry_entities").fetchone()[0]
        entities = conn.execute("SELECT count(DISTINCT entry_number) FROM proposed_entry_entities").fetchone()[0]
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
    print(json.dumps({"status": "ok", "proposed_edges": len(rows), "total_proposed_edges": count, "entries_with_proposed_entities": entities, "canonical_or_live_writes": False}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

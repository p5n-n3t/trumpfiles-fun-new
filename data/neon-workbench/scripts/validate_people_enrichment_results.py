#!/usr/bin/env python3
"""Validate proposal-only people-enrichment packet results against inputs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_ROOT = ROOT / "data/neon-workbench/external/people-enrichment-2026-10-25"
ROLES = {"subject", "actor", "official", "target", "mentioned"}
ENTITY_TYPES = {"organization", "agency", "company", "country", "media", "other"}
STATUSES = {"enriched", "no_supported_people", "needs_source"}


def jsonl(path: Path) -> list[dict]:
    result = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as error:
            raise ValueError(f"{path}:{line_number}: invalid JSON ({error})") from error
        if not isinstance(value, dict):
            raise ValueError(f"{path}:{line_number}: expected object")
        result.append(value)
    return result


def urls(value: object) -> set[str]:
    found: set[str] = set()
    if isinstance(value, str) and value.startswith(("http://", "https://")):
        found.add(value)
    elif isinstance(value, dict):
        for item in value.values():
            found.update(urls(item))
    elif isinstance(value, list):
        for item in value:
            found.update(urls(item))
    return found


def valid_url(value: object) -> bool:
    if not isinstance(value, str):
        return False
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def check_entity(entity: object, source_urls: set[str], kind: str, where: str) -> list[str]:
    if not isinstance(entity, dict):
        return [f"{where}: {kind} is not an object"]
    errors = []
    if not isinstance(entity.get("name"), str) or not entity["name"].strip():
        errors.append(f"{where}: {kind} missing name")
    if kind == "person" and entity.get("role") not in ROLES:
        errors.append(f"{where}: invalid person role")
    if kind == "organization" and entity.get("entity_type") not in ENTITY_TYPES:
        errors.append(f"{where}: invalid organization type")
    url = entity.get("source_url")
    if not valid_url(url):
        errors.append(f"{where}: {kind} invalid source URL")
    elif url not in source_urls:
        errors.append(f"{where}: {kind} source URL was not supplied by input")
    if not isinstance(entity.get("evidence_claim"), str) or not entity["evidence_claim"].strip():
        errors.append(f"{where}: {kind} missing evidence claim")
    confidence = entity.get("confidence")
    if not isinstance(confidence, (int, float)) or isinstance(confidence, bool) or not 0 <= confidence <= 1:
        errors.append(f"{where}: {kind} invalid confidence")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--packet", action="append", default=[])
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    manifest = json.loads((args.root / "manifest.json").read_text(encoding="utf-8"))
    selected = set(args.packet) if args.packet else None
    findings: list[str] = []
    checked_packets = 0
    checked_entries = 0
    for packet in manifest["packets"]:
        name = Path(packet["file"]).name
        if selected and name not in selected:
            continue
        source_path = args.root / packet["file"]
        result_path = args.root / "results" / name
        if not result_path.exists():
            findings.append(f"{name}: missing result file")
            continue
        inputs = jsonl(source_path)
        results = jsonl(result_path)
        expected = {row["entry_number"]: urls(row) for row in inputs}
        observed: dict[int, dict] = {}
        for index, row in enumerate(results, 1):
            where = f"{name}:{index}"
            entry_number = row.get("entry_number")
            if not isinstance(entry_number, int):
                findings.append(f"{where}: invalid entry_number")
                continue
            if entry_number in observed:
                findings.append(f"{where}: duplicate entry_number {entry_number}")
                continue
            observed[entry_number] = row
            if entry_number not in expected:
                findings.append(f"{where}: outside assigned entry_number {entry_number}")
                continue
            status = row.get("status")
            if status not in STATUSES:
                findings.append(f"{where}: invalid status")
                continue
            people = row.get("people")
            organizations = row.get("organizations")
            if not isinstance(people, list) or not isinstance(organizations, list):
                findings.append(f"{where}: people and organizations must be arrays")
                continue
            if status != "enriched" and (people or organizations):
                findings.append(f"{where}: non-enriched record contains entities")
            if status == "enriched" and not (people or organizations):
                findings.append(f"{where}: enriched record has no entities")
            if status != "enriched" and not isinstance(row.get("reason"), str):
                findings.append(f"{where}: terminal empty status needs reason")
            for entity in people:
                findings.extend(check_entity(entity, expected[entry_number], "person", where))
            for entity in organizations:
                findings.extend(check_entity(entity, expected[entry_number], "organization", where))
        missing = sorted(set(expected) - set(observed))
        if missing:
            findings.append(f"{name}: missing {len(missing)} entries")
        checked_packets += 1
        checked_entries += len(inputs)
    result = {
        "status": "PASS" if not findings else "FAIL",
        "checked_packets": checked_packets,
        "checked_entries": checked_entries,
        "findings": findings,
    }
    report_path = args.report or args.root / "results-validation.json"
    report_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if not findings else 1


if __name__ == "__main__":
    raise SystemExit(main())

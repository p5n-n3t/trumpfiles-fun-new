#!/usr/bin/env python3
"""Read-only validation for the exact Half-A append-only recovery package.
Run from any directory: python3 path/to/validate.py
Checks structure, source URL syntax, provenance metadata, editorial flags,
positive description ranges, and (when Git is available) protected diff scope.
Does NOT claim that source URLs verify the underlying factual assertions.
"""
import collections
import json
import pathlib
import subprocess
import sys
from urllib.parse import urlparse

PACKAGE = pathlib.Path(__file__).resolve().parent
ROOT = PACKAGE.parents[3]
PREFIX = "data/neon-workbench/external/web-evidence-recovery-half-a-2026-10-20/"
BASE = "3af4d448606ed190acbdc2fb83456ff164b0f005"
ASSIGNED = """entry-1670 entry-1716 entry-1768 entry-1770 entry-2349 entry-2373 entry-2494 entry-2518 entry-2557 entry-2562
entry-2571 entry-2615 entry-3212 entry-3371 entry-4285 entry-5329 entry-5731 entry-5732 entry-5735 entry-5737
entry-5743 entry-5746 entry-5749 entry-5755 entry-5756 entry-5760 entry-5761 entry-5826 entry-5844 entry-5850
entry-5863 entry-5899 entry-6200 entry-6239 entry-6280 entry-6315 entry-6316 entry-6398 entry-6413 entry-6415
entry-6417 entry-6421 entry-6423 entry-6430 entry-6432 entry-6439 entry-6440 entry-6444 entry-6451 entry-6455
entry-6457 entry-6484 entry-6498 entry-6501 entry-6504 entry-6517 entry-6564 entry-6582 entry-6584 entry-6595""".split()
EXPECTED_COUNTS = {"repaired_proposal": 1, "supported_partial": 7, "still_unresolved": 52}
FILES = {"final-terminal-results.jsonl", "research-log.jsonl", "checkpoint.json", "PROGRESS.md", "validation-report.json", "README.md", "REVIEWER-HANDOFF.md", "validate.py"}
errors = []

def check(test, explanation):
    if not test:
        errors.append(explanation)

def load_jsonl(name):
    try:
        return [json.loads(line) for line in (PACKAGE / name).read_text().splitlines() if line.strip()]
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"Cannot read {name}: {exc}")
        return []

def load_json(name):
    try:
        return json.loads((PACKAGE / name).read_text())
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"Cannot read {name}: {exc}")
        return {}

def valid_url(value):
    try:
        return isinstance(value, str) and urlparse(value).scheme in ("http", "https") and bool(urlparse(value).hostname) and not any(c.isspace() for c in value)
    except ValueError:
        return False

records = load_jsonl("final-terminal-results.jsonl")
research = load_jsonl("research-log.jsonl")
checkpoint = load_json("checkpoint.json")
report = load_json("validation-report.json")
check(len(ASSIGNED) == 60 and len(set(ASSIGNED)) == 60, "validator assignment manifest corrupt")
check(len(records) == 60, f"terminal record count {len(records)} != 60")
check(len(research) == 60, f"research log count {len(research)} != 60")
check([r.get("record_id") for r in records] == ASSIGNED, "terminal record list differs from exact ordered assignment")
check(len({r.get("record_id") for r in records}) == 60, "duplicate terminal record")
check({r.get("record_id") for r in research} == set(ASSIGNED) and len({r.get("record_id") for r in research}) == 60, "missing/duplicate/unassigned research log ID")
check(checkpoint.get("assignment_ids") == ASSIGNED, "checkpoint assignment mismatch")
counts = dict(collections.Counter(r.get("outcome") for r in records))
check(counts == EXPECTED_COUNTS, f"outcome counts changed: {counts}")
check(checkpoint.get("outcome_counts") == counts, "checkpoint count mismatch")
check(report.get("counts") == counts, "validation report count mismatch")
check(set(x.name for x in PACKAGE.iterdir() if x.is_file()) == FILES, "package file manifest differs from exact eight-file deliverable")

for index, record in enumerate(records):
    rid = record.get("record_id")
    check(record.get("assignment_index") == index, f"{rid}: assignment_index mismatch")
    check(record.get("assigned_worker") == index // 10 + 1, f"{rid}: worker partition mismatch")
    check(record.get("outcome") in EXPECTED_COUNTS, f"{rid}: invalid terminal outcome")
    check(record.get("proposal_only") is True and record.get("publication_eligible") is False and record.get("requires_manual_editorial_review") is True, f"{rid}: publication gate missing")
    check(bool(record.get("original_title")) and bool(record.get("original_claim")), f"{rid}: original frozen record missing")
    provenance = record.get("provenance_pointer") or {}
    check(provenance.get("review_pr") == 71 and bool(provenance.get("review_path")), f"{rid}: missing PR71 provenance pointer")
    for key in ("original_source_urls", "source_urls"):
        values = record.get(key)
        check(isinstance(values, list), f"{rid}: {key} not a list")
        if isinstance(values, list):
            check(all(valid_url(url) for url in values), f"{rid}: malformed {key}")
            check(len(values) == len(set(values)), f"{rid}: duplicate {key}")
    seen = record.get("source_provenance")
    check(isinstance(seen, list), f"{rid}: source_provenance not list")
    if isinstance(seen, list):
        for item in seen:
            check(isinstance(item, dict), f"{rid}: malformed source provenance row")
            if isinstance(item, dict):
                url = item.get("source_url") or item.get("url")
                check(not url or valid_url(url), f"{rid}: invalid provenance URL")
                check(bool(item.get("access_status")), f"{rid}: source access status not documented")
    if record.get("outcome") == "still_unresolved":
        check(bool(record.get("exact_blocker") or record.get("exact_blockers")), f"{rid}: missing precise blocker")
        check(bool(record.get("why_cannot_repair")), f"{rid}: missing no-repair explanation")
    else:
        check(bool(record.get("source_urls")) and bool(seen), f"{rid}: positive result without exact evidence")
        for key in ("title", "short_description", "medium_description", "long_description"):
            check(isinstance(record.get(key), str) and bool(record[key]), f"{rid}: empty positive copy {key}")
        check(isinstance(record.get("category"), str) and bool(record["category"]) and isinstance(record.get("tags"), list), f"{rid}: missing proposal-only category/tags")
        if isinstance(record.get("title"), str):
            check(len(record["title"]) <= 180, f"{rid}: title too long")
        if isinstance(record.get("short_description"), str):
            check(len(record["short_description"]) <= 180, f"{rid}: short text too long")
        if isinstance(record.get("medium_description"), str):
            check(45 <= len(record["medium_description"].split()) <= 90, f"{rid}: medium word count invalid")
        if isinstance(record.get("long_description"), str):
            check(140 <= len(record["long_description"].split()) <= 300, f"{rid}: long word count invalid")
        check(len({record.get("short_description"), record.get("medium_description"), record.get("long_description")}) == 3, f"{rid}: identical copy tiers")

for log in research:
    rid = log.get("record_id")
    check(isinstance(log.get("queries_attempted"), list) and isinstance(log.get("source_urls_considered"), list) and isinstance(log.get("access_notes"), list), f"{rid}: malformed research log")
    check(log.get("source_packet_pr") == 71, f"{rid}: provenance PR mismatch")
    check(log.get("timestamp_utc_date") == "2026-10-20", f"{rid}: research timestamp mismatch")
    if isinstance(log.get("source_urls_considered"), list):
        check(all(valid_url(url) for url in log["source_urls_considered"]), f"{rid}: malformed researched URL")

try:
    cmd = ["git", "-C", str(ROOT), "diff", "--cached", "--name-status", BASE]
    changes = subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL).splitlines()
    check(bool(changes), "No commit additions found")
    for line in changes:
        status, _, path = line.partition("\t")
        check(status == "A" and path.startswith(PREFIX) and path.removeprefix(PREFIX) in FILES, f"protected diff: {line}")
    check(len(changes) == len(FILES), f"Git committed change count {len(changes)} != {len(FILES)}")
except (OSError, subprocess.CalledProcessError):
    print("NOTE: Git history unavailable; skipped committed diff scope validation", file=sys.stderr)

if errors:
    print(f"FAIL: {len(errors)} errors")
    for error in errors:
        print(" - " + error)
    sys.exit(1)
print("PASS: 60 exact IDs, 60 research logs, 6x10 partitions, source URLs, provenance, copy tiers, flags, and append-only Git scope")
print("Outcome counts:", json.dumps(counts, sort_keys=True))

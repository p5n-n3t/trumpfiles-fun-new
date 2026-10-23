#!/usr/bin/env python3
"""
Phase 2 data-quality validation for fresh-event candidates.

Applies the data-quality-frameworks skill's six dimensions (Completeness,
Uniqueness, Validity, Accuracy, Consistency, Timeliness) as explicit, independent
checks against the merged candidate file, the score file, and the two dedup
reference indexes. Written as a standalone script in the spirit of Phase 1's
"independent coordinator validator... a separate code path from the generation
script" rather than trusting any single producing step's self-report.

Exit code is 0 only if every check in REQUIRED passes. Checks in ADVISORY are
reported but do not fail the run (documented, non-blocking observations).
"""
import json
import re
import sys
from datetime import datetime

VALID_CATEGORIES = {
    'Authoritarianism', 'Government Corruption', 'Human Rights Violations',
    'Grift / Financial Exploitation', 'National Security Violations',
    'Foreign Policy', 'Election Interference', 'Press Freedom',
    'Environmental Destruction', 'Conspiracy Theories / Disinformation',
}
VALID_ALLEGATION_STATUS = {"established", "allegation", "mixed"}
VALID_CONFIDENCE = {"high", "medium", "low", "deferred"}
CUTOFF = "2026-10-23"
EARLIEST_FRESH = "2026-08-20"  # first date in the prior 106-candidate ledger


def load_jsonl(path):
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]


def word_count(text):
    return len(re.findall(r"\S+", text or ""))


def valid_date(value):
    try:
        datetime.strptime(value, "%Y-%m-%d")
        return True
    except (TypeError, ValueError):
        return False


def run(candidates_path, scores_path, frozen_recent_path, existing_fresh_path):
    candidates = load_jsonl(candidates_path)
    scores = {s["candidate_id"]: s for s in load_jsonl(scores_path)}
    frozen_recent = load_jsonl(frozen_recent_path)
    existing_fresh = {r["candidate_id"]: r for r in load_jsonl(existing_fresh_path)}

    errors = []
    advisories = []

    # --- Completeness ---
    required_fields = [
        "candidate_id", "event_date", "date_start", "date_end", "title",
        "description_short", "description_medium", "description_long",
        "category", "source_urls", "sources",
    ]
    for c in candidates:
        cid = c.get("candidate_id", "<missing id>")
        for field in required_fields:
            value = c.get(field)
            if value in (None, "", []):
                errors.append(f"[completeness] {cid}: missing or empty '{field}'")

    # --- Uniqueness ---
    ids = [c["candidate_id"] for c in candidates if c.get("candidate_id")]
    dupe_ids = {x for x in ids if ids.count(x) > 1}
    if dupe_ids:
        errors.append(f"[uniqueness] duplicate candidate_id values within this batch: {sorted(dupe_ids)}")

    collisions_with_prior = sorted(set(ids) & set(existing_fresh.keys()))
    if collisions_with_prior:
        errors.append(f"[uniqueness] candidate_id collides with an already-proposed fresh candidate: {collisions_with_prior}")

    date_title_seen = {}
    for c in candidates:
        key = (c.get("event_date"), (c.get("title") or "").strip().lower())
        date_title_seen.setdefault(key, []).append(c["candidate_id"])
    for key, cids in date_title_seen.items():
        if len(cids) > 1:
            errors.append(f"[uniqueness] exact date+title collision within this batch: {key} -> {cids}")

    frozen_by_date_title = {}
    for r in frozen_recent:
        frozen_by_date_title.setdefault((r.get("date_start"), (r.get("title") or "").strip().lower()), []).append(r["entry_number"])
    for c in candidates:
        key = (c.get("event_date"), (c.get("title") or "").strip().lower())
        if key in frozen_by_date_title:
            errors.append(f"[uniqueness] {c['candidate_id']} exact-matches frozen catalogue entry_number(s) {frozen_by_date_title[key]} on date+title")

    existing_by_date_title = {}
    for cid, r in existing_fresh.items():
        existing_by_date_title.setdefault((r.get("event_date"), (r.get("title") or "").strip().lower()), []).append(cid)
    for c in candidates:
        key = (c.get("event_date"), (c.get("title") or "").strip().lower())
        if key in existing_by_date_title:
            errors.append(f"[uniqueness] {c['candidate_id']} exact-matches prior fresh candidate(s) {existing_by_date_title[key]} on date+title")

    # --- Validity ---
    for c in candidates:
        cid = c.get("candidate_id", "<missing id>")
        if c.get("category") not in VALID_CATEGORIES:
            errors.append(f"[validity] {cid}: category {c.get('category')!r} not in VALID_CATEGORIES")
        for field in ("event_date", "date_start", "date_end"):
            if not valid_date(c.get(field)):
                errors.append(f"[validity] {cid}: invalid or missing date field '{field}' = {c.get(field)!r}")
        if valid_date(c.get("date_start")) and valid_date(c.get("date_end")) and c["date_end"] < c["date_start"]:
            errors.append(f"[validity] {cid}: date_end precedes date_start")
        allegation = c.get("allegation_or_established")
        if allegation not in VALID_ALLEGATION_STATUS:
            errors.append(f"[validity] {cid}: allegation_or_established {allegation!r} not one of {sorted(VALID_ALLEGATION_STATUS)}")
        short = c.get("description_short") or c.get("title") or ""
        if len(short) > 180:
            errors.append(f"[validity] {cid}: description_short/title is {len(short)} chars, limit 180")
        medium_words = word_count(c.get("description_medium"))
        if not (45 <= medium_words <= 90):
            errors.append(f"[validity] {cid}: description_medium is {medium_words} words, required 45-90")
        long_words = word_count(c.get("description_long"))
        if not (140 <= long_words <= 300):
            errors.append(f"[validity] {cid}: description_long is {long_words} words, required 140-300")
        for url in c.get("source_urls") or []:
            if not re.match(r"^https?://", url or ""):
                errors.append(f"[validity] {cid}: source URL is not http(s): {url!r}")
        if cid not in scores:
            errors.append(f"[validity] {cid}: no impact-v2 score row found")
        else:
            s = scores[cid]
            if s.get("evidence_confidence") not in VALID_CONFIDENCE:
                errors.append(f"[validity] {cid}: score confidence {s.get('evidence_confidence')!r} invalid")
            if s.get("evidence_confidence") == "high":
                errors.append(f"[validity] {cid}: scoring pass is deterministic and must never assign 'high' confidence")
            dims = s.get("dimensions", {})
            for k, v in dims.items():
                if not (0 <= v <= 10):
                    errors.append(f"[validity] {cid}: dimension {k}={v} out of 0-10 range")
            recomputed = round(sum(dims.values()) / len(dims), 1) if dims else None
            if recomputed is not None and abs(recomputed - s.get("impact_v2_composite", -999)) > 0.05:
                errors.append(f"[validity] {cid}: composite {s.get('impact_v2_composite')} does not match recomputed mean {recomputed}")

    # --- Consistency ---
    for c in candidates:
        cid = c.get("candidate_id", "<missing id>")
        for tag_field in ("people_tags", "organization_tags"):
            tags = c.get(tag_field) or []
            if len(tags) != len(set(tags)):
                errors.append(f"[consistency] {cid}: duplicate values within {tag_field}")
        source_urls = set(c.get("source_urls") or [])
        for s in c.get("sources") or []:
            if s.get("url") not in source_urls:
                advisories.append(f"[consistency] {cid}: source object url {s.get('url')!r} not listed in source_urls")

    # --- Timeliness ---
    for c in candidates:
        cid = c.get("candidate_id", "<missing id>")
        if valid_date(c.get("event_date")):
            if c["event_date"] > CUTOFF:
                errors.append(f"[timeliness] {cid}: event_date {c['event_date']} is after the stated research cutoff {CUTOFF}")
            if c["event_date"] < EARLIEST_FRESH:
                advisories.append(f"[timeliness] {cid}: event_date {c['event_date']} predates the existing fresh-event lane start {EARLIEST_FRESH}; confirm it is not already in the frozen catalogue")

    return errors, advisories, len(candidates)


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("usage: validate_fresh_events.py <candidates.jsonl> <scores.jsonl> <frozen_recent_index.jsonl> <existing_fresh_index.jsonl>", file=sys.stderr)
        sys.exit(2)
    errors, advisories, n = run(*sys.argv[1:5])
    print(f"Validated {n} candidates.")
    print(f"REQUIRED errors: {len(errors)}")
    for e in errors:
        print("  -", e)
    print(f"ADVISORY notes: {len(advisories)}")
    for a in advisories:
        print("  -", a)
    sys.exit(1 if errors else 0)

#!/usr/bin/env python3
"""
Phase 2 fresh-event impact-v2 scoring.

Deterministic and explainable, following the same 10-criterion rubric, composite
formula, and confidence-gate discipline as Phase 1
(data/neon-workbench/external/lightsprint-phase-1-scoring-2026-10-22/scoring-coverage-report.md),
adapted for fresh-event candidates, which have no legacy trump_individual_scores row,
no financial_cost_usd/reach_estimate/duration_days columns, and no pre-2026-08-21
category taxonomy (fresh candidates use only the 10-value VALID_CATEGORIES enum from
scripts/enrichment-contract.mjs, not the legacy catalogue's 51 free-text categories).

Where Phase 1 fell back to a legacy axis or a category-bucket baseline, this pass falls
back to a documented category baseline for the new 10-category taxonomy, and to values
derived directly from the candidate record itself (a dollar figure actually present in
its sourced description, its own tag counts, its own event date) rather than inventing
anything. This is intentionally a different basis label
(`fresh_event_category_baseline_plus_record_derived`) from Phase 1's
`structured_metadata_only`/`reviewed_evidence`, because the inputs differ; see
PHASE-2-METHODOLOGY.md for the full writeup.

No row here is marked "high" confidence, matching Phase 1's rule: a deterministic pass
never self-assigns the top confidence tier.
"""
import json
import math
import re
import sys
from datetime import date, datetime

CRITERIA = [
    "direct_documented_harm",
    "people_institutions_affected",
    "democratic_institutional_damage",
    "civil_rights_public_safety_impact",
    "financial_material_consequence",
    "abuse_of_power",
    "misinformation_deception_severity",
    "recurrence_persistence",
    "historical_precedential_significance",
    "current_relevance",
]

# One documented baseline row per category in scripts/enrichment-contract.mjs
# VALID_CATEGORIES. Each value is a considered, modest 0-10 starting point for that
# criterion given what the category name itself denotes - not derived from any single
# entry's facts. See PHASE-2-METHODOLOGY.md criterion-by-criterion rationale.
CATEGORY_BASELINE = {
    "Authoritarianism": {
        "direct_documented_harm": 6, "people_institutions_affected": 5,
        "democratic_institutional_damage": 8, "civil_rights_public_safety_impact": 5,
        "financial_material_consequence": 2, "abuse_of_power": 8,
        "misinformation_deception_severity": 4, "recurrence_persistence": 5,
        "historical_precedential_significance": 7,
    },
    "Government Corruption": {
        "direct_documented_harm": 4, "people_institutions_affected": 5,
        "democratic_institutional_damage": 6, "civil_rights_public_safety_impact": 3,
        "financial_material_consequence": 5, "abuse_of_power": 7,
        "misinformation_deception_severity": 4, "recurrence_persistence": 5,
        "historical_precedential_significance": 5,
    },
    "Human Rights Violations": {
        "direct_documented_harm": 7, "people_institutions_affected": 6,
        "democratic_institutional_damage": 5, "civil_rights_public_safety_impact": 8,
        "financial_material_consequence": 2, "abuse_of_power": 6,
        "misinformation_deception_severity": 3, "recurrence_persistence": 5,
        "historical_precedential_significance": 6,
    },
    "Grift / Financial Exploitation": {
        "direct_documented_harm": 3, "people_institutions_affected": 4,
        "democratic_institutional_damage": 3, "civil_rights_public_safety_impact": 2,
        "financial_material_consequence": 6, "abuse_of_power": 6,
        "misinformation_deception_severity": 4, "recurrence_persistence": 5,
        "historical_precedential_significance": 4,
    },
    "National Security Violations": {
        "direct_documented_harm": 7, "people_institutions_affected": 6,
        "democratic_institutional_damage": 6, "civil_rights_public_safety_impact": 4,
        "financial_material_consequence": 3, "abuse_of_power": 6,
        "misinformation_deception_severity": 4, "recurrence_persistence": 4,
        "historical_precedential_significance": 6,
    },
    "Foreign Policy": {
        "direct_documented_harm": 5, "people_institutions_affected": 5,
        "democratic_institutional_damage": 3, "civil_rights_public_safety_impact": 2,
        "financial_material_consequence": 4, "abuse_of_power": 4,
        "misinformation_deception_severity": 4, "recurrence_persistence": 4,
        "historical_precedential_significance": 5,
    },
    "Election Interference": {
        "direct_documented_harm": 5, "people_institutions_affected": 6,
        "democratic_institutional_damage": 8, "civil_rights_public_safety_impact": 5,
        "financial_material_consequence": 2, "abuse_of_power": 7,
        "misinformation_deception_severity": 5, "recurrence_persistence": 5,
        "historical_precedential_significance": 7,
    },
    "Press Freedom": {
        "direct_documented_harm": 4, "people_institutions_affected": 4,
        "democratic_institutional_damage": 6, "civil_rights_public_safety_impact": 4,
        "financial_material_consequence": 2, "abuse_of_power": 5,
        "misinformation_deception_severity": 4, "recurrence_persistence": 4,
        "historical_precedential_significance": 5,
    },
    "Environmental Destruction": {
        "direct_documented_harm": 6, "people_institutions_affected": 5,
        "democratic_institutional_damage": 3, "civil_rights_public_safety_impact": 4,
        "financial_material_consequence": 4, "abuse_of_power": 4,
        "misinformation_deception_severity": 3, "recurrence_persistence": 4,
        "historical_precedential_significance": 4,
    },
    "Conspiracy Theories / Disinformation": {
        "direct_documented_harm": 3, "people_institutions_affected": 4,
        "democratic_institutional_damage": 4, "civil_rights_public_safety_impact": 3,
        "financial_material_consequence": 1, "abuse_of_power": 3,
        "misinformation_deception_severity": 7, "recurrence_persistence": 5,
        "historical_precedential_significance": 4,
    },
}

DOLLAR_RE = re.compile(
    r"\$\s?([0-9]+(?:\.[0-9]+)?)\s*(trillion|billion|million|thousand)?", re.IGNORECASE
)
MULT = {"thousand": 1e3, "million": 1e6, "billion": 1e9, "trillion": 1e12, None: 1.0}


def extract_max_dollar_usd(*texts):
    best = None
    for text in texts:
        if not text:
            continue
        for amount, unit in DOLLAR_RE.findall(text):
            try:
                value = float(amount) * MULT[unit.lower() if unit else None]
            except (ValueError, KeyError):
                continue
            if best is None or value > best:
                best = value
    return best


def financial_score_from_usd(usd):
    # Phase 1 anchor points: US$1M -> 0, US$1B -> ~5, US$1.6T -> 10 (log10 scale).
    if usd is None or usd < 1e6:
        return None
    lo, hi = math.log10(1e6), math.log10(1.6e12)
    score = (math.log10(usd) - lo) / (hi - lo) * 10
    return round(max(0.0, min(10.0, score)), 1)


def current_relevance(event_date_str, cutoff_date):
    try:
        event_date = datetime.strptime(event_date_str, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return 5.0  # undated fallback, matches a neutral midpoint rather than guessing
    days = max(0, (cutoff_date - event_date).days)
    # 30-day half-life: an event dated today scores 10; 30 days old scores 5; the
    # oldest fresh candidates (~64 days before an Oct 23 cutoff) score ~2.3. Chosen
    # because every fresh candidate in this lane is within the last ~2 months by
    # construction, unlike Phase 1's frozen-catalogue decay which spans back to 1927.
    return round(10.0 * (0.5 ** (days / 30.0)), 1)


def confidence_gate(sources, allegation_or_established):
    n = len(sources or [])
    has_primary_or_recognized = any(
        s.get("is_primary") or s.get("publisher") for s in (sources or [])
    )
    if n == 0:
        return "deferred"
    if n == 1 or not has_primary_or_recognized:
        return "low"
    if allegation_or_established == "allegation" and n < 3:
        return "low"
    return "medium"  # never "high" in a deterministic pass - matches Phase 1's rule


def score_candidate(candidate, cutoff_date):
    category = candidate.get("category")
    baseline = CATEGORY_BASELINE.get(category)
    basis_notes = []
    if baseline is None:
        basis_notes.append(f"unrecognized category {category!r}; used neutral baseline 4.0 for all criteria")
        baseline = {c: 4.0 for c in CRITERIA if c != "current_relevance"}

    values = {c: float(baseline.get(c, 4.0)) for c in CRITERIA if c != "current_relevance"}

    # people_institutions_affected: never score lower than the category baseline just
    # because few tags were recorded, but raise it when the record names many people/orgs.
    tag_count = len(candidate.get("people_tags") or []) + len(candidate.get("organization_tags") or [])
    tag_derived = round(min(10.0, 2.0 + 2.1 * math.log10(1 + tag_count)), 1) if tag_count else 0.0
    if tag_derived > values["people_institutions_affected"]:
        values["people_institutions_affected"] = tag_derived
        basis_notes.append(f"people_institutions_affected raised to {tag_derived} from {tag_count} named people/orgs tags")

    # financial_material_consequence: use an actual dollar figure from the candidate's
    # own sourced text when one is present; otherwise keep the category baseline.
    usd = extract_max_dollar_usd(candidate.get("description_long"), candidate.get("description_medium"))
    fin_score = financial_score_from_usd(usd)
    if fin_score is not None:
        values["financial_material_consequence"] = fin_score
        basis_notes.append(f"financial_material_consequence derived from largest dollar figure in record text (~${usd:,.0f}) via log10 scale")

    # misinformation_deception_severity: allegations require more editorial caution,
    # matching the legacy credibility_risk axis's "higher means more corroboration needed".
    allegation_status = candidate.get("allegation_or_established", "mixed")
    if allegation_status == "allegation":
        values["misinformation_deception_severity"] = round(min(10.0, values["misinformation_deception_severity"] + 1.5), 1)
    elif allegation_status == "mixed":
        values["misinformation_deception_severity"] = round(min(10.0, values["misinformation_deception_severity"] + 0.75), 1)

    values["current_relevance"] = current_relevance(candidate.get("event_date"), cutoff_date)

    composite = round(sum(values[c] for c in CRITERIA) / len(CRITERIA), 1)
    confidence = confidence_gate(candidate.get("sources"), allegation_status)

    return {
        "candidate_id": candidate["candidate_id"],
        "scoring_version": "impact-v2-phase2-fresh-event",
        "event_date": candidate.get("event_date"),
        "category": category,
        "dimensions": values,
        "impact_v2_composite": composite,
        "evidence_confidence": confidence,
        "basis": "fresh_event_category_baseline_plus_record_derived",
        "basis_notes": basis_notes or ["all ten criteria from documented category baseline; no record-derived adjustment applied"],
        "source_count": len(candidate.get("sources") or []),
        "allegation_or_established": allegation_status,
    }


def main():
    if len(sys.argv) != 4:
        print("usage: score_fresh_events.py <candidates.jsonl> <cutoff YYYY-MM-DD> <out.jsonl>", file=sys.stderr)
        sys.exit(1)
    in_path, cutoff_str, out_path = sys.argv[1], sys.argv[2], sys.argv[3]
    cutoff_date = datetime.strptime(cutoff_str, "%Y-%m-%d").date()

    rows = []
    with open(in_path) as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))

    scored = [score_candidate(r, cutoff_date) for r in rows]

    with open(out_path, "w") as f:
        for s in scored:
            f.write(json.dumps(s, ensure_ascii=False) + "\n")

    composites = [s["impact_v2_composite"] for s in scored]
    conf_counts = {}
    for s in scored:
        conf_counts[s["evidence_confidence"]] = conf_counts.get(s["evidence_confidence"], 0) + 1
    print(f"scored {len(scored)} candidates -> {out_path}")
    print(f"composite range: {min(composites)} - {max(composites)}, mean {sum(composites)/len(composites):.2f}")
    print(f"confidence breakdown: {conf_counts}")


if __name__ == "__main__":
    main()

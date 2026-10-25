#!/usr/bin/env python3
"""Convert recovered Trumpfile drafts to the versioned enrichment contract.

This is an offline proposal-only transformation. It never assigns entry
numbers or mutates the frozen catalogue, Neon, or Neo4j.
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
INPUT = ROOT / "data/neon-workbench/external/enrichment-discovery-2026-10-24/trumpfile/recovered-entry-drafts/drafts.jsonl"
OUT = ROOT / "data/neon-workbench/external/enrichment-discovery-2026-10-24/trumpfile/recovered-entry-drafts/standardized"
FIELDS = ("insanity", "authoritarianism", "lawlessness", "absurdity", "danger", "credibility_risk", "recency_intensity", "impact_scope")

DETAILS = {
    21724: ("2026-05-26", "Human Rights Violations", "Immigration Enforcement Pressure", "Reuters", (3, 5, 4, 3, 2, 4, 10, 8), "new_candidate", ()),
    21766: ("2026-06-02", "Government Corruption", "Executive Appointments", "Associated Press", (2, 4, 3, 3, 2, 4, 10, 7), "new_candidate", ()),
    21818: ("2026-06-25", "Government Corruption", "Public Health Governance", "STAT", (3, 5, 4, 3, 3, 4, 10, 7), "expand_existing", (5816, 6619, 6725)),
    21827: ("2026-04-22", "National Security Violations", "Military Leadership Changes", "Navy Times", (2, 3, 4, 2, 2, 3, 10, 6), "expand_existing", (3426, 4078)),
    21912: ("2026-02-04", "Election Interference", "Voting-System Investigations", "Reuters", (4, 5, 5, 4, 3, 6, 10, 7), "expand_existing", (2139, 329)),
    21967: ("2026-07-21", "Government Corruption", "Medicaid Payment Administration", "CBS News", (2, 4, 4, 2, 2, 4, 10, 8), "probable_duplicate_existing", (4411,)),
    22004: ("2026-07-31", "Conspiracy Theories / Disinformation", "Unsupported Public Attribution", "CBS News", (5, 4, 6, 4, 3, 7, 10, 7), "new_candidate", ()),
    22007: ("2026-08-09", "Government Corruption", "White House Personnel", "Reuters", (2, 3, 3, 2, 2, 3, 10, 6), "new_candidate", (3406, 3766)),
    22152: ("2026-08-31", "National Security Violations", "Military Leadership Resignation", "CBS News", (3, 4, 5, 3, 3, 5, 10, 7), "new_candidate", ()),
    22158: ("2026-08-28", "Foreign Policy", "Venezuela Oil Arrangements", "Associated Press", (3, 5, 5, 3, 3, 5, 10, 8), "expand_existing", (1079, 1080, 2199)),
}


def source_type(publisher: str) -> str:
    return "wire_report" if publisher in {"Reuters", "Associated Press"} else "news_report"


def score_explanations() -> dict[str, str]:
    return {
        "danger": "Proposed from the documented event scope only; not a legal or moral finding.",
        "authoritarianism": "Proposed from the documented institutional-power context only.",
        "lawlessness": "Proposed from the documented procedural context only.",
        "insanity": "Proposed from the unusualness of the documented event only.",
        "absurdity": "Proposed from the unusual or performative character of the documented event only.",
        "credibility_risk": "Higher values indicate editorial caution and corroboration needs, not factual falsity.",
        "recency_intensity": "A 2026 event in the current collection window.",
        "impact_scope": "Proposed from the documented public or institutional scope only.",
    }


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    raw_rows = [json.loads(line) for line in INPUT.read_text(encoding="utf-8").splitlines() if line.strip()]
    rows = []
    for raw in raw_rows:
        post_id = raw["post_id"]
        date, category, subcategory, publisher, scores, disposition, related = DETAILS[post_id]
        url = raw["source_urls"][0]
        values = dict(zip(FIELDS, scores, strict=True))
        enrichment = {
            "schema_version": "2026-08-21.1",
            "identity": {"entry_number": None, "event_id": f"tf-{post_id}-{date}"},
            "title": raw["title"],
            "summaries": {
                "short": raw["description_short"],
                "medium": raw["description_medium"],
                "long": raw["description_long"],
            },
            "dates": {"start": date, "end": None},
            "era": {"phase": "White House 2:2", "raw_phase": "White House 2:2", "status": "mapped"},
            "taxonomy": {"category": category, "subcategory": subcategory},
            "tags": {
                "people": raw["people_tags"],
                "organizations": raw["organization_tags"],
                "locations": [],
                "topics": raw["keywords"],
            },
            "sources": [{
                "url": url, "title": None, "publisher": publisher, "date_published": date,
                "source_type": source_type(publisher), "confidence": 0.9, "status": "verified",
            }],
            "metrics": {"values": values, "explanations": score_explanations()},
            "related_entry_ids": [str(number) for number in related],
            "evidence_claims": [{"claim": raw["description_short"], "source_url": url}],
            "provenance": {
                "source": "trumpfile-second-pass-recovery-2026-10-25",
                "model": "proposal-standardizer",
                "enrichment_version": "2026-08-21.1",
                "enriched_at": "2026-10-25T00:00:00Z",
            },
            "quality_status": "ready",
        }
        rows.append({
            "proposal_metadata": {
                "trumpfile_post_id": post_id,
                "proposal_only": True,
                "review_status": "PROPOSED_NOT_APPROVED",
                "reconciliation_disposition": disposition,
                "existing_entry_numbers": list(related),
            },
            "enrichment": enrichment,
        })
    output_path = OUT / "standardized-proposals.jsonl"
    output_path.write_text("\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in rows) + "\n", encoding="utf-8")
    report = {
        "status": "pending_contract_validation",
        "input_records": len(raw_rows),
        "output_records": len(rows),
        "unique_event_ids": len({row["enrichment"]["identity"]["event_id"] for row in rows}),
        "disposition_counts": {key: sum(row["proposal_metadata"]["reconciliation_disposition"] == key for row in rows) for key in sorted({row["proposal_metadata"]["reconciliation_disposition"] for row in rows})},
    }
    (OUT / "standardization-report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

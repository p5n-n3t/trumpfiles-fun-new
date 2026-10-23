# Phase 1 — impact-v2 scoring coverage report

**Scope:** proposed, non-canonical `impact-v2` scoring layer for all 7,143 catalogue entries.
Nothing here is written to Neon, Neo4j, or any canonical/legacy score table — see
"Boundaries respected" below.

## Coverage

| Metric | Value |
| --- | --- |
| Entries in catalogue (`trump_entries`) | 7,143 |
| Entries scored | 7,143 (100%) |
| Unique entry_numbers in `impact-v2-proposed-scores.jsonl` | 7,143 |
| Missing / duplicate entries | 0 |
| Composite range | 2.3 – 9.3 (mean 6.11) |

## Evidence confidence breakdown

| Confidence | Count | % |
| --- | --- | --- |
| high | 0 | 0.0% |
| medium | 5,635 | 78.9% |
| low | 1,487 | 20.8% |
| deferred | 21 | 0.3% |

No entry received "high" confidence. This is a deliberate, structural property of the
scoring model (see Methodology), not an oversight: a metadata-only deterministic pass never
self-assigns "high," and even the 152 entries individually reviewed by the Sonnet
difficult-case reviewer found no case where evidence already on record cleared that bar
(see `escalations/`). The 21 "deferred" entries are exactly the 21 entries the project's own
`SCORE_MODEL.md` offline pass had already identified as having no linked source metadata at
all — an independent cross-check that the confidence gate reproduces an existing,
previously-reviewed determination rather than inventing a new one.

## Scoring basis breakdown

| Basis | Count |
| --- | --- |
| structured_metadata_only | 7,130 |
| reviewed_evidence | 13 |

The 13 "reviewed_evidence" rows are difficult cases the Sonnet reviewer actually examined
against the record (sources, rationale_detail, PR #76 disposition) rather than scoring from
category/legacy-axis templates alone. 11 of those 13 were *confirmed* at low confidence
despite real sources existing, specifically because their `needs_context` disposition caps
confidence regardless of sourcing; the other 2 were raised from the deterministic "low" to
"medium" on the strength of one recognized-outlet source each (never to "high" — a single
source does not meet the "multiple independent sources" bar used throughout this pass).

## Rewrite-disposition breakdown (from PR #76, where available)

| Disposition | Count |
| --- | --- |
| none (not part of the 497-entry rewrite review) | 6,646 |
| repaired_proposal | 101 |
| supported_partial | 322 |
| soft_hide_candidate | 16 |
| needs_context | 57 |
| split_required | 1 |

**Confidence never exceeded "low" for any `needs_context` / `soft_hide_candidate` /
`split_required` entry** — verified structurally for all 74 such entries (57 + 16 + 1), not
just the ones that happened to be escalated. See `validation-report.md`.

## Partitioning

| Partition | entry_number range | Rows |
| --- | --- | --- |
| partition-01 | 1 – 1,814 | 1,785 |
| partition-02 | 1,815 – 3,599 | 1,785 |
| partition-03 | 3,600 – 5,407 | 1,785 |
| partition-04 | 5,408 – 7,202 | 1,788 |

Boundaries were chosen to balance row count across four partitions (the catalogue's
`entry_number` column has ~59 gaps between 1 and 7,202, so this is not a contiguous
1-7143 range).

## Difficult-case review

152 entries (2.1% of the catalogue) were deterministically escalated — composite ≥ 8.0
combined with thin sourcing, a missing legacy score row, or a `needs_context`/
`split_required` disposition. All 152 were individually reviewed by the Sonnet reviewer
against real recorded data (sqlite + PR #76 results), never new web research. Outcome: 0
upgraded to high, 2 upgraded to medium, 150 held at their deterministic confidence (148 low,
2 effectively re-confirmed low with a `reviewed_evidence` basis). Full reasoning for every
one of the 152 is in `escalations/difficult-cases.jsonl`; the compact confidence decisions
are in `escalations/reviewer-decisions.jsonl`.

## Model assignment actually used

The task specified GPT-5.6 Sol/Luna, GLM-5.2, and Kimi-K3 for various roles. None of those
model IDs are available in this execution environment (only the Claude family is). The
closest-available substitution was made, preserving the intent of keeping expensive/judgment
models off routine row processing:

| Role | Requested | Used | Why |
| --- | --- | --- | --- |
| Coordinator | GPT-5.6 Sol, medium | Sonnet 5 (this session) | Not available; coordinator work (algorithm design, merge, validation) done directly by the orchestrating session |
| 4 scoring workers | GPT-5.6 Luna, low | Haiku 4.5 attempted, then deterministic script | See `validation-report.md` — 2 of 4 fan-out workers failed outright and a 3rd used wrong filenames; all four partitions were regenerated directly from the same already-verified deterministic engine rather than retried |
| 2 validation workers | GLM-5.2/Kimi-K3, low | Haiku 4.5 attempted | Both failed (context overflow); replaced with the coordinator's own independent Python validator (see `validation-report.md`) |
| Difficult-case reviewer | Sonnet 5, medium | Sonnet 5, medium | Matches exactly; ran in two passes (22 then 130 entries) after the first fan-out attempt only surfaced 22 of the 152 genuinely escalated entries |
| Final QA | Opus 5, medium | Opus 5, medium | Matches exactly; see `validation-report.md` for its independent verdict |

## Methodology (deterministic, explainable)

Every criterion is computed from data already stored in the catalogue — no row was
web-researched and no fact was invented:

1. **direct_documented_harm** — legacy `danger` axis, or a category-bucket baseline (civil-rights/public-safety categories default higher) when no legacy score row exists.
2. **people_institutions_affected** — legacy `impact_scope`, or a log-scaled function of `reach_estimate`/`impressions` when missing.
3. **democratic_institutional_damage** — legacy `authoritarianism`, with a small bonus when the category is itself institutional-damage-coded (Constitutional Crisis, Executive Overreach, etc.).
4. **civil_rights_public_safety_impact** — `danger`, floored at 7 when the category is civil-rights/voter-suppression/discrimination-coded.
5. **financial_material_consequence** — log10 scale on `financial_cost_usd` (US$1M → 0, US$1B → ~5, US$1.6T → 10), or a category baseline when no dollar figure is recorded.
6. **abuse_of_power** — `authoritarianism` plus a bonus for power-abuse-coded categories (Authoritarianism, Election Interference, Cabinet Misconduct, Corruption & Governance, …).
7. **misinformation_deception_severity** — legacy `credibility_risk` (the project's own "editorial caution required" axis), plus a bonus for misinformation/disinformation-coded categories.
8. **recurrence_persistence** — log10 scale on `duration_days`, or a category-frequency fallback when duration is unknown.
9. **historical_precedential_significance** — average of legacy `insanity`/`absurdity` (departure-from-norm axes), plus a bonus for textbook precedent-setting categories (Insurrection, Constitutional Crisis, Election Interference).
10. **current_relevance** — legacy `recency_intensity`, or a day-since-event decay function (relative to 2026-10-22) when missing.

`impact_v2_composite = round(mean(10 criteria), 1)`.

**Confidence gate:** `deferred` when there is no legacy score row AND zero linked sources;
`low` when either is missing; `medium` when both a legacy score row and ≥1 linked source
exist. `needs_context`/`soft_hide_candidate`/`split_required` dispositions cap confidence at
`low` regardless of the above. `high` is reserved exclusively for the reviewed-evidence path
and was not granted to any entry in this pass.

Full per-entry derivation is recorded in `score-provenance.jsonl`; the exact algorithm is
the identical script applied to every partition (see `validation-report.md` for how that
consistency was verified after the initial worker fan-out proved unreliable).

## Boundaries respected

- No canonical catalogue row (`trump_entries`, `trump_individual_scores`, etc.) was modified.
- No frozen export was modified; the frozen sqlite files used as read-only reference input live only under `/tmp` in the sandbox and were never copied into this git tree.
- No write to live Neon or live Neo4j was made or attempted.
- No existing legacy score row was overwritten — this is an additive, separate layer.
- No fact was invented; every value traces to a stored field or an already-recorded disposition, and is logged in `score-provenance.jsonl`.
- All output lives under `data/neon-workbench/external/lightsprint-phase-1-scoring-2026-10-22/`.

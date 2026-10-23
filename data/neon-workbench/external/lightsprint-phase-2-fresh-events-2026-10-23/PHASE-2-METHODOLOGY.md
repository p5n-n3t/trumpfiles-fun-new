# Phase 2 methodology — research, scoring, and model assignment

## Research methodology

Three parallel research workers (see `coordinator-ledger.json` for exact prompts and
timestamps) used the project's established actor-lane split
(`fresh-event-ledgers/fresh-events-next/2026-10-03/PROMPT.md`: administration/official
actions belong to one lane unless a family member is the primary actor, in which case they
belong to the family/business lane) to avoid overlapping research. Each worker:

1. Read the ingestion playbook's tone rules, scope ("What Counts As an Entry" /
   "What Does Not Count"), and source hierarchy before drafting anything.
2. Read `scripts/enrichment-contract.mjs` for the 10-value `VALID_CATEGORIES` enum that all
   fresh-event candidates (unlike the legacy catalogue's 51 free-text categories) must use.
3. Checked every candidate against `frozen-recent-index.jsonl` (288 frozen-catalogue rows
   dated 2026-08-01 or later) and `existing-fresh-candidates-index.jsonl` (the 106 prior
   proposed candidates) before accepting it, and recorded the comparison in `duplicate_review`.
4. Used the Exa MCP connector for live web search (this sandbox's built-in `WebSearch` and
   `WebFetch` tools return a metering error and do not work here), preferring primary sources
   (official statements, court filings, SEC filings) and recognized outlets per the playbook's
   source hierarchy.
5. Wrote candidates only when the facts supported the exact character/word limits already in
   use for this project's fresh-event cards (`description_short` <=180 characters,
   `description_medium` 45-90 words, `description_long` 140-300 words), attributing every
   allegation explicitly and distinguishing it from established fact per this task's writing
   style instructions, and declined to pad out thin leads into fake candidates (14 leads were
   left as documented, unresolved leads instead).

A fourth step, consolidation, deduplication, scoring, and validation, was done directly by
the orchestrating session rather than by a fourth worker, following Phase 1's own lesson that
mechanical/consistency-dependent work is more reliable when done once, directly, with an
independent verification script, than when distributed across workers whose self-reports
cannot be fully trusted without checking the files they actually wrote.

## Scoring methodology

Every one of the 147 fresh-event candidates (106 carried forward, 41 new) was scored on the
same 10 criteria, composite formula (`round(mean(10 criteria), 1)`), and confidence-gate
discipline (no deterministic pass may assign "high") that Phase 1 used for the canonical
7,143-entry catalogue. The formula itself cannot be identical, because fresh-event candidates
have no `trump_individual_scores` row, no `financial_cost_usd`/`reach_estimate`/
`duration_days` columns, and predate the 10-category taxonomy that only the legacy
catalogue's older 51-category scheme covered with Phase 1's category-coded bonuses
(e.g. "Constitutional Crisis," "Cabinet Misconduct"). This pass is deliberately a different,
explicitly labeled basis (`fresh_event_category_baseline_plus_record_derived`, never
Phase 1's `structured_metadata_only`/`reviewed_evidence`) built only from data present on
each candidate record itself:

1. **direct_documented_harm**, **democratic_institutional_damage**,
   **civil_rights_public_safety_impact**, **abuse_of_power**,
   **historical_precedential_significance** — a documented, fixed baseline per category (see
   `CATEGORY_BASELINE` in `scoring/score_fresh_events.py`), chosen deliberately in the
   mid-range (never above 8) consistent with Phase 1's rule that a metadata-only pass should
   not inflate into the top of the scale. These five criteria are not adjusted per-record;
   every candidate in the same category gets the same baseline for these five.
2. **people_institutions_affected** — the category baseline, raised (never lowered) when a
   candidate names more people/organizations than a log-scaled threshold; several
   well-documented candidates (the UAE emoluments lawsuit, the Sokolov investigation) scored
   above their category baseline here because of how many named actors their own sourcing
   recorded.
3. **financial_material_consequence** — the category baseline, overridden by an actual dollar
   figure extracted from the candidate's own `description_long`/`description_medium` text
   (regex-matched, not invented) and converted with Phase 1's exact log10 anchor points
   (US$1M -> 0, US$1B -> ~5, US$1.6T -> 10). Candidates whose sourcing names a specific dollar
   figure (the $2 billion UAE stablecoin purchase, the $6.6 billion Maryland shipyard deal,
   the $201 million Sokolov fund) are scored from that figure rather than a category guess.
4. **misinformation_deception_severity** — the category baseline, raised when a candidate is
   marked `allegation` (+1.5) or `mixed` (+0.75) rather than `established`, matching the
   legacy `credibility_risk` axis's documented meaning ("editorial caution required before
   amplification; higher means more corroboration is needed").
5. **recurrence_persistence** — category baseline only; fresh events are by construction
   single-point-in-time and this project's 10-category taxonomy does not map cleanly enough
   onto the legacy 51-category frequency data to compute a reliable record-derived value.
6. **current_relevance** — never a baseline. Computed directly from each candidate's own
   `event_date` relative to the 2026-10-23 research cutoff, using a 30-day half-life decay
   (an event dated the cutoff day scores 10; 30 days old scores 5; the oldest fresh candidate,
   64 days old, scores ~2.3). This mirrors Phase 1's own day-since-event decay fallback, with
   a shorter half-life appropriate to a lane whose entire span is ~2 months rather than a
   catalogue reaching back to 1927.

**Confidence gate**: `deferred` if zero sources are recorded (did not occur in this batch;
no candidate without at least one source reached candidate status); `low` if exactly one
source, or if no source carries `is_primary`/a named publisher, or if the candidate is marked
`allegation` with fewer than 3 sources; `medium` otherwise. No candidate was assigned `high`;
that tier is reserved for a human editorial review pass that has not yet occurred for this
batch, exactly as Phase 1 reserved it for its own reviewed-evidence path.

Full per-candidate output, including every `basis_notes` entry explaining which adjustments
fired, is in `scoring/impact-v2-fresh-event-scores.jsonl`.

## Model assignment actually used

The originating fresh-event research prompt
(`fresh-event-ledgers/fresh-events-next/2026-10-03/PROMPT.md`) specifies "GPT-6 Luna low" for
routine per-batch research workers. As in Phase 1, no non-Claude model is available in this
execution environment.

| Role | Requested (original prompt) | Used | Why |
| --- | --- | --- | --- |
| Orchestrator/coordinator | (not specified in the fresh-event prompt; this task explicitly names Sonnet 5) | Sonnet 5 (this session) | Matches this task's explicit instruction; consolidation, dedup, scoring-engine design, and validation were done directly by this session rather than fanned out further, per Phase 1's lesson that judgment- and consistency-dependent work is unreliable when distributed |
| Research workers (3 parallel lanes) | GPT-6 Luna, low | Sonnet 5 (via the `Agent` tool, `general-purpose` subagent) | GPT-6 is unavailable (Claude family only). A low-tier Claude model (Haiku) was considered but not used: unlike Phase 1's purely mechanical row-scoring work, fresh-event research requires live multi-source verification, duplicate screening against two reference files, allegation/established attribution discipline, and exact-limit prose drafting in one pass — judgment-heavy work of the same kind Phase 1 found a low-tier model unreliable at (2 of 4 scoring workers and both validators failed outright; a third wrote data under the wrong filenames). Using the same tier as the orchestrator for this judgment-heavy work, while still running all three lanes concurrently for genuine wall-clock parallelism, was judged the more faithful way to honor the original prompt's intent of fast, reliable fan-out |

All three research workers' output was verified by reading the files they actually wrote
(not their self-reported summaries), consistent with Phase 1's explicit lesson that a
worker's own completion report is not sufficient evidence that its output exists or is
correct.

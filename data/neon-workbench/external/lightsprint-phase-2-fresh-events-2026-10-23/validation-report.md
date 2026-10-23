# Phase 2 — validation report

Scope: completeness, uniqueness, validity, consistency, and timeliness checks against the
41 new fresh-event candidates this phase produced, and a lighter completeness/uniqueness/
validity pass across the full 147-candidate master file (41 new + 106 carried forward from
prior research passes). Dimensions follow the data-quality-frameworks skill. Checks were run
by `scoring/validate_fresh_events.py`, a script independent of `scoring/score_fresh_events.py`
(the generation path), against the files actually committed in this PR, not against any
in-memory or self-reported state.

## 41 new Phase 2 candidates — full validation

| Check | Result |
| --- | --- |
| Completeness (all required fields present and non-empty) | 0 failures |
| Uniqueness (no duplicate candidate_id within this batch) | 0 failures |
| Uniqueness (no candidate_id collision with the 106 prior candidates) | 0 failures |
| Uniqueness (no exact date+title match against the frozen catalogue or prior candidates) | 0 failures |
| Validity (category is one of the 10 `VALID_CATEGORIES`) | 0 failures |
| Validity (event_date/date_start/date_end are valid ISO dates, date_end >= date_start) | 0 failures |
| Validity (description_short <=180 chars) | 0 failures |
| Validity (description_medium 45-90 words) | 0 failures |
| Validity (description_long 140-300 words) | 0 failures |
| Validity (source URLs are http(s)) | 0 failures |
| Validity (every candidate has an impact-v2 score row; no row marked "high" confidence) | 0 failures |
| Validity (every scored dimension in 0-10 range; composite matches recomputed mean) | 0 failures |
| Consistency (no duplicate values within people_tags/organization_tags) | 0 failures |
| Timeliness (event_date <= 2026-10-23 cutoff) | 0 failures |

**REQUIRED errors: 0. ADVISORY notes: 0.**

An additional automated fuzzy-duplicate pass (significant-token overlap >=50% combined with
event dates within 3 days of each other) found zero near-duplicates within the 41 new
candidates, against the 106 prior candidates, or against the 288 frozen-catalogue rows dated
2026-08-01 or later. A further automated scan of all 41 candidates' titles and descriptions
for banned AI-writing patterns (em dashes; "it's worth noting"; "despite these challenges";
"delve"; three consecutive sentences of identical word count; and others from the deslop/
anti-ai-slop-writing skill references) found zero hits.

One genuine cross-worker duplicate was caught and resolved before validation: the
administration and gap-check lanes independently drafted the same October 22 shareholder
lawsuit (naming Trump personally over a UAE-linked World Liberty Financial crypto deal). The
richer of the two versions, which cites the primary court-filing PDF, was kept; the other was
dropped. This is documented in `coordinator-consolidation-log.json`.

## Full 147-candidate master file — lighter pass

The 84-candidate September batch (`research_phase: phase1-fresh-prior`, from the
`perplexity-fresh-events/2026-09-30` ledger) predates this project's current three-tier
synopsis schema and carries only a single `synopsis` field, duplicated here into
`description_short`/`description_medium`; it has no `description_long`. This phase did not
fabricate a long-form synopsis for 84 records it did not itself research, since doing so
would mean writing new prose about events this phase did not verify, which directly
contradicts the "never invent a fact" rule applied to this phase's own research. This is
reported as a pre-existing, documented gap rather than silently left unflagged:

| Check | Result |
| --- | --- |
| Completeness (candidate_id, event_date, category, source_urls, short description present) | 0 failures |
| Completeness (description_long present) | 84 advisory notes (the pre-existing September-batch gap described above); 0 failures among the other 63 carried-forward + 41 new candidates |
| Uniqueness (no duplicate candidate_id across all 147) | 0 failures |
| Validity (category is one of the 10 `VALID_CATEGORIES`) | 0 failures (1 pre-existing defect found and corrected: a candidate using the non-canonical category `Democratic Backsliding` was remapped to `Election Interference`, the closest fit given the entry concerns an FCC political-ad-rate rule benefiting one party ahead of the midterms; see `_category_corrected_from` on that record) |
| Validity (every candidate has an impact-v2 score row; no row marked "high") | 0 failures |
| Timeliness (every event_date falls within 2026-08-20 - 2026-10-23) | 0 failures |

**REQUIRED errors: 0. ADVISORY notes: 84 (all the same documented, pre-existing gap).**

## Accuracy (the one dimension no script can fully automate)

A script can confirm a source URL is well-formed and that a dollar figure appears in text; it
cannot confirm the underlying reporting is accurate. For the 41 new candidates, the
orchestrating session read a non-random sample of 8 of 41 (about 20%) in full, cross-checking
their sourced claims against the cited articles/filings, including every candidate marked
`allegation` that names a living person by claim of wrongdoing (the Kushner/Vanity Fair
hacked-phone allegations, the UAE emoluments lawsuit, the Barron Trump/Andrew Tate
congressional letter). In every sampled case: allegations were attributed to their source and
paired with the subject's on-record denial where one existed; established facts cited at
least one primary or two independent mainstream sources; and no dollar figure, date, or quote
in the drafted text exceeded what the cited sources actually state.

## Known, deliberately out-of-scope items

- 14 leads remain genuinely unresolved (`fresh-event-candidates/unresolved-leads.jsonl`),
  each with its exact blocker. None were padded into candidates to inflate the count.
- The 106 prior candidates' `allegation_or_established` field is defaulted to `mixed` with an
  explicit `_allegation_status_note`, since that classification did not exist when they were
  authored and re-verifying all 106 individually was out of scope for this pass; it does not
  affect their score's `misinformation_deception_severity` in a way that was independently
  re-checked per record.

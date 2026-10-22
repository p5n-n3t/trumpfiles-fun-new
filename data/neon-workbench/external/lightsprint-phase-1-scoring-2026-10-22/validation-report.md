# Phase 1 — impact-v2 validation report

## 1. Fan-out reliability (reported for transparency)

The first fan-out attempt (4 scoring workers + 2 validators, Haiku/low-effort) had a 57%
failure rate: 2 scoring workers and both validators crashed with "prompt is too long"
(from loading full partition-sized files into their own context instead of filtering
file-to-file), one worker wrote the right data under the wrong filenames, and one worker
returned a passing self-check with **zero files actually written to disk**. None of this
was taken at face value — every worker's claimed output was checked against the real
filesystem and the source database before being trusted. See `coordinator-ledger.json` for
the full account and recovery actions. The difficult-case reviewer (Sonnet) is the one
component of the original fan-out that worked correctly on the first attempt and was kept.

## 2. Coordinator's independent structural validation

Run by a validator script separate from the generation script, over the final merged
`impact-v2-proposed-scores.jsonl` (7,143 rows), cross-checked against the authoritative
`trump_entries` table in the reference sqlite catalogue:

| Check | Result |
| --- | --- |
| Entry count matches catalogue (7,143) | **PASS** — 7,143 / 7,143 |
| Zero missing entry_numbers | **PASS** — 0 missing |
| Zero extra/out-of-catalogue entry_numbers | **PASS** — 0 extra |
| Zero duplicate entry_numbers | **PASS** — 0 duplicates |
| Every criterion is an integer 0–10 | **PASS** — 0 violations across 71,430 criterion values |
| Every composite == round(mean(10 criteria), 1) | **PASS** — 0 mismatches, recomputed for all 7,143 rows |
| evidence_confidence ∈ {high, medium, low, deferred} | **PASS** — 0 invalid values |
| No needs_context/soft_hide_candidate/split_required entry has confidence=high | **PASS** — 0 violations across all 74 such entries |
| deferred-or-low-confidence-scores.jsonl is an exact subset | **PASS** — 1,508 rows, exactly matches the low+deferred filter |
| No modification outside the dated Phase 1 directory | **PASS** — see `git diff --stat` in the PR; only paths under `data/neon-workbench/external/lightsprint-phase-1-scoring-2026-10-22/` are touched |
| No legacy score row overwritten | **PASS** — this layer is purely additive; `trump_individual_scores` was read-only reference data in `/tmp`, never written to, and was never copied into the repository |
| 152 reviewer decisions applied, 0 forbidden overrides | **PASS** — all 152 difficult-case decisions merged; 0 attempts to set high confidence on a capped-disposition entry |

Full machine-readable result: see `coordinator-ledger.json`. Raw check output is
reproducible from the merge script's JSON summary (total_rows=7143, missing_count=0,
extra_count=0, criteria_errors=0, composite_errors=0, confidence_errors=0,
cap_violations=0, all_clean=true).

## 3. Final independent QA (Opus, after all other work completed)

**Overall verdict: ALL CHECKS PASSED.** The QA pass explicitly did not trust this
document's own "coordinator" checks above and recomputed everything from the raw jsonl
files and the reference sqlite database independently.

| # | Check | Result |
| --- | --- | --- |
| 1 | 7,143 unique entry_numbers, exact match to `trump_entries` | **PASS** |
| 2 | `score-provenance.jsonl` has the same 7,143 entries, fields consistent | **PASS** |
| 3 | All 71,430 criterion values integers 0–10; composite recomputed for every row | **PASS** — 0 mismatches |
| 4 | `evidence_confidence` ∈ {high, medium, low, deferred} only | **PASS** — medium 5,635 / low 1,487 / deferred 21, no other values |
| 5 | No needs_context/soft_hide_candidate/split_required entry has confidence=high | **PASS** — all 74 such entries (57+16+1) verified low; `rewrite_disposition` matches `terminal_disposition` in all 497 PR #76 rows, 0 mismatches |
| 6 | No "high" confidence was self-assigned by the deterministic/metadata-only path | **PASS** — zero `"high"` values anywhere in the dataset; reviewer path produced 150 low / 2 medium / 0 high |
| 7 | `deferred-or-low-confidence-scores.jsonl` is an exact subset | **PASS** — 1,508 rows, byte-identical to their merged counterparts |
| 8 | Criterion values are genuinely derived per-entry, not templated/copy-pasted | **PASS** — bulk cross-check of every row's quoted legacy axes and composite against `trump_individual_scores` (0 mismatches); 4,540 distinct criterion vectors across 7,143 rows; 16 entries hand-sampled across all 4 partitions (including 4 escalated/reviewed ones), all plausible for their specific title/data |
| 9 | Read-only / additive only; no canonical writes; no frozen sqlite committed | **PASS** — no SQL write statements anywhere in the directory; no `.sqlite`/`.db` files present |
| 10 | 152 reviewer decisions match the real escalation set and the reviewer's factual claims check out | **PASS** — escalation set independently rebuilt from the composite≥8.0 + thin-evidence rule (152, matching exactly); bulk-checked all 152 claimed source counts/dispositions/legacy composites against the database (0 false claims); 3 hand spot-checked (entries 5094, 5334, 214) word-for-word against `disposition_rationale` |

### Non-blocking observations from this QA pass, and how they were handled

1. **Partition copies were briefly stale after the difficult-case review** (13 rows still showed pre-review `scoring_basis`/confidence). *Fixed*: all four partition directories were regenerated from the final post-review merged data (see commit); `impact-v2-proposed-scores.jsonl`, `score-provenance.jsonl`, and `deferred-or-low-confidence-scores.jsonl` in every `partitions/partition-0N/` directory now match the top-level merged files exactly.
2. **`difficult-cases.jsonl`'s `composite_score` field held the legacy `trump_individual_scores` composite, not the impact-v2 composite that actually triggered escalation** (visible on entry 5240: legacy 7.88 vs. the real trigger, 8.1). *Fixed*: every row in `difficult-cases.jsonl` now also carries `legacy_composite_score` (the original field, explicitly relabeled) and `impact_v2_composite` (the correct, escalation-triggering value), plus a one-line `composite_score_note` explaining the distinction.
3. **`score_rationale`'s "N linked source(s)" count mixes two sources**: the normalized `trump_sources` row count when present, else the length of the `trump_entries.sources` JSON cache. This is an intentional fallback (a cached source array is still real recorded data, not fabricated), documented here rather than changed, since 1,412 rows legitimately have a cached source but zero normalized `trump_sources` rows. The "Methodology" section of `scoring-coverage-report.md` describes this fallback explicitly.
4. **515 entries use fixed category-baseline defaults** for `people_institutions_affected` (and 481 of those also for `misinformation_deception_severity`) because they lack the corresponding legacy axis (`impact_scope`/`credibility_risk`). This is a known limitation of a metadata-only pass for entries outside the legacy-scored set, not a rule violation — these entries skew toward `low`/`deferred` confidence already (158 of the 515 are `medium`, all pre-existing legacy-scored entries missing only one of the two axes). Left as-is; worth revisiting if Phase 1 is ever extended to backfill those two axes specifically.

None of the four observations affected entry count, criterion bounds, composite math, confidence-enum validity, or the disposition confidence cap — the blocking correctness checks (1–7, 9) all passed before these fixes were applied, and the two fixes applied (1 and 2) make the data more internally consistent, not less.

## 4. Overall result

**All validation requirements in the task are met: exactly 7,143 unique entry numbers,
zero missing/duplicate rows, every criterion an integer 0–10, every composite
mathematically correct, all confidence values valid, no modification outside the new dated
directory, no legacy score row overwritten.** Confirmed independently three times: by the
coordinator's own validator, by the final Opus QA pass, and by direct spot-checks against
the raw sqlite database and PR #76 results during this report's preparation.

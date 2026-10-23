# Phase 1 — impact-v2 scoring — PROGRESS

Status: **complete**, pending final QA sign-off (see `validation-report.md`).

## Timeline

1. **Prerequisite check** — confirmed `main` did not include the completed PR #76 rewrite
   work, and that this repository's branches/PRs contained none of the scoring inputs
   (`SCORE_MODEL.md`, `rescore-lane-input.json`, `schema-v2-draft.md`, the sqlite export).
   Reported this blocker before doing any scoring work.
2. **Input resolution** — the actual inputs were located on
   `origin/codex/langsmith-cloud-inputs-20261022` (verified as a genuine branch on the real
   GitHub repo, built directly on PR #76's head commit). Copied read-only into `/tmp` in the
   sandbox; never committed to this git tree.
3. **Methodology design** — built and unit-tested a deterministic impact-v2 scoring engine
   against the full 7,143-entry catalogue, grounded in the legacy 8-axis scores, category,
   financial/reach/duration fields, and the PR #76 rewrite-disposition data.
4. **Branch created**: `lightsprint/phase-1-catalogue-scoring-20261022` from `main`.
5. **Fan-out attempt #1** — 4 scoring workers (partition split) + 2 validators + 1
   difficult-case reviewer. **2 of 4 scoring workers and both validators failed** ("prompt
   too long" from loading full files into context); a 3rd scoring worker wrote the right
   data under the wrong filenames; a 4th reported a passing self-check with **zero files
   actually written to disk** (caught only because the coordinator verifies files directly
   rather than trusting self-reports). The difficult-case reviewer completed and was
   spot-checked against the raw database — genuine, accurate, well-reasoned.
6. **Recovery** — discarded all unreliable worker file output. Regenerated all four
   partitions directly from the same already-verified deterministic engine (no algorithm
   change, so consistency across partitions is guaranteed). Dispatched a second
   difficult-case review pass for the 130 escalated entries the failed workers never
   surfaced (the first pass only covered 22/152). Spot-checked its highest-stakes claims
   (a `needs_context` cap and both confidence upgrades) against the raw database.
7. **Coordinator merge** — merged all four partitions plus all 152 reviewer decisions into
   the top-level required files; ran an independent structural validator (separate code path
   from the generation script) over the full merged set: **0 missing, 0 duplicate, 0
   criterion-bound errors, 0 composite-math errors, 0 confidence-enum errors, 0
   disposition-cap violations.**
8. **Final independent QA** — Opus audit of the merged output, re-deriving checks from
   scratch rather than trusting any prior report. Outcome recorded in
   `validation-report.md`.

## What is NOT done in this phase (by design)

- No canonical/legacy score row was changed.
- No Neon or Neo4j write was made.
- Phase 2 (fresh-event research) and Phase 3 (Neo4j staging) are explicitly out of scope
  for this phase and were not started.

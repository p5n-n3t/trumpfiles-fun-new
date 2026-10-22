# Uniform DB / graph / retrieval progress

## 2026-09-24 — offline baseline

- Source of truth is frozen at `data/neon-export/sqlite/trump_local.sqlite`; production Neon is write-blocked pending local acceptance.
- Created working root `data/neon-workbench/working/` and copied the frozen SQLite export to `working/trump_local_work.sqlite`.
- Created `shards/` and `patches/approved/` lanes for independently auditable output.
- Baseline validator: **pass**.

| Check | Baseline |
| --- | ---: |
| entries | 7,143 |
| scores | 7,058 |
| sources | 4,771 |
| keywords | 18,328 |
| unscored | 85 |
| short text | 112 |
| exact duplicate groups | 40 |
| invalid phases | 2,543 |
| entries without HTTP source | 1,375 |

## Execution gates

1. All transformations are patch JSONL or isolated SQLite copies; the frozen export stays untouched.
2. Soft-hide is the only removal mechanism and must include an audit reason.
3. Source discovery must use credible URLs; no invented links.
4. Neo4j remains a projection of Postgres-shaped records, never a source of truth.
5. Neon upload requires reviewed ordered patches, dry-run counts, local validation, and explicit final release decision.

## Active lanes

- Phase remap + dedupe review: isolated SQLite and approved patch outputs.
- Entity/alias/link bootstrap: Postgres-shaped graph patch outputs.
- Rewrite + score enrichment: evidence-preserving approved patch outputs.
- Orchestrator: source shard setup, schema/retrieval/Neo4j implementation plan, merge/validation.

## 2026-09-24 — merged offline patch acceptance

- Added `scripts/validate_merged_patches.py`, a read-only gate that validates every currently merged lane against the frozen SQLite export; its reports are in `reports/merged_patch_validation.{json,md}`.
- **Patch-integrity gate: pass (0 errors).** Phase queue coverage is 2,543 = 2,541 canonical remaps + 2 explicit cross-era deferrals. Dedupe decisions cover 59 reviewed soft-hides across 40 clusters, each retaining an audit reason, canonical target, and merge-before-hide ordering.
- **Content queue coverage: pass.** All 112 rewrite records have an accompanying audit record and meet the title (20+) and synopsis (80+) floor. The 85-score queue is completely accounted for as 64 provisional score records plus 21 explicit source-triage deferrals; no frozen score row is overwritten.
- **Graph patch integrity: pass.** The bootstrap contains 716 entities, 17 evidence-bound aliases, 4,749 `mentioned` entity-entry links, and 56 explicit entry links. The validator proves every emitted graph link resolves to frozen-export entries/tags and that every frozen `people_tags` occurrence is represented exactly once after documented alias normalization.
- **Release remains blocked.** Source triage artifacts are not yet present: 1,375 frozen entries lack an HTTP source and there are no `sources_add.jsonl` or `sourceless_soft_hide.jsonl` patches. Schema v2, corpus generation, Neo4j re-import, retrieval smoke tests, and a reviewed small-batch Neon plan remain unvalidated. No Neon or frozen-export writes were performed in this lane.

## 2026-09-28 — continued offline integration

- Recovered 1,890 unique generated rationales from the old agent-1 dispatcher and RotoXY waves. Of these, 1,774 pass the structural/length contract and are centralized in `patches/candidates/rationale_salvage_2026-09-28.jsonl`; 116 failed that contract and 2,953 of the 4,843-item expansion queue have no recovered output. Of the 1,774 candidates, 1,093 have a source record in at least one checked layer and 681 have none. Source presence does not prove claim-level factual accuracy, so none of these candidates is approved for publication yet.
- ChatGPT Web is actively writing `external/chatgpt-web-sources/`. At the 07:28 UTC checkpoint, 1,165 of 1,219 assigned entries were processed, leaving 54. Its live files contained 44 repeated `(entry_number,url)` rows and three entries present in both accepted and unresolved output. The source integration preflight is in `reports/source_integration_preflight_2026-09-28.md`; merge must wait for a stable completed snapshot and entry-level review.
- Consolidated the agent-2 backfill safety patch into main. The backfill defaults to dry run, retries transient Exa failures, and reports row failures separately; its 16 focused tests passed. Consolidated agent-1's reusable rewrite orchestrator and its four focused tests passed. The discarded two-root dispatcher state remains archived in agent-1 rather than copied into the canonical workbench.
- Re-ran merged-patch validation: six checks, zero errors, one incomplete-source warning. The offline retrieval corpus has 7,084 documents and passed the 20-query structural/lexical smoke test. This is not semantic, live Worker, or production proof.
- A full-catalog severity rubric proposal and worktree/technical audits are in `reports/`. A 120-entry benchmark, local graph-table staging, and a safer Neo4j projection are in progress. Existing 64 score patches remain provisional; 21 of the original 85 unscored entries remain deferred for source review.
- Neon, Vectorize, Neo4j, and deployment remain unchanged during this integration. Release requires final source disposition, claim review, a locked scoring benchmark, local graph/patch acceptance, fresh Neon drift checks, ordered application, post-apply reconciliation, and live retrieval/client verification.

## 2026-09-28 — completed source queue and graph dry run

- ChatGPT Web finalized its assigned queue: 1,219 of 1,219 target entry IDs, with 725 accepted and 494 unresolved in the checkpoint. Source JSONL had 901 accepted rows before pair deduplication; 44 repeated `(entry_number,url)` rows were identified. The final source compiler checks exact assignment coverage and emits 852 unique URL pairs as **candidates only**. It excludes two out-of-target entry IDs and all current accepted/unresolved conflicts (4234, 4306, 5661). The 494 unresolved entries still require claim correction, further research, or auditable disposition. `reports/source_compilation_2026-09-28.json` contains the exact reconciliation.
- The graph is populated in an isolated local SQLite copy: 716 entities, 17 aliases, 4,749 mentioned links, and 56 explicit entry links. The updated Neo4j importer defaults to a read-only local projection; its dry run resolves 49,333 relationships and three focused tests pass. No live Neo4j re-import has run.
- The full-catalog severity design has a 120-entry benchmark manifest. Two independent reviewers completed a 20-entry pilot: 19 paired scores and one shared deferral. They were within one point on 106 of 114 dimension comparisons; two three-point disagreements led to clarified rules for private financial benefit and court rulings. The remaining benchmark and adjudication are not complete, so no full-catalog scores are approved.
- An isolated source preview loaded 156 previously approved source rows and 852 candidate pairs into a disposable SQLite copy, with candidate provenance explicit. It raised relational-table HTTP coverage from 4,356 to 5,234 of 7,143 entries and left 1,909 without a relational HTTP row. This 1,909 figure is **not** the earlier 1,375 baseline, which also counts HTTP URLs in legacy embedded source data. The preview is neither a factual approval nor a Neon migration.
- Two independent provisional reviews now cover all 120 selected severity benchmark entries. The reproducible analyzer found 112 numeric pairs, five shared deferrals, three one-sided deferrals, and 64 adjudication-queue records. Per-axis agreement fails for procedural abuse (87/112 within one) and duration/reversibility (89/112); composite agreement is 98/112 (87.5%), below the 90% gate. The rubric is **not locked** and full-catalog scoring must wait for adjudication and a revised benchmark pass. See `reports/severity_benchmark_agreement_2026-09-28.md`.

## 2026-10-05 — offline editorial queues reconciled

- Authoritative snapshot: `external/card-consistency21-2026-10-05/manifest-20261005T120428Z.json`. Every one of the 7,143 frozen IDs plus 84 new candidates has a disposition: 7,227 total, no missing IDs. The 283 records held before rewriting remain accounted for, not silently excluded.
- Descriptions: 6,891 complete; 53 staged records need context; 283 prior holds (32 split-required, 111 soft-hide candidates, 59 approved duplicates, 81 unresolved). All 6,891 completed descriptions meet short <=180 characters, medium 45–90 words, long 140–300 words. Existing sufficient copy was preserved except explicit supported consistency corrections. Core insight labels cover exactly these 6,891 completed records.
- Impact-v2 remains a **provisional editorial comparative index**, not a measured real-world harm score or a completed independent factual release review. Full catalog: 6,758 numeric proposals and 469 deferrals. Only 6,739 numeric proposals have complete descriptions and eligible release ranks; 19 historical numeric scores attached to held descriptions are withheld. Totals use exact decimal weights and deterministic ranks without random jitter; legitimate score ties remain.
- All 653 offline gap assignments and 653 independent QA outcomes are saved. The final 21 card consistency assignments produced 20 narrow supported proposals and one explicit hold (1181: unresolved event/date/Trump-link evidence). Coordinator score amendments remove explicitly unsupported institutional, procedural or persistent effects; originals are preserved in provenance. Three inline-wrapper formatting mismatches were resolved using separate full amendments, with no deletion or rewriting of history.
- Append-only audit checks all 132 final gap/QA/consistency jobs across 495 Git file revisions: zero missing historical rows. Local focused tests and the independent Ora5 checksum/universe/formula/rank check are distinct from source-page verification. The two 100-entry core-label pilots justified the seven-field expansion; speculative money, population and relationship enrichment was not generalized from them.
- A resource-capped, exclusive-lock systemd supervisor monitors cloud work every 300 seconds, retries/reassigns confirmed failures, collects outputs and checkpoints. Its finite queue now has all 486 jobs complete; no native bulk worker is running. Local coordination and VM validation are not additional AI model workers.
- Canonical records, frozen export, Neon, Vectorize and Neo4j remain unchanged. Offline completion is not production approval. Remaining production gates: exact current Neon branch/schema and NULL-target preflight, current compute/storage budget evidence, distinct content release review, then bounded manually invoked import and post-apply/live retrieval checks. No automatic retrying Actions import was enabled.

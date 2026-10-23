# Phase 3 validation report

**PASS for offline staging.** All 7,143 frozen canonical entries and all 147 Phase 2
candidates are covered. The candidate graph remains separate and unapproved. These
checks establish an inspectable projection; they do not certify every underlying
claim or assert that all real-world relationships are known.

## Inputs and scope

Base main commit: 63b1faecca80c05d0bf525649306a537b19ac7ac.
Read-only input commit: 15dda3e706e11aeb39564e52db9f4d98bc796a1d on
codex/langsmith-cloud-inputs-20261022. Exactly four input files were extracted under
/tmp/phase3-inputs; no SQLite input is committed. Existing Phase 1/2 artifacts remain
untouched. Phase 1 scoring and Phase 2 research were read, not repeated. The input
branch's draft informs the labels; frozen raw category/phase values are retained to
avoid silently changing catalogue classification.

| Temporary input | SHA-256 |
| --- | --- |
| frozen/trump_local.sqlite | 9f1d4f07d066ab08e515fc8367c3beb4d21f822d03218dbee597ff032252c1d7 |
| graph/schema_v2_graph_staged.sqlite | 9ed991d1d3d3226c31176fa82db0dfb47f76371fa56182aa4f51d482e2a8cdb2 |
| project-docs/TODO-uniform-db.md | 5ab7b13e6583bc50e353b8ec6633a97fc9e0baba1f5e9effefa9a75de7a32967 |
| project-docs/schema-v2-draft.md | 19143f9f82ca043abf10f9fb4d473800719a1dc80cd5fefe3fa3b9dc8a8ab3b7 |

The generator hashes all four inputs before and after reading, opens SQLite with
mode=ro and immutable=1, and enables query_only. The reproduction validator compares
all five JSONL files, graph-summary.json and projection-manifest.json byte-for-byte
against a fresh generation in /tmp. The manifest also records the exact entry-number
and candidate-ID sets and the Phase 2 master file hash.

## Reconciled counts

| Canonical node type | Count |
| --- | ---: |
| Category | 51 |
| Entry | 7,143 |
| Organization | 74 |
| Person | 573 |
| Phase | 25 |
| Source | 6,100 |
| Theme | 8,443 |

**Canonical total: 22,409 nodes; 50,313 relationships.** All canonical nodes and
relationships have CANONICAL status. Confidence is faithful-extraction confidence,
not approval of a claim.

| Canonical relationship type | Count |
| --- | ---: |
| HAS_THEME | 23,708 |
| IN_CATEGORY | 7,143 |
| IN_PHASE | 7,143 |
| MENTIONS | 4,600 |
| SOURCED_FROM | 7,719 |

The review graph has **147 ProposedCandidate roots, 1,307 total nodes, 1,160
relationships, and 2,467 rows**. Every row is PROPOSED_NOT_APPROVED. There is no Entry
label, allocated entry_number, shared canonical node ID or cross-layer relationship.
The dry-run import plan excludes every proposed and withheld row.

**Withheld: 1,473 records** — 1,098 source-value/URL issues; 149 links to untyped
other entities; 116 entry-link/duplicate candidates; 110 proposed-to-canonical
research references. The 116 consist of 56 staged editorial RELATES_TO claims,
one additional JSON self-link and 59 pending duplicate decisions. No ACTOR_IN,
TARGET_OF, RELATES_TO, SAME_AS or PRECEDES edge is supported strongly enough for
this projection; none is invented. Dates and shared names do not create edges.
There are 647 entity-alias audit rows; only explicit mappings are used. No duplicate
same-type entities or conflicting normalized aliases occur in the current input.

## Commands and results

Commands below run from this directory unless a repository-root path is shown.
Full exact argv, stdout, stderr and exit codes are in validation-runs.json.

| Command | Run 1 exit | Run 2 exit | Result |
| --- | ---: | ---: | --- |
| node validate-graph-staging.mjs --reproduce /tmp/phase3-inputs | 0 | 0 | Full validation and regeneration match |
| node neo4j-dry-run-import.mjs | 0 | 0 | DRY_RUN; execution_enabled=false; identical canonical plan |

The paired stdout and stderr are byte-identical. Graph data hashes are in
projection-manifest.json and in the dry-run stdout. Default import quantities are
22,409 nodes and 50,313 relationships; proposed_import_rows=0 and
ambiguous_import_rows=0. The suggested future batch size is 250, concurrency 1.

Additional checks:

- node --test graph-staging.test.mjs: **13 passed, exit 0**. Includes explicit Phase 2
  candidate injection as a canonical Entry, illegal Entry label in review data,
  number allocation, status leakage, cross-layer endpoints, duplicate IDs/aliases,
  missing provenance/basis, unsupported labels/types, unsafe URLs and import flags.
- python3 -B test_projection_rules.py: **4 passed, exit 0**. In-memory fixtures cover
  mismatching-alias refusal, alias-row provenance, untyped-entity withholding and
  refusal to invent/upgrade source URL schemes.
- From repository root: node --test scripts/enrichment-contract.test.mjs
  scripts/stage-trump-claims.test.mjs scripts/backfill-sources-state.test.mjs:
  **31 passed, exit 0**.
- bun run lint: **exit 0**, 0 errors and 186 warnings in existing repository files;
  none in this package. package.json defines no check or test:changed script, so
  those steps are skipped. A production build is unnecessary for this offline data
  package and is not run against the active preview.

An initial new test expected the illegal-label error but received the earlier
coverage error. The bad graph was rejected; the validator now checks the prohibited
Entry label first and all 13 tests pass. Reviewers also found missing field-level
proposed Source metadata provenance and two latent alias-handling risks. These are
fixed, regenerated and covered by the final repeated checks. No known current-data
structural defect remains.

## Manual inspection and independent QA

The coordinator manually inspected **20 canonical relationships: four each of
MENTIONS, SOURCED_FROM, HAS_THEME, IN_CATEGORY and IN_PHASE**, comparing fields with
immutable SQLite rows. The list, stable relationship IDs, entry numbers, targets and
checked bases are in worker-notes/coordinator-manual-review.md. An additional check
read entry 2264's sources[0].url directly to confirm its JSON-only BBC source edge.
The independent QA worker records another 20 source-checked examples. Relationship
workers separately audit explicit mentions, all 110 withheld candidate crosslinks,
1,448 proposed structured evidence tuples and all 558 populated proposed source
publisher/date values. Detailed findings and limits are in worker-notes/.

## Proof

/proof routes this branch to /logic-proof, which runs /flow-diff. Old: merge-base
with origin/main at 63b1fae; new: this task's working tree. All changed Python and
JavaScript runtime files sit on the following three charted flows. Schema declarations
are reviewed as an offline contract, not an executed migration. Generated data,
reports and tests add no independent runtime flow. Diagram line counts exclude
comments, blank lines, Python docstrings and tests.

- [Offline Canonical Projection](https://lightsprint-image-uploads.s3.us-east-1.amazonaws.com/uploads/images/2026-10-23/bgciPPzmRK9oo8j9hUQdt.png)
- [Proposed Candidate Isolation](https://lightsprint-image-uploads.s3.us-east-1.amazonaws.com/uploads/images/2026-10-23/fLgGOdzcs1rjjRZCqNvN0.png)
- [Offline Validation And Import Plan](https://lightsprint-image-uploads.s3.us-east-1.amazonaws.com/uploads/images/2026-10-23/gHk81ehxSD2-0u8ktyfHD.png)

Canonical extraction and candidate isolation are **Proven** by full regeneration,
source comparisons, negative tests and independent audits. Default validation and
import planning are **Proven** by runtime results. The explicit apply-refusal branch
is **Read only**: the flag is deliberately never supplied under the task boundary;
code inspection confirms it exits before any import operation. Offline schema DDL
is also **Read only**, with idempotent IF NOT EXISTS declarations; no Neo4j server
is used to execute it. No live import is claimed to be tested. The Python alias tests
use in-memory synthetic fixtures; graph generation and manual samples use the real
pinned input snapshots. All three diagrams are hosted and registered in the task's
verification set. There is no application UI change or route to capture.

## Offline safety and remaining human decisions

**Neon and live Neo4j were untouched.** The package has no database driver, live
endpoint, credential lookup or network client. Its safety audit rejects environment
credential reads and known network/database imports. Runtime commands are local
SQLite reads, local generation, validators and tests; the default importer reads only
staged JSONL and prints JSON. No --apply flag, existing scripts/neo4j-import.mjs,
live database client, deployment, candidate promotion or canonical mutation is run.
Repository network operations are input fetches, dependency downloads for diagram
rendering, git publishing and PR metadata only. Frozen input hashes remain unchanged.

Source validity checks cover HTTPS syntax and secret-free URLs, not availability,
primary-source quality or claim entailment. Raw non-HTTPS/non-URL source values are
quarantined with exact provenance and withholding reasons; they are not projected as
Source.url. Legacy raw taxonomy and provisional aliases still need human review.
No entry merge, fuzzy identity decision, ownership, kinship, coordination, causality
or wrongdoing is inferred. All 7,143 entries remain distinct despite pending merges.

The next action is human editorial review of the package and 147 unapproved
candidates. Any later deployment requires separate approval and a reviewed
Neon-first migration, followed by a verified Neo4j rebuild; DEPLOYMENT-PLAN.md
specifies backup, bounded batching, compute safeguards, rollback and verification.
Merging this PR approves staging artifacts only.

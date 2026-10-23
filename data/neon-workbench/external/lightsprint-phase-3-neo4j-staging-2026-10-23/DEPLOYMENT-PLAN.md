# Later deployment: separate human approval required

This package performs no deployment. Neon remains the source of truth; Neo4j is
a rebuildable projection. Approval to merge this staging PR does not approve a
database write. The dry-run importer has no database driver or apply implementation.
The existing scripts/neo4j-import.mjs is outside this package and must not be used
with live credentials during Phase 3.

## 1. Review and freeze a release

A human reviews entity identity, alias mappings, URL omissions, raw phase/category
labels, and withheld relationships. All 7,143 existing entries remain distinct,
including entries named in pending duplicate decisions. Do not authorize merges,
soft-hides, or stronger roles merely by accepting the graph projection. Record each
approved change as an append-only decision with reviewer and evidence.

The 147 candidates remain PROPOSED_NOT_APPROVED. Review their allegations, denials,
sources and duplicate checks separately. None can enter the canonical graph through
this package. Any future candidate approval needs a separate catalogue ingestion
change, human decision, entry-number allocation process, and regenerated graph.

Pin the approved commit, input fingerprints and artifact hashes. Re-run the validator,
full regeneration comparison and dry-run plan. Resolve drift against a new read-only
export of the then-current Neon catalogue before approving a release. Do not replay
this older snapshot over newer catalogue data.

## 2. Backup and rehearse

Before any future write, take a restorable Neon backup/branch or full export of every
affected table, schema, constraints and row counts. Record the backup identifier,
release identifier, checksums and tested restore procedure. Preserve original
catalogue and scoring history. Export or snapshot the current Neo4j database and
record projection version and counts; test restoration in an isolated database.

Implement and rehearse a separate Neon migration/importer in an isolated branch.
Use additive graph tables and an import-release ledger. Preserve canonical IDs and
existing entry numbers; validate foreign keys. Store entity aliases and field-level
provenance in the relational source of truth. Do not overwrite catalogue titles,
categories, phases or Phase 1 scores from this projection. Keep review-only data in
separate staging tables with a constraint prohibiting canonical publication.

## 3. Import to Neon first

Only after explicit human approval, have a future deployment implementation use
managed secrets without writing them to source, logs, this package or command output.
Start with 100 rows in one transaction and one connection. Verify the transaction
before advancing. Use batches of at most 250 rows, concurrency 1, parameterized writes,
stable-id upserts and a durable release/batch checkpoint. Commit each verified batch;
stop on an unexpected conflict, status leak, dangling reference or count mismatch.
Retry transient errors with bounded exponential backoff; do not retry data errors.

Set a per-run statement timeout, connection limit, row cap, time cap and compute-budget
cap based on the actual free-tier allowance. Measure the first batch and estimate the
whole run before proceeding. Pause between batches; stop before the allowance is
exhausted, avoid busy polling and unbounded scans, and let compute suspend when idle.
Do not upgrade a plan or increase compute automatically.

Re-export the new relational graph and compare stable IDs, per-type counts, provenance,
entry coverage and content hashes with the approved projection. Verify no candidate is
an Entry and no canonical catalogue/scoring row changed. Only a reconciled Neon graph
release may become the source for the second step.

## 4. Rebuild Neo4j second

Implement a separate reviewed projection importer reading the verified Neon graph
release. Do not import these JSONL files directly into live Neo4j before Neon matches.
Use a new isolated database/instance or a versioned projection, within the service's
actual free-tier limits; if a parallel database is unavailable, require a maintenance
window and a tested backup/restore plan before replacing anything.

Apply the idempotent schema definitions in that isolated target. Batch nodes first,
then relationships, at most 250 records with concurrency 1. Persist checkpoints and
release tags; parameterize values and allowlist labels/types. Serialize provenance as
a JSON string because Neo4j properties cannot contain nested maps. Preserve id,
status, confidence, basis and origin_entry_number. Keep all proposed and withheld
rows out. Stop for memory pressure, storage limits, transaction timeouts or a compute
budget breach; resume by checkpoint only after a human reviews the cause.

Compare every ID and endpoint, per-label/type/status counts, URL format, provenance,
and at least 20 diverse sampled relationships to the verified Neon release. Test path
queries and retrieval using the new projection before switching readers. Check
counts and error rates immediately after cutover and after the first scheduled job.

## 5. Rollback

Before cutover, discard only the incomplete new Neo4j projection and leave readers
on the old version. After cutover, switch readers back to the saved version or restore
the tested backup. For Neon, undo only rows introduced by the failed release using
its release ledger, in bounded transactions with foreign-key order, or restore the
isolated branch/backup according to the rehearsed plan. Never delete shared entities
or overwrite intervening catalogue edits. Verify restored IDs, counts, hashes and
reader health. Record failure and rollback as append-only release events.

The next action after Phase 3 is human review of this offline package and the 147
unapproved candidates; then, if approved, a separately scoped Neon-first migration.

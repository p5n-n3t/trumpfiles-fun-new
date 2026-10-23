# Phase 3 offline graph staging

This is an inspectable projection, not a catalogue edit or a deployment. Canonical
Entry nodes reproduce all 7,143 frozen entries. Shared entity identities come from
explicit staged identities and links; source and taxonomy values come from the
frozen catalogue. Original phase/category spellings remain visible. Confidence
measures structured extraction, not the truth of an allegation.

The separate candidate file has candidate-scoped identities and no Entry labels or
allocated entry numbers. Every record is PROPOSED_NOT_APPROVED. Candidate references
to existing entries are retained as withheld research references. Similar names,
text co-occurrence, date order, pending duplicate decisions and editorial pattern
claims do not create canonical edges. See the ambiguity file for individual reasons.

## Reproduction

Use Python 3 and Node 22 with no external packages or credentials. Fetch the input
branch read-only, and extract only the four files named in projection-manifest.json
from its pinned commit to temporary storage. Keep both SQLite files outside git.
The generator opens them with mode=ro, immutable=1 and query_only enabled.

From this directory, with those inputs under /tmp/phase3-inputs:

```sh
python3 -B generate-graph-staging.py --input-root /tmp/phase3-inputs
node validate-graph-staging.mjs --reproduce /tmp/phase3-inputs
node neo4j-dry-run-import.mjs
node --test graph-staging.test.mjs
```

Repeat the validator and dry-run commands and compare stdout byte-for-byte. The
validator's reproduction mode regenerates the five JSONL files, summary and manifest
in /tmp, compares their bytes and removes the temporary output. The manifest lists
the exact canonical entry and candidate ID sets, so matching a count alone cannot
hide a replaced record. Canonical JSONL rows are sorted by stable ID; keys are sorted.

Node IDs use entry:<existing-number>, entity:<explicit-staged-id>, or a SHA-256
prefix of the exact typed value. Alias maps preserve only explicit mappings. Source
URLs retain path, query and fragment; only scheme and host normalization are allowed.
HTTP, bare hostnames, credentials and secret-like query parameters are withheld.
No source availability or claim truth is reverified in this phase.

The importer reads only staged JSONL and prints a plan. It excludes review-only and
withheld records. Apply is reserved and unimplemented; even a future explicit flag
cannot make this package connect to a database. It was never supplied in this task.
See DEPLOYMENT-PLAN.md for the separate human-approved procedure.

The task-assigned branch is retained for PR linking. The requested
lightsprint/phase-3-neo4j-staging-20261023 branch points at the same release commit.

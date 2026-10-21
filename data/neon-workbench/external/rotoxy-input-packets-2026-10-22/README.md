# ROTOXY historical-enrichment input packets — 2026-10-22

These four JSONL packets are immutable, minimal copies of the 72 frozen-export records assigned to the `trumpfiles-historical-enrichment-20261022-r2` job.

- `ls-01-records.jsonl` through `ls-04-records.jsonl` contain 18 records each.
- Each row includes only the identifiers and editorial/source context needed for research.
- They do not replace, modify, or publish the frozen export, canonical records, Neon database, or prior lane history.
- Cloud workers must write their append-only proposals only to their assigned `data/neon-workbench/external/rotoxy-historical-enrichment-2026-10-22/ls-XX/` directory on a new branch.

The source frozen export remains local at `data/neon-export/tables/trump_entries.jsonl`.

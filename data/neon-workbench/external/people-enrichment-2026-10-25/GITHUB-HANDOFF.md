# GitHub-only continuation handoff

This directory is a **proposal-only, offline** enrichment lane. It is published so
a GitHub-connected agent can continue without local-shell access.

## Safety boundary

Do **not** edit the frozen export, canonical catalogue, live Neon database, or
live Neo4j. Do not treat this staged SQLite file as an import instruction. Every
new relationship remains a proposed, source-backed record until a later review.

## Start here

1. Read `README.md`, `INSTRUCTIONS.md`, and `RESULT-SCHEMA.md`.
2. For source research, read `source-recovery/INSTRUCTIONS.md` and only the
   allocated files in `source-recovery/packets/`.
3. Before taking a packet, check whether its matching file already exists in
   `source-recovery/results/`. Existing result files are claimed and must not be
   replaced.
4. Write one terminal row per input row using the exact schema, then run
   `data/neon-workbench/scripts/validate_people_source_recovery.py` for each
   completed packet.
5. Commit only your new result files and a concise progress note on a new branch
   based on this branch. Open a draft PR back to this branch; do not merge it.

## Useful artifacts

- `source-recovery/packets/`: deterministic 25-record research packets.
- `source-recovery/results/`: completed source-recovery outputs.
- `source-recovery/entity-inputs/`: evidence-constrained entity extraction inputs.
- `source-recovery/entity-results/`: proposed people/organization relationships.
- `reports/source_recovery_audit_2026-10-25.json`: a point-in-time coverage report;
  regenerate it locally only if you have a suitable environment.
- `working/schema_v2_entity_enrichment_staged.sqlite`: offline proposal snapshot,
  included for review/reference only.

## Research standard

Use direct credible HTTPS sources. Prefer official records, court/government
documents, Reuters, AP, and reputable contemporaneous reporting. Do not use a
search-result URL as evidence. Keep unsupported records as `no_credible_source`;
do not invent names, actions, causation, roles, or wrongdoing.

## Current external assignment

`CHATGPT-WEB-ASSIGNMENT.md` lists the packets reserved for a GitHub-based
ChatGPT Web worker. If a listed result already exists when you begin, skip it.
`CLAUDE-CODE-ASSIGNMENT.md` is reserved for the continuing Claude worker and
must not be touched.

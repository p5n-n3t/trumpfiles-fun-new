# LangSmith cloud input bundle — 2026-10-22

This branch is an **input-and-staging bundle only** for a cloud research and
editorial workflow. It is based on `codex/web-needs-context-rewrite-20261022`.
It must not be merged into `main` directly.

## What is included

- `frozen/trump_local.sqlite` — the 7,143-entry frozen catalogue used only for
  reading, duplicate detection, and proposed-copy/scoring inputs.
- `graph/schema_v2_graph_staged.sqlite` — a local staged graph database for
  read-only Neo4j dry-runs and graph-proposal validation. It is not a live
  database and has no credentials.
- `project-docs/` — the current score rubric, rescore queue, schema draft,
  impact migration draft, progress and uniformity TODO.
- `fresh-event-ledgers/` — prior candidate/research ledgers used to avoid
  duplicating already logged current-event research.
- The parent branch's `assignment-packets/` and
  `web-needs-context-rewrite-2026-10-22/` directories, containing all 497
  rewrite inputs and the 107 terminal outcomes already completed.

## Boundaries

- Do not modify frozen records, canonical records, live Neon, or a live Neo4j
  instance.
- Write proposed results only to a new dated output directory.
- Never turn historical copy or URL hints into verified facts without research.
- Treat evidence confidence as separate from editorial impact scoring.
- A graph relationship needs explicit source/metadata support; do not infer one
  merely because two names or keywords appear together.

## Starting state

- Existing description-rewrite scope: 497 numbered entries.
- Terminal outcomes already recorded: 107.
- Remaining exact rewrite scope: 390, as recorded in the parent branch
  checkpoint.
- Fresh-event ledgers are leads, not import-ready records.
- Existing staged graph may have no curated entity/entry links; build and
  validate proposals before any live graph action.

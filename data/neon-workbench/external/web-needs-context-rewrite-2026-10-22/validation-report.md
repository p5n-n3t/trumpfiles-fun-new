# Validation report — Trump Files description rewrite

Completed at 2026-10-22T18:47:04Z against the authoritative manifest and packet files.

## Assignment coverage

- Assigned manifest IDs: **497**
- Terminal result rows: **497**
- Unique result IDs: **497**
- Missing IDs: **0**
- Duplicate IDs: **0**
- IDs outside the assignment: **0**
- Unnumbered historical row processed: **no**
- Allowed terminal dispositions only: **pass**; counts: `{"needs_context": 57, "repaired_proposal": 101, "soft_hide_candidate": 16, "split_required": 1, "supported_partial": 322}`

## JSONL and source integrity

- All six partition result files and research logs parse as JSONL: **pass**.
- Merged results and merged research log parse as JSONL: **pass**.
- Partition outputs match their assigned packet ranges exactly: **pass**.
- Result citations: **569**; merged research-log rows: **569**.
- Result citations and research-log rows match one-to-one by record ID and URL, including title, publisher, source type, and claims: **pass**.
- Source URL format: **pass**; every cited and logged URL uses HTTPS with a hostname, and each citation includes a title, publisher, and supported-claims field.
- Exact repeated full long descriptions: **0**; exact sentence repeats within one long description: **0**. Across records, 65 exact sentence strings recur (334 uses beyond their first occurrence), mostly recurring factual caveats across related topics.
- Short descriptions ending in a truncation ellipsis after the independent review: **0**; 21 clipped short fields were rewritten as complete summaries.

## Description field checks

- Proposed titles: **497/497 nonempty** (no maximum length is defined in the archive spec).
- Short descriptions: **25–180 characters**; all at or below 180: **pass**.
- Medium descriptions: **45–90 words**; all within 45–90: **pass**.
- Long descriptions: **140–258 words**; all within 140–300: **pass**.
- Word counts use the validator tokenizer `\b[\w’'-]+\b`.

## Partition coverage

| Worker range | Records | Research sources | Status |
|---|---:|---:|---|
| partition-01 through packet 01-08 | 95 | 95 | pass |
| partition-09 through packet 09-16 | 80 | 69 | pass |
| partition-17 through packet 17-24 | 80 | 116 | pass |
| partition-25 through packet 25-32 | 80 | 72 | pass |
| partition-33 through packet 33-40 | 80 | 81 | pass |
| partition-41 through packet 41-49 | 82 | 136 | pass |

This report validates structure, field limits, citation formatting, and exact manifest coverage. Editorial support is represented by each record’s attributed copy, source claims, rationale, and terminal disposition. No frozen export, canonical record, Neon database, historical lane, score, or source history was modified.

## Repository check

- `npm run lint`: **pass**, 0 errors and 186 warnings in unchanged application source files.
- The repository defines no `test` or `check` script; none was run.

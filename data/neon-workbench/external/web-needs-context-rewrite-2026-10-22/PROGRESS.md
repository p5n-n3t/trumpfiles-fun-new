# Trump Files needs-context rewrite — 2026-10-22

## Status: partial, NOT ready for PR or canonical import

- Input branch: `codex/web-needs-context-assignment-20261022`
- Working branch: `codex/web-needs-context-rewrite-20261022`
- Source: authoritative **497 numbered catalogue** record manifest. The one unnumbered historical `needs_context` row is excluded.
- **All 49 input packets exactly matched** the manifest's ordered record numbers and IDs; six ownership ranges remain disjoint.
- **107 valid terminal outcomes**, **390 unprocessed**. Unprocessed entries are *not* counted as `needs_context`.
- Status counts: `repaired_proposal` 40; `supported_partial` 0; `needs_context` 51; `soft_hide_candidate` 16; `split_required` 0.
- Of 107 terminal records: **9 independently rewritten/source-checked on 2026-10-22**, **98 carefully mapped from an existing source-focused 2026-10-05 reviewed consolidation**. Previous results are explicitly marked as prior review and retain source fact mapping; no newly performed source checks are claimed for them.
- Source references: 265; distinct HTTPS URLs: 244; two historical HTTP-only URLs were omitted without inventing HTTPS substitutes.
- Resolved-current-row validation: JSONL, assignment, duplicates, title/short/medium/long for 40 repaired proposals, HTTPS URL syntax and blockers for 67 nonusable dispositions all **PASS**.

## Worker ownership / actual coverage

| Partition owner | Packets | Assigned | Terminal | Unprocessed |
|---|---|---:|---:|---:|
| worker-01 | 01–08 | 95 | 25 | 70 |
| worker-02 | 09–16 | 80 | 11 | 69 |
| worker-03 | 17–24 | 80 | 16 | 64 |
| worker-04 | 25–32 | 80 | 29 | 51 |
| worker-05 | 33–40 | 80 | 10 | 70 |
| worker-06 | 41–49 | 82 | 16 | 66 |

The ownership directories contain partition-specific JSONL files; **they are not proof of six active workers**. New GPT-6 Luna agent dispatch via ROTOXY returned internal errors. Current prior-reviewed proposals came from already committed historical work, not new delegated sessions.

## Unfinished acceptance steps

1. Research and issue exactly one terminal disposition for the remaining **390** numbers, prioritizing safe narrowing, not blanket `needs_context` placeholders.
2. Consolidate each owner's full final output only after every assigned ID is accounted for (avoid duplicate historical revisions); then assemble `merged/final-terminal-results.jsonl`.
3. Run whole-batch QA on length limits, materially distinct prose, cited source support, HTTPS format, exact terminal coverage and no canonical/frozen/Neon diff.
4. Open **one draft PR against main** only when all 497 outcomes and a passing release report exist. Do not merge or import.

Only the new append-only output directory has been modified. Frozen exports, canonical records, Neon scripts/data, scoring, source history and old lanes are untouched.

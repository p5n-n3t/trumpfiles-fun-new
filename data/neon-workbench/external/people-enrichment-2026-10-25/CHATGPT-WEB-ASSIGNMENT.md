# ChatGPT Web assignment — source recovery

Work only on these source-recovery packets:

`007, 010, 013, 016, 019, 022, 026, 029, 032, 035, 038, 041, 044, 047, 050, 053, 056, 059, 062, 065, 068, 071, 074, 077, 080, 083, 086, 089, 092, 095, 098, 101, 104, 107, 110, 113, 116`

This is 37 packets × 25 records = 925 entries. Do not touch any other packet,
canonical record, frozen export, SQLite database, Neon database, or Neo4j.

Read the project instructions and:

- `data/neon-workbench/external/people-enrichment-2026-10-25/source-recovery/INSTRUCTIONS.md`
- Every packet assigned above from `source-recovery/packets/`.

For every input record: find at most two direct, credible HTTPS sources for the
specific event. Prefer official records, Reuters, AP, major reputable reporting,
or a court/government document. Do not use search-result pages. Do not invent a
source, people, causation, or alleged wrongdoing.

Create exactly one JSONL result record for every input record at:

`data/neon-workbench/external/people-enrichment-2026-10-25/source-recovery/results/source-recovery-NNN.jsonl`

Each object needs:

```json
{
  "entry_number": 123,
  "status": "source_found",
  "sources": [{"url":"https://...","title":"...","publisher":"...","date":"YYYY-MM-DD","confidence":0.8}],
  "supported_event_claim": "short neutral claim actually supported by the source",
  "reason": "why this source supports the event"
}
```

Use `no_credible_source` with an empty `sources` array and an exact explanation
when appropriate. Save and validate every packet immediately:

```bash
python3 data/neon-workbench/scripts/validate_people_source_recovery.py --packet source-recovery-NNN.jsonl
```

Do the entire assignment before stopping. At the end, report complete packet
numbers, counts of `source_found`/`no_credible_source`, validation status, and
the result files created. Do not merge, push, import, or deploy anything.

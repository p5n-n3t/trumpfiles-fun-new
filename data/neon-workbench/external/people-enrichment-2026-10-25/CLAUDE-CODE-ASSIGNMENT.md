# Claude Code assignment — source recovery

You own only these source-recovery packets:

`008, 011, 014, 017, 020, 024, 027, 030, 033, 036, 039, 042, 045, 048, 051, 054, 057, 060, 063, 066, 069, 072, 075, 078, 081, 084, 087, 090, 093, 096, 099, 102, 105, 108, 111, 114`

This is 36 packets × 25 records = 900 entries. You are not alone in the
repository. Do not edit or revert unrelated work, canonical records, frozen
exports, SQLite databases, Neon, Neo4j, scripts, or result files owned by
another worker.

Read:

- `data/neon-workbench/external/people-enrichment-2026-10-25/source-recovery/INSTRUCTIONS.md`
- Each assigned packet in `source-recovery/packets/`.

For each input record, search for at most two direct credible sources for its
central event. Use official records or high-quality reporting. Never cite a
search results page. Do not infer wrongdoing or fill gaps. For each packet,
write exactly one JSONL row per input record at:

`data/neon-workbench/external/people-enrichment-2026-10-25/source-recovery/results/source-recovery-NNN.jsonl`

Each row must include: `entry_number`, status (`source_found` or
`no_credible_source`), up to two source objects with HTTPS URLs, a short
neutral supported-event claim, and a precise reason. Validate every completed
packet with:

```bash
python3 data/neon-workbench/scripts/validate_people_source_recovery.py --packet source-recovery-NNN.jsonl
```

Work through the whole assigned list, saving each packet immediately. At the
end, report completed packet numbers, source-found/no-source totals, and only
the files you created.

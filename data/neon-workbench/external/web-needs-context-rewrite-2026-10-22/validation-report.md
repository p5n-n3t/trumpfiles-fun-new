# Needs-context rewrite validation — INCOMPLETE

Updated 2026-10-22T14:56:36.789Z

| Test | Evidence / result |
|---|---|
| Authorized numbered assignment | PASS — 497 unique `entry-N` catalogue IDs |
| Excluded unnumbered historical row | PASS |
| 49 compact input packets vs manifest | PASS — all record IDs and ordering match |
| Six non-overlapping worker ownership partitions | PASS — 95 / 80 / 80 / 80 / 80 / 82 |
| Terminal coverage | **INCOMPLETE — 107/497, missing 390** |
| One terminal per currently processed record | PASS — 107 unique records |
| Duplicate terminal IDs | PASS — 0 |
| Outside-assignment or wrong-worker IDs | PASS — 0 |
| Submitted JSONL parses / required disposition fields | PASS — 107 |
| Four copy fields and limits for usable `repaired_proposal` | PASS — 40 records, short <=180 characters, medium 45–90 words, long 140–300 words |
| Nonusable records have exact reasons or blockers | PASS — 67 records |
| Source URLs valid HTTPS syntax | PASS — 265 references (244 distinct); 2 unsafe HTTP leads omitted |
| Research log coverage of submitted terminal IDs | PASS — 107/107 |
| Copy is materially distinct | 9 new repairs manually reviewed; 31 historical pass proposals previously source-focused reviewed. Further final QA required |
| Real-time source verification | 9 newly researched; 98 reused previous audit with provenance, NOT independently rechecked here |
| Frozen/canonical/Neon files changed | PASS — no writes outside new output directory |
| Merged final 497-row file | NOT CREATED; coordinator must wait for all 497 |
| Draft PR to main | NOT OPENED; coverage prerequisite unmet |

**Editorial acceptance is not complete.** 390 IDs have no terminal outcome. Never mark them `needs_context` merely to make the count pass. The 51 existing `needs_context` dispositions refer only to actually researched historical records with recorded blockers.

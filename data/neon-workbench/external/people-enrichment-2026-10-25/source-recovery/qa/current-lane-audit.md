# Current people-enrichment lane QA audit

Audit date: 2026-10-25  
Scope: read-only audit of the currently present source-recovery and entity-result JSONL files. Validator reports were written under `/tmp`; this Markdown file is the only repository file written for the audit.

## Coverage and validation summary

| Check | Inputs / expected | Present results | Validator outcome | Coverage findings |
|---|---:|---:|---|---|
| Source recovery | 116 packet JSONLs | 79 JSONLs / 1,975 rows | `validate_people_source_recovery.py`: 79 PASS, 0 FAIL | All 79 present files matched their packet entry-number sets. Exact row order matched; no within-file or cross-packet duplicate entry numbers. 37 packet result files are absent. |
| Entity follow-up | 79 entity-input JSONLs | 79 JSONLs / 1,975 rows | `validate_people_enrichment_results.py`: FAIL, 79 packets / 1,975 entries checked | All present entity results matched their inputs exactly in row count and order; no within-file or cross-packet duplicate entry numbers. Entity-input, entity-result, and source-result filename sets matched. |

The 37 source-recovery packets without a result file are: 007, 010, 013, 016, 019, 022, 026, 029, 032, 035, 038, 041, 044, 047, 050, 053, 056, 059, 062, 065, 068, 071, 074, 077, 080, 083, 086, 089, 092, 095, 098, 101, 104, 107, 110, 113, and 116. These were absent and therefore not passed to the source-recovery validator.

## Findings

The entity validator reported 12 findings, all `source URL was not supplied by input` errors:

- Packet 014, result row 5 (entry 664): one person and two organization source URLs.
- Packet 014, result row 20 (entry 679): one person and two organization source URLs.
- Packet 014, result row 21 (entry 680): one organization source URL.
- Packet 014, result row 23 (entry 682): one person and one organization source URL.
- Packet 017, result row 9 (entry 743): one organization source URL.
- Packet 017, result row 13 (entry 747): two person source URLs.

No other validator findings were reported. Across the checked files, there were no extra or missing entry numbers within present packet/result pairs, no ordering mismatches, no duplicate entry numbers, and no cross-lane packet filename mismatches.

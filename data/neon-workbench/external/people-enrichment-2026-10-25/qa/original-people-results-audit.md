# Original people-result lane integrity audit

Audit scope: every present `people-NNN.jsonl` file directly under `results/`.

## Coverage

- Packet files: 29
- Entries: 2,900 (100 in each packet)
- Unique entry numbers: 2,900
- Duplicate entry numbers across the complete result set: none

## Terminal statuses

| Status | Count |
| --- | ---: |
| `enriched` | 1,193 |
| `needs_source` | 1,355 |
| `no_supported_people` | 352 |
| **Total** | **2,900** |

## Validator results

Ran `scripts/validate_people_enrichment_results.py` separately against each of the 29 present packets, redirecting its report output to a temporary directory so no additional repository files were written. All 29 invocations exited successfully. Validator findings: none.

Validated packets: 001–008, 013–014, 021–025, 031–034, and 041–050 (only present packet files are included in these ranges).

No people-result files or databases were modified.

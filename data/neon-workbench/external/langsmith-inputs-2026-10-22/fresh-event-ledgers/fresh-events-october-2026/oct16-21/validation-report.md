# Validation report

## Current status: not yet passing

Parsed candidate records are valid JSON and count to 11; unresolved leads count to 5. The first full validation run failed on card constraints. Findings from the audit:

- `fresh-20261020-whip-announcement` has a short description over 180 characters and a medium description over 90 words.
- The East Potomac and women’s-health medium descriptions exceed the 90-word maximum.
- The CNN candidate’s supported-claim URLs do not match the exact source URL in its source list (the AP URL has a differing character sequence); correct against the original report.
- Event/date consistency and all long descriptions still require a complete rerun after corrections.

No claim should be considered approved or loaded into canonical data. After edits, rerun checks for JSONL parsing, unique IDs, inclusive-window dates, exact date fields, title/short/medium/long bounds (short ≤180 chars; medium 45–90 words; long 140–300 words), required card fields, HTTPS source references, supported-claim URL membership, proposed status, and unresolved-lead blockers.

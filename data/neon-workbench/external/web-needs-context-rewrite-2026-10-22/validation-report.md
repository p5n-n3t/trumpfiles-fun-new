# Validation report — partial, not release-ready

Updated: 2026-10-22T14:48:29.117Z

| Validation | Result |
|---|---|
| Authoritative assignment | PASS — 497 numbered unique records |
| Excluded unnumbered non-catalogue record | PASS — not assigned |
| All 49 compact input packets vs manifest | PASS — exact entry numbers and record IDs, including order |
| Six disjoint partitions | PASS — 95 + 80 + 80 + 80 + 80 + 82 = 497 |
| Terminal outcomes present | **9/497 — incomplete** |
| Terminal outcomes missing | **488 — BLOCKING** |
| Duplicate results in submitted files | PASS — 0 |
| Outside-assignment IDs in submitted files | PASS — 0 |
| Submitted JSONL parses and required fields | PASS — 9 records |
| Submitted title, short <=180 char | PASS — 9 records |
| Submitted medium 45–90 words | PASS — 9 records |
| Submitted long 140–300 words | PASS — 9 records |
| Short, medium and long materially distinct | Editorial review performed on current 9 proposals; full QA pending |
| Submitted source URL HTTPS format | PASS — 22 URL references |
| Research log coverage for committed results | PASS — 9/9 |
| Frozen, canonical, Neon changes | PASS — no writes outside the newly created output directory |
| Full 497-entry merged validation | **NOT PASSED — 488 missing** |
| Draft PR against main | **NOT OPENED** |

Validation errors in committed subset: [].

The full acceptance gate MUST NOT be marked passing or opened as a completed PR until all 488 missing records are individually researched and assigned a defensible terminal disposition.

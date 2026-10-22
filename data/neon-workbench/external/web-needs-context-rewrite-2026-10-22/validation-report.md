# Validation report — partial checkpoint

Date: 2026-10-22T14:41:28.576Z

| Check | Result |
|---|---|
| Authoritative manifest numbered entries | **PASS: 497** |
| Manifest unique numbered IDs and `entry-N` mapping | **PASS: 497** |
| Six non-overlapping packet ownership groups | **PASS: 95 + 80 + 80 + 80 + 80 + 82 = 497** |
| Numbered entries with a terminal result | **5/497 — INCOMPLETE** |
| Missing terminal results | **492 — BLOCKING** |
| Duplicate terminal IDs in current submitted results | **PASS: 0** |
| Outside-assignment terminal IDs in current submitted results | **PASS: 0** |
| Current terminal JSONL parse and required schema | **PASS** |
| Title present and short <=180 characters | **PASS on 5 proposals** |
| Medium 45–90 words; long 140–300 words | **PASS on 5 proposals** |
| Description layers materially distinct | **Human-reviewed on 5 proposals; requires further batch QA** |
| Credible HTTPS formatting | **PASS on 10 URL references** |
| Canonical, frozen and Neon changes | **No writes were made outside this new append-only output directory** |
| Complete 497-entry QA | **NOT YET PASSING — 492 outcomes absent** |
| Draft PR | **NOT OPENED** |

This is explicitly a **partial** report, not a claim that all 497 records have been rewritten or verified. The complete terminal file must be built and revalidated only after all six partition outputs are available.

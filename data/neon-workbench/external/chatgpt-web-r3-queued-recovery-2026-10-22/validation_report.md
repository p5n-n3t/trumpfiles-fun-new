# Validation report — R3 queued historical evidence recovery (2026-10-22)

**Overall result: PASS** (structural/schema/description/HTTPS-format validation)

| Check | Result |
|---|---|
| Exact authorized entry count | 24/24, PASS |
| Authorized ID set (sorted) | 853, 854, 1670, 1716, 1768, 1770, 2373, 2494, 2518, 2562, 2615, 3212, 4285, 5732, 5735, 5737, 5743, 5746, 5863, 5899, 6239, 6280, 6417, 6421 |
| Missing terminal IDs | 0 (none) |
| Duplicate terminal IDs | 0 (none) |
| Outside terminal IDs | 0 (none) |
| Research log count | 24/24 |
| Research-log duplicates or missing | 0 duplicates / 0 missing |
| JSONL syntax | PASS: both files parsed successfully, one object per nonempty line |
| Exact terminal schema, allowed outcomes, unresolved null fields and blockers | PASS |
| Short description (<=180 Unicode JS characters) | PASS |
| Medium description (45–90 whitespace-delimited words) | PASS |
| Long description (140–300 whitespace-delimited words) | PASS |
| All source URL strings begin with `https://` and conform to absolute URL syntax | PASS |
| Source references / distinct URL strings | 34 / 33 |
| Canonical/history/Neon edits | None; all five proposed output paths are in new directory |

## Per-entry validation

| Entry | Outcome | Short chars | Medium words | Long words | Sources |
|---:|---|---:|---:|---:|---:|
| 853 | still_unresolved | — | — | — | 1 |
| 854 | repaired_proposal | 144 | 64 | 187 | 3 |
| 1670 | still_unresolved | — | — | — | 0 |
| 1716 | still_unresolved | — | — | — | 0 |
| 1768 | still_unresolved | — | — | — | 0 |
| 1770 | still_unresolved | — | — | — | 0 |
| 2373 | supported_partial | 163 | 62 | 155 | 1 |
| 2494 | supported_partial | 144 | 64 | 142 | 2 |
| 2518 | still_unresolved | — | — | — | 1 |
| 2562 | supported_partial | 113 | 61 | 149 | 1 |
| 2615 | supported_partial | 147 | 66 | 166 | 2 |
| 3212 | supported_partial | 147 | 57 | 146 | 1 |
| 4285 | supported_partial | 169 | 61 | 165 | 3 |
| 5732 | still_unresolved | — | — | — | 0 |
| 5735 | supported_partial | 146 | 55 | 194 | 1 |
| 5737 | supported_partial | 136 | 59 | 174 | 1 |
| 5743 | still_unresolved | — | — | — | 2 |
| 5746 | still_unresolved | — | — | — | 1 |
| 5863 | supported_partial | 128 | 66 | 194 | 3 |
| 5899 | supported_partial | 143 | 68 | 218 | 3 |
| 6239 | repaired_proposal | 164 | 62 | 156 | 3 |
| 6280 | supported_partial | 147 | 68 | 180 | 2 |
| 6417 | supported_partial | 147 | 68 | 178 | 2 |
| 6421 | supported_partial | 149 | 55 | 178 | 1 |

A dash means a required null copy field in a `still_unresolved` record. Length checks are applied to every non-null field. Three copy lengths were checked independently; all non-null copy fields exist only for supported or repaired outcomes.

## Important limitations

- URL syntax and editorial relevance were assessed, but a number of newspaper, archival and government sites restrict automated retrieval. **This test does not guarantee HTTP 200 accessibility** for each URL, or validate all long-term redirects. Protected pages require manual source QA.
- Input packet allegations were not treated as verified assertions; `sources[].supports` describes only what was actually evidenced or, for contextual blocker sources, what the source does **not** establish.
- Source totals count citations, not independent claims or evidentiary quality.
- The sixth queued ROTOXY task did not produce an output; these four entries were researched by the supervising ChatGPT Web agent and tagged in `research_log.jsonl`.
- No database migration, canonical application, visibility/score update, historical-file change, or merge is part of this lane.

## Raw error arrays

```json
{
  "missing": [],
  "duplicates": [],
  "outside": [],
  "badSources": [],
  "wordErrors": [],
  "schemaErrors": [],
  "logDuplicates": [],
  "logMissing": []
}
```

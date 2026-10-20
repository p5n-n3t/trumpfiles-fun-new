# Reviewer handoff — Trump Files 119-record evidence recovery

**Source:** PR [#71](https://github.com/p5n-n3t/trumpfiles-fun-new/pull/71), fixed head `3af4d448606ed190acbdc2fb83456ff164b0f005`. **Proposal branch:** draft [PR #72](https://github.com/p5n-n3t/trumpfiles-fun-new/pull/72), targeting PR #71 branch. **Do not merge** without independent review.

## Final disposition

- **119/119 terminal:** 1 repaired proposal, 5 supported partials, 113 still unresolved.
- Source exclusion untouched: 2 previously repaired, 2 prior partials, 1 split-ready and 25 soft-hide candidates (30 total).
- Real independent Codex CLI processes completed six exclusive modulo-six worker assignments.
- All 119 unique source IDs are accounted for; no duplicate or outside IDs. All outcomes are proposal-only, publication-ineligible and require manual review.

## Source-supported narrowed candidates

| ID | Status | Narrowed claim | Critical caveat |
|---|---|---|---|
| `entry-2557` | Supported partial | Michael Caputo worked for Bloc Lytvyn in Ukraine in 2007 | Extracted testimony pp. 13 and 73–74 verifies a brief Kyiv residence and Bloc Lytvyn work in 2007; Kyiv Post corroborates the campaign work. January 5, exact duration, contract and respon... |
| `entry-5863` | Repaired proposal | Eric Trump stops direct charity fundraising amid access concerns in December 2016 | Contemporaneous NPR reporting dated December 22, 2016 verifies Eric’s withdrawal from direct fundraising; Nonprofit Quarterly separately dates the suspension announcement to December 22. ... |
| `entry-6607` | Supported partial | Hegseth issued Pentagon DEI guidance on January 29, 2025 | Directly read IG announcement and court opinion verify January 29 guidance and its curricular prohibition. Original memo and report URLs returned 403; Government Executive fetch failed. J... |
| `entry-6672` | Supported partial | Trump Media shareholder United Atlantic Ventures reports stake reduced to 100 shares | Fresh SEC filing and Reuters retrieval establish a named shareholder and documented reduction to 100 shares, resolving part of the missing-transaction blocker. Supported partial only: exa... |
| `entry-6774` | Supported partial | Trump urges Supreme Court to restrict nationwide injunctions | Full Reuters syndication accessed; original Reuters URL failed. March 20 is verified as the report date; the original social-media timestamp was not independently recovered. The primary C... |
| `entry-6802` | Supported partial | Reports say DOJ subpoena sought Fani Willis's travel records | Both full articles accessed, but both rely on the same NYT reporting and are not independent confirmation of the subpoena. Partial support only: no subpoena text, opening date, direct Bon... |

Each candidate has exact source URLs and title/short/medium/long copy in its own `workers/worker-XX/outcomes.jsonl`. Their accurate, narrower portions do not prove the original broad claims. Source URLs and chronology need final human fact-check.

## Spot-checks of primary and contemporaneous evidence

- `entry-2557`: [House Intelligence Committee Caputo testimony](https://intelligence.house.gov/uploadedfiles/michael_caputo_testimony_july_14_2017.pdf), printed p. 13 and p. 73, contains his own account of Ukraine/Bloc Lytvyn work; self-report, not independent evidence of every implication.
- `entry-5863`: [Eric Trump Foundation announcement](https://www.erictrumpfoundation.com/) confirms ending direct fundraising effective December 31, 2016; [AP-syndicated reporting](https://www.cbsnews.com/miami/news/eric-trump-to-stop-fundraising-for-his-charity/) describes the December decision. Do not imply the later state inquiry caused it.
- `entry-6607`: [Department of Defense January 29, 2025 announcement](https://www.defense.gov/News/News-Stories/Article/Article/4047592/defense-secretary-directs-creation-of-task-force-to-restore-americas-fighting-f/) confirms guidance, not unsupported claims about specific dismissals or measured retention effects.
- `entry-6672`: [September 26, 2024 SEC Schedule 13G](https://www.sec.gov/Archives/edgar/data/1849635/000149315224038295/formsc13-g.htm) establishes UAV ownership reduced to 100 shares; does not establish exact sales dates, prices or retail losses.
- `entry-6802`: [Reuters report](https://www.reuters.com/world/us/us-doj-seeks-information-georgia-prosecutor-willis-nyt-reports-2025-09-27/) attributes a subpoena report to the New York Times, not a released subpoena. The reported investigation target and direct Bondi involvement are unknown.
- `entry-6774`: review Reuters-syndicated report and primary Court context separately. Legal context cannot authenticate the timestamp of a particular Trump statement.

## Unresolved and QA cautions

- 113 records remain blocked with event-specific explanations; do **not** synthesize a substitute incident just to create a publishable claim.
- 11 unresolved entries have no exact URL to report from the new searches, usually because the ID or allegation could not be matched to an identifiable event. Keep these as search-only negative results, not proof of nonexistence. The IDs are: `entry-6444`, `entry-6595`, `entry-6637`, `entry-2571`, `entry-6455`, `entry-6950`, `entry-5731`, `entry-5732`, `entry-6582`, `entry-6779`, `entry-6791`.
- Mechanical URL validation checks scheme/host/syntax, not page reachability, authenticity, or the implication of an article. Individual source access restrictions may persist.
- Attributed testimony and reports are not independently proven causation. If the only support is an article repeating another report, label it correctly.

## Validation and scope

- `validate.py` checks exact 119 source IDs, six exclusive worker partitions, JSONL syntax, statuses, required fields, URL syntax, proposal character/word limits and Git diff scope.
- Git comparison to the PR #71 head shows only newly added paths under this folder. No canonical, frozen-export, Neon, migration, scoring or historic editorial-lane files changed.
- This validator makes **no Neon database connections**; it establishes repository change isolation, not the contents of a live remote database.
- Final source-level editorial sign-off remains required. **Keep the PR as DRAFT, unmerged.**

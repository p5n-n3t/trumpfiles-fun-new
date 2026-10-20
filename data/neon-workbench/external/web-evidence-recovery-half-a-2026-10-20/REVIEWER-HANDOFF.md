# Final reviewer handoff — Half A, 2026-10-20

**Status:** all 60 records terminally classified; draft PR only, unmerged. These are research and editorial proposals, not canonically verified entries.

## Exact coverage and gate

- Source: draft PR #71 at `3af4d448606ed190acbdc2fb83456ff164b0f005`.
- Output: `final-terminal-results.jsonl` (60 rows), `research-log.jsonl` (60 rows).
- Fixed six worker slices of exactly ten IDs each, recorded in `checkpoint.json`.
- Outcomes: **1 repaired proposal; 7 supported partials; 52 still unresolved**.
- ALL entries: `proposal_only=true`, `publication_eligible=false`, `requires_manual_editorial_review=true`.
- Validator: `python3 validate.py` checks exact assignments, JSONL, URL syntax, provenance presence, copy constraints and Git change scope. URL syntax and search hits **do not** prove source-event identity.

## Positive proposal editorial checklist

| ID | Outcome | Review risk / priority | Primary source or attributed report |
|---|---|---|---|
| `entry-2349` | `supported_partial` | Context only: no identifiable Trump action | [Evidence](https://www.news.co.uk/our-history/) |
| `entry-2557` | `supported_partial` | Year-level correction; exact day unverified | [Evidence](https://intelligence.house.gov/uploadedfiles/michael_caputo_testimony_july_14_2017.pdf) |
| `entry-2571` | `supported_partial` | Context only: no identifiable Trump action | [Evidence](https://www.ynetnews.com/articles/0,7340,L-3695344,00.html) |
| `entry-3371` | `supported_partial` | Investigation-attributed, not independently audio-authenticated | [Evidence](https://vsquare.org/kremlin-hotline-how-hungary-coordinates-with-russia-blocking-ukraine-from-the-eu/) |
| `entry-5329` | `supported_partial` | Attributed prosecutor email; underlying flight logs not inspected | [Evidence](https://www.reuters.com/world/us/us-justice-department-releases-new-tranche-epstein-files-2025-12-23/) |
| `entry-5731` | `supported_partial` | Backlog supported, one-day collapse not supported | [Evidence](https://www.ssa.gov/news/assets/materials/press/2025/accomplishments.pdf) |
| `entry-6457` | `repaired_proposal` | Same-event narrow correction; prioritize | [Evidence](https://www.centcom.mil/MEDIA/PUBLIC-RELEASES/Article/4223915/us-and-qatari-forces-successfully-defend-against-iranian-ballistic-missile-atta/) |
| `entry-6595` | `supported_partial` | Trump directive, not Bondi dismissal on January 20 | [Evidence](https://www.govinfo.gov/content/pkg/FR-2025-01-29/html/2025-01950.htm) |

### Exact supported scope and exclusions

- **`entry-2349`:** News UK acquisition chronology identifies News of the World on January 2, 1969; no Trump/Mogilevich nexus. Keep it attributed and publication-ineligible pending direct editorial review.
- **`entry-2557`:** House Intelligence Committee testimony supports Caputo working in Kyiv for Bloc Lytvyn during 2007; no Putin-directed takeover. Keep it attributed and publication-ineligible pending direct editorial review.
- **`entry-2571`:** Reuters/Israeli statistics support Netanyahu taking office March 31, 2009; remove Trump assertion. Keep it attributed and publication-ineligible pending direct editorial review.
- **`entry-3371`:** VSquare consortium reports 2023 Szijjártó–Lavrov call in investigation published April 8, 2026; does not prove Trump participation. Keep it attributed and publication-ineligible pending direct editorial review.
- **`entry-5329`:** Reuters reports a 2020 prosecutor email described eight flights in the 1990s, not the frozen 11-flight count; email makes no criminal allegation. Keep it attributed and publication-ineligible pending direct editorial review.
- **`entry-5731`:** SSA reported ~950,000 pending initial disability claims and 222-day average processing; Urban Institute discusses July backlog; not a July 25 event affecting millions. Keep it attributed and publication-ineligible pending direct editorial review.
- **`entry-6457`:** CENTCOM confirms Iran attacked Al Udeid Qatar on June 23, 2025 and reported no US/Qatari casualties; original June 14, Iraq/UAE impacts and deaths not supported. Keep it attributed and publication-ineligible pending direct editorial review.
- **`entry-6595`:** Federal Register Jan 20 proclamation directs AG to pursue dismissal of pending Jan 6 indictments; Bondi had not yet taken office; scope is not every ally. Keep it attributed and publication-ineligible pending direct editorial review.

Three of these (`entry-2349`, `entry-2571`, `entry-3371`) are documented **context-only** events with no independently established Trump act; do not import into a Trump-event feed without a verified nexus. `entry-5731` describes agency conditions rather than a verified single-day presidential action. `entry-5329` is attributed to an uninspected prosecutor email and **does not establish criminal conduct**.

## Unresolved terminal blockers — exact IDs only

Each original blocker is preserved verbatim in the result ledger. This is a navigation index, not a new terminal status.

| ID | Main remaining evidentiary blocker |
|---|---|
| `entry-1670` | No named pledge, original deadline, dated AP before-and-after status comparison, or evidence of reduced narrative durability on March 4, 2026 is identified. |
| `entry-1716` | No individual promise, deadline, dated status item, or March 4, 2026 comparison establishes the claimed persistent exposure. |
| `entry-1768` | No specific pledge, ambiguous criterion, criterion change, changed Trump statement, or dated March 4, 2026 AP assessment is identified. |
| `entry-1770` | No identified pledge, sequence of review dates, measured credibility effect, or March 4, 2026 outcome supports the claimed long-tail risk. |
| `entry-2373` | No evidence identifies publication of this compilation, Trump membership or participation, or a specific Trump-linked action on January 20, 1981. |
| `entry-2494` | The alleged rehearsal request/conduct lacks independently corroborated testimony and an established date; the original Casler post could not be re-read. Evidence does not tie the separate dressing-room accounts to the same rehearsal episode. |
| `entry-2518` | The exact Friedman passage supporting the attributed greatest-threat-to-democracy warning, its May 1, 2000 date, and any event-specific Trump connection remain unverified. |
| `entry-2562` | No directly checked matching January 3, 2008 New York Times profile, its article text/date, or evidence that Rubenstein arranged that particular interview is established. |
| `entry-2615` | No specific Manafort action assisting Russia’s March 16, 2014 takeover of Crimea is documented in the checked sources; the synopsis also incorrectly extends control of Crimea to control of Ukraine. |
| `entry-3212` | The January 7 sighting is corroborated, but the asserted removal of junk, service purpose and any claimed public or policy consequence remain unestablished. |
| `entry-4285` | No checked source establishes a specific Strive energy holding, Ramaswamy policy action and resulting investor benefit during July 1–August 9, 2026; the claimed fiduciary conflict and Roivant/FDA component lack event-specific evidence. |
| `entry-5732` | No contemporaneous source verifies that Trump demanded three Supreme Court justices resign around July 18, 2025 or called those justices “enemies of the people” and “corrupt.” |
| `entry-5735` | No named coordinated operation, participating cities, July 21 date, event-level arrest count in the thousands or same-operation evidence of citizen/permanent-resident detentions is established. |
| `entry-5737` | No transcript, recording, post or contemporaneous report verifies the alleged July 29, 2025 threat to fire “disloyal” federal judges or the claimed absolute presidential removal authority. |
| `entry-5743` | No dated U.S. withdrawal announcement, diplomatic record or contemporaneous report establishes an actual U.S. exit from all Ukraine peace negotiations on July 23 or in late July 2025. |
| `entry-5746` | No matching August 4, 2025 statement, recording, transcript or contemporary report establishes a formal NATO withdrawal threat, the freeloading language or the alleged Article 5 refusal. |
| `entry-5749` | No named arrested reporter, August 7 arrest record, Espionage Act charge, leak-case docket or Patel directive supports the alleged multiple journalist arrests. |
| `entry-5755` | No identified August 22, 2025 pardon wave, recipient or warrant matches the allegation; donor links, noncooperation and bypassed review remain unestablished. |
| `entry-5756` | No original address-publication post, authenticated exact quotation, named congressional witness or identified hearing/proceeding nexus is established for August 25, 2025. |
| `entry-5760` | The alleged August 21, 2025 Supreme Court clean-water case/order, the executive order it supposedly invalidated and any subsequent agency noncompliance directive remain unidentified. |
| `entry-5761` | No defined index and months support the alleged aggregate 6% increase by August 26; no same-event suppression attempt, causal tariff estimate or documented destruction of household savings is identified. |
| `entry-5826` | No identified early-2025 foreign payer, pressured membership transaction, paid stay, new emoluments filing or dated disclosure refusal establishes the alleged January 25 event. |
| `entry-5844` | No identifiable Melania White House paid meeting, participant, approximately $100,000 transaction, personal-business recipient or formal OGE complaint is documented for the alleged early-2025 arrangement. |
| `entry-5850` | No early-2025 Saudi tourism contract, award notice, named Saudi counterparty, service description or payment to Ivanka Trump substantiates the alleged $3.9 million deal. |
| `entry-5863` | No contemporaneous announcement or report establishes a June 2017 suspension of the annual golf fundraising events, its asserted causal connection to the AG examination, or the frozen June 30 date. |
| `entry-5899` | No loan schedule or matching record substantiates over $640 million from private wealth in the late 1990s/2000s across Chicago, Las Vegas and Doral, or the January 1, 1998 event date. |
| `entry-6200` | No dated Trump post, recording, transcript or credible matching report verifies the January 10, 2023 “Dr. Death” wording, COVID-creation accusation, or demand that Fauci be prosecuted and jailed. |
| `entry-6239` | The alleged January 2025 Border Patrol pardon recipients, criminal cases, offenses and clemency warrants remain unidentified; the asserted subsequent abuse increase has no named dataset, baseline or causal evidence. |
| `entry-6280` | No identified 2025 blanket directive, named subpoena, withheld document request, inspector-general clearance order or compliance case establishes the claimed administration-wide refusal beginning January 20. |
| `entry-6315` | No identified CIA program, affected country, termination directive, decision-maker or matching report establishes the alleged February 15, 2025 multinational shutdown. |
| `entry-6316` | No agency announcement, case record or credible contemporaneous report identifies a March 20, 2025 classified-leak investigation targeting Gina Haspel or a leak attributable to her. |
| `entry-6398` | No identified September 2025 interview, rally, date, venue, exact wording or recording establishes Trump refusing to accept a possible 2028 presidential-election loss. |
| `entry-6413` | No contemporaneous February 2025 Trump statement, exact court-martial threat, directive or proceeding establishes the claimed targeting of retired generals including both Milley and Mattis. |
| `entry-6415` | No same-event February 2025 Trump statement or directive establishes tax-exempt-status threats against Harvard, Columbia and other universities as a group for resisting DEI orders, or the February 1 date. |
| `entry-6417` | No identified March 2025 Trump quotation, post, transcript or venue establishes a personal claim of authority to override federal court orders he considers wrong or political. |
| `entry-6421` | No dated directive, actual list or identified case verifies February 2025 cross-agency disloyalty termination lists using social posts, donations and coworker reporting, compiled through DOGE access for Schedule F firings. |
| `entry-6423` | No February 2025 public statement by Trump or a named senior White House official threatens arrest or prosecution of both Mark Milley and Mark Esper for criticism, and neither alleged response is sourced. |
| `entry-6430` | No January 20, 2025 order text or matching injunction establishes indefinite detention without bond hearings or judicial review or an explicit displacement of INA protections. |
| `entry-6432` | No February 2025 proposal text, proposing official, dated statement or contemporaneous report establishes military tribunals for civilian immigration cases or the asserted backlog rationale. |
| `entry-6439` | The February 15, 2025 composite supplies no linked declarations, transfer orders, accounts, amounts or matched GAO decisions and injunctions establishing emergency redirections to border wall, defense and deportations. |
| `entry-6440` | No March 2025 executive-order number/title/text, identifiable internal directive, FISC order reference or named civil-liberties case establishes commander-in-chief authority superseding FISA warrants for U.S.-citizen surveillance. |
| `entry-6444` | No identified April 2025 filing, case or dated quotation asserts the frozen blanket immunity theory covering essentially any in-office action across criminal and civil accountability. |
| `entry-6451` | No named or otherwise credibly identified NSC official, sourced internal warning, dated pressure/retribution episode or investigative account connects punishment to a legal objection over Iranian cultural targets. |
| `entry-6455` | No May 12, 2025 social-media post or matching May statement threatens Iran with obliteration specifically if nuclear talks fail; alleged emergency allied consultations and Iranian program/alert responses are unsourced. |
| `entry-6484` | No dated January 2025 executive or State Department instrument establishes rescission of the assessment, withdrawal of Saudi officials’ visa restrictions or termination of the Khashoggi Ban. |
| `entry-6498` | No quotation, venue, recording or dated April 2024 report establishes the alleged repeated claim that Trump beat Obama in 2016. |
| `entry-6501` | No original nuclear-weapons tweet, archived capture or contemporary report supports the hearby spelling on May 9, 2019; the opened date-specific archive displays no match. |
| `entry-6504` | Alleged October 1, 2023 one-hour Donald Trump civil-fraud deposition and more than thirty memory disclaimers lack an identifiable transcript, timed segment and reproducible count. |
| `entry-6517` | No contemporary source establishes a January 26, 2017 Electoral College map personally altered by Trump with Sharpie, changed state results, or repeated display of that altered map. |
| `entry-6564` | No property/address, Trump-linked legal seller, Russian-linked buyer, sale date, price or deed identifies the alleged post-presidency inflated-price sale. Frozen January 1, 2021 also precedes Trump’s departure from office. |
| `entry-6582` | No named Trump-family recipient, signed warrant or January 20 Trump proclamation supports preemptive pardons for his family; directly reviewed family-pardon reporting instead names Joe Biden. |
| `entry-6584` | No 2025 warrant, proclamation, recipient entry or contemporary report establishes a second Joe Arpaio pardon for the 2017 contempt conduct. |

## Editorial release gates

1. For each positive proposal, reopen the underlying cited source (PDF page/section, official release, contemporary article); validate date, named actor, exact narrow statement and attribution independently.
2. Resolve or explicitly retain mismatches in original vs repaired dates, event identity, and causation; do not substitute merely adjacent true facts.
3. Do not treat `supported_partial` as ready-to-publish. No canonical import, Neon update, migration, scoring adjustment, historical lane rewrite, or auto-publication is authorized.
4. Keep the PR **DRAFT and unmerged**, and retain all 52 unresolved until verifiable same-event evidence emerges.
5. Prior recovery PR #72 may overlap these IDs as earlier independent research; do not merge both outcomes as separate canonical rows. This handoff belongs only to the 60 user-assigned Half A IDs.

## Source-access caveat

The completed JSONL files distinguish directly opened sources from search results, syndicated accounts, blocked originals, and attribution-only reporting. The reviewer should inspect `source_provenance` and `research-log.jsonl` for limitations before approving any new record. The newly added `validate.py` is a **structural** validator, not an assertion that each claim is substantively proved.

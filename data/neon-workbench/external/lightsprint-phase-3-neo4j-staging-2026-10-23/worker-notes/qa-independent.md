# Independent QA — Phase 3 offline graph staging

## Result

No unresolved graph integrity, coverage, provenance, URL-policy, or offline-execution defects found in the final generated output. I independently read the staged JSONL and the immutable SQLite inputs, and did not use the network or write to either database. No implementation or generated output was changed for this review.

One interim issue was resolved before this final pass: proposed `SOURCED_FROM` provenance initially omitted structured source metadata, and proposed candidate descriptions lacked field-level provenance. The regenerated graph now carries those fields; I checked all 147 candidate roots and all 289 proposed `SOURCED_FROM` edges against the Phase 2 JSONL values.

## Independent integrity and count checks

| Measure | Independently checked result |
| --- | ---: |
| Canonical nodes | 22,409 |
| Canonical Entries | 7,143 |
| Canonical relationships | 50,313 |
| Proposed candidates | 147 |
| Proposed nodes / relationships / total rows | 1,307 / 1,160 / 2,467 |
| Withheld rows | 1,473 |
| Entity alias records | 647 |

Canonical node counts by type: Entry 7,143; Theme 8,443; Source 6,100; Person 573; Organization 74; Category 51; Phase 25. Canonical relationship counts: HAS_THEME 23,708; IN_CATEGORY 7,143; IN_PHASE 7,143; MENTIONS 4,600; SOURCED_FROM 7,719. Proposed relationship counts: MENTIONS 724; IN_CATEGORY 147; SOURCED_FROM 289.

The 7,143 canonical entry numbers and titles exactly match the frozen `trump_entries` rows and the manifest ID set. All 147 proposed root IDs and titles exactly match the pinned Phase 2 candidate file and manifest set. Each JSONL has unique record IDs. Every canonical relationship has two existing endpoints and a supported direction/type pair. Typed Person/Organization display names have no duplicate identities; aliases have no cross-identity normalized collisions. The 22 summary count and breakdown fields independently recomputed from the graph all match `graph-summary.json`.

All proposed rows carry `PROPOSED_NOT_APPROVED`; there are no proposed `Entry` labels, canonical IDs, canonical endpoints, or allocated entry-number/entry-id property keys. Candidate root source fields and descriptions have exact source-field provenance. Proposed source edges include all fields from each structured source object, and all 289 such edges were checked against their owning candidate rows.

The 6,100 canonical Source URLs are explicit absolute HTTPS URLs, have no credentials, whitespace or backslashes, and contain no secret-like query parameter. All 1,098 withheld source URL records have reasons consistent with their source values: 863 are not explicit absolute HTTPS URLs, 178 source records contain no explicit URL field, and 57 source values are not URL strings. No Source URL was checked for current liveness or claim support.

Withheld totals by kind independently reconcile to 1,473: source_url 1,098; unsupported_entity_link 149; entry_relationship 116; proposed_to_canonical 110.

## Twenty manually inspected canonical relationship examples

For every example below, all listed provenance field/value records were looked up in the named SQLite database and matched exactly. The justification is limited to what that structured source field supports.

### MENTIONS

- `rel:07986345fa3f82ec037a0937` — Entry 5357, “DOJ Filings Reveal Systematic Obstruction and Concealment of Classified Documents at Mar-a-Lago” → Person Jay Bratt. `entity_entry_links.role='mentioned'` (12 provenance values checked); supports a mention only.
- `rel:44c5ca30524f934e4680762f` — Entry 6965, “Trump Signs Executive Order on Stargate — $500B AI Infrastructure Pledge Raises Conflict Questions” → Person Masayoshi Son. `entity_entry_links.role='mentioned'` (12 values checked); supports a mention only.
- `rel:9d105595ffe0828a9cfeeadc` — Entry 5901, “Ivana Trump Rape Allegation in 1990 Divorce Deposition — Later Recanted Under Legal Pressure and NDA” → Person Donald Trump. `entity_entry_links.role='mentioned'` (12 values checked); supports a mention only and does not establish the allegation.
- `rel:00e01585e73d2e7d49f5cf63` — Entry 6195, “Trump Calls January 6 Rioters 'Hostages' and 'Patriots,' Rewrites Insurrection History (2023)” → Person William Barr. `entity_entry_links.role='mentioned'`, frozen `people_tags[2]='Bill Barr'`, and staged alias `entity_aliases.alias='Bill Barr'` → canonical name William Barr; this explicit link and alias path support a mention only.

### HAS_THEME

- `rel:07fb42c0bfde58079a3fe156` — Entry 133, “Voice of America Dismantlement - 'Radical Propaganda' Media Destruction” → Theme “authoritarian narrative”. `trump_entries.keywords[6]='authoritarian narrative'`; exact keyword match.
- `rel:462ad401ec3726c8f6e0ae8f` — Entry 926, “Pardons William L. Kale” → Theme “clemency”. `trump_entries.keywords[2]='clemency'`; exact keyword match.
- `rel:9dc147d079a5a05667809b15` — Entry 224, “Whistleblower Persecution and Prosecution - Federal Employee Retaliation System” → Theme “espionage act prosecution”. `trump_entries.keywords[3]='espionage act prosecution'`; exact keyword match.
- `rel:f0ba056fe783d8101c49df4c` — Entry 4233, “Post-DOGE Remnants Embed Throughout Government Despite Official Shutdown” → Theme “government oversight”. `trump_entries.keywords[6]='government oversight'`; exact keyword match.

### IN_CATEGORY

- `rel:073fec59700d34179478acd1` — Entry 5482, “Apprentice Producer Alleges Trump Used Racial Slurs on Set” → Category “Human Rights Violations”. `trump_entries.category='Human Rights Violations'`; exact raw category.
- `rel:4438b8b403849003f405d30a` — Entry 7053, “BBC Tries to Force Trump Family to Testify in Defamation Lawsuit” → Category “Press Freedom”. `trump_entries.category='Press Freedom'`; exact raw category.
- `rel:9d6a16c0acb721c88589836c` — Entry 2374, “Trump asks FBI for protection in Atlantic City, help with investigations” → Category “Government Corruption”. `trump_entries.category='Government Corruption'`; exact raw category.
- `rel:f19818fe0059c4f3b7c3f9f6` — Entry 4240, “Doug Burgum Sells Record Oil Leases in Alaska, Calls Energy Transition a \"Fantasy\"” → Category “Environmental”. `trump_entries.category='Environmental'`; exact raw category.

### IN_PHASE

- `rel:076afd4d743cfd330e1c0bc0` — Entry 543, “Trump Attacks Megyn Kelly with “Blood” Comment After Debate” → Phase “Campaign Trail”. `trump_entries.phase='Campaign Trail'`; exact raw phase.
- `rel:462bcd19d4b218768534dd9b` — Entry 2451, “Trump: Robert Maxwell is outed as an agent of Mossad, Israel” → Phase “Post-Presidency”. `trump_entries.phase='Post-Presidency'`; exact raw phase.
- `rel:9c2508ca77c659052225ceae` — Entry 4925, “Trump Invokes Alien Enemies Act with False Invasion Claim About Tren de Aragua” → Phase “White House 2:2”. `trump_entries.phase='White House 2:2'`; exact raw phase.
- `rel:f0e58f1d58cc8c237431d690` — Entry 4862, “USAID Shutdown Kills Hundreds of Thousands, Ends Lifesaving Programs Worldwide” → Phase “White House 2:2”. `trump_entries.phase='White House 2:2'`; exact raw phase.

### SOURCED_FROM

- `rel:078ffae25998fae6013f5ece` — Entry 2524, “Donald Trump calls local news, uses 9/11 as a promotional opportunity” → Source “On 9/11, Trump noted on TV that his Financial District building was now the ‘tallest’”. `trump_entries.sources[0].url='https://www.washingtonpost.com/news/post-politics/wp/2016/09/11/on-911-trump-noted-that-he-now-owned-the-financial-districts-tallest-building/'`; explicit valid HTTPS source field.
- `rel:464d96ac42fe0677831e6b04` — Entry 4112, “Trump: Foreigners in U.S. must apply for green cards abroad, new Trump administration rule says” → Source “New policy designed to force foreigners in the US to apply for a green card abroad”. `trump_entries.sources[0].url='https://apnews.com/article/immigration-green-cards-uscis-citizenship-border-trump-8f64f9ada5c3f04e511a7b3cf43eaa13'`; explicit valid HTTPS source field.
- `rel:9ba5670c920c8b7977939c3e` — Entry 2204, “Trump Called Mail Voting 'Cheating' Days After Using It Himself” → Source “Trump calls voting by mail 'cheating' just days after voting by mail”. `trump_entries.sources[0].url='https://www.theguardian.com/us-news/2026/mar/24/trump-mail-in-voting-cheating-ballot'`; explicit valid HTTPS source field.
- `rel:f0fc9afae9002d7fd6c6bde3` — Entry 2495, “Donald Trump sexually assaults model Amy Dorris” → Source “Donald Trump accused of sexual assault by former model ...”. `trump_entries.sources[0].url='https://www.theguardian.com/us-news/2020/sep/17/donald-trump-accused-of-sexual-assault-by-former-model-amy-dorris'`; explicit valid HTTPS source field.

## Offline execution checks and limits

The validator with `--reproduce /tmp/phase3-inputs` and the default dry-run importer each passed twice; stdout and stderr were byte-identical between each pair. Reproduction was deterministic. The dry-run reports `execution_enabled:false`, includes only canonical graph records, and imports zero proposed or ambiguous rows. Code inspection found no credential reads or network/database client path in the staging scripts; the generator opens the two SQLite inputs read-only and enables `query_only`. The reserved `--apply` option was not invoked. I did not run the test suites, make network requests, write to either database, or perform a live import.

This review confirms a faithful, conservative projection of the supplied structured records. It does not confirm the truth of entry claims, whether URLs still resolve, or whether a cited source supports an entry.

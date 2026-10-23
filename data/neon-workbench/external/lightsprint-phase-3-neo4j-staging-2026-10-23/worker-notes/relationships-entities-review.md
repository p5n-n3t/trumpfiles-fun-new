# Canonical entity-to-entry MENTIONS review

I compared `canonical_entities.py` and the generated `graph-relationships.jsonl` with the immutable frozen and staged SQLite snapshots. I found no current-data issue in the canonical MENTIONS edges reviewed.

The staged database has 716 entities and 4,749 `entity_entry_links`; every link row has `role = mentioned`. The projection emits 4,600 MENTIONS edges to entities typed `person` or `org`. Each emitted edge joins to its staged `entity_entry_links` row and entity row, the entry exists in both snapshots, and the frozen `people_tags` field supplies an exact matching name or explicit alias. The 149 links to `entity_type = other` are withheld. The frozen entity/link tables exist but contain no rows; the entry-side evidence is the frozen `trump_entries.people_tags` field.

The 4,600 edges do not come from text co-occurrence. The projector iterates the explicit staged link table, requires the `mentioned` role, and uses frozen tags to resolve the entity name and add evidence. In this snapshot, 4,560 edges match the canonical entity name exactly, 39 match an explicit alias only, and one edge has both a canonical-name tag and an alias tag. The exported edges have `status = CANONICAL`, `origin_entry_number` equal to the source `entry:N`, and provenance for the staged link/entity plus matching frozen tag. Their basis explicitly limits the meaning to a mention and disclaims any additional role or wrongdoing.

| Relationship ID | Frozen entry | Target entity | Frozen tag | Staged role |
| --- | --- | --- | --- | --- |
| `rel:0055102262c5d23013ac3e8d` | `entry:6302` — Trump Meets Russian Officials in Oval Office Day After Firing Comey | `entity:ent_aeaabd04dcc4ae05c088d408` — Sergei Lavrov | `Sergei Lavrov` | `mentioned` |
| `rel:005764a1d8be3bc8cc9273f8` | `entry:5875` — Trump Asks Comey to “Let Flynn Go” After FBI Counterintelligence Investigation | `entity:ent_b05b168dbdc86372493c2949` — Robert Mueller | `Robert Mueller` | `mentioned` |
| `rel:00612ead92d139286cfb821f` | `entry:6601` — Trump DOJ Drops Antitrust Case Against Google — Major Trump Donor | `entity:ent_b895d9ec16d6d00523271eef` — Donald Trump | `Donald Trump` | `mentioned` |
| `rel:00e01585e73d2e7d49f5cf63` | `entry:6195` — Trump Calls January 6 Rioters “Hostages” and “Patriots,” Rewrites Insurrection History (2023) | `entity:ent_c990392eed75c5ebe476b896` — William Barr | `Bill Barr` (explicit alias) | `mentioned` |
| `rel:01af64c2ff57ab69d061c229` | `entry:6725` — RFK Jr. Dismantles CDC Vaccine Advisory Committee ACIP | `entity:ent_a0a33a3909db45bb49d211e8` — Robert F. Kennedy Jr. | `RFK Jr` (explicit alias) | `mentioned` |
| `rel:02acdc68a5c44e52f74a4b87` | `entry:6229` — Trump Defies Federal Court Order to Stop Deportation Flights | `entity:ent_5d42d517837b1d50e605d1ec` — Pam Bondi | `Pamela Bondi` (explicit alias) | `mentioned` |
| `rel:00d654f3ed627d3984b35b66` | `entry:6474` — Trump Administration Blocks UN Ceasefire Resolutions on Gaza | `entity:ent_91f11af0ce7a08f0e0e5ca3a` — Marco Rubio | `Marco Rubio` | `mentioned` |
| `rel:00d710cd0ad6da0b061f2c46` | `entry:6459` — Trump Deploys Two Carrier Strike Groups to Persian Gulf | `entity:ent_c919c7c36fb5cdcf8e07e12f` — Lloyd Austin | `Lloyd Austin` | `mentioned` |
| `rel:00a1ee3e15b0a8cec26215fc` | `entry:5329` — 11 Documented Epstein Flights: Trump Flew Palm Beach–New York on Epstein Aircraft 11 Times | `entity:ent_817971ba9e8994a671fd4905` — Eva Dubin | `Eva Dubin` | `mentioned` |
| `rel:00c19c08eefb126731de05a3` | `entry:6652` — Trump’s 2017 Tax Cuts Add $1.9 Trillion to Deficit — 83% of Benefits Go to Top 1% | `entity:ent_367faf10703558efa046fdd2` — Mitch McConnell | `Mitch McConnell` | `mentioned` |

Alias resolution is exact: canonical names, `entities.aliases`, and `entity_aliases.alias` are indexed as explicit values. NFKC plus casefold is used to detect collisions across entity IDs, not to fuzzy-match tags; collisions are withheld. All 17 staged `entity_aliases` rows in this snapshot agree with the staged entity’s canonical name and are also present in that entity’s `aliases` JSON, so alias-backed relationship evidence remains traceable in the entity row. No role is inferred from an alias.

The coordinator resolved two latent alias-path risks after this review. Mismatching alias canonical names are now withheld before lookup or alias export; MENTIONS carries the matching entity_aliases row provenance directly. In-memory tests cover both mismatch refusal and matching-alias provenance. Current graph counts are unchanged because the 17 input alias rows agree with their identities.

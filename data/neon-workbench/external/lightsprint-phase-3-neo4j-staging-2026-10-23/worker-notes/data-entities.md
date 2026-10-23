# Canonical entity projection notes

`canonical_entities.build(frozen, staged)` reads only the frozen `trump_entries.people_tags` field and the staged `entities`, `entity_aliases`, and `entity_entry_links` tables. It uses exact string equality for canonical names and explicit aliases. It does not inspect descriptions or entry prose, infer entity types, merge identities, or infer a role beyond the staged `mentioned` value.

## Frozen input counts

- The staged `entities` table has 716 rows: 573 `person`, 74 `org`, and 69 `other`.
- The staged `entity_entry_links` table has 4,749 rows: 4,432 person links, 168 organization links, and 149 links to `other` entities. All staged link roles are `mentioned`, and every link references an existing staged entity and entry.
- The projection emits 647 typed entity nodes, 647 alias records, and 4,600 `MENTIONS` relationships. It withholds all 149 `other` links because that type cannot safely map to `Person` or `Organization`. Each withheld link retains the staged link row, entity identity, and any exactly matching frozen people tag as provenance. All 69 `other` identities have at least one link in this input; the worker also records an unsupported identity with its row provenance if a later input has no links for it.
- Frozen `people_tags` contains 4,750 tag occurrences. Each resolves by exact canonical name or explicit alias to a staged identity and link. Entry 6684 includes both `Mohammed bin Salman` and its explicit alias `MBS` for the same entity link; both tag values are retained in that relationship's provenance.
- There are 17 explicit alias pairs in `entities.aliases` and 17 in `entity_aliases`; they describe the same 17 supported entity/alias pairs. The alias export has one row per emitted Person or Organization node and includes the canonical name once in its `aliases` array.
- The staged names have no current NFKC+casefold alias collisions or duplicate same-type display names. The worker detects those conflicts for future inputs, reports them as ambiguities, withholds colliding aliases, and does not merge identities.

## Interpretation limits

`MENTIONS` records the explicit staged link only. It does not establish wrongdoing or any additional role. Alias conflicts, missing identities or links, malformed aliases, and unsupported link types are recorded as ambiguities rather than silently merged or discarded. Confidence `medium` describes faithful projection of the structured input, not the truth of any underlying claim.

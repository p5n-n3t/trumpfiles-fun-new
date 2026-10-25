# Worker result contract

Each input entry receives exactly one JSONL object with:

- entry_number: the assigned integer.
- status: enriched, no_supported_people, or needs_source.
- people: zero or more objects with name, role, source_url, evidence_claim,
  and 0-to-1 confidence.
- organizations: zero or more objects with name, entity_type, source_url,
  evidence_claim, and 0-to-1 confidence.
- locations, topics: arrays.
- reason: required for no_supported_people or needs_source.

Allowed people roles: subject, actor, official, target, mentioned.

Allowed organization entity types: organization, agency, company, country,
media, other.

Rules:

- Use one of the input record's actual evidence URLs. Do not cite a
  search-results page.
- Do not treat a reporter, source publisher, title, office, family
  association, party, place, or pronoun as a person.
- A role is an event-specific relationship, not an assumption about a person.
- People and organizations must be empty for no_supported_people and
  needs_source.
- Keep original people_tags out of the result unless an input source supports
  the link; legacy tags are already preserved separately.
- Output one line for every assigned entry number and no other entry numbers.
- These are proposal-only outputs. Do not edit SQLite, canonical JSONL, Neon,
  or Neo4j.

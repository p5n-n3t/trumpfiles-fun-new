# People and relationship enrichment — proposal lane

## What this adds

`people_tags` already exists in the legacy catalogue, but it is blank on many
entries and mixes people, organizations, and other concepts. This lane keeps
that field for compatibility while separating people, organizations, locations,
and topics in the staging model. It also adds source-backed relationship evidence
so a graph edge can explain *why* a person is connected to an entry.

## Relationship rules

- `subject`: the central person/event subject.
- `actor`: a person documented as taking the action.
- `official`: a named officeholder acting in that capacity.
- `target`: a documented person affected by the action.
- `mentioned`: named context only.

No role may be inferred from a name alone. Every proposed relationship needs a
source URL and a brief source-grounded claim. Organizations go in a distinct
tag set; locations and themes remain separate so the graph does not turn every
concept into a fake person.

## Status

This is offline-only. It produces batches for the 5,247 catalogue entries with
empty legacy `people_tags`. The frozen export, canonical data, Neon, and live
Neo4j are not altered.

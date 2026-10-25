# Schema v2 — FIRST DRAFT only

Goal: one uniform model that (1) stays source of truth in Postgres/Neon, (2) maps cleanly to Neo4j, (3) supports chatbot retrieval — without rewriting the app yet.

## Why incomplete.so graph is useless today

`entities`, `entity_entry_links`, and `trump_entry_links` exist in Neon but have **0 rows**.
`scripts/neo4j-import.mjs` currently synthesizes `(:Person)` only from `trump_entries.people_tags` text arrays. There is no durable entity identity, alias merge, or typed role graph in Postgres. Until those tables are filled (or replaced), Neo4j is a derived projection, not a second source of truth.

## Design principles

1. **Postgres is SoT.** Neo4j is a projection/index for path queries and network UI.
2. **Stable IDs.** Keep numeric `entry_number` for public URLs; add opaque `entry_id` (UUID or `evt-…` from enrichment-contract) for joins/embeddings.
3. **Normalize dual storage.** Sources live in one relational table; drop or demote `trump_entries.sources` jsonb to a cache.
4. **Canonical enums.** Phases/categories follow `scripts/enrichment-contract.mjs` (`VALID_PHASES`, `VALID_CATEGORIES`); keep `raw_phase` for lossless cleanup.
5. **Soft-hide, don’t delete.** Retrieval flags for chatbot without destroying audit history.

## Proposed Postgres tables (v2)

### `entries` (replaces / wraps `trump_entries`)

| Column | Type | Notes |
|--------|------|-------|
| entry_id | uuid PK | stable internal id |
| entry_number | int UNIQUE | public # |
| title | text NOT NULL | |
| synopsis | text | blurb |
| rationale | text | scoring/narrative rationale |
| embedding_text | text | title + synopsis + key claims, embedding-ready |
| category | text | canonical |
| subcategory | text | |
| phase | text | canonical (VALID_PHASES) |
| raw_phase | text | original label |
| date_start / date_end | date | |
| retrieval_weight | real DEFAULT 1.0 | chatbot ranking boost/dampen |
| soft_hidden | boolean DEFAULT false | hide from public/chat without delete |
| hide_reason | text | |
| people_tags / org_tags / topic_tags | text[] | transitional; prefer link tables |
| created_at / updated_at | timestamptz | |

### `entry_scores` (replaces `trump_individual_scores`)

One row per entry: danger, authoritarianism, lawlessness, insanity, absurdity, credibility_risk, recency_intensity, impact_scope, composite, rationale_short, rationale_detail.

### `sources` (replaces `trump_sources` + jsonb)

source_id, entry_id/entry_number, url, title, publisher, date_published, source_type, http_status_last, is_primary.

### `keywords` / `themes`

keyword rows or a `themes` vocabulary + `entry_themes` M2M.

### Graph tables (fill these — currently empty)

- **`entities`**: id, name, entity_type (`person`|`org`|`other`), aliases[], description
- **`entity_entry_links`**: entity_id, entry_number, role (`mentioned`|`actor`|`target`|…)
- **`entry_links`**: from_entry, to_entry, relation_type (`PRECEDES`|`RELATES_TO`|`SAME_AS`|…)

## Neo4j mapping

### 2026-10-25 graph-enrichment correction

The earlier shorthand above is superseded by this additive compatibility rule:

- Preserve the specific exported entity types: person, organization, agency,
  company, country, media, and other. Do not collapse them in Postgres.
- Extend entity-to-entry links with nullable claim_text, source_url, and
  provenance_type. Existing legacy-tag links stay valid as mentioned links;
  source-backed editorial links must state their source and claim.
- Keep a separate entity_entry_evidence ledger where one entity-to-entry role
  needs multiple sources. It records entity, entry, role, source URL, claim,
  confidence, extraction method, and review status.
- Keep people_tags as a compatibility/display field during backfill. Store
  organizations, locations, and topics separately; do not turn every named
  thing into a person node.

For Neo4j projection, person becomes Person; organization, agency, company,
country, and media become Organization with their entity type retained as a
property; other or unknown becomes Entity. A relationship retains the generic
MENTIONS type initially and carries role, claim_text, source_url, and
provenance_type as properties. Role-specific relationship labels can be a
later projection change after coverage is validated.

| Postgres | Neo4j |
|----------|-------|
| entries | `(:Entry {entry_id, entry_number, title, phase, category, …})` |
| entities (person/org) | `(:Person)` / `(:Org)` / `(:Entity)` |
| sources | `(:Source {url, publisher})` |
| keywords/themes | `(:Theme)` / `(:Keyword)` |
| phase / category enums | `(:Phase)`, `(:Category)` |
| entity_entry_links | `[:MENTIONS]` / role-specific |
| entry_links | `[:RELATES_TO]`, `[:SAME_AS]`, `[:PRECEDES]` |
| sources ↔ entries | `[:SOURCED_FROM]` |

Aligns with today’s network page (Event≈Entry, Person, Category) while adding Source/Theme and typed edges.

## Chatbot retrieval fields

Minimum viable retrieval document per entry:

- `entry_id`, `entry_number`
- `title`, `synopsis` (blurb), `rationale`
- `tags` (themes + people + orgs)
- `embedding_text`
- `retrieval_weight`, `soft_hidden`
- optional score vector for filter/boost

## Migration sketch (later)

1. Add new columns / tables beside legacy (`entry_id`, `raw_phase`, `embedding_text`, flags).
2. Backfill from export sqlite offline; validate counts.
3. Populate `entities` + links from `people_tags` (dedupe names → aliases).
4. Unify sources (table wins; merge jsonb leftovers).
5. Re-run Neo4j import from v2 tables.
6. Only then cut app queries over — out of scope for this dump.

## Non-goals for this draft

- No app rewrite.
- No live Neon writes from this prep step.
- No claim that Neo4j is currently authoritative.

// OFFLINE SCHEMA SPECIFICATION ONLY. No credentials, endpoint, or execution procedure.
// Neo4j 5 community-compatible constraints. Repeat declarations are idempotent.
CREATE CONSTRAINT phase3_entry_id IF NOT EXISTS FOR (n:Entry) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT phase3_entry_number IF NOT EXISTS FOR (n:Entry) REQUIRE n.entry_number IS UNIQUE;
CREATE CONSTRAINT phase3_person_id IF NOT EXISTS FOR (n:Person) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT phase3_organization_id IF NOT EXISTS FOR (n:Organization) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT phase3_source_id IF NOT EXISTS FOR (n:Source) REQUIRE n.id IS UNIQUE;
CREATE INDEX phase3_source_url IF NOT EXISTS FOR (n:Source) ON (n.url);
CREATE CONSTRAINT phase3_theme_id IF NOT EXISTS FOR (n:Theme) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT phase3_category_id IF NOT EXISTS FOR (n:Category) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT phase3_phase_id IF NOT EXISTS FOR (n:Phase) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT phase3_proposed_id IF NOT EXISTS FOR (n:ProposedCandidate) REQUIRE n.id IS UNIQUE;
CREATE INDEX phase3_entry_title IF NOT EXISTS FOR (n:Entry) ON (n.display_name);
CREATE INDEX phase3_person_name IF NOT EXISTS FOR (n:Person) ON (n.display_name);
CREATE INDEX phase3_org_name IF NOT EXISTS FOR (n:Organization) ON (n.display_name);
CREATE INDEX phase3_review_status IF NOT EXISTS FOR (n:ProposedCandidate) ON (n.status);
// LABELS: Entry, Person, Organization, Source, Theme, Category, Phase.
// REVIEW-ONLY LABEL: ProposedCandidate; never Entry. Review graph is not imported.
// DIRECTION AND RELATIONSHIP CONTRACT (enforced offline by validate-graph-staging.mjs):
// (Entry)-[:MENTIONS]->(Person|Organization)
// (Person|Organization)-[:ACTOR_IN|TARGET_OF]->(Entry): explicit roles only.
// (Entry)-[:SOURCED_FROM]->(Source)
// (Entry)-[:HAS_THEME]->(Theme)
// (Entry)-[:IN_CATEGORY]->(Category)
// (Entry)-[:IN_PHASE]->(Phase)
// (Entry)-[:RELATES_TO|SAME_AS|PRECEDES]->(Entry): explicit objective basis only.
// Every relationship: id, status, confidence, basis, provenance, origin_entry_number.
// Serialize provenance to a JSON STRING on import: Neo4j properties cannot store maps.
// Review-only counterpart: ProposedCandidate in place of Entry, origin_candidate_id
// in place of origin_entry_number, disjoint candidate-scoped endpoints and status
// PROPOSED_NOT_APPROVED on EVERY record. Never allocate entry_number in this layer.
// Neo4j community constraints cannot restrict relationship type or require these
// properties; offline validation is mandatory before any future approved projection.

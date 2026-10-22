# Todo — uniform + optimized Trump DB

Source of truth for offline work: `data/neon-export/` (JSONL + `sqlite/trump_local.sqlite`).
Do bulk edits locally; push curated patches to Neon later in small batches.

## Phase 0 — Freeze & workbench (done)
- [x] Full live Neon export (entries, scores, sources, keywords + schemas)
- [x] Local SQLite with indexes
- [x] Issue seed + empty queues
- [x] Schema v2 first draft (`schema-v2-draft.md`)
- [x] gitignore dump folders

## Phase 1 — Clean the catalog text & labels
1. **Dedupe** (~43 exact-title groups / ~106 entries): keep one canonical entry; soft-hide or merge extras; log decisions in `queues/dedupe.jsonl`.
2. **Phase normalize** (~2,543 bad/null): map via enrichment-contract (`White House 2` → `White House 2:2`, etc.); keep `raw_phase`.
3. **Category normalize** (~447 outside contract): remap or extend the allowed set deliberately.
4. **Rewrite shorts** (~112): title ≥20 chars, synopsis ≥80 (and multi-length blurbs later for cards/chat/SEO).
5. **Fill missing rationale_short** (~3.5k from prior audit): short “why this entry matters” for retrieval + UI.

## Phase 2 — Sources as one truth
6. **Unify sources**: prefer `trump_sources` table; merge leftover jsonb URLs; retire dual-store drift.
7. **Backfill missing http(s)** (~1,375): find at least one working primary URL per entry; record publisher + last http check.
8. **Soft-hide** entries that stay sourceless after honest search (don’t delete).

## Phase 3 — Scoring (decide methodology first)
9. **Lock a new score model** (weighted composite + clear criteria; or keep 5 axes with weights + confidence).
10. **Score the 85 unscored** under the new rules.
11. **Optional full rescore** offline on SQLite; write patch set; spot-check before Neon upload.
12. Separate **community feedback** scores from AI scores if you add user signals later.

## Phase 4 — Schema v2 (Postgres SoT, Neo4j projection)
13. Add beside legacy: `entry_id`, `embedding_text`, `retrieval_weight`, `soft_hidden`, `raw_phase`.
14. Normalize tables: `entries`, `entry_scores`, `sources`, themes/keywords M2M.
15. **Populate graph tables** (today 0 rows — why incomplete.so is empty/wrong):
    - `entities` (person/org + aliases)
    - `entity_entry_links` (role: actor / target / mentioned)
    - `entry_links` (PRECEDES / RELATES_TO / SAME_AS)
16. Build entities from `people_tags` first (dedupe names → aliases), then enrich.
17. Rewrite `scripts/neo4j-import.mjs` to project from those tables (Entry, Person/Org, Source, Theme, Phase, Category + MENTIONS / SOURCED_FROM / RELATES_TO / SAME_AS / PRECEDES).
18. Rebuild Neo4j; verify incomplete.so / network UI shows real structure, not tag soup.

## Phase 5 — Chatbot memory corpus (Trumpstein retrieval)
19. Define retrieval document per entry: id, number, title, synopsis, rationale, tags, embedding_text, weight, soft_hidden, optional scores.
20. Generate `embedding_text` + embeddings; store in Vectorize (or chosen index) keyed by `entry_id`.
21. Retrieval pipeline: hybrid (keyword + vector) → rerank with weight/scores → cite entry_numbers; live web search only as supplement, never instead of corpus.
22. Add light feedback: “right entry?” / useful / flag → adjust `retrieval_weight` offline.
23. Prompt + routing: prefer corpus hits; refuse or hedge when no good entry matches.

## Phase 6 — Upload & cutover
24. Build patch JSONL from workbench queues; validate counts against SQLite.
25. Apply to Neon in small batches (protect free compute).
26. Re-export / diff to confirm.
27. Point app + Trumpstein + Neo4j import at v2 fields; only then retire dual jsonb / legacy columns.

## Suggested order of attack
Dedupe → phase/category → sources → rewrite → score model → entity graph → embeddings/chat → Neo4j rebuild → Neon upload.

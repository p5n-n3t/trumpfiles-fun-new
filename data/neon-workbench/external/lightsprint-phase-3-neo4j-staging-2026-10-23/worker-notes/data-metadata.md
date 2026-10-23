# Canonical metadata projection notes

`canonical_metadata.build(frozen, staged)` reads the frozen `trump_sources`, `trump_entries`, and `trump_keywords` tables. It uses `trump_sources` as the primary source catalogue, then supplements it with explicit URL values from the frozen `sources`, `fact_check_sources`, and structured `entry_links` JSON fields. The `entry_links.reporting` value can contribute a source URL; it never creates an entry-to-entry relationship. `staged` is accepted for the coordinator interface but is not used to replace raw catalogue fields.

Source URLs pass through the shared `source_url` helper. It accepts explicit absolute HTTPS URLs and rejects HTTP, bare domains, malformed values, credentials, whitespace, backslashes, and secret-like query parameters. The projection does not add a scheme or otherwise upgrade a value. Equivalent URLs use the helper's normalization and share `stable_id('source', normalized_url)`. All columns from `trump_sources` and all structured source fields are retained in provenance. Table metadata takes priority over JSON metadata; JSON fills absent fields, and differing metadata is kept visible in source-node notes.

Themes use exact string identity from frozen `trump_entries.keywords` JSON and `trump_keywords.keyword`. Category and phase nodes use the exact raw strings in frozen `trump_entries.category` and `trump_entries.phase`; staged normalized values are not used. No aliases or fuzzy merges are produced. Confidence describes extraction from structured data, not the truth or quality of the underlying source.

## Frozen input and projection counts

Counts below are from the frozen input and a read-only `build` against the 2026-10-23 staged snapshot.

- The frozen database has 7,143 entries, 4,771 `trump_sources` rows, and 18,328 `trump_keywords` rows. Every source and keyword row currently references an existing entry. The worker withholds any such row whose endpoint is missing in a later snapshot, retaining the full row in an ambiguity record. A source node backed by a row with only withheld uses remains identifiable and is annotated with the withheld-use count.
- The projection emits 6,100 Source, 8,443 Theme, 51 Category, and 25 Phase nodes. It emits 7,719 `SOURCED_FROM`, 23,708 `HAS_THEME`, 7,143 `IN_CATEGORY`, and 7,143 `IN_PHASE` relationships. There are no aliases.
- All 7,143 entries have a non-empty raw category and phase, so the current projection has no missing-facet ambiguities. Category and phase confidence `high` means the exact raw field was projected; it does not validate the classification.
- It emits 1,098 source-value ambiguities: 862 values that are not explicit absolute HTTPS URLs, 57 non-string URL values, 178 structured source records with no URL field, and one invalid URL in `trump_sources`. Each ambiguity records its exact `origin_field`, reason, and source-field provenance. It emits no dangling-reference ambiguities for the current input.
- Of the source table's 4,771 rows, 4,770 contain accepted HTTPS URLs and one contains an HTTP URL (`source_id` 7652). The accepted table URLs reduce to 3,637 normalized URLs before JSON supplements. The projection records metadata conflicts in 335 Source nodes rather than overwriting them silently.

## Known limits

- Legacy strings such as `"news"` in `sources` are not treated as publishers or URLs. They remain ambiguous values. Bare domains in `entry_links.reporting` are also withheld; the projection does not assume `https://`.
- Structured source records with no URL are retained as ambiguities. `entry_links.reporting` is only checked as source metadata and is never read as an entry graph link.
- Theme identity is exact, including case and whitespace. Category and phase identity is also exact. The projection does not normalize labels or combine similar values.
- URL equivalence follows `source_url` normalization only. Redirects, publisher identity, URL query reordering, and fragment equivalence are not inferred.
- A read-only census found no valid HTTPS string leaves missed inside nested source lists or `entry_links` string arrays in this snapshot. If a later input adds such a shape, it should be handled only where the string's source-URL role is explicit.

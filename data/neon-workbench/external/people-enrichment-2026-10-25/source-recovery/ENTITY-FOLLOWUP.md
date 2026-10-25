# Entity follow-up after source recovery

For each completed source-recovery packet with status source_found, create one
people/entity proposal per assigned entry using the same fields and rules in
the parent RESULT-SCHEMA.md.

The only permitted evidence URLs are the URLs in that entry's recovered
source record. Do not infer a person, role, or organization from a headline
alone. If the recovered source supports the event but not a named relationship,
return no_supported_people with empty entity arrays.

Write entity results into source-recovery/entity-results using the same packet
file name. This stays proposal-only and must not modify any database.

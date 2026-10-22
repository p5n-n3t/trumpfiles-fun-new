# Offline provisional score model

## Purpose and status

This is a compatibility-preserving, evidence-aware scoring pass for the 85
entries that had no row in `trump_individual_scores` in the frozen export.
It is **not** a fact-finding pass, a publication approval, or a model of
community sentiment. The output is an offline patch that must be reviewed with
source triage before any Neon write.

The legacy table and visualizations expect eight integer axes from 0 to 10 and
a `composite_score`. This pass retains those fields, adds patch-only
`confidence`, `confidence_reason`, and `scoring_version` metadata, and
uses the legacy-compatible arithmetic mean:

```
composite_score =
  mean(insanity, absurdity, danger, authoritarianism, lawlessness,
       credibility_risk, recency_intensity, impact_scope)
```

The composite is a routing/display priority signal, not a measure of truth,
criminal liability, or moral worth. Future schema v2 should persist confidence
and source-review state separately rather than fold either into the composite.

## Axis definitions

| Axis | Meaning in this pass |
| --- | --- |
| insanity | Degree to which the recorded conduct departs from ordinary public norms |
| absurdity | Unusual or performative character of the recorded conduct |
| danger | Plausible harm if the documented conduct or policy is accurate |
| authoritarianism | Concentration of power, retaliation, or erosion of institutional independence described by the record |
| lawlessness | Apparent conflict with legal or procedural norms described by the record |
| credibility_risk | Editorial caution required before amplification; higher means more corroboration is needed |
| recency_intensity | Currentness of the event in this 2026-era export, not importance |
| impact_scope | Apparent scale of people, institutions, or systems affected |

Scores are assigned from the entry's existing category and stated scope only.
That keeps the offline pass reproducible and prevents unsupported details from
being introduced by a scorer. Category-level templates deliberately produce
moderate values unless the category itself describes broad institutional or
human impact.

## Confidence gate

- **medium**: two or more linked source records, or one linked record from a
  recognized institutional/news domain in the frozen metadata.
- **low**: one linked record whose publisher/domain could not be classified by
  this offline pass.
- **deferred**: no linked source metadata. These entries do not receive score
  rows and are listed in `patches/approved/scores_rejected.jsonl`.

No row is marked high confidence: this lane did not fetch URLs, test
reachability, or compare each claim against the source text.

## Acceptance counts

- Queue reviewed: 85
- Provisional score patches: 64
- Deferred for missing source metadata: 21
- Existing score rows changed: 0

Before an upload, a source-triage worker must resolve each deferred item and a
reviewer must sample the score/category fit. Community feedback must remain in
a distinct table or field and must not overwrite these editorial scores.

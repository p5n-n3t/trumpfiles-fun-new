# Held149 reviewer handoff

**Source:** draft [PR #69](https://github.com/p5n-n3t/trumpfiles-fun-new/pull/69). New append-only proposal tree branched from `main`; do not merge directly into canonical data.

**Coverage:** 149 / 149 eligible parent IDs (109 holds and 40 unverified drafts). Disposition counts: {"soft_hide_candidate":25,"still_unresolved":119,"repaired_proposal":2,"supported_partial":2,"split_ready":1}. Six sorted, non-overlapping worker JSONL ledgers and checkpoint files are provided; no excluded source status has been reprocessed.

**Review four candidate proposals:** `entry-380` (Melania Trump's announcement; attributed, not independently proven child cases), `entry-2458` (1993 Trump lawsuit against federal tribal gaming treatment, not a merits judgment), `entry-5237` (Ellis appointed Feb 3; sworn in Feb 10), `entry-6356` (2023 Haigh bank testimony, **not** unsupported double-billing). Precise publisher URLs, dates, and how they were accessed are embedded in each proposal. Check provenance before publication.

**Parent `entry-5832`:** mapped to WHO January 20 order and a separate UNESCO announcement. The WHO child has sourced copy; the UNESCO child remains withheld pending substantive verification and is **not** a ready-to-publish event. Preserve these internal parent/child IDs without creating canonical IDs.

**Remaining outcomes:** `still_unresolved` retains event-specific blockers, and `soft_hide_candidate` is a recommendation with a reason, not a deletion. None can be published by default. `publication_eligible=false` for the entire ledger.

**Validation:** zero ID/URL/schema/text-length errors. Four layers use title and short up to 180 characters, medium 45–90 words, long 140–300 words. A structural validator does not authenticate all historical events.

**Worker caveat:** This toolset cannot launch six real subagents. The six partition files were completed by one agent with deterministic coverage, with separate checkpoints; independent QA remains necessary. Neither PR #69 nor canonical datasets were modified.

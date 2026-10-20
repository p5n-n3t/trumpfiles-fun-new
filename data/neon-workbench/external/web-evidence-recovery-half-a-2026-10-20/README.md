# Trump Files — Half A evidence recovery (append-only)

Scope is exactly the 60 IDs in `checkpoint.json` under `assignment_ids`, each processed once in six non-overlapping ten-entry research partitions. The baseline is [draft PR #71](https://github.com/p5n-n3t/trumpfiles-fun-new/pull/71) at `3af4d448606ed190acbdc2fb83456ff164b0f005`. The original PR71 review packet, frozen export, and previously performed research were read only; earlier research may be cited as context, **not** as independent source verification. New source access attempts and limitations are documented in `research-log.jsonl`.

`final-terminal-results.jsonl` is an append-only proposal layer: one `repaired_proposal`, `supported_partial`, or `still_unresolved` per record. A positive outcome has distinct title/short/medium/long copy and exact supporting source URLs. An unresolved outcome explains its precise blocker and never substitutes an unrelated event. The preserved `original_source_urls` do not imply verification; inspect `source_provenance`, `evidence_note`, and the research log for each outcome's access status.

Everything is **publication_eligible=false**, **proposal_only=true**, and requires independent source-level editorial review. No automated import, Neon change, canonical/frozen rewrite, score update, migration, or merger is authorized.

See `PROGRESS.md`, `checkpoint.json`, and `validation-report.json` for outcome counts and QA.

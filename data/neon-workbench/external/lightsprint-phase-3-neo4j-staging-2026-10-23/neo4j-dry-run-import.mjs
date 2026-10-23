#!/usr/bin/env node
// No live execution implementation is shipped in this offline staging package.
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import { HERE, FILES, readGraph, validateRecords, sha } from './validate-graph-staging.mjs';

const args = process.argv.slice(2);
if (args.includes('--apply')) {
  console.error('REFUSED: --apply is reserved for a separate human-approved deployment implementation. This offline package cannot connect to a database.');
  process.exitCode = 2;
} else if (args.length) {
  console.error('REFUSED: only the default dry-run is implemented; unknown flags are not accepted.');
  process.exitCode = 2;
} else {
  try {
    // Reads only the five staged JSONL files. Proposed rows are validated but excluded from import.
    const plan = validateRecords(readGraph());
    console.log(JSON.stringify({mode: 'DRY_RUN', execution_enabled: false, ...plan,
      import_nodes: plan.canonical_nodes, import_relationships: plan.canonical_relationships,
      proposed_import_rows: 0, ambiguous_import_rows: 0,
      suggested_batch_size: 250, suggested_concurrency: 1,
      inputs_sha256: Object.fromEntries(FILES.map(file => [file, sha(readFileSync(join(HERE, file)))]))}));
  } catch (error) { console.error(`DRY RUN FAILED: ${error.message}`); process.exitCode = 1; }
}

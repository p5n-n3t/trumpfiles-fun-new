#!/usr/bin/env node
// Offline, read-only validation. From repository root: node data/neon-workbench/external/web-needs-context-rewrite-2026-10-22/validate-results.mjs
import fs from 'node:fs';
import path from 'node:path';

const home = 'data/neon-workbench/external/web-needs-context-rewrite-2026-10-22';
const read = f => fs.readFileSync(path.join(process.cwd(), home, f), 'utf8');
const jsonl = f => read(f).split(/\r?\n/).filter(s => s.trim()).map((line, n) => {
  try { return JSON.parse(line); } catch (e) { throw new Error(`${f} line ${n + 1}: ${e.message}`); }
});
const manifest = JSON.parse(read('assignment-partitions.json'));
const owners = new Map();
const errors = [];
for (const part of manifest.partitions) {
  for (const row of part.records) {
    if (owners.has(row.record_id)) errors.push(`duplicate assignment ${row.record_id}`);
    owners.set(row.record_id, {entry_number: row.entry_number, worker: part.worker_partition});
  }
}
if (owners.size !== 497 || manifest.assigned_count !== 497) errors.push(`assignment manifest has ${owners.size} not 497`);
const allowed = new Set(['repaired_proposal', 'supported_partial', 'needs_context', 'soft_hide_candidate', 'split_required']);
const results = new Map();
const status = Object.fromEntries([...allowed].map(s => [s, 0]));
let urlReferences = 0;
const wordCount = s => String(s || '').trim().split(/\s+/).filter(Boolean).length;
for (const part of manifest.partitions) {
  const dir = path.join(process.cwd(), home, part.worker_partition);
  if (!fs.existsSync(dir)) continue;
  const files = fs.readdirSync(dir).filter(f => /^terminal-results.*\.jsonl$/.test(f)).sort();
  for (const file of files) for (const row of jsonl(path.join(part.worker_partition, file))) {
    const id = row.record_id;
    if (!owners.has(id)) errors.push(`outside assignment ${id}`);
    if (results.has(id)) errors.push(`duplicate terminal outcome ${id}`);
    results.set(id, row);
    if (!allowed.has(row.status)) errors.push(`invalid status ${id}`);
    else status[row.status]++;
    if (row.entry_number !== owners.get(id)?.entry_number || row.worker_partition !== part.worker_partition || owners.get(id)?.worker !== part.worker_partition) errors.push(`wrong ID/partition ${id}`);
    if (!Array.isArray(row.source_urls)) errors.push(`missing source array ${id}`);
    for (const url of row.source_urls || []) {
      urlReferences++;
      if (!/^https:\/\/[^\s]+$/.test(url)) errors.push(`non-HTTPS URL for ${id}`);
    }
    if (row.title != null && (!String(row.title).trim() || String(row.title).length > 180)) errors.push(`bad title ${id}`);
    if (row.description_short != null && String(row.description_short).length > 180) errors.push(`short >180 ${id}`);
    if (row.status === 'repaired_proposal') {
      if (!row.title || !row.description_short || !row.description_medium || !row.description_long) errors.push(`missing complete copy ${id}`);
      if (wordCount(row.description_medium) < 45 || wordCount(row.description_medium) > 90) errors.push(`medium length ${id}`);
      if (wordCount(row.description_long) < 140 || wordCount(row.description_long) > 300) errors.push(`long length ${id}`);
      const normalize = x => String(x || '').toLowerCase().replace(/\s+/g, ' ').trim();
      if (new Set([row.description_short,row.description_medium,row.description_long].map(normalize)).size < 3) errors.push(`duplicated copy layers ${id}`);
      if (!(row.source_urls || []).length) errors.push(`complete has no sources ${id}`);
    } else if (!String(row.reason_or_blocker || '').trim()) errors.push(`missing precise blocker ${id}`);
  }
}
const research = jsonl('research-log.jsonl');
const researchIds = new Set(research.map(r => r.record_id));
for (const id of results.keys()) if (!researchIds.has(id)) errors.push(`missing research log ${id}`);
const missing = [...owners.keys()].filter(x => !results.has(x));
const report = {
  assigned: owners.size,
  terminal: results.size,
  missing: missing.length,
  missing_ids: missing,
  status_counts: status,
  source_url_references: urlReferences,
  researched_terminal_ids: [...results.keys()].filter(x => researchIds.has(x)).length,
  duplicate_research_log_ids: research.length - researchIds.size,
  errors,
  structurally_valid_current_results: errors.length === 0,
  full_acceptance_pass: missing.length === 0 && errors.length === 0
};
console.log(JSON.stringify(report, null, 2));
process.exitCode = report.full_acceptance_pass ? 0 : 1;

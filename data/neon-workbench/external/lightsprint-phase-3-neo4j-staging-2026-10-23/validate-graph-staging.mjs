#!/usr/bin/env node
// Offline validator: no environment reads, network clients, or database drivers.
import { readFileSync, mkdtempSync, rmSync, readdirSync } from 'node:fs';
import { resolve, dirname, join } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { createHash } from 'node:crypto';
import { spawnSync } from 'node:child_process';

export const HERE = dirname(fileURLToPath(import.meta.url));
export const FILES = ['graph-nodes.jsonl', 'graph-relationships.jsonl',
  'proposed-candidate-graph.jsonl', 'ambiguous-relationships.jsonl', 'entity-aliases.jsonl'];
export const LABELS = new Set(['Entry', 'Person', 'Organization', 'Source', 'Theme', 'Keyword', 'Category', 'Phase']);
export const TYPES = new Set(['MENTIONS', 'ACTOR_IN', 'TARGET_OF', 'SOURCED_FROM', 'HAS_THEME',
  'IN_CATEGORY', 'IN_PHASE', 'RELATES_TO', 'SAME_AS', 'PRECEDES']);
const CANONICAL = 'CANONICAL';
const PROPOSED = 'PROPOSED_NOT_APPROVED';
const CONFIDENCE = new Set(['high', 'medium', 'low']);
export const sha = value => createHash('sha256').update(value).digest('hex');
const assert = (condition, message) => { if (!condition) throw new Error(message); };
const nonempty = value => typeof value === 'string' && value.trim().length > 0;
const tally = (rows, key) => Object.fromEntries([...new Set(rows.map(r => r[key]))].sort()
  .map(value => [value, rows.filter(r => r[key] === value).length]));
const equal = (a, b) => JSON.stringify(sortObject(a)) === JSON.stringify(sortObject(b));
function sortObject(value) {
  if (Array.isArray(value)) return value.map(sortObject);
  if (value && typeof value === 'object') return Object.fromEntries(Object.keys(value).sort().map(k => [k, sortObject(value[k])]));
  return value;
}

function validUrl(raw) {
  assert(nonempty(raw) && !/[\s\\]/u.test(raw), 'Malformed source URL');
  const u = new URL(raw);
  assert(u.protocol === 'https:' && u.hostname.includes('.') && !u.username && !u.password, 'Source URL must be HTTPS without credentials');
  for (const key of u.searchParams.keys()) assert(!/^(token|key|api_key|apikey|secret|password|access_token|signature|sig|x-amz-.*)$/i.test(key), 'Secret-like source URL query');
}

function checkProvenance(row) {
  assert(Array.isArray(row.provenance) && row.provenance.length > 0, `Missing provenance: ${row.id}`);
  for (const p of row.provenance) {
    assert(nonempty(p.input) && nonempty(p.table) && p.row_key !== undefined && nonempty(p.field) && Object.hasOwn(p, 'value'), `Incomplete provenance: ${row.id}`);
  }
  assert(CONFIDENCE.has(row.confidence), `Invalid confidence: ${row.id}`);
}

function unique(rows, name) {
  const ids = new Set();
  for (const row of rows) {
    assert(nonempty(row.id) && !ids.has(row.id), `Duplicate/missing ID in ${name}: ${row.id}`);
    ids.add(row.id);
  }
  return ids;
}

function noAllocatedNumber(value) {
  if (!value || typeof value !== 'object') return;
  for (const [key, item] of Object.entries(value)) {
    assert(!['entry_number', 'origin_entry_number', 'canonical_entry_number', 'entry_id'].includes(key), 'Proposed row allocated a canonical entry identity');
    noAllocatedNumber(item);
  }
}

function checkNode(row, proposed) {
  assert(row.record_type === 'node' && nonempty(row.display_name), `Invalid node: ${row.id}`);
  assert((proposed ? new Set([...LABELS].filter(x => x !== 'Entry').concat('ProposedCandidate')) : LABELS).has(row.type), `Unsupported label: ${row.type}`);
  checkProvenance(row);
  if (row.type === 'Source') validUrl(row.url);
  if (row.type === 'Entry') {
    assert(Number.isInteger(row.entry_number) && row.entry_number > 0 && row.id === `entry:${row.entry_number}`, 'Invalid canonical entry identity');
    assert(!Object.hasOwn(row, 'candidate_id') && !Object.hasOwn(row, 'origin_candidate_id'), 'Proposed candidate leaked into canonical Entry');
  }
}

function checkRelationship(row, nodes, proposed) {
  assert(row.record_type === 'relationship' && TYPES.has(row.type), `Unsupported relationship type: ${row.type}`);
  assert(nonempty(row.basis), `Missing basis: ${row.id}`);
  checkProvenance(row);
  const s = nodes.get(row.source), t = nodes.get(row.target);
  assert(s && t, `Dangling endpoint: ${row.id}`);
  const entryType = proposed ? 'ProposedCandidate' : 'Entry';
  const pair = (sourceTypes, targetTypes) => sourceTypes.includes(s.type) && targetTypes.includes(t.type);
  const valid = row.type === 'MENTIONS' ? pair([entryType], ['Person', 'Organization'])
    : ['ACTOR_IN', 'TARGET_OF'].includes(row.type) ? pair(['Person', 'Organization'], [entryType])
    : row.type === 'SOURCED_FROM' ? pair([entryType], ['Source'])
    : row.type === 'HAS_THEME' ? pair([entryType], ['Theme', 'Keyword'])
    : row.type === 'IN_CATEGORY' ? pair([entryType], ['Category'])
    : row.type === 'IN_PHASE' ? pair([entryType], ['Phase'])
    : pair([entryType], [entryType]);
  assert(valid, `Invalid relationship direction/label pair: ${row.id}`);
  if (proposed) {
    assert(s.origin_candidate_id === row.origin_candidate_id && t.origin_candidate_id === row.origin_candidate_id, 'Proposed relationship crosses candidate namespaces');
  } else {
    assert(Number.isInteger(row.origin_entry_number) && nodes.get(`entry:${row.origin_entry_number}`)?.type === 'Entry', `Invalid origin entry: ${row.id}`);
    assert([s.id, t.id].includes(`entry:${row.origin_entry_number}`), `Origin is not an endpoint: ${row.id}`);
    assert(!Object.hasOwn(row, 'origin_candidate_id'), 'Proposed relationship leaked into canonical graph');
  }
}

function uniqueRelationships(rows) {
  const keys = new Set();
  for (const row of rows) {
    const key = JSON.stringify([row.source, row.target, row.type, row.origin_entry_number ?? row.origin_candidate_id]);
    assert(!keys.has(key), `Duplicate logical relationship: ${row.id}`);
    keys.add(key);
  }
}

export function readGraph(directory = HERE) {
  return Object.fromEntries(FILES.map(file => {
    const text = readFileSync(join(directory, file), 'utf8');
    const rows = text.trim() ? text.trimEnd().split('\n').map((line, i) => {
      try { return JSON.parse(line); } catch { throw new Error(`Invalid JSON: ${file}:${i + 1}`); }
    }) : [];
    for (let i = 1; i < rows.length; i++) assert(rows[i - 1].id < rows[i].id, `Unsorted or duplicate records: ${file}`);
    return [file, rows];
  }));
}

export function validateRecords(graph, expected = {}) {
  const nodes = graph[FILES[0]], relationships = graph[FILES[1]], proposed = graph[FILES[2]];
  const withheld = graph[FILES[3]], aliases = graph[FILES[4]];
  const ids = unique(nodes, FILES[0]);
  unique(relationships, FILES[1]);
  uniqueRelationships(relationships);
  const proposedIds = unique(proposed, FILES[2]);
  unique(withheld, FILES[3]);
  unique(aliases, FILES[4]);
  const nodeMap = new Map(nodes.map(r => [r.id, r]));
  for (const row of nodes.concat(relationships, aliases)) {
    assert(row.status === CANONICAL && !row.id.startsWith('proposed:'), `Canonical status leakage: ${row.id}`);
    assert(!Object.hasOwn(row, 'origin_candidate_id') && !Object.hasOwn(row, 'candidate_id'), 'Candidate origin in canonical layer');
  }
  for (const row of nodes) checkNode(row, false);
  for (const row of relationships) checkRelationship(row, nodeMap, false);
  const entries = nodes.filter(r => r.type === 'Entry').map(r => r.entry_number).sort((a, b) => a - b);
  assert(entries.length === 7143, 'Canonical entry coverage must equal 7143');
  if (expected.canonical_entry_numbers) assert(equal(entries, expected.canonical_entry_numbers), 'Canonical entry set differs from pinned input');
  const pnodes = proposed.filter(r => r.record_type === 'node');
  const prels = proposed.filter(r => r.record_type === 'relationship');
  for (const row of pnodes) assert(row.type !== 'Entry', 'Unsupported label: Entry in proposed graph');
  uniqueRelationships(prels);
  const pmap = new Map(pnodes.map(r => [r.id, r]));
  const candidateIds = pnodes.filter(r => r.type === 'ProposedCandidate').map(r => r.origin_candidate_id).sort();
  assert(candidateIds.length === 147 && new Set(candidateIds).size === 147, 'Proposed candidate coverage must equal 147');
  if (expected.proposed_candidate_ids) assert(equal(candidateIds, expected.proposed_candidate_ids), 'Candidate set differs from pinned Phase 2 input');
  for (const row of proposed) {
    assert(row.status === PROPOSED && nonempty(row.origin_candidate_id) && candidateIds.includes(row.origin_candidate_id), 'Proposed status/origin leakage');
    noAllocatedNumber(row);
    assert(!ids.has(row.id) && !ids.has(row.source) && !ids.has(row.target), 'Proposed graph touches canonical identity');
    if (row.record_type === 'node') {
      assert(row.id === `proposed:${row.origin_candidate_id}` || row.id.startsWith(`proposed:${row.origin_candidate_id}:`), 'Invalid candidate namespace');
      checkNode(row, true);
    } else checkRelationship(row, pmap, true);
  }
  assert(pnodes.length + prels.length === proposed.length, 'Unknown proposed record kind');
  for (const id of ids) assert(!proposedIds.has(id), 'Cross-layer node ID overlap');
  const aliasOwners = new Map(), entityNames = new Set();
  for (const row of aliases) {
    assert(nodeMap.get(row.id)?.type === row.type && ['Person', 'Organization'].includes(row.type), 'Alias has invalid entity target');
    checkProvenance(row);
    assert(nonempty(row.canonical_name) && nonempty(row.source_basis) && Array.isArray(row.aliases), 'Invalid alias record');
    const seen = new Set();
    for (const alias of row.aliases) {
      assert(nonempty(alias), 'Empty entity alias');
      const key = `${row.type}:${alias.normalize('NFKC').toLowerCase()}`;
      assert(!seen.has(key), 'Duplicate entity alias');
      seen.add(key);
      assert(!aliasOwners.has(key) || aliasOwners.get(key) === row.id, 'Entity alias belongs to multiple identities');
      aliasOwners.set(key, row.id);
    }
  }
  for (const row of nodes.filter(r => ['Person', 'Organization'].includes(r.type))) {
    const key = `${row.type}:${row.display_name.normalize('NFKC').toLowerCase()}`;
    assert(!entityNames.has(key), 'Duplicate canonical entity display identity');
    entityNames.add(key);
    assert(aliases.some(a => a.id === row.id), `Missing alias audit record: ${row.id}`);
  }
  for (const row of withheld) {
    assert(row.record_type === 'withheld' && nonempty(row.kind) && nonempty(row.reason), 'Withheld relationship needs exact reason');
    checkProvenance(row);
    if (row.status === PROPOSED) {
      noAllocatedNumber(row);
      assert(candidateIds.includes(row.origin_candidate_id), 'Invalid withheld candidate origin');
    }
  }
  return {canonical_nodes: nodes.length, canonical_entries: entries.length,
    canonical_relationships: relationships.length, proposed_candidates: candidateIds.length,
    proposed_nodes: pnodes.length, proposed_relationships: prels.length,
    withheld: withheld.length, aliases: aliases.length,
    canonical_nodes_by_type: tally(nodes, 'type'), canonical_relationships_by_type: tally(relationships, 'type')};
}

export function validateDirectory(directory = HERE) {
  const manifest = JSON.parse(readFileSync(join(directory, 'projection-manifest.json'), 'utf8'));
  const graph = readGraph(directory);
  const result = validateRecords(graph, manifest);
  for (const [file, expected] of Object.entries(manifest.artifacts_sha256)) {
    assert(!file.includes('/') && !file.includes('..'), 'Invalid artifact manifest path');
    assert(sha(readFileSync(join(directory, file))) === expected, `Artifact digest mismatch: ${file}`);
  }
  const summary = JSON.parse(readFileSync(join(directory, 'graph-summary.json'), 'utf8'));
  assert(summary.canonical.nodes === result.canonical_nodes && summary.canonical.relationships === result.canonical_relationships
    && summary.proposed.nodes === result.proposed_nodes && summary.proposed.relationships === result.proposed_relationships
    && summary.withheld.rows === result.withheld && summary.entity_alias_records === result.aliases, 'Summary count mismatch');
  assert(equal(summary.canonical.nodes_by_type, result.canonical_nodes_by_type)
    && equal(summary.canonical.relationships_by_type, result.canonical_relationships_by_type), 'Summary type count mismatch');
  const pnodes = graph[FILES[2]].filter(r => r.record_type === 'node');
  const prels = graph[FILES[2]].filter(r => r.record_type === 'relationship');
  for (const [section, nodes, rels] of [['canonical', graph[FILES[0]], graph[FILES[1]]], ['proposed', pnodes, prels]]) {
    assert(equal(summary[section].nodes_by_type, tally(nodes, 'type'))
      && equal(summary[section].relationships_by_type, tally(rels, 'type'))
      && equal(summary[section].nodes_by_confidence, tally(nodes, 'confidence'))
      && equal(summary[section].relationships_by_confidence, tally(rels, 'confidence')), 'Summary breakdown mismatch');
  }
  assert(equal(summary.canonical.nodes_by_status, tally(graph[FILES[0]], 'status'))
    && equal(summary.canonical.relationships_by_status, tally(graph[FILES[1]], 'status'))
    && equal(summary.proposed.rows_by_status, tally(graph[FILES[2]], 'status'))
    && equal(summary.withheld.by_kind, tally(graph[FILES[3]], 'kind')), 'Summary status/withheld count mismatch');
  for (const file of ['schema.cypher', 'neo4j-dry-run-import.mjs', 'validate-graph-staging.mjs',
    'validation-report.md', 'PROGRESS.md', 'checkpoint.json', 'coordinator-ledger.json', 'DEPLOYMENT-PLAN.md']) {
    assert(readFileSync(join(directory, file)).length > 0, `Missing/empty deliverable: ${file}`);
  }
  assert(manifest.offline_only === true, 'Manifest must assert offline-only scope');
  // This package must never acquire an execution path that reads credentials or opens a client.
  for (const file of readdirSync(directory).filter(f => /\.(mjs|py)$/.test(f))) {
    const code = readFileSync(join(directory, file), 'utf8');
    const forbidden = [new RegExp('process' + '\\.env'), new RegExp('os' + '\\.environ'),
      /\b(?:fetch|https?\.request|https?\.get)\s*\(/, /(?:import\s+.*from\s*|require\s*\()['"](?:neo4j-driver|pg|@neondatabase\/serverless)/,
      new RegExp('\\b(?:psy' + 'copg|requ' + 'ests|urllib\\.request)\\b')];
    assert(!forbidden.some(p => p.test(code)), `Live credential/network capability found: ${file}`);
  }
  return result;
}

if (process.argv[1] && import.meta.url === pathToFileURL(resolve(process.argv[1])).href) {
  try {
    const args = process.argv.slice(2);
    assert(args.length === 0 || (args.length === 2 && args[0] === '--reproduce'), 'Usage: node validate-graph-staging.mjs [--reproduce /absolute/input-root]');
    const result = validateDirectory();
    if (args.length) {
      const directory = mkdtempSync('/tmp/phase3-reproduce-');
      try {
        const run = spawnSync('python3', ['-B', join(HERE, 'generate-graph-staging.py'), '--input-root', resolve(args[1]), '--output', directory], {encoding: 'utf8'});
        assert(run.status === 0, `Regeneration failed: ${run.stderr}`);
        for (const file of [...FILES, 'graph-summary.json', 'projection-manifest.json']) assert(sha(readFileSync(join(HERE, file))) === sha(readFileSync(join(directory, file))), `Non-deterministic output: ${file}`);
      } finally { rmSync(directory, {recursive: true, force: true}); }
    }
    console.log(JSON.stringify({ok: true, ...result, deterministic_reproduction: args.length > 0}));
  } catch (error) { console.error(`VALIDATION FAILED: ${error.message}`); process.exitCode = 1; }
}

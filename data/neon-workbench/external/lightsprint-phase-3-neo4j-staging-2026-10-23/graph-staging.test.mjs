import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import { spawnSync } from 'node:child_process';
import { HERE, FILES, readGraph, validateRecords, validateDirectory } from './validate-graph-staging.mjs';

const graph = readGraph();
const manifest = JSON.parse(readFileSync(join(HERE, 'projection-manifest.json'), 'utf8'));
function changed(file, predicate, mutate) {
  const rows = [...graph[file]];
  const i = rows.findIndex(predicate);
  assert.ok(i >= 0, 'Fixture target must exist');
  rows[i] = mutate(structuredClone(rows[i]));
  return {...graph, [file]: rows};
}
const node = type => row => row.type === type;
test('all pinned canonical entries and proposed candidates validate independently', () => {
  const result = validateDirectory();
  assert.equal(result.canonical_entries, 7143);
  assert.equal(result.proposed_candidates, 147);
});
test('a Phase 2 candidate cannot appear as a canonical Entry', () => {
  const candidate = graph[FILES[2]].find(node('ProposedCandidate'));
  const leaked = {...candidate, id: 'entry:999999', type: 'Entry', status: 'CANONICAL', entry_number: 999999};
  assert.throws(() => validateRecords({...graph, [FILES[0]]: [...graph[FILES[0]], leaked]}, manifest), /Candidate origin/);
});
test('candidate label cannot be changed to Entry inside review graph', () => {
  assert.throws(() => validateRecords(changed(FILES[2], node('ProposedCandidate'), r => ({...r, type: 'Entry'})), manifest), /Unsupported label/);
});
test('candidate cannot gain a canonical number or approval', () => {
  for (const mutate of [r => ({...r, entry_number: 7203}), r => ({...r, status: 'CANONICAL'})]) {
    assert.throws(() => validateRecords(changed(FILES[2], node('ProposedCandidate'), mutate), manifest), /allocated|status/);
  }
});
test('candidate relationship cannot reach a canonical node', () => {
  assert.throws(() => validateRecords(changed(FILES[2], r => r.record_type === 'relationship', r => ({...r, target: 'entry:1'})), manifest), /canonical identity/);
});
test('duplicate node identities and dangling endpoints fail', () => {
  assert.throws(() => validateRecords({...graph, [FILES[0]]: [...graph[FILES[0]], graph[FILES[0]][0]]}, manifest), /Duplicate/);
  assert.throws(() => validateRecords(changed(FILES[1], () => true, r => ({...r, target: 'missing:node'})), manifest), /Dangling/);
});
test('unsupported labels and inferred relationship types fail', () => {
  assert.throws(() => validateRecords(changed(FILES[0], node('Person'), r => ({...r, type: 'Suspect'})), manifest), /Unsupported label/);
  assert.throws(() => validateRecords(changed(FILES[1], () => true, r => ({...r, type: 'OWNS'})), manifest), /Unsupported relationship/);
});
test('relationships require field-level provenance and a basis', () => {
  assert.throws(() => validateRecords(changed(FILES[1], () => true, r => ({...r, provenance: []})), manifest), /Missing provenance/);
  assert.throws(() => validateRecords(changed(FILES[1], () => true, r => ({...r, basis: ''})), manifest), /Missing basis/);
});
test('source URL cannot use HTTP, credentials, whitespace, or secret query', () => {
  for (const url of ['http://example.org/a', 'https://user:pass@example.org/', 'https://example.org/a b', 'https://example.org/?token=example']) {
    assert.throws(() => validateRecords(changed(FILES[0], node('Source'), r => ({...r, url})), manifest), /URL/);
  }
});
test('duplicate aliases and unknown origin entries fail', () => {
  assert.throws(() => validateRecords(changed(FILES[4], r => r.aliases.length > 0,
    r => ({...r, aliases: [...r.aliases, r.aliases[0]]})), manifest), /Duplicate entity alias/);
  assert.throws(() => validateRecords(changed(FILES[1], () => true, r => ({...r, origin_entry_number: 999999})), manifest), /Invalid origin/);
});
test('canonical record cannot carry proposed status', () => {
  assert.throws(() => validateRecords(changed(FILES[0], node('Entry'), r => ({...r, status: 'PROPOSED_NOT_APPROVED'})), manifest), /Canonical status leakage/);
});
test('dry-run reads files and excludes every proposed record from import', () => {
  const run = spawnSync(process.execPath, [join(HERE, 'neo4j-dry-run-import.mjs')], {encoding: 'utf8'});
  assert.equal(run.status, 0, run.stderr);
  const plan = JSON.parse(run.stdout);
  assert.equal(plan.execution_enabled, false);
  assert.equal(plan.proposed_import_rows, 0);
  assert.equal(plan.ambiguous_import_rows, 0);
});
test('unrecognized import flags fail closed', () => {
  const run = spawnSync(process.execPath, [join(HERE, 'neo4j-dry-run-import.mjs'), '--execute'], {encoding: 'utf8'});
  assert.equal(run.status, 2);
  assert.match(run.stderr, /REFUSED/);
});

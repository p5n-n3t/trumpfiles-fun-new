#!/usr/bin/env python3
"""Regenerate staged files from pinned local read-only inputs. No network dependencies."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sqlite3
import sys

sys.dont_write_bytecode = True
from projection_common import FROZEN, STAGED, PHASE2, node, provenance
import canonical_entities
import canonical_metadata
import entry_relationships
import proposed_projection

HERE = Path(__file__).resolve().parent
EXTERNAL = HERE.parent
BASE_COMMIT = '63b1faecca80c05d0bf525649306a537b19ac7ac'
JSONL_FILES = ['graph-nodes.jsonl', 'graph-relationships.jsonl',
               'proposed-candidate-graph.jsonl', 'ambiguous-relationships.jsonl',
               'entity-aliases.jsonl']


def encoded(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, sort_keys=True, ensure_ascii=False, indent=2) + '\n')


def counts(rows, key):
    return dict(sorted(Counter(r[key] for r in rows).items()))


def generate(input_root, output):
    input_paths = [FROZEN, STAGED, 'project-docs/TODO-uniform-db.md',
                   'project-docs/schema-v2-draft.md']
    before = {p: sha(input_root / p) for p in input_paths}
    candidate_path = EXTERNAL / PHASE2
    candidates = [json.loads(s) for s in candidate_path.read_text().splitlines() if s]
    assert len(candidates) == 147 and len({r['candidate_id'] for r in candidates}) == 147
    connections = [sqlite3.connect((input_root / p).as_uri() + '?mode=ro&immutable=1', uri=True)
                   for p in [FROZEN, STAGED]]
    for c in connections:
        c.row_factory = sqlite3.Row
        c.execute('PRAGMA query_only=ON')
    frozen, staged = connections
    entries = list(frozen.execute('SELECT * FROM trump_entries ORDER BY entry_number'))
    assert len(entries) == 7143
    assert {r['entry_number'] for r in entries} == {r[0] for r in staged.execute('SELECT entry_number FROM trump_entries')}
    nodes = [node('entry:' + str(r['entry_number']), 'Entry', r['title'],
                  [provenance(FROZEN, 'trump_entries', r['entry_number'], 'entry_number', r['entry_number']),
                   provenance(FROZEN, 'trump_entries', r['entry_number'], 'title', r['title'])],
                  'high', entry_number=r['entry_number'], title=r['title'],
                  date_start=r['date_start'], date_end=r['date_end'], synopsis=r['synopsis'],
                  raw_category=r['category'], raw_phase=r['phase']) for r in entries]
    relationships, aliases, ambiguous = [], [], []
    for module in [canonical_entities, canonical_metadata, entry_relationships]:
        part = module.build(frozen, staged)
        nodes.extend(part['nodes'])
        relationships.extend(part['relationships'])
        aliases.extend(part['aliases'])
        ambiguous.extend(part['ambiguous'])
    proposed, pending = proposed_projection.build(candidates)
    ambiguous.extend(pending)
    for c in connections:
        c.close()
    assert before == {p: sha(input_root / p) for p in input_paths}, 'Read-only input changed'
    output.mkdir(parents=True, exist_ok=True)
    arrays = [nodes, relationships, proposed, ambiguous, aliases]
    for filename, rows in zip(JSONL_FILES, arrays):
        rows.sort(key=lambda r: (r['id'], encoded(r)))
        assert len({r['id'] for r in rows}) == len(rows), 'Duplicate id in ' + filename
        (output / filename).write_text(''.join(encoded(r) + '\n' for r in rows))
    degree = Counter()
    for r in relationships:
        degree.update([r['source'], r['target']])
    entity_types = {'Person', 'Organization'}
    top = sorted(({'id': n['id'], 'display_name': n['display_name'], 'type': n['type'],
                   'evidence_backed_relationships': degree[n['id']]}
                  for n in nodes if n['type'] in entity_types),
                 key=lambda n: (-n['evidence_backed_relationships'], n['id']))[:20]
    pnodes = [r for r in proposed if r['record_type'] == 'node']
    prels = [r for r in proposed if r['record_type'] == 'relationship']
    summary = {
        'canonical': {'nodes': len(nodes), 'entries': len(entries), 'relationships': len(relationships),
                      'nodes_by_type': counts(nodes, 'type'), 'relationships_by_type': counts(relationships, 'type'),
                      'nodes_by_confidence': counts(nodes, 'confidence'), 'relationships_by_confidence': counts(relationships, 'confidence'),
                      'nodes_by_status': counts(nodes, 'status'), 'relationships_by_status': counts(relationships, 'status')},
        'proposed': {'candidates': len(candidates), 'nodes': len(pnodes), 'relationships': len(prels), 'rows': len(proposed),
                     'nodes_by_type': counts(pnodes, 'type'), 'relationships_by_type': counts(prels, 'type'),
                     'nodes_by_confidence': counts(pnodes, 'confidence'), 'relationships_by_confidence': counts(prels, 'confidence'),
                     'rows_by_status': counts(proposed, 'status')},
        'withheld': {'rows': len(ambiguous), 'by_kind': counts(ambiguous, 'kind'),
                     'by_confidence': counts(ambiguous, 'confidence')},
        'entity_alias_records': len(aliases), 'top_connected_entities': top,
        'confidence_meaning': 'Confidence in faithful structured projection, not claim truth or editorial approval',
        'limitations': ['Coverage includes all frozen entries and Phase 2 candidates; it does not establish every real-world relationship.',
                       'No text co-occurrence, fuzzy identity merge, inferred role, chronology, kinship, ownership, coordination, causality or wrongdoing.',
                       'Source URLs are parsed offline; availability and claim support were not rechecked.',
                       'Raw category and phase labels are retained without catalogue normalization.',
                       'Other-type entities and pending duplicate decisions are withheld, not silently recast.']}
    write_json(output / 'graph-summary.json', summary)
    manifest = {'base_commit': BASE_COMMIT, 'input_branch': 'codex/langsmith-cloud-inputs-20261022',
                'input_commit': '15dda3e706e11aeb39564e52db9f4d98bc796a1d',
                'input_files_sha256': before, 'repository_inputs_sha256': {PHASE2: sha(candidate_path)},
                'canonical_entry_numbers': sorted(r['entry_number'] for r in entries),
                'proposed_candidate_ids': sorted(r['candidate_id'] for r in candidates),
                'artifacts_sha256': {p: sha(output / p) for p in JSONL_FILES + ['graph-summary.json']},
                'offline_only': True}
    write_json(output / 'projection-manifest.json', manifest)
    print(encoded({'canonical_nodes': len(nodes), 'canonical_relationships': len(relationships),
                   'proposed_candidates': len(candidates), 'proposed_rows': len(proposed), 'withheld': len(ambiguous)}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input-root', required=True, type=Path)
    parser.add_argument('--output', type=Path, default=HERE)
    args = parser.parse_args()
    generate(args.input_root.resolve(), args.output.resolve())

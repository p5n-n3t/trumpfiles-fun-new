"""Review-only, candidate-scoped graph; no canonical identity or entry allocation."""
import json
from projection_common import (PROPOSED, PHASE2, stable_id, provenance,
                               source_url, ambiguity)


def build(candidates):
    nodes, relationships, withheld = [], [], []
    for candidate in candidates:
        cid = candidate['candidate_id']
        root = 'proposed:' + cid
        p = lambda field, value: provenance(PHASE2, 'candidates', cid, field, value)
        common = {'status': PROPOSED, 'origin_candidate_id': cid, 'confidence': 'medium'}
        nodes.append({'record_type': 'node', 'id': root, 'type': 'ProposedCandidate',
                      'display_name': candidate['title'], **common,
                      'provenance': [p(field, candidate[field]) for field in
                                     ['candidate_id', 'title', 'event_date', 'description_short',
                                      'description_medium', 'description_long', 'allegation_or_established',
                                      'uncertainty']] + ([p('_allegation_status_note', candidate['_allegation_status_note'])]
                                                        if '_allegation_status_note' in candidate else []),
                      'event_date': candidate['event_date'],
                      'description_short': candidate['description_short'],
                      'description_medium': candidate['description_medium'],
                      'description_long': candidate['description_long'],
                      'allegation_or_established': candidate['allegation_or_established'],
                      'uncertainty': candidate['uncertainty'],
                      'allegation_status_note': candidate.get('_allegation_status_note'),
                      'approval': 'Human editorial approval has not been granted'})
        local = {}

        def add(type, name, relation, evidence, **properties):
            key = (type, properties.get('url', name))
            if key not in local:
                nid = root + ':' + stable_id(type.lower(), key[1])
                n = {'record_type': 'node', 'id': nid, 'type': type,
                     'display_name': name, **common, 'provenance': [], **properties}
                edge = {'record_type': 'relationship', 'id': stable_id('proposed-rel', [root, nid, relation]),
                        'source': root, 'target': nid, 'type': relation, **common,
                        'basis': 'Explicit Phase 2 structured field; review-only, not an approved assertion',
                        'provenance': []}
                local[key] = n, edge
            n, edge = local[key]
            for item in evidence if isinstance(evidence, list) else [evidence]:
                if item not in n['provenance']:
                    n['provenance'].append(item)
                    edge['provenance'].append(item)

        for field, type in [('people_tags', 'Person'), ('organization_tags', 'Organization')]:
            for name in candidate.get(field, []):
                if isinstance(name, str) and name.strip():
                    add(type, name, 'MENTIONS', p(field, name))
        for field, type, rel in [('category', 'Category', 'IN_CATEGORY'),
                                 ('phase', 'Phase', 'IN_PHASE')]:
            if candidate.get(field):
                add(type, candidate[field], rel, p(field, candidate[field]))
        for name in candidate.get('keywords', []):
            add('Theme', name, 'HAS_THEME', p('keywords', name))
        source_rows = [(f'sources[{i}].url', s.get('url'), s)
                       for i, s in enumerate(candidate.get('sources', []))]
        source_rows += [('source_urls', u, {}) for u in candidate.get('source_urls', [])]
        for field, raw, metadata in source_rows:
            url, reason = source_url(raw)
            if reason:
                withheld.append(ambiguity('invalid_proposed_source', reason, [p(field, raw)],
                                          status=PROPOSED, origin_candidate_id=cid,
                                          raw_value=raw))
            else:
                evidence = [p(field, raw)]
                if metadata:
                    prefix = field.rsplit('.', 1)[0]
                    evidence += [p(prefix + '.' + key, value) for key, value in sorted(metadata.items())]
                add('Source', metadata.get('title') or url, 'SOURCED_FROM', evidence,
                    url=url, publisher=metadata.get('publisher'),
                    date_published=metadata.get('date_published'))
        for n, edge in local.values():
            nodes.append(n)
            relationships.append(edge)
        # Dedup screening references are not approved graph assertions.
        for target in candidate.get('related_entry_numbers', []):
            withheld.append(ambiguity('proposed_to_canonical',
                'Phase 2 related_entry_numbers is a research/dedup reference; no approved cross-layer relationship or event identity decision',
                [p('related_entry_numbers', target)], status=PROPOSED,
                origin_candidate_id=cid, possible_target='entry:' + str(target),
                requested_type='RELATES_TO'))
    return nodes + relationships, withheld

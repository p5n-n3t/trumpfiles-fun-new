"""Deterministic canonical entity projection from frozen and staged SQLite inputs."""
import json
import unicodedata

from projection_common import (CANONICAL, ambiguity, empty_result, node,
                               provenance, relationship)


STAGED_DB = 'graph/schema_v2_graph_staged.sqlite'
FROZEN_DB = 'frozen/trump_local.sqlite'
ENTITY_TYPES = {'person': 'Person', 'org': 'Organization'}


def _row_provenance(database, table, key, row):
    """Return field-level provenance for every field in a source row."""
    return [provenance(database, table, key, field, row[field])
            for field in row.keys()]


def _normalized(value):
    return unicodedata.normalize('NFKC', value).casefold()


def _decoded_aliases(raw, entity_id, issues):
    """Read strings explicitly stored in entities.aliases, reporting bad data."""
    if raw is None or raw == '':
        return []
    try:
        values = json.loads(raw) if isinstance(raw, str) else raw
    except (TypeError, ValueError) as exc:
        issues.append(ambiguity(
            'invalid_entity_aliases', 'entities.aliases is not valid JSON',
            [provenance(STAGED_DB, 'entities', entity_id, 'aliases', raw)],
            entity_id='entity:' + str(entity_id), raw_value=raw,
            detail=str(exc)))
        return []
    if not isinstance(values, list):
        issues.append(ambiguity(
            'invalid_entity_aliases', 'entities.aliases is not a JSON array',
            [provenance(STAGED_DB, 'entities', entity_id, 'aliases', raw)],
            entity_id='entity:' + str(entity_id), raw_value=raw))
        return []
    aliases = []
    for index, value in enumerate(values):
        if isinstance(value, str) and value:
            aliases.append(value)
        else:
            issues.append(ambiguity(
                'invalid_entity_alias', 'Alias value is not a non-empty string',
                [provenance(STAGED_DB, 'entities', entity_id,
                            'aliases[' + str(index) + ']', value)],
                entity_id='entity:' + str(entity_id), raw_value=value))
    return aliases


def build(frozen, staged):
    """Build typed entity nodes and explicit ``mentioned`` relationships.

    Both arguments are read-only SQLite connections with ``sqlite3.Row`` rows.
    Names resolve only by exact equality against canonical names or explicit
    alias fields. NFKC+casefold is used only to detect export conflicts.
    """
    result = empty_result()
    nodes = result['nodes']
    relationships = result['relationships']
    aliases_out = result['aliases']
    ambiguous = result['ambiguous']

    entity_rows = list(staged.execute('SELECT * FROM entities ORDER BY id'))
    entities = {row['id']: row for row in entity_rows}
    names_by_entity = {}
    name_evidence = {}
    alias_rows_by_entity = {}

    for row in entity_rows:
        entity_id = row['id']
        explicit_aliases = _decoded_aliases(row['aliases'], entity_id, ambiguous)
        names_by_entity[entity_id] = set([row['name'], *explicit_aliases])
        row_evidence = _row_provenance(STAGED_DB, 'entities', entity_id, row)
        name_evidence[entity_id] = {
            name: list(row_evidence) for name in names_by_entity[entity_id]
        }

    for row in staged.execute(
            'SELECT * FROM entity_aliases ORDER BY entity_id, alias'):
        entity_id = row['entity_id']
        key = str(entity_id) + '|' + row['alias']
        evidence = _row_provenance(STAGED_DB, 'entity_aliases', key, row)
        if entity_id not in entities:
            ambiguous.append(ambiguity(
                'orphan_entity_alias', 'Alias row references no staged entity',
                evidence, entity_id='entity:' + str(entity_id), alias=row['alias']))
            continue
        if row['canonical_name'] != entities[entity_id]['name']:
            ambiguous.append(ambiguity(
                'entity_alias_canonical_mismatch',
                'entity_aliases.canonical_name differs from the staged entity name; the rows remain separate',
                evidence + [
                    provenance(STAGED_DB, 'entities', entity_id, 'id', entity_id),
                    provenance(STAGED_DB, 'entities', entity_id, 'name', entities[entity_id]['name'])],
                entity_id='entity:' + str(entity_id), alias=row['alias'],
                alias_canonical_name=row['canonical_name'],
                entity_name=entities[entity_id]['name']))
            continue
        alias_rows_by_entity.setdefault(entity_id, []).append(row)
        names_by_entity[entity_id].add(row['alias'])
        name_evidence[entity_id].setdefault(row['alias'], []).extend(evidence)

    normalized_ids = {}
    for entity_id, names in names_by_entity.items():
        for name in names:
            normalized_ids.setdefault(_normalized(name), set()).add(entity_id)

    # Names that normalize to the same value on multiple rows are withheld
    # from alias lists and tag resolution. The corresponding entity IDs stay
    # separate; no identity merge is attempted.
    conflicting_name_norms = {
        norm: ids for norm, ids in normalized_ids.items() if len(ids) > 1
    }
    for norm, ids in sorted(conflicting_name_norms.items()):
        evidence = []
        raw_names = set()
        for entity_id in sorted(ids):
            for name in names_by_entity[entity_id]:
                if _normalized(name) == norm:
                    raw_names.add(name)
                    evidence.extend(name_evidence[entity_id].get(name, []))
        ambiguous.append(ambiguity(
            'normalized_entity_alias_collision',
            'Explicit names normalize to the same NFKC+casefold value across staged entity ids; conflicting aliases are withheld and identities remain separate',
            evidence, normalized_name=norm, raw_names=sorted(raw_names),
            entity_ids=['entity:' + str(entity_id) for entity_id in sorted(ids)]))

    # A same-type canonical display-name collision would fail graph validation.
    # Keep the identity evidence as an ambiguity and withhold those nodes and links.
    display_name_groups = {}
    for row in entity_rows:
        graph_type = ENTITY_TYPES.get(row['entity_type'])
        if graph_type:
            key = (graph_type, _normalized(row['name']))
            display_name_groups.setdefault(key, []).append(row['id'])
    display_conflicted_ids = set()
    for (graph_type, norm), ids in sorted(display_name_groups.items()):
        if len(ids) > 1:
            display_conflicted_ids.update(ids)
            ambiguous.append(ambiguity(
                'duplicate_entity_display_name',
                'Same-type staged entities have duplicate NFKC+casefold display names; nodes and links are withheld rather than merged',
                [value for entity_id in sorted(ids)
                 for value in _row_provenance(
                     STAGED_DB, 'entities', entity_id, entities[entity_id])],
                graph_type=graph_type, normalized_name=norm,
                entity_ids=['entity:' + str(entity_id) for entity_id in sorted(ids)]))

    # Entity aliases from all explicit sources are available for tag lookup,
    # but alias export is limited to identities with a graph node.
    for row in entity_rows:
        entity_id = row['id']
        graph_type = ENTITY_TYPES.get(row['entity_type'])
        if graph_type is None or entity_id in display_conflicted_ids:
            continue
        graph_id = 'entity:' + str(entity_id)
        nodes.append(node(
            graph_id, graph_type, row['name'],
            [provenance(STAGED_DB, 'entities', entity_id, 'id', entity_id),
             provenance(STAGED_DB, 'entities', entity_id, 'name', row['name']),
             provenance(STAGED_DB, 'entities', entity_id, 'entity_type', row['entity_type'])],
            'medium', staged_entity_type=row['entity_type']))

        # Keep at most one string for each normalized alias on this identity.
        # Prefer the exact canonical name, then the lexical first explicit alias.
        names_by_norm = {}
        for name in names_by_entity[entity_id]:
            norm = _normalized(name)
            if norm in conflicting_name_norms:
                continue
            if norm not in names_by_norm or name == row['name']:
                names_by_norm[norm] = name
        aliases = sorted(names_by_norm.values())
        aliases_out.append({
            'id': graph_id,
            'type': graph_type,
            'canonical_name': row['name'],
            'aliases': aliases,
            'source_basis': 'staged entities.name; staged entities.aliases; staged entity_aliases.alias',
            'provenance': _row_provenance(STAGED_DB, 'entities', entity_id, row) + [
                value for alias_row in alias_rows_by_entity.get(entity_id, [])
                for value in _row_provenance(
                    STAGED_DB, 'entity_aliases',
                    str(entity_id) + '|' + alias_row['alias'], alias_row)
            ],
            'confidence': 'medium',
            'status': CANONICAL,
        })

    frozen_entries = {
        row['entry_number']: row
        for row in frozen.execute(
            'SELECT entry_number, people_tags FROM trump_entries ORDER BY entry_number')
    }
    staged_entries = {
        row['entry_number'] for row in staged.execute(
            'SELECT entry_number FROM trump_entries ORDER BY entry_number')
    }

    name_to_entities = {}
    for entity_id, names in names_by_entity.items():
        for name in names:
            if _normalized(name) not in conflicting_name_norms:
                name_to_entities.setdefault(name, set()).add(entity_id)

    # Match every frozen source tag, including tags with no staged identity or
    # no link. This preserves raw tag evidence instead of silently dropping it.
    tag_matches = {}
    for entry_number, row in frozen_entries.items():
        raw_tags = row['people_tags']
        if raw_tags is None or raw_tags == '':
            continue
        try:
            tags = json.loads(raw_tags) if isinstance(raw_tags, str) else raw_tags
        except (TypeError, ValueError) as exc:
            ambiguous.append(ambiguity(
                'invalid_people_tags', 'people_tags is not valid JSON',
                [provenance(FROZEN_DB, 'trump_entries', entry_number,
                            'people_tags', raw_tags)],
                entry_number=entry_number, raw_value=raw_tags, detail=str(exc)))
            continue
        if not isinstance(tags, list):
            ambiguous.append(ambiguity(
                'invalid_people_tags', 'people_tags is not a JSON array',
                [provenance(FROZEN_DB, 'trump_entries', entry_number,
                            'people_tags', raw_tags)],
                entry_number=entry_number, raw_value=raw_tags))
            continue
        for index, tag in enumerate(tags):
            tag_evidence = provenance(
                FROZEN_DB, 'trump_entries', entry_number,
                'people_tags[' + str(index) + ']', tag)
            if not isinstance(tag, str) or not tag:
                ambiguous.append(ambiguity(
                    'invalid_people_tag', 'People tag is not a non-empty string',
                    [tag_evidence], entry_number=entry_number, raw_value=tag))
                continue
            norm = _normalized(tag)
            if norm in conflicting_name_norms:
                ambiguous.append(ambiguity(
                    'ambiguous_people_tag',
                    'Frozen people tag matches names that normalize to a collision across staged entity ids',
                    [tag_evidence], entry_number=entry_number, tag=tag,
                    entity_ids=['entity:' + str(entity_id)
                                for entity_id in sorted(conflicting_name_norms[norm])]))
                continue
            ids = name_to_entities.get(tag, set())
            if not ids:
                ambiguous.append(ambiguity(
                    'unmatched_people_tag',
                    'Frozen people tag has no exact staged canonical name or explicit alias',
                    [tag_evidence], entry_number=entry_number, tag=tag))
                continue
            if len(ids) > 1:
                ambiguous.append(ambiguity(
                    'ambiguous_people_tag',
                    'Frozen people tag maps to multiple staged entity ids; no identity was selected',
                    [tag_evidence], entry_number=entry_number, tag=tag,
                    entity_ids=['entity:' + str(entity_id)
                                for entity_id in sorted(ids)]))
                continue
            entity_id = next(iter(ids))
            tag_matches.setdefault((entry_number, entity_id), []).append(
                (tag, tag_evidence))

    links = list(staged.execute(
        'SELECT * FROM entity_entry_links ORDER BY entry_number, entity_id, id'))
    linked_pairs = set()
    linked_entity_ids = set()
    for link in links:
        entry_number = link['entry_number']
        entity_id = link['entity_id']
        linked_pairs.add((entry_number, entity_id))
        linked_entity_ids.add(entity_id)
        entity = entities.get(entity_id)
        link_evidence = _row_provenance(
            STAGED_DB, 'entity_entry_links', link['id'], link)
        entity_evidence = (_row_provenance(STAGED_DB, 'entities', entity_id, entity)
                           if entity is not None else [
                               provenance(STAGED_DB, 'entity_entry_links', link['id'],
                                          'entity_id', entity_id)])
        matching_tags = tag_matches.get((entry_number, entity_id), [])
        evidence = link_evidence + entity_evidence + [item[1] for item in matching_tags]
        for tag, _ in matching_tags:
            evidence.extend(p for p in name_evidence.get(entity_id, {}).get(tag, [])
                            if p['table'] == 'entity_aliases')
        graph_type = ENTITY_TYPES.get(entity['entity_type']) if entity else None

        if entity is None:
            reason = 'Staged entity link references no staged entity identity'
        elif entity_id in display_conflicted_ids:
            reason = 'Staged entity identity has a duplicate same-type display name and is withheld'
        elif graph_type is None:
            reason = ('Staged entity_type cannot be safely typed as Person or Organization; '
                      'the explicit link is withheld')
        elif link['role'] != 'mentioned':
            reason = 'Staged link role is not the supported explicit role mentioned'
        elif entry_number not in frozen_entries or entry_number not in staged_entries:
            reason = 'Staged entity link references no entry in both input databases'
        else:
            relationships.append(relationship(
                'entry:' + str(entry_number), 'entity:' + str(entity_id), 'MENTIONS',
                entry_number,
                'Explicit staged entity_entry_links role=mentioned; establishes mention only and does not establish wrongdoing or any additional role',
                evidence, 'medium'))
            continue

        ambiguous.append(ambiguity(
            'unsupported_entity_link', reason, evidence,
            link_id=link['id'], entity_id='entity:' + str(entity_id),
            entry_number=entry_number, role=link['role'],
            staged_entity_type=entity['entity_type'] if entity else None,
            matching_people_tags=[item[0] for item in matching_tags]))

    for (entry_number, entity_id), matches in sorted(tag_matches.items()):
        if (entry_number, entity_id) in linked_pairs:
            continue
        evidence = [item[1] for item in matches]
        evidence.extend(name_evidence.get(entity_id, {}).get(matches[0][0], []))
        ambiguous.append(ambiguity(
            'people_tag_without_staged_link',
            'Frozen people tag has a staged identity but no explicit entity_entry_links row for this entry',
            evidence, entry_number=entry_number,
            entity_id='entity:' + str(entity_id),
            people_tags=[item[0] for item in matches]))

    # Unsupported identities without links still need an explicit disposition.
    for entity_id, entity in sorted(entities.items()):
        if ENTITY_TYPES.get(entity['entity_type']) or entity_id in linked_entity_ids:
            continue
        ambiguous.append(ambiguity(
            'unsupported_entity_identity',
            'Staged entity_type cannot be safely typed as Person or Organization; identity is retained only as withheld evidence',
            _row_provenance(STAGED_DB, 'entities', entity_id, entity),
            entity_id='entity:' + str(entity_id),
            staged_entity_type=entity['entity_type'], canonical_name=entity['name']))

    for key in ('nodes', 'relationships', 'aliases', 'ambiguous'):
        result[key].sort(key=lambda item: item['id'])
    return result

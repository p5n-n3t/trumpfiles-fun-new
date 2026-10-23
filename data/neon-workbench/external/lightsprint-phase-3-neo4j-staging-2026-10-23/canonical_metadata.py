"""Deterministic canonical metadata projection from the frozen SQLite inputs."""
import json
from collections import defaultdict

from projection_common import (
    FROZEN,
    ambiguity,
    empty_result,
    node,
    provenance,
    relationship,
    source_url,
    stable_id,
)


_SOURCE_METADATA_FIELDS = (
    'title', 'publisher', 'date_published', 'source_type',
)
_URL_FIELD_NAMES = {'url', 'source_url'}


def _json_key(value):
    """A stable representation for equality, deduplication, and ordering."""
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':'), default=str)


def _unique_provenance(values):
    by_key = {}
    for value in values:
        by_key[_json_key(value)] = value
    return [by_key[key] for key in sorted(by_key)]


def _row_value(row, key, default=None):
    try:
        return row[key]
    except (IndexError, KeyError):
        return default


def _json_value(raw, entry_number, field, result):
    if raw is None or raw == '':
        return None
    if not isinstance(raw, str):
        return raw
    try:
        return json.loads(raw)
    except (TypeError, ValueError) as exc:
        result['ambiguous'].append(ambiguity(
            'metadata_json',
            'Could not parse frozen JSON field: ' + str(exc),
            [provenance(FROZEN, 'trump_entries', entry_number, field, raw)],
            origin_entry_number=entry_number,
        ))
        return None


def _leaf_provenance(value, entry_number, field):
    """Return provenance for every field in one structured source record."""
    found = []

    def visit(item, path):
        if isinstance(item, dict):
            if not item:
                found.append(provenance(FROZEN, 'trump_entries', entry_number, path, item))
                return
            for key in sorted(item, key=lambda part: str(part)):
                visit(item[key], path + '.' + str(key))
        elif isinstance(item, list):
            if not item:
                found.append(provenance(FROZEN, 'trump_entries', entry_number, path, item))
                return
            for index, child in enumerate(item):
                visit(child, path + '[' + str(index) + ']')
        else:
            found.append(provenance(FROZEN, 'trump_entries', entry_number, path, item))

    visit(value, field)
    return found


def _source_candidate(raw_url, url_field, entry_number, all_fields, metadata, sources, result):
    normalized, reason = source_url(raw_url)
    url_origin = provenance(FROZEN, 'trump_entries', entry_number, url_field, raw_url)
    if reason:
        result['ambiguous'].append(ambiguity(
            'source_url', reason, _unique_provenance(list(all_fields) + [url_origin]),
            origin_entry_number=entry_number, origin_field=url_field,
        ))
        return
    record = sources.setdefault(normalized, {
        'provenance': [], 'metadata_candidates': defaultdict(list), 'uses': defaultdict(list),
    })
    record['provenance'].extend(all_fields)
    if url_origin not in all_fields:
        record['provenance'].append(url_origin)
    for field in _SOURCE_METADATA_FIELDS:
        value = metadata.get(field)
        if value is not None and value != '':
            record['metadata_candidates'][field].append((
                1, len(record['metadata_candidates'][field]), value, url_field,
            ))
    record['uses'][entry_number].extend(all_fields)
    if url_origin not in all_fields:
        record['uses'][entry_number].append(url_origin)


def _missing_url_record(record, record_field, entry_number, all_fields, result):
    record_origin = provenance(FROZEN, 'trump_entries', entry_number, record_field, record)
    result['ambiguous'].append(ambiguity(
        'source_url', 'Structured source record has no explicit URL field',
        _unique_provenance(list(all_fields) + [record_origin]),
        origin_entry_number=entry_number, origin_field=record_field,
    ))


def _walk_url_fields(value, path, entry_number, sources, result, reporting_is_source=False):
    """Collect explicit URL fields from one structured source record."""
    found = 0

    def visit(item, current_path):
        nonlocal found
        if isinstance(item, dict):
            record_fields = _leaf_provenance(item, entry_number, current_path)
            for key in sorted(item, key=lambda part: str(part)):
                key_name = str(key)
                child = item[key]
                child_path = current_path + '.' + key_name
                lower_key = key_name.lower()
                if lower_key in _URL_FIELD_NAMES:
                    _source_candidate(child, child_path, entry_number, record_fields,
                                      item if isinstance(item, dict) else {}, sources, result)
                    found += 1
                elif reporting_is_source and lower_key == 'reporting':
                    _source_candidate(child, child_path, entry_number, record_fields,
                                      {}, sources, result)
                    found += 1
                elif isinstance(child, (dict, list)):
                    visit(child, child_path)
        elif isinstance(item, list):
            for index, child in enumerate(item):
                visit(child, current_path + '[' + str(index) + ']')

    visit(value, path)
    return found


def _extract_json_source_field(value, field, entry_number, sources, result):
    """Extract URLs from the three supported frozen entry source fields."""
    if value is None:
        return
    if field == 'entry_links':
        # The reporting value is a source candidate only. It is never an entry edge.
        _walk_url_fields(value, field, entry_number, sources, result, reporting_is_source=True)
        return

    if isinstance(value, list):
        for index, item in enumerate(value):
            item_field = field + '[' + str(index) + ']'
            if isinstance(item, str) or item is None:
                leaf = provenance(FROZEN, 'trump_entries', entry_number, item_field, item)
                _source_candidate(item, item_field, entry_number, [leaf], {}, sources, result)
            elif isinstance(item, dict):
                count = _walk_url_fields(item, item_field, entry_number, sources, result)
                if count == 0:
                    _missing_url_record(item, item_field, entry_number,
                                        _leaf_provenance(item, entry_number, item_field), result)
            elif isinstance(item, list):
                _walk_url_fields(item, item_field, entry_number, sources, result)
            else:
                leaf = provenance(FROZEN, 'trump_entries', entry_number, item_field, item)
                _source_candidate(item, item_field, entry_number, [leaf], {}, sources, result)
        return

    if isinstance(value, dict):
        count = _walk_url_fields(value, field, entry_number, sources, result)
        if count == 0:
            _missing_url_record(value, field, entry_number,
                                _leaf_provenance(value, entry_number, field), result)
        return

    leaf = provenance(FROZEN, 'trump_entries', entry_number, field, value)
    _source_candidate(value, field, entry_number, [leaf], {}, sources, result)


def _table_provenance(row, table, row_key):
    return [
        provenance(FROZEN, table, row_key, key, row[key])
        for key in sorted(row.keys())
    ]


def _add_table_source(row, entry_numbers, sources, result):
    entry_number = _row_value(row, 'entry_number')
    fields = _table_provenance(row, 'trump_sources', _row_value(row, 'source_id'))
    entry_exists = str(entry_number) in entry_numbers
    if not entry_exists:
        result['ambiguous'].append(ambiguity(
            'dangling_source_use',
            'Source row references an entry_number absent from frozen trump_entries',
            fields, origin_entry_number=entry_number,
            endpoint='entry:' + str(entry_number),
        ))
    raw_url = _row_value(row, 'url')
    normalized, reason = source_url(raw_url)
    if reason:
        url_origin = provenance(FROZEN, 'trump_sources', _row_value(row, 'source_id'), 'url', raw_url)
        result['ambiguous'].append(ambiguity(
            'source_url', reason, _unique_provenance(fields + [url_origin]),
            origin_entry_number=entry_number, origin_field='url',
        ))
        return
    record = sources.setdefault(normalized, {
        'provenance': [], 'metadata_candidates': defaultdict(list), 'uses': defaultdict(list),
    })
    record['provenance'].extend(fields)
    if entry_exists:
        record['uses'][entry_number].extend(fields)
    else:
        record['dangling_use_count'] = record.get('dangling_use_count', 0) + 1
    for field in _SOURCE_METADATA_FIELDS:
        value = _row_value(row, field)
        if value is not None and value != '':
            record['metadata_candidates'][field].append((
                0, len(record['metadata_candidates'][field]), value,
                'trump_sources.' + field,
            ))


def _add_theme(theme_value, entry_number, field, themes, result):
    if not isinstance(theme_value, str) or theme_value == '':
        result['ambiguous'].append(ambiguity(
            'theme_value', 'Theme value is not a non-empty string',
            [provenance(FROZEN, 'trump_entries', entry_number, field, theme_value)],
            origin_entry_number=entry_number,
        ))
        return
    record = themes.setdefault(theme_value, {'provenance': [], 'uses': defaultdict(list)})
    item = provenance(FROZEN, 'trump_entries', entry_number, field, theme_value)
    record['provenance'].append(item)
    record['uses'][entry_number].append(item)


def _metadata_choice(candidates, field, notes):
    if not candidates:
        return None
    ordered = sorted(candidates, key=lambda item: (item[0], item[1], item[3]))
    chosen = ordered[0][2]
    chosen_key = _json_key(chosen)
    seen = {chosen_key}
    for _, _, other, origin in ordered[1:]:
        other_key = _json_key(other)
        if other_key in seen:
            continue
        seen.add(other_key)
        notes.append('Conflicting ' + field + ' metadata; kept ' + repr(chosen) +
                     ', also saw ' + repr(other) + ' at ' + origin)
    return chosen


def _facet_value(entry, entry_number, field, facet_type, facets, result):
    raw = _row_value(entry, field)
    item = provenance(FROZEN, 'trump_entries', entry_number, field, raw)
    if raw is None or raw == '':
        result['ambiguous'].append(ambiguity(
            'missing_facet', 'Entry has no raw ' + field + ' value in frozen trump_entries',
            [item], origin_entry_number=entry_number, facet=facet_type,
        ))
        return
    if not isinstance(raw, str):
        result['ambiguous'].append(ambiguity(
            'invalid_facet', 'Raw ' + field + ' value is not a string',
            [item], origin_entry_number=entry_number, facet=facet_type,
        ))
        return
    key = (facet_type, raw)
    record = facets.setdefault(key, {'provenance': [], 'uses': defaultdict(list)})
    record['provenance'].append(item)
    record['uses'][entry_number].append(item)


def build(frozen, staged):
    """Build canonical source, theme, category, and phase records.

    `frozen` and `staged` are caller-owned sqlite3 connections configured with
    sqlite3.Row. This projection reads `frozen` only; `staged` is accepted to
    match the coordinator interface and is intentionally not used as a source
    of raw catalogue values.
    """
    del staged
    result = empty_result()
    sources = {}
    themes = {}
    facets = {}
    theme_edges = defaultdict(list)
    facet_edges = defaultdict(list)

    entries = frozen.execute('SELECT * FROM trump_entries ORDER BY entry_number').fetchall()
    entry_numbers = {str(_row_value(entry, 'entry_number')) for entry in entries}
    for row in frozen.execute('SELECT * FROM trump_sources ORDER BY source_id'):
        _add_table_source(row, entry_numbers, sources, result)

    for entry in entries:
        entry_number = _row_value(entry, 'entry_number')
        entry_key = 'entry:' + str(entry_number)

        for field in ('sources', 'fact_check_sources', 'entry_links'):
            parsed = _json_value(_row_value(entry, field), entry_number, field, result)
            if parsed is not None:
                _extract_json_source_field(parsed, field, entry_number, sources, result)

        raw_keywords = _json_value(_row_value(entry, 'keywords'), entry_number, 'keywords', result)
        if raw_keywords is not None:
            if isinstance(raw_keywords, list):
                for index, item in enumerate(raw_keywords):
                    if isinstance(item, list):
                        for nested_index, nested in enumerate(item):
                            _add_theme(nested, entry_number,
                                       'keywords[' + str(index) + '][' + str(nested_index) + ']',
                                       themes, result)
                    else:
                        _add_theme(item, entry_number, 'keywords[' + str(index) + ']', themes, result)
            else:
                result['ambiguous'].append(ambiguity(
                    'theme_value', 'Entry keywords JSON is not a list',
                    [provenance(FROZEN, 'trump_entries', entry_number, 'keywords',
                                _row_value(entry, 'keywords'))],
                    origin_entry_number=entry_number,
                ))

        _facet_value(entry, entry_number, 'category', 'Category', facets, result)
        _facet_value(entry, entry_number, 'phase', 'Phase', facets, result)

    columns = {row['name'] for row in frozen.execute('PRAGMA table_info(trump_keywords)')}
    if {'entry_number', 'keyword'}.issubset(columns):
        order = 'keyword_id' if 'keyword_id' in columns else 'entry_number, keyword'
        for row in frozen.execute('SELECT * FROM trump_keywords ORDER BY ' + order):
            entry_number = _row_value(row, 'entry_number')
            keyword = _row_value(row, 'keyword')
            if str(entry_number) not in entry_numbers:
                result['ambiguous'].append(ambiguity(
                    'dangling_theme_use',
                    'Keyword row references an entry_number absent from frozen trump_entries',
                    _table_provenance(row, 'trump_keywords', _row_value(row, 'keyword_id')),
                    origin_entry_number=entry_number,
                    endpoint='entry:' + str(entry_number),
                ))
                continue
            if not isinstance(keyword, str) or keyword == '':
                result['ambiguous'].append(ambiguity(
                    'theme_value', 'Theme value is not a non-empty string',
                    _table_provenance(row, 'trump_keywords', _row_value(row, 'keyword_id')),
                    origin_entry_number=entry_number,
                ))
                continue
            record = themes.setdefault(keyword, {'provenance': [], 'uses': defaultdict(list)})
            item = provenance(FROZEN, 'trump_keywords', _row_value(row, 'keyword_id'),
                              'keyword', keyword)
            record['provenance'].append(item)
            record['uses'][entry_number].append(item)

    for normalized_url in sorted(sources):
        record = sources[normalized_url]
        notes = []
        properties = {'url': normalized_url}
        for field in _SOURCE_METADATA_FIELDS:
            value = _metadata_choice(record['metadata_candidates'].get(field, []), field, notes)
            if value is not None:
                properties[field] = value
        display_name = properties.get('title') or properties.get('publisher')
        if not display_name:
            from urllib.parse import urlsplit
            display_name = urlsplit(normalized_url).hostname or normalized_url
        source_id = stable_id('source', normalized_url)
        if record.get('dangling_use_count'):
            notes.append(str(record['dangling_use_count']) +
                         ' source row use(s) were withheld because the entry endpoint is missing')
        if not record['uses']:
            notes.append('No valid frozen entry uses remain for this source node')
        result['nodes'].append(node(
            source_id, 'Source', display_name,
            _unique_provenance(record['provenance']), confidence='medium',
            **properties, **({'notes': sorted(set(notes))} if notes else {}),
        ))
        for entry_number, edge_provenance in sorted(record['uses'].items(), key=lambda item: str(item[0])):
            result['relationships'].append(relationship(
                'entry:' + str(entry_number), source_id, 'SOURCED_FROM', entry_number,
                'explicit_valid_https_url', _unique_provenance(edge_provenance), confidence='medium',
            ))

    for theme in sorted(themes):
        record = themes[theme]
        theme_id = stable_id('theme', theme)
        result['nodes'].append(node(
            theme_id, 'Theme', theme, _unique_provenance(record['provenance']),
            confidence='medium', keyword=theme,
        ))
        for entry_number, edge_provenance in sorted(record['uses'].items(), key=lambda item: str(item[0])):
            theme_edges[('entry:' + str(entry_number), theme_id, entry_number)].extend(edge_provenance)

    for (facet_type, raw_value), record in sorted(facets.items()):
        facet_id = stable_id(facet_type.lower(), raw_value)
        result['nodes'].append(node(
            facet_id, facet_type, raw_value, _unique_provenance(record['provenance']),
            confidence='high', value=raw_value,
        ))
        for entry_number, edge_provenance in sorted(record['uses'].items(), key=lambda item: str(item[0])):
            facet_edges[(facet_type, 'entry:' + str(entry_number), facet_id, entry_number)].extend(edge_provenance)

    for (entry_id, theme_id, entry_number), edge_provenance in sorted(theme_edges.items()):
        result['relationships'].append(relationship(
            entry_id, theme_id, 'HAS_THEME', entry_number,
            'exact_keyword_string', _unique_provenance(edge_provenance), confidence='medium',
        ))
    for (facet_type, entry_id, facet_id, entry_number), edge_provenance in sorted(facet_edges.items()):
        relation_type = 'IN_CATEGORY' if facet_type == 'Category' else 'IN_PHASE'
        result['relationships'].append(relationship(
            entry_id, facet_id, relation_type, entry_number,
            'exact_raw_entry_field', _unique_provenance(edge_provenance), confidence='high',
        ))

    result['nodes'].sort(key=lambda item: item['id'])
    result['relationships'].sort(key=lambda item: item['id'])
    result['ambiguous'].sort(key=lambda item: item['id'])
    return result

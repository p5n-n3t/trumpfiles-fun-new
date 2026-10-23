"""Conservative, offline projection of entry-to-entry relationship candidates."""

try:
    from .projection_common import ambiguity, empty_result, parse_json, provenance
except ImportError:  # Loaded as a standalone projection module from its directory.
    import importlib.util
    from pathlib import Path

    _common_spec = importlib.util.spec_from_file_location(
        '_phase3_projection_common', Path(__file__).with_name('projection_common.py'))
    _common = importlib.util.module_from_spec(_common_spec)
    _common_spec.loader.exec_module(_common)
    ambiguity = _common.ambiguity
    empty_result = _common.empty_result
    parse_json = _common.parse_json
    provenance = _common.provenance


_FROZEN = 'frozen/trump_local.sqlite'
_STAGED = 'graph/schema_v2_graph_staged.sqlite'
_ALLOWED_TYPES = {'SAME_AS', 'RELATES_TO', 'PRECEDES'}


def _tables(connection):
    return {row['name'] for row in connection.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table'")}


def _rows(connection, table):
    """Read a known table without changing either input connection."""
    return [dict(row) for row in connection.execute(f'SELECT * FROM {table}')]


def _entry_id(value):
    """Return the canonical graph id for an integer-like entry number."""
    try:
        number = int(value)
    except (TypeError, ValueError):
        return None
    return f'entry:{number}'


def _link_ambiguity(*, reason, origin, target, raw_note, raw_type,
                    source_url, fields, provenance_rows, json_candidate=None,
                    table='trump_entry_links', row_id=None):
    return ambiguity(
        'entry_relationship', reason, provenance_rows,
        origin_entry_number=origin,
        target_entry_number=target,
        source=_entry_id(origin),
        target=_entry_id(target),
        table=table,
        row_id=row_id,
        candidate_relation_type=raw_type,
        raw_note=raw_note,
        source_url=source_url,
        fields=fields,
        json_candidate=json_candidate,
    )


def _relationship_reason(raw_type, raw_note, source_url, origin, target,
                         json_candidate=None):
    reasons = []
    if json_candidate is not None:
        # Table rows pass a wrapper with normalized table fields plus the raw
        # JSON object; JSON-only candidates pass that object directly.
        json_value = json_candidate.get('candidate', json_candidate)
        json_type = json_candidate.get('type') or json_value.get('relation_type')
        if not raw_type:
            raw_type = json_type
    normalized_type = str(raw_type or '').strip().upper()
    if normalized_type not in _ALLOWED_TYPES:
        reasons.append(
            f"relation type {raw_type!r} is not one of the allowed types "
            'SAME_AS, RELATES_TO, or PRECEDES')
    if origin is not None and target is not None and str(origin) == str(target):
        reasons.append('the candidate is a self-link')
    note_text = str(raw_note or '').strip()
    note_lower = note_text.lower()
    if note_lower.startswith('both '):
        claim_gap = (
            'the note asserts a shared pattern or theme but does not identify '
            'a specific shared event or record that connects these two entries')
    elif any(term in note_lower for term in
             ('escalat', 'expansion', 'culmination', 'implementation')):
        claim_gap = (
            'the note asserts an escalation, expansion, implementation, or '
            'culmination path but does not give dated or record-based evidence '
            'that establishes that path between these entries')
    elif any(term in note_lower for term in
             ('implements', 'through', 'achieving', 'enabling', 'began with')):
        claim_gap = (
            'the note asserts a causal or implementation link but does not cite '
            'evidence that establishes that connection between these entries')
    else:
        claim_gap = (
            'the note states an interpretation but does not identify an '
            'objective event or record that establishes the connection')
    reasons.append(claim_gap)
    if not source_url:
        reasons.append('source_url is empty, so the asserted connection has no citation here')
    return '; '.join(reasons) + '.'


def _json_candidates(staged):
    """Yield only explicit JSON entry-to-entry claims, never URL references."""
    if 'trump_entries' not in _tables(staged):
        return
    columns = {row['name'] for row in staged.execute(
        'PRAGMA table_info(trump_entries)')}
    if not {'entry_number', 'entry_links'} <= columns:
        return
    for row in staged.execute(
            'SELECT entry_number, entry_links FROM trump_entries '
            'WHERE entry_links IS NOT NULL AND entry_links != ?', ('',)):
        raw = row['entry_links']
        try:
            links = parse_json(raw, default=[])
        except (TypeError, ValueError):
            continue
        if not isinstance(links, list):
            continue
        for index, candidate in enumerate(links):
            if not isinstance(candidate, dict):
                continue
            # A URL/source item without an explicit target is not a graph edge.
            if candidate.get('to_entry_number') is None:
                continue
            yield {
                'origin': row['entry_number'],
                'target': candidate.get('to_entry_number'),
                'type': candidate.get('relation_type'),
                'note': candidate.get('note'),
                'source_url': candidate.get('source_url'),
                'candidate': candidate,
                'index': index,
                'raw': raw,
            }


def build(frozen, staged):
    """Project reviewed entry relationships while retaining rejected claims.

    Inputs are read-only SQLite connections whose rows are ``sqlite3.Row``.
    Staged narrative claims and duplicate-merge proposals are kept in the
    ambiguity stream until their evidence and review state support a graph edge.
    """
    result = empty_result()
    frozen_tables = _tables(frozen)
    staged_tables = _tables(staged)

    # The frozen snapshot is the authoritative baseline. Its link table is
    # currently empty; do not treat staged editorial additions as frozen facts.
    frozen_link_count = (frozen.execute(
        'SELECT count(*) FROM trump_entry_links').fetchone()[0]
        if 'trump_entry_links' in frozen_tables else 0)
    if frozen_link_count:
        raise ValueError(
            'Frozen trump_entry_links contains rows; refusing to silently omit '
            'or promote frozen relationship candidates without an explicit review.')

    json_by_key = {}
    for candidate in _json_candidates(staged) or ():
        key = (str(candidate['origin']), str(candidate['target']),
               str(candidate['note'] or ''))
        json_by_key.setdefault(key, []).append(candidate)

    consumed_json = set()
    if 'trump_entry_links' in staged_tables:
        for row in _rows(staged, 'trump_entry_links'):
            origin = row.get('entry_number')
            target = row.get('to_entry_number')
            raw_type = row.get('relation_type')
            note = row.get('note')
            source_url = row.get('source_url')
            key = (str(origin), str(target), str(note or ''))
            matching = json_by_key.get(key, [])
            json_candidate = matching.pop(0) if matching else None
            if json_candidate is not None:
                consumed_json.add((str(json_candidate['origin']),
                                   str(json_candidate['target']),
                                   str(json_candidate['note'] or ''),
                                   json_candidate['index']))

            row_key = row.get('link_id')
            provenance_rows = [
                provenance(_STAGED, 'trump_entry_links', row_key, field,
                           row.get(field))
                for field in ('link_id', 'entry_number', 'to_entry_number',
                              'relation_type', 'note', 'source_url')
            ]
            if json_candidate is not None:
                provenance_rows.append(provenance(
                    _STAGED, 'trump_entries', json_candidate['origin'],
                    'entry_links', json_candidate['raw']))

            reason = _relationship_reason(
                raw_type, note, source_url, origin, target, json_candidate)
            result['ambiguous'].append(_link_ambiguity(
                reason=reason,
                origin=origin,
                target=target,
                raw_note=note,
                raw_type=raw_type,
                source_url=source_url,
                fields=row,
                provenance_rows=provenance_rows,
                json_candidate=(json_candidate['candidate']
                                if json_candidate is not None else None),
                row_id=row_key,
            ))

    # JSON can contain explicit relation objects not present in the dedicated
    # relation table. Preserve each such claim once; ignore ordinary source URLs.
    for key, candidates in json_by_key.items():
        for candidate in candidates:
            consumed_key = (str(candidate['origin']), str(candidate['target']),
                            str(candidate['note'] or ''), candidate['index'])
            if consumed_key in consumed_json:
                continue
            result['ambiguous'].append(_link_ambiguity(
                reason=_relationship_reason(
                    candidate['type'], candidate['note'],
                    candidate['source_url'], candidate['origin'],
                    candidate['target'], candidate['candidate']),
                origin=candidate['origin'],
                target=candidate['target'],
                raw_note=candidate['note'],
                raw_type=candidate['type'],
                source_url=candidate['source_url'],
                fields={
                    'entry_number': candidate['origin'],
                    'to_entry_number': candidate['target'],
                    'relation_type': candidate['type'],
                    'note': candidate['note'],
                    'source_url': candidate['source_url'],
                },
                provenance_rows=[provenance(
                    _STAGED, 'trump_entries', candidate['origin'],
                    'entry_links', candidate['raw'])],
                json_candidate=candidate['candidate'],
                table='trump_entries.entry_links',
                row_id=f"{candidate['origin']}:{candidate['index']}",
            ))

    # Soft-hidden duplicates remain proposals. pending_review requires content
    # and/or source reconciliation, so it is not yet evidence for SAME_AS.
    if 'workbench_soft_hide_staging_v2' in staged_tables:
        for row in _rows(staged, 'workbench_soft_hide_staging_v2'):
            if row.get('state') != 'pending_review':
                continue
            origin = row.get('entry_number')
            target = row.get('canonical_entry_number')
            reason = (
                'the duplicate merge is pending_review; its staged soft-hide '
                'record still requires review and any indicated content/source '
                'merge, so it does not establish a canonical SAME_AS edge')
            provenance_rows = [
                provenance(_STAGED, 'workbench_soft_hide_staging_v2', origin,
                           field, row.get(field))
                for field in ('entry_number', 'canonical_entry_number',
                              'reason', 'decision_source',
                              'requires_content_merge', 'requires_source_union',
                              'state', 'staged_at')
            ]
            result['ambiguous'].append(_link_ambiguity(
                reason=reason,
                origin=origin,
                target=target,
                raw_note=row.get('reason'),
                raw_type='SAME_AS',
                source_url=None,
                fields=row,
                provenance_rows=provenance_rows,
                table='workbench_soft_hide_staging_v2',
                row_id=origin,
            ))

    return result

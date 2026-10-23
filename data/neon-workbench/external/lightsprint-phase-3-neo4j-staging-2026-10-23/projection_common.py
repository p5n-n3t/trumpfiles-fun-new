"""Offline projection primitives. No environment, network, or database writes."""
import hashlib
import json
from urllib.parse import urlsplit, urlunsplit, parse_qsl

CANONICAL = 'CANONICAL'
PROPOSED = 'PROPOSED_NOT_APPROVED'
FROZEN = 'frozen/trump_local.sqlite'
STAGED = 'graph/schema_v2_graph_staged.sqlite'
PHASE2 = 'lightsprint-phase-2-fresh-events-2026-10-23/fresh-event-candidates/all-fresh-candidates-master.jsonl'

def stable_id(kind, value):
    return kind + ':' + hashlib.sha256(str(value).encode()).hexdigest()[:24]

def parse_json(value, default=None):
    if value is None or value == '':
        return [] if default is None else default
    if not isinstance(value, str):
        return value
    return json.loads(value)

def provenance(database, table, key, field, value):
    return {'input': database, 'table': table, 'row_key': key,
            'field': field, 'value': value}

def node(id, type, display_name, provenance, confidence='medium', **properties):
    return {'record_type': 'node', 'id': id, 'type': type,
            'display_name': display_name, 'status': CANONICAL,
            'confidence': confidence, 'provenance': provenance, **properties}

def relationship(source, target, type, origin_entry_number, basis, provenance,
                 confidence='medium'):
    return {'record_type': 'relationship',
            'id': stable_id('rel', json.dumps([source, target, type, origin_entry_number], ensure_ascii=False)),
            'source': source, 'target': target, 'type': type, 'status': CANONICAL,
            'origin_entry_number': origin_entry_number,
            'basis': basis, 'provenance': provenance, 'confidence': confidence}

def ambiguity(kind, reason, provenance, **properties):
    row = {'record_type': 'withheld', 'kind': kind, 'reason': reason,
           'confidence': 'low', 'provenance': provenance, **properties}
    row['id'] = stable_id('withheld', json.dumps(row, sort_keys=True, ensure_ascii=False))
    return row

def source_url(raw):
    """Only explicit HTTPS URLs. Do not invent a scheme or upgrade HTTP."""
    if not isinstance(raw, str):
        return None, 'Source value is not a URL string'
    try:
        u = urlsplit(raw)
        if u.scheme != 'https' or not u.hostname or '.' not in u.hostname:
            return None, 'Source is not an explicit absolute HTTPS URL'
        if u.username or u.password or any(ch.isspace() for ch in raw) or '\\' in raw:
            return None, 'Source URL contains credentials, whitespace, or backslashes'
        u.port
        secret_keys = {'token', 'key', 'api_key', 'apikey', 'secret', 'password', 'access_token', 'signature', 'sig'}
        if any(k.lower() in secret_keys or k.lower().startswith('x-amz-') for k, _ in parse_qsl(u.query)):
            return None, 'Source URL contains a secret-like query parameter'
        return urlunsplit((u.scheme, u.netloc.lower(), u.path or '/', u.query, u.fragment)), None
    except ValueError:
        return None, 'Source URL cannot be parsed'

def empty_result():
    return {'nodes': [], 'relationships': [], 'aliases': [], 'ambiguous': []}

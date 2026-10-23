"""Offline edge-case tests using only in-memory SQLite fixtures."""
import json
import sqlite3
import unittest

import canonical_entities
from projection_common import source_url


class ProjectionRules(unittest.TestCase):
    def setUp(self):
        self.frozen = sqlite3.connect(':memory:')
        self.staged = sqlite3.connect(':memory:')
        for connection in [self.frozen, self.staged]:
            connection.row_factory = sqlite3.Row
            connection.execute('CREATE TABLE trump_entries(entry_number INTEGER PRIMARY KEY, people_tags TEXT)')
            connection.execute('INSERT INTO trump_entries VALUES(1, ?)', (json.dumps(['Bob']),))
        self.staged.executescript('''
            CREATE TABLE entities(id TEXT, name TEXT, entity_type TEXT, aliases TEXT);
            CREATE TABLE entity_aliases(entity_id TEXT, alias TEXT, canonical_name TEXT, source TEXT);
            CREATE TABLE entity_entry_links(id TEXT, entity_id TEXT, entry_number INTEGER, role TEXT);
            INSERT INTO entities VALUES('x', 'Alice', 'person', '[]');
            INSERT INTO entity_entry_links VALUES('link-1', 'x', 1, 'mentioned');
        ''')

    def tearDown(self):
        self.frozen.close()
        self.staged.close()

    def test_mismatching_alias_is_withheld_before_identity_lookup(self):
        self.staged.execute("INSERT INTO entity_aliases VALUES('x','Bob','Wrong identity','fixture')")
        result = canonical_entities.build(self.frozen, self.staged)
        self.assertNotIn('Bob', result['aliases'][0]['aliases'])
        self.assertIn('entity_alias_canonical_mismatch', {r['kind'] for r in result['ambiguous']})
        self.assertIn('unmatched_people_tag', {r['kind'] for r in result['ambiguous']})
        self.assertFalse(any(p['table'] == 'entity_aliases' for r in result['relationships'] for p in r['provenance']))

    def test_matching_alias_evidence_reaches_the_relationship(self):
        self.staged.execute("INSERT INTO entity_aliases VALUES('x','Bob','Alice','fixture')")
        result = canonical_entities.build(self.frozen, self.staged)
        self.assertIn('Bob', result['aliases'][0]['aliases'])
        edge = result['relationships'][0]
        self.assertEqual(edge['type'], 'MENTIONS')
        self.assertTrue(any(p['table'] == 'entity_aliases' and p['field'] == 'alias' and p['value'] == 'Bob' for p in edge['provenance']))

    def test_unsupported_entity_type_cannot_become_a_person(self):
        self.staged.execute("UPDATE entities SET entity_type='other'")
        result = canonical_entities.build(self.frozen, self.staged)
        self.assertEqual(result['nodes'], [])
        self.assertEqual(result['relationships'], [])
        self.assertEqual(result['aliases'], [])
        self.assertIn('unsupported_entity_link', {r['kind'] for r in result['ambiguous']})

    def test_source_urls_are_not_upgraded_or_given_an_invented_scheme(self):
        for value in ['www.example.org/page', 'http://example.org/page', 'https://user:pass@example.org/', 'https://example.org/?token=example']:
            self.assertIsNone(source_url(value)[0])
        self.assertEqual(source_url('https://EXAMPLE.org/page')[0], 'https://example.org/page')


if __name__ == '__main__':
    unittest.main()

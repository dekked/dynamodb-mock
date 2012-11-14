# -*- coding: utf-8 -*-

import unittest, mock
import sqlite3, cPickle as pickle
from ddbmock import config

config.STORAGE_SQLITE_FILE = ':memory:'
TABLE_NAME = 'test_table'

ITEM1 = {"key":"value 1"}
ITEM2 = {"key":"value 2"}
ITEM3 = {"key":"value 3"}
ITEM4 = {"key":"value 4"}

ITEM5 = {"key":"value 5"}
ITEM6 = {"key":"value 6"}

class TestSQLiteStore(unittest.TestCase):
    def setUp(self):
        from ddbmock.database.storage.sqlite import conn

        conn.execute('DROP TABLE IF EXISTS `test_table`')
        conn.execute('''CREATE TABLE `test_table` (
          `hash_key` blob NOT NULL,
          `range_key` blob NOT NULL,
          `data` blob NOT NULL,
          PRIMARY KEY (`hash_key`,`range_key`)
        );''')

        conn.executemany('''INSERT INTO `test_table` VALUES (?, ?, ?)''',
                         [
                            (123, 'toto', buffer(pickle.dumps(ITEM1, 2))),
                            (123, 'titi', buffer(pickle.dumps(ITEM2, 2))),
                            (123, 'tata', buffer(pickle.dumps(ITEM3, 2))),
                            (456, 'toto', buffer(pickle.dumps(ITEM4, 2))),
                         ])

        conn.commit()

        self.conn = conn

    def tearDown(self):
        self.conn.execute('DROP TABLE `test_table`')
        self.conn.commit()

    def test_truncate(self):
        from ddbmock.database.storage.sqlite import Store

        store = Store(TABLE_NAME)
        store.truncate()

        count = self.conn.execute('SELECT Count(*) FROM test_table').fetchone()
        self.assertEqual(0, count[0])

    def test_iter(self):
        from ddbmock.database.storage.sqlite import Store

        store = Store(TABLE_NAME)
        self.assertEqual([ITEM1, ITEM2, ITEM3, ITEM4], list(store))

    def test_get_item(self):
        from ddbmock.database.storage.sqlite import Store

        store = Store(TABLE_NAME)
        self.assertEqual(ITEM2, store[(123, 'titi')])
        self.assertEqual(ITEM4, store[(456, 'toto')])

        self.assertEqual({
                            'toto': ITEM1,
                            'titi': ITEM2,
                            'tata': ITEM3,
                         }, store[(123, None)])

        self.assertRaises(KeyError, store.__getitem__, (404, None))
        self.assertRaises(KeyError, store.__getitem__, (132, '404'))

    def test_del_item(self):
        from ddbmock.database.storage.sqlite import Store

        store = Store(TABLE_NAME)
        del store[123, 'toto']
        del store[123, 'titi']
        del store[404, 'titi']
        del store[456, 'toto']

        # it's not real unit test: I use __iter__ to check
        self.assertEqual([ITEM3], list(store))

    def test_set_item(self):
        from ddbmock.database.storage.sqlite import Store

        store = Store(TABLE_NAME)

        store[123, 'titi'] = ITEM5
        store[456, 'titi'] = ITEM6

        # it's not real unit test: I use __iter__ to check
        self.assertEqual([ITEM1, ITEM3, ITEM4, ITEM5, ITEM6], list(store))

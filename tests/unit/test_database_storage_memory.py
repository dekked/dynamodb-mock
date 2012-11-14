# -*- coding: utf-8 -*-

import unittest, mock

NAME = "TableName"
HASH = "hash_key"
HASH_404 = "hash_key 404"
RANGE1 = "range_key 1"
RANGE2 = "range_key 2"
RANGE_404 = "range_key 404"
DATA1 = {"key": "value 1"}
DATA2 = {"key": "value 2"}

class TestMemoryStore(unittest.TestCase):
    def test_truncate(self):
        from ddbmock.database.storage.memory import Store

        ms = Store(NAME)

        ms.data[1] = "some data"
        ms.data[2] = "some data"
        ms.data[3] = "some data"
        ms.data[4] = "some data"
        ms.data[5] = "some data"

        ms.truncate()

        self.assertFalse(ms.data)

    def test_set_item(self):
        from ddbmock.database.storage.memory import Store

        ms = Store(NAME)

        ms[HASH,RANGE1] = DATA1
        self.assertEqual(DATA1, ms.data[HASH][RANGE1])

    def test_get_item(self):
        from ddbmock.database.storage.memory import Store

        ms = Store(NAME)

        ms.data[HASH][RANGE1] = DATA1
        ms.data[HASH][RANGE2] = DATA2

        self.assertRaises(KeyError, ms.__getitem__, (HASH_404, None))
        self.assertRaises(KeyError, ms.__getitem__, (HASH_404, RANGE1))
        self.assertRaises(KeyError, ms.__getitem__, (HASH_404, RANGE1))
        self.assertRaises(KeyError, ms.__getitem__, (HASH, RANGE_404))

        self.assertEqual(DATA1, ms[HASH, RANGE1])
        self.assertEqual(DATA2, ms[HASH, RANGE2])
        self.assertEqual({RANGE1:DATA1, RANGE2:DATA2}, ms[HASH, None])

    def test_del_item(self):
        from ddbmock.database.storage.memory import Store

        ms = Store(NAME)

        ms.data[HASH][RANGE1] = DATA1
        ms.data[HASH][RANGE2] = DATA2

        self.assertRaises(KeyError, ms.__delitem__, (HASH_404, None))
        self.assertRaises(KeyError, ms.__delitem__, (HASH_404, RANGE1))
        self.assertRaises(KeyError, ms.__delitem__, (HASH_404, RANGE1))
        self.assertRaises(KeyError, ms.__delitem__, (HASH, RANGE_404))

        del ms[HASH, RANGE1]
        del ms[HASH, RANGE2]
        self.assertNotIn(RANGE1, ms.data[HASH])
        self.assertNotIn(RANGE2, ms.data[HASH])

    def test_iter(self):
        from ddbmock.database.storage.memory import Store

        ms = Store(NAME)

        ms.data[HASH][RANGE1] = DATA1
        ms.data[HASH][RANGE2] = DATA2

        self.assertEqual([DATA1, DATA2], list(ms))

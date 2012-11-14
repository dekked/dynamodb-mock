# -*- coding: utf-8 -*-

import unittest


class TestItemFieldComparison(unittest.TestCase):
    def test_eq(self):
        from ddbmock.database.comparison import eq

        self.assertTrue(eq({u'S': u'waldo'}, {u'S': u'waldo'}))
        self.assertFalse(eq({u'S': u'waldo'}, {u'S': u'on-time'}))
        self.assertFalse(eq(None, {u'S': u'on-time'}))

    def test_le(self):
        from ddbmock.database.comparison import le

        self.assertTrue(le({u'S': u'waldo'}, {u'S': u'waldo'}))
        self.assertTrue(le({u'S': u'waldo'}, {u'S': u'waldo1'}))
        self.assertFalse(le({u'S': u'waldo'}, {u'S': u'wald'}))

        self.assertTrue(le({u'N': u'42'}, {u'N': u'42'}))
        self.assertTrue(le({u'N': u'42'}, {u'N': u'42.001'}))
        self.assertFalse(le({u'N': u'42'}, {u'N': u'7'}))

        self.assertFalse(le(None, {u'N': u'7'}))

    def test_lt(self):
        from ddbmock.database.comparison import lt

        self.assertFalse(lt({u'S': u'waldo'}, {u'S': u'waldo'}))
        self.assertTrue(lt({u'S': u'waldo'}, {u'S': u'waldo1'}))
        self.assertFalse(lt({u'S': u'waldo'}, {u'S': u'wald'}))

        self.assertFalse(lt({u'N': u'42'}, {u'N': u'42'}))
        self.assertTrue(lt({u'N': u'42'}, {u'N': u'42.001'}))
        self.assertFalse(lt({u'N': u'42'}, {u'N': u'7'}))

        self.assertFalse(lt(None, {u'N': u'7'}))

    def test_ge(self):
        from ddbmock.database.comparison import ge

        self.assertTrue(ge({u'S': u'waldo'}, {u'S': u'waldo'}))
        self.assertFalse(ge({u'S': u'waldo'}, {u'S': u'waldo1'}))
        self.assertTrue(ge({u'S': u'waldo'}, {u'S': u'wald'}))

        self.assertTrue(ge({u'N': u'42'}, {u'N': u'42'}))
        self.assertFalse(ge({u'N': u'42'}, {u'N': u'42.001'}))
        self.assertTrue(ge({u'N': u'42'}, {u'N': u'7'}))

        self.assertFalse(ge(None, {u'N': u'7'}))

    def test_gt(self):
        from ddbmock.database.comparison import gt

        self.assertFalse(gt({u'S': u'waldo'}, {u'S': u'waldo'}))
        self.assertFalse(gt({u'S': u'waldo'}, {u'S': u'waldo1'}))
        self.assertTrue(gt({u'S': u'waldo'}, {u'S': u'wald'}))

        self.assertFalse(gt({u'N': u'42'}, {u'N': u'42'}))
        self.assertFalse(gt({u'N': u'42'}, {u'N': u'42.001'}))
        self.assertTrue(gt({u'N': u'42'}, {u'N': u'7'}))

        self.assertFalse(gt(None, {u'N': u'7'}))

    def test_begins_with(self):
        from ddbmock.database.comparison import begins_with

        self.assertTrue(begins_with({u'S': u'waldo'}, {u'S': u'waldo'}))
        self.assertTrue(begins_with({u'S': u'waldo'}, {u'S': u'wal'}))
        self.assertFalse(begins_with({u'S': u'waldo'}, {u'S': u'waldo-mario'}))

        self.assertFalse(begins_with(None, {u'S': u'waldo-mario'}))

    def test_between(self):
        from ddbmock.database.comparison import between

        self.assertTrue(between({u'S': u'waldo'}, {u'S': u'wal-mart'}, {u'S': u'walee'}))
        self.assertFalse(between({u'S': u'waldo'}, {u'S': u'wale'}, {u'S': u'walee'}))
        self.assertTrue(between({u'N': u'42'}, {u'N': u'7'}, {u'N': u'123'}))
        self.assertTrue(between({u'N': u'42'}, {u'N': u'42'}, {u'N': u'42'}))
        self.assertFalse(between({u'N': u'42'}, {u'N': u'43'}, {u'N': u'123'}))

        self.assertFalse(between(None, {u'N': u'43'}, {u'N': u'123'}))

    def test_null(self):
        from ddbmock.database.comparison import null

        self.assertTrue(null(None))
        self.assertFalse(null([]))
        self.assertFalse(null({}))
        self.assertFalse(null(False))
        self.assertFalse(null({u'N': u'42'}))

    def test_not_null(self):
        from ddbmock.database.comparison import not_null

        self.assertFalse(not_null(None))
        self.assertTrue(not_null([]))
        self.assertTrue(not_null({}))
        self.assertTrue(not_null(False))
        self.assertTrue(not_null({u'N': u'42'}))

    def test_contains(self):
        from ddbmock.database.comparison import contains

        self.assertTrue(contains({u'S': u'waldo'}, {u'S': u'al'}))
        self.assertFalse(contains({u'S': u'waldo'}, {u'S': u'alee'}))
        self.assertTrue(contains({u'SS': [u'waldo']}, {u'S': u'waldo'}))
        self.assertFalse(contains({u'SS': [u'waldo']}, {u'S': u'al'}))
        self.assertTrue(contains({u'NS': [u'123']}, {u'N': u'123'}))
        self.assertFalse(contains({u'NS': [u'123']}, {u'N': u'12'}))

    def test_not_contains(self):
        from ddbmock.database.comparison import not_contains

        self.assertFalse(not_contains({u'S': u'waldo'}, {u'S': u'al'}))
        self.assertTrue(not_contains({u'S': u'waldo'}, {u'S': u'alee'}))
        self.assertFalse(not_contains({u'SS': [u'waldo']}, {u'S': u'waldo'}))
        self.assertTrue(not_contains({u'SS': [u'waldo']}, {u'S': u'al'}))
        self.assertFalse(not_contains({u'NS': [u'123']}, {u'N': u'123'}))
        self.assertTrue(not_contains({u'NS': [u'123']}, {u'N': u'12'}))

    def test_in(self):
        import ddbmock.database.comparison as c

        # This module is intended to be used reflexively, so... normal behovior
        test_in = getattr(c, 'in')

        pool = [
            {u'S': u'waldo'},
            {u'N': u'123'},
        ]

        self.assertTrue(test_in({u'S': u'waldo'}, *pool))
        self.assertTrue(test_in({u'N': u'123'}, *pool))
        self.assertFalse(test_in({u'S': u'wal'}, *pool))
        self.assertFalse(test_in({u'N': u'12'}, *pool))

    def test_type_mismatch(self):
        import ddbmock.database.comparison as c
        from ddbmock.database.comparison import (
            between, begins_with, eq, lt, le, gt, ge, contains)
        test_in = getattr(c, 'in')

        target = {u'S': u'waldo'}
        target2 = {u'NS': [u'123']}
        rule = {u'N': u'123'}

        self.assertRaises(TypeError, eq, target, rule)
        self.assertRaises(TypeError, lt, target, rule)
        self.assertRaises(TypeError, le, target, rule)
        self.assertRaises(TypeError, gt, target, rule)
        self.assertRaises(TypeError, ge, target, rule)
        self.assertRaises(TypeError, begins_with, target, rule)
        self.assertRaises(TypeError, between, target, rule, rule)
        self.assertRaises(TypeError, contains, target, rule)
        self.assertRaises(TypeError, contains, rule, rule) # can not use contains on number
        self.assertRaises(TypeError, test_in, target2, rule) # target can only be scalar

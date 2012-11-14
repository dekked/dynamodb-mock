# -*- coding: utf-8 -*-

import unittest

# tests
# - actions
# - expected values
# - size computation (fields)
# - size computation (item)

FIELDNAME = "fieldname"
VALUE_S = {u"S": u"String value ê"}
VALUE_N = {u"N": u"123"}
VALUE_B = {u"B": u"QmluYXJ5IGRhdGE=="}
VALUE_SS = {u"SS": [u"String value", u"Ludia", u"Waldo ç"]}
VALUE_NS = {u"NS": [u"456", u"789"]}
VALUE_BS = {u"BS": [u"QmluYXJ5IGRhdGE==", u"enV0IGRlIHp1dA=="]}

VALUE_SS_DEL = {u"SS": [u"Ludia", u"zinga"]}
VALUE_SS_SUR = {u"SS": [u"String value", u"Waldo ç"]}
VALUE_SS_RES = {u"SS": [u'Ludia', u'Waldo ç', u'String value', u'zinga']}
VALUE_N_X2 = {u"N": u"246"}

VALUE_S_BIG = {u"S": u"abcd"*31415}  # if you don't see the geek ref here, your not a geek

ITEM_TYPE = {
    u'S': VALUE_S,
    u'B': VALUE_B,
    u'N': VALUE_N,
    u'SS': VALUE_SS,
    u'BS': VALUE_BS,
    u'NS': VALUE_NS,
}

ITEM_BIG = {
    u'big field': VALUE_S_BIG,
}

class TestItem(unittest.TestCase):
    # actions
    def test_action_put(self):
        from ddbmock.database.item import Item

        item = Item({})
        item._apply_action(FIELDNAME, {"Action": "PUT", "Value": VALUE_S})
        self.assertEqual([(FIELDNAME, VALUE_S)], item.items())

    def test_action_delete(self):
        from ddbmock.database.item import Item

        # field does not exist (just ignores)
        item = Item({})
        item._apply_action(FIELDNAME, {"Action": "DELETE", "Value": VALUE_S})
        self.assertEqual([], item.items())

        # delete scalar value
        item = Item({
            FIELDNAME: VALUE_S,
        })
        item._apply_action(FIELDNAME, {"Action": "DELETE"})
        self.assertEqual([], item.items())

        # delete set from set
        item = Item({
            FIELDNAME: VALUE_SS,
        })
        item._apply_action(FIELDNAME, {"Action": "DELETE", "Value": VALUE_SS_DEL})
        self.assertEqual([(FIELDNAME, VALUE_SS_SUR)], item.items())

        # delete set all from set
        item = Item({
            FIELDNAME: VALUE_SS,
        })
        item._apply_action(FIELDNAME, {"Action": "DELETE", "Value": VALUE_SS})
        self.assertEqual([], item.items())

    def test_action_add(self):
        from ddbmock.database.item import Item

        # add value to int field
        item = Item({FIELDNAME: VALUE_N})
        item._apply_action(FIELDNAME, {"Action": "ADD", "Value": VALUE_N})
        self.assertEqual([(FIELDNAME, VALUE_N_X2)], item.items())

        # push value to any set
        item = Item({FIELDNAME: VALUE_SS})
        item._apply_action(FIELDNAME, {"Action": "ADD", "Value": VALUE_SS_DEL})
        self.assertEqual([(FIELDNAME, VALUE_SS_RES)], item.items())

        # field does not exist
        item = Item({})
        item._apply_action(FIELDNAME, {"Action": "ADD", "Value": VALUE_NS})
        self.assertEqual([(FIELDNAME, VALUE_NS)], item.items())


    def test_action_type_mismatch(self):
        from ddbmock.database.item import Item
        from ddbmock.errors import ValidationException

        # delete from set, set of same type
        item = Item({
            FIELDNAME: VALUE_SS,
        })
        self.assertRaises(ValidationException,
                          item._apply_action,
                          FIELDNAME, {"Action": "DELETE", "Value": VALUE_S})
        self.assertEqual([(FIELDNAME, VALUE_SS)], item.items())
        self.assertRaises(ValidationException,
                          item._apply_action,
                          FIELDNAME, {"Action": "DELETE", "Value": VALUE_NS})
        self.assertEqual([(FIELDNAME, VALUE_SS)], item.items())

        # delete value from scalar field (fail)
        item = Item({
            FIELDNAME: VALUE_S,
        })
        self.assertRaises(ValidationException,
                          item._apply_action,
                          FIELDNAME, {"Action": "DELETE", "Value": VALUE_S})
        self.assertEqual([(FIELDNAME, VALUE_S)], item.items())

        # add to scalar non number field
        item = Item({FIELDNAME: VALUE_S})
        self.assertRaises(ValidationException,
                          item._apply_action,
                          FIELDNAME, {"Action": "ADD", "Value": VALUE_S})
        self.assertEqual([(FIELDNAME, VALUE_S)], item.items())

        # add to set of different type
        item = Item({FIELDNAME: VALUE_SS})
        self.assertRaises(ValidationException,
                          item._apply_action,
                          FIELDNAME, {"Action": "ADD", "Value": VALUE_NS})
        self.assertEqual([(FIELDNAME, VALUE_SS)], item.items())

        # add non number to non existing field
        item = Item({})
        self.assertRaises(ValidationException,
                          item._apply_action,
                          FIELDNAME, {"Action": "ADD", "Value": VALUE_S})
        self.assertEqual([], item.items())

    def test_expected_field_does_not_exist(self):
        from ddbmock.database.item import Item
        from ddbmock.errors import ConditionalCheckFailedException

        # ok
        item = Item({})
        item.assert_match_expected({
           FIELDNAME: {u'Exists': False}
        })

        # mismatch
        item = Item({FIELDNAME: VALUE_SS})
        self.assertRaises(ConditionalCheckFailedException,
                          item.assert_match_expected,
                          {FIELDNAME: {u'Exists': False}})

    def test_expected_field_exists_value(self):
        from ddbmock.database.item import Item
        from ddbmock.errors import ConditionalCheckFailedException

        # ok
        item = Item({FIELDNAME: VALUE_S})
        item.assert_match_expected({
           FIELDNAME: {'Exists': True, 'Value': VALUE_S}
        })

        # exitence mismatch
        item = Item({})
        self.assertRaises(ConditionalCheckFailedException,
                          item.assert_match_expected,
                          {FIELDNAME: {'Exists': True, 'Value': VALUE_S}})

        # type mismatch
        item = Item({FIELDNAME: VALUE_S})
        self.assertRaises(ConditionalCheckFailedException,
                          item.assert_match_expected,
                          {FIELDNAME: {'Exists': True, 'Value': VALUE_N}})

    def test_size_computation(self):
        from ddbmock.database.item import Item

        item = Item(ITEM_TYPE)

        self.assertEqual(0, item.get_field_size(u"toto"))
        self.assertEqual(8, item.get_field_size(u"N"))
        self.assertEqual(15, item.get_field_size(u"S"))
        self.assertEqual(12, item.get_field_size(u"B"))
        self.assertEqual(16, item.get_field_size(u"NS"))
        self.assertEqual(30, item.get_field_size(u"SS"))
        self.assertEqual(24, item.get_field_size(u"BS"))

    def test_item_size_computation(self):
        from ddbmock.database.item import Item

        item1 = Item()
        item2 = Item(ITEM_TYPE)

        # cache init
        self.assertIsNone(item1.size)
        self.assertIsNone(item2.size)

        # compute size
        s1 = item1.get_size()
        s2 = item2.get_size()

        self.assertEqual(0, s1)
        self.assertEqual(114, s2)

        # check cache
        self.assertEqual(s1, item1.size)
        self.assertEqual(s2, item2.size)

        # any call to "update item" invalidates the cache
        item1.apply_actions({})
        item2.apply_actions({})

        self.assertIsNone(item1.size)
        self.assertIsNone(item2.size)

class TestItemSize(unittest.TestCase):
    def test_unit_from_size(self):
        from ddbmock.database.item import ItemSize

        self.assertEqual(1, ItemSize(0).as_units())  # not less than 1 unit
        self.assertEqual(1, ItemSize(1).as_units())
        self.assertEqual(1, ItemSize(1024).as_units())
        self.assertEqual(2, ItemSize(1025).as_units())
        self.assertEqual(3, ItemSize(2049).as_units())

    def test_unit_add(self):
        from ddbmock.database.item import ItemSize

        self.assertEqual(ItemSize(4), ItemSize(1)+ItemSize(3))
        self.assertEqual(ItemSize, type(ItemSize(1)+ItemSize(3)))

    def test_size_with_index(self):
        from ddbmock.database.item import ItemSize

        self.assertEqual(0+100, ItemSize(0).with_indexing_overhead())
        self.assertEqual(1+100, ItemSize(1).with_indexing_overhead())
        self.assertEqual(1024+100, ItemSize(1024).with_indexing_overhead())
        self.assertEqual(2049+100, ItemSize(2049).with_indexing_overhead())

    def test_item_unit_computation(self):
        # full chain test (~functional)
        from ddbmock.database.item import Item

        item1 = Item(ITEM_BIG)
        item2 = Item(ITEM_TYPE)

        self.assertEqual(123, item1.get_size().as_units())  # If I tell you the '123' is not on purpose, you won't believe me, will you ? Especially when Pi is involved
        self.assertEqual(1, item2.get_size().as_units())


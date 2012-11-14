# -*- coding: utf-8 -*-

import unittest

KEY_NAME = "ze chi name"
KEY_TYPE = "humanoid"

KEY_DEF = {
    'AttributeName': KEY_NAME,
    'AttributeType': KEY_TYPE,
}

KEY_VALUE = "TadaList"

KEY1 = {KEY_TYPE: KEY_VALUE}
KEY2 = {"Hey! me incompatible type: alien bacteria": KEY_VALUE}

class TestKey(unittest.TestCase):
    # actions
    def test_key_init(self):
        from ddbmock.database.key import Key

        k = Key(KEY_NAME, KEY_TYPE)
        self.assertEqual(KEY_NAME, k.name)
        self.assertEqual(KEY_TYPE, k.typename)

    def test_key_from_dict(self):
        from ddbmock.database.key import Key

        k = Key.from_dict(KEY_DEF)
        self.assertEqual(KEY_NAME, k.name)
        self.assertEqual(KEY_TYPE, k.typename)

    def test_key_read(self):
        from ddbmock.database.key import Key
        from ddbmock.errors import ValidationException

        k = Key(KEY_NAME, KEY_TYPE)
        self.assertEqual(KEY_VALUE, k.read(KEY1))
        self.assertRaises(ValidationException,
                          k.read,
                          KEY2)

    def test_to_dict(self):
        from ddbmock.database.key import Key

        k = Key(KEY_NAME, KEY_TYPE)

        expected = {
            "AttributeName": KEY_NAME,
            "AttributeType": KEY_TYPE,
        }

        self.assertEqual(expected, k.to_dict())

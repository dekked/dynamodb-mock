# -*- coding: utf-8 -*-

import unittest, mock

# tests
# - delete callback
# - create table persist schema

TABLE_NAME = "tabloid"
TABLE_NAME2 = "razoroid"

TABLE_RT = 45
TABLE_WT = 123

HASH_KEY = {"AttributeName":"hash_key","AttributeType":"N"}
RANGE_KEY = {"AttributeName":"range_key","AttributeType":"S"}

class TestDB(unittest.TestCase):
    def setUp(self):
        from ddbmock.database import dynamodb

        dynamodb.data[TABLE_NAME] = mock.Mock()
        dynamodb.store[TABLE_NAME, False] = dynamodb.data[TABLE_NAME]

    def test_internal_delete_table(self):
        from ddbmock.database import dynamodb

        # delete a table
        dynamodb._internal_delete_table(TABLE_NAME)
        self.assertNotIn(TABLE_NAME, dynamodb.data)

        # make sure deleting already deleted table does not harm
        dynamodb._internal_delete_table(TABLE_NAME)

    def test_delete_table(self):
        from ddbmock.database import dynamodb

        dynamodb.delete_table(TABLE_NAME)
        dynamodb.data[TABLE_NAME].delete.assert_called_with(callback=dynamodb._internal_delete_table)

    @mock.patch('ddbmock.database.db.dynamodb.store')
    def test_create_table_saves_schema(self, m_store):
        from ddbmock.database.db import dynamodb

        data = {
            "TableName": TABLE_NAME2,
            "KeySchema": {
                "HashKeyElement": HASH_KEY,
                "RangeKeyElement": RANGE_KEY,
            },
            "ProvisionedThroughput": {
                "ReadCapacityUnits": TABLE_RT,
                "WriteCapacityUnits": TABLE_WT,
            }
        }

        dynamodb.create_table(TABLE_NAME2, data)

        m_store.__setitem__.assert_called_with(
                                               (TABLE_NAME2, False),
                                               dynamodb.data[TABLE_NAME2],
                                              )

    @mock.patch('ddbmock.database.db.Store')
    def test_init_reloads_schema(self, m_store):
        from ddbmock.database.db import DynamoDB
        old_internal_state = DynamoDB._shared_data
        DynamoDB._shared_data = {'data': {}, 'store': None}

        table1 = mock.Mock()
        table2 = mock.Mock()
        table1.name = TABLE_NAME
        table2.name = TABLE_NAME2
        m_store.return_value.__iter__.return_value = [table1, table2]

        dynamodb = DynamoDB()

        m_store.assert_called_with('~*schema*~')
        self.assertIn(TABLE_NAME, dynamodb.data)
        self.assertIn(TABLE_NAME2, dynamodb.data)
        self.assertEqual(table1, dynamodb.data[TABLE_NAME])
        self.assertEqual(table2, dynamodb.data[TABLE_NAME2])


        DynamoDB._shared_data = old_internal_state

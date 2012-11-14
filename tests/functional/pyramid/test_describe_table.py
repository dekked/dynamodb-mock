# -*- coding: utf-8 -*-

import unittest, mock, json, time

NOW = time.time()

TABLE_NAME = 'Table-1'
TABLE_RT = 45
TABLE_WT = 123
TABLE_HK_NAME = u'hash_key'
TABLE_HK_TYPE = u'N'
TABLE_RK_NAME = u'range_key'
TABLE_RK_TYPE = u'S'

HEADERS = {
    'x-amz-target': 'dynamodb_20111205.DescribeTable',
    'content-type': 'application/x-amz-json-1.0',
}

# Goal here is not to test the full API, this is done by the Boto tests
class TestDescribeTable(unittest.TestCase):
    @mock.patch("ddbmock.database.table.time")  # Brrr
    def setUp(self, m_time):
        from ddbmock.database.db import dynamodb
        from ddbmock.database.table import Table
        from ddbmock.database.key import PrimaryKey
        from ddbmock import main
        app = main({})
        from webtest import TestApp
        self.app = TestApp(app)

        m_time.time.return_value = NOW

        dynamodb.hard_reset()

        hash_key = PrimaryKey(TABLE_HK_NAME, TABLE_HK_TYPE)
        range_key = PrimaryKey(TABLE_RK_NAME, TABLE_RK_TYPE)
        t1 = Table(TABLE_NAME, TABLE_RT, TABLE_WT, hash_key, range_key, status='ACTIVE')
        dynamodb.data[TABLE_NAME] = t1

    def tearDown(self):
        from ddbmock.database.db import dynamodb
        dynamodb.hard_reset()

    def test_describe_table(self):
        from ddbmock.database.db import dynamodb
        from sys import getsizeof

        request = {"TableName": TABLE_NAME}

        expected = {
            u'Table': {
                u'CreationDateTime': NOW,
                u'ItemCount': 0,
                u'KeySchema': {
                    u'HashKeyElement': {
                        u'AttributeName': TABLE_HK_NAME,
                        u'AttributeType': TABLE_HK_TYPE,
                    },
                    u'RangeKeyElement': {
                        u'AttributeName': TABLE_RK_NAME,
                        u'AttributeType': TABLE_RK_TYPE,
                    },
                },
                u'ProvisionedThroughput': {
                    u'ReadCapacityUnits': TABLE_RT,
                    u'WriteCapacityUnits': TABLE_WT,
                },
                u'TableName': TABLE_NAME,
                u'TableSizeBytes': 0,
                u'TableStatus': u'ACTIVE',
            }
        }

        res = self.app.post_json('/', request, HEADERS, status=200)
        self.assertEqual(expected, json.loads(res.body))
        self.assertEqual('application/x-amz-json-1.0; charset=UTF-8', res.headers['Content-Type'])


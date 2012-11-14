# -*- coding: utf-8 -*-

from ddbmock.database import dynamodb

def list_tables(post):
    return {
        'TableNames': dynamodb.list_tables()
    }


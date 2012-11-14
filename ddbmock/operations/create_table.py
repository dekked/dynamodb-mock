# -*- coding: utf-8 -*-

from ddbmock.database import dynamodb

def create_table(post):
    table = dynamodb.create_table(post[u'TableName'], post)

    return {
        "TableDescription": table.to_dict(verbose=False),
    }

# -*- coding: utf-8 -*-

from ddbmock.database import dynamodb

def delete_table(post):
    name = post[u'TableName']
    table = dynamodb.delete_table(name)

    return {
        'TableDescription': table.to_dict(verbose=False)
    }

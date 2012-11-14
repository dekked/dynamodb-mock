# -*- coding: utf-8 -*-

from ddbmock.database import dynamodb

def load_table(func):
    def loader(post, *args):
        name = post[u'TableName']
        table = dynamodb.get_table(name)

        return func(post, table, *args)
    return loader


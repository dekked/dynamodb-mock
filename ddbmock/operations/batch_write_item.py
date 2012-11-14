# -*- coding: utf-8 -*-

from ddbmock.database import dynamodb

def batch_write_item(post):
    #TODO: limit to 25/batch
    #TODO: unprocessed keys

    return {
        "Responses": dynamodb.write_batch(post[u'RequestItems']),
    }

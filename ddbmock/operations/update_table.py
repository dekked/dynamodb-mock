# -*- coding: utf-8 -*-

from . import load_table

@load_table
def update_table(post, table):
    table.update_throughput(post[u'ProvisionedThroughput'][u'ReadCapacityUnits'],
                            post[u'ProvisionedThroughput'][u'WriteCapacityUnits'],
                           )

    desc = table.to_dict()

    return {
        "TableDescription": desc,
    }

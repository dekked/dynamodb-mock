# -*- coding: utf-8 -*-

from . import load_table
from ddbmock.utils import push_write_throughput

@load_table
def delete_item(post, table):
    item = table.delete_item(post[u'Key'], post[u'Expected'])

    capacity = item.get_size().as_units()
    push_write_throughput(table.name, capacity)

    if post[u'ReturnValues'] == "ALL_OLD":
        return {
            "ConsumedCapacityUnits": capacity,
            "Attributes": item,
        }
    else:
        return {
            "ConsumedCapacityUnits": capacity,
        }

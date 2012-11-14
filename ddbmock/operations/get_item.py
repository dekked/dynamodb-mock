# -*- coding: utf-8 -*-

from . import load_table
from ddbmock.utils import push_read_throughput

@load_table
def get_item(post, table):
    base_capacity = 1 if post[u'ConsistentRead'] else 0.5
    item = table.get(post[u'Key'], post[u'AttributesToGet'])

    if item is not None:
        capacity = base_capacity*item.get_size().as_units()
        push_read_throughput(table.name, capacity)
        return {
            "ConsumedCapacityUnits": capacity,
            "Item": item,
        }
    else:
        push_read_throughput(table.name, base_capacity)
        return {
            "ConsumedCapacityUnits": base_capacity,
        }

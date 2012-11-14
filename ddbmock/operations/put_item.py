# -*- coding: utf-8 -*-

from . import load_table
from ddbmock.utils import push_write_throughput

@load_table
def put_item(post, table):
    old, new = table.put(post[u'Item'], post[u'Expected'])
    capacity = max(old.get_size().as_units(), new.get_size().as_units())

    push_write_throughput(table.name, capacity)

    ret = {
        "ConsumedCapacityUnits": capacity,
    }

    if post[u'ReturnValues'] == "ALL_OLD":
        ret["Attributes"] = old

    return ret

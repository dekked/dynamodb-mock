# -*- coding: utf-8 -*-

from . import load_table
from ddbmock.utils import push_write_throughput

@load_table
def update_item(post, table):
    old, new = table.update_item(
            post[u'Key'],
            post[u'AttributeUpdates'],
            post[u'Expected'],
    )

    capacity = max(old.get_size().as_units(), new.get_size().as_units())
    push_write_throughput(table.name, capacity)
    ret = {"ConsumedCapacityUnits": capacity}

    if post[u'ReturnValues'] == "ALL_OLD":
        ret["Attributes"] = old
    elif post[u'ReturnValues'] == "ALL_NEW":
        ret["Attributes"] = new
    elif post[u'ReturnValues'] == "UPDATED_OLD":
        ret["Attributes"] = old - new
    elif post[u'ReturnValues'] == "UPDATED_NEW":
        ret["Attributes"] = new - old

    return ret

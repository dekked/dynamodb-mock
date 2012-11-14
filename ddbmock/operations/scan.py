# -*- coding: utf-8 -*-

from . import load_table
from ddbmock.utils import push_write_throughput
from ddbmock.errors import ValidationException

@load_table
def scan(post, table):
    if post[u'AttributesToGet'] and post[u'Count']:
        raise ValidationException("Can not filter fields when only count is requested")

    results = table.scan(
        post[u'ScanFilter'],
        post[u'AttributesToGet'],
        post[u'ExclusiveStartKey'],
        post[u'Limit'],
    )

    capacity = 0.5*results.size.as_units()
    push_write_throughput(table.name, capacity)

    ret = {
        "Count": len(results.items),
        "ScannedCount": results.scanned,
        "ConsumedCapacityUnits": capacity,
        #TODO: last evaluated key where applicable
    }

    if not post[u'Count']:
        ret[u'Items'] = results.items

    return ret

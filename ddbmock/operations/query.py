# -*- coding: utf-8 -*-

from . import load_table
from ddbmock.utils import push_write_throughput
from ddbmock.errors import ValidationException

@load_table
def query(post, table):
    if post[u'AttributesToGet'] and post[u'Count']:
        raise ValidationException("Can filter fields when only count is requested")

    base_capacity = 1 if post[u'ConsistentRead'] else 0.5

    results = table.query(
        post[u'HashKeyValue'],
        post[u'RangeKeyCondition'],
        post[u'AttributesToGet'],
        post[u'ExclusiveStartKey'],
        not post[u'ScanIndexForward'],
        post[u'Limit'],
    )

    capacity = base_capacity*results.size.as_units()
    push_write_throughput(table.name, capacity)

    ret = {
        "Count": len(results.items),
        "ConsumedCapacityUnits": capacity,
    }

    if results.last_key is not None:
        ret['LastEvaluatedKey'] = results.last_key

    if not post[u'Count']:
        ret[u'Items'] = results.items

    return ret

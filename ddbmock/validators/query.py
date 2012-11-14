# -*- coding: utf-8 -*-

from .types import (
    table_name, Required, item_schema, consistent_read, limit, scan_index_forward,
    attributes_to_get_schema, key_field_value, range_key_condition, Boolean,
    get_key_schema)

post = {
    u'TableName': table_name,
    u'HashKeyValue': key_field_value,
    Required(u'RangeKeyCondition', None): range_key_condition,
    Required(u'ScanIndexForward', True): scan_index_forward,
    Required(u'Count', False): Boolean,
    Required(u'Limit', None): limit,
    Required(u'ExclusiveStartKey', None): get_key_schema,
    Required(u'AttributesToGet', []): attributes_to_get_schema,
    Required(u'ConsistentRead', False): consistent_read,  #FIXME: handle default
}

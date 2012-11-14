# -*- coding: utf-8 -*-

from .types import (
    table_name, Required, item_schema, consistent_read, limit, scan_filter,
    attributes_to_get_schema, key_field_value, Boolean, get_key_schema)

post = {
    u'TableName': table_name,
    Required(u'ScanFilter', {}): scan_filter,
    Required(u'Count', False): Boolean,
    Required(u'Limit', None): limit,
    Required(u'ExclusiveStartKey', None): get_key_schema,
    Required(u'AttributesToGet', []): attributes_to_get_schema,
}

# -*- coding: utf-8 -*-

from .types import (table_name, get_key_schema, return_values_all,
                    expected_schema, attribute_update_schema, Required)

post = {
    u'TableName': table_name,
    u'Key': get_key_schema,
    u'AttributeUpdates': attribute_update_schema,
    Required(u'Expected', {}): expected_schema,
    Required(u'ReturnValues', u'NONE'): return_values_all,
}

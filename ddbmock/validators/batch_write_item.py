# -*- coding: utf-8 -*-

from .types import table_name, item_schema, get_key_schema, Any

post = {
    u"RequestItems": {
        table_name: [Any(
            {
                u"PutRequest": {
                    u"Item": item_schema,
                }
            },{
                u"DeleteRequest": {
                    u"Key": get_key_schema,
                }
            },
        )],
    },
}

# -*- coding: utf-8 -*-

from .types import table_name, table_key_schema, provisioned_throughtput

post = {
    u'TableName': table_name,
    u'KeySchema': table_key_schema,
    u'ProvisionedThroughput': provisioned_throughtput,
}

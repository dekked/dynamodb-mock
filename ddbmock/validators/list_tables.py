# -*- coding: utf-8 -*-

from .types import table_name, table_page, Required

post = {
    Required(u'ExclusiveStartTableName', None): table_name,
    Required(u'Limit', None): table_page,
}

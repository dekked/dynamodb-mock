# -*- coding: utf-8 -*-

from . import load_table

@load_table
def describe_table(post, table):
    return {
        "Table": table.to_dict()
    }

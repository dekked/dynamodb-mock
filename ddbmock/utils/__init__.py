# -*- coding: utf-8 -*-

from .stat import Stat
from ddbmock import config
import logging

tp_stat = {
    'read': {},
    'write': {},
}

req_logger = logging.getLogger("Request logger")
req_logger.addHandler(logging.NullHandler())

tp_logger = logging.getLogger("Throughput logger")
tp_logger.addHandler(logging.NullHandler())

def push_read_throughput(table_name, value):
    if table_name not in tp_stat['read']:
        tp_stat['read'][table_name] = Stat("`%s` read throughput" % table_name,
                                               config.STAT_TP_SAMPLE,
                                               config.STAT_TP_AGGREG,
                                               tp_logger)
    tp_stat['read'][table_name].push(value)

def push_write_throughput(table_name, value):
    if table_name not in tp_stat['write']:
        tp_stat['write'][table_name] = Stat("`%s` write throughput" % table_name,
                                                config.STAT_TP_SAMPLE,
                                                config.STAT_TP_AGGREG,
                                                tp_logger)
    tp_stat['write'][table_name].push(value)

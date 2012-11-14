# -*- coding: utf-8 -*-

from .table import Table
from .item import ItemSize
from .storage import Store
from collections import defaultdict
from ddbmock import config
from ddbmock.utils import push_write_throughput, push_read_throughput
from ddbmock.errors import (ResourceNotFoundException,
                            ResourceInUseException,
                            LimitExceededException,
                           )

# All validations are performed on *incomming* data => already done :)

class DynamoDB(object):
    _shared_data = {
        'data': {},
        'store': None,
    }

    def __init__(self):
        cls = type(self)
        self.__dict__ = cls._shared_data

        # At first instanciation, attempt to reload the database schema
        if self.store is None:
            self.store = Store('~*schema*~')
            for table in self.store:
                self.data[table.name] = table

    def hard_reset(self):
        for table in self.data.values():
            table.store.truncate() # FIXME: should be moved in table
        self.data.clear()
        self.store.truncate()

    def list_tables(self):
        return self.data.keys()

    def get_table(self, name):
        if name in self.data:
            return self.data[name]
        raise ResourceNotFoundException("Table {} does not exist".format(name))

    def create_table(self, name, data):
        if name in self.data:
            raise ResourceInUseException("Table {} already exists".format(name))
        if len(self.data) >= config.MAX_TABLES:
            raise LimitExceededException("Table limit reached. You can not have more than {} tables simultaneously".format(config.MAX_TABLES))

        self.data[name] = Table.from_dict(data)
        self.store[name, False] = self.data[name]
        return self.data[name]

    def _internal_delete_table(self, name):
        """This is ran only after the timer is exhausted"""
        if name in self.data:
            self.data[name].store.truncate()  # FIXME: should be moved in table
            del self.data[name]
            del self.store[name, False]

    def delete_table(self, name):
        if name not in self.data:
            raise ResourceNotFoundException("Table {} does not exist".format(name))
        self.data[name].delete(callback=self._internal_delete_table)

        return self.data[name]

    def get_batch(self, batch):
        ret = defaultdict(dict)

        for tablename, batch in batch.iteritems():
            base_capacity = 1 if batch[u'ConsistentRead'] else 0.5
            fields = batch[u'AttributesToGet']
            table = self.get_table(tablename)
            units = ItemSize(0)
            items = []
            for key in batch[u'Keys']:
                item = table.get(key, fields)
                if item:
                    units += item.get_size().as_units()
                    items.append(item)
            push_read_throughput(tablename, base_capacity*units)
            ret[tablename][u'Items'] = items
            ret[tablename][u'ConsumedCapacityUnits'] = base_capacity*units

        return ret

    def write_batch(self, batch):
        ret = defaultdict(dict)

        for tablename, operations in batch.iteritems():
            table = self.get_table(tablename)
            units = ItemSize(0)
            for operation in operations:
                if u'PutRequest' in operation:
                    old, new = table.put(operation[u'PutRequest'][u'Item'], {})
                    units += max(old.get_size().as_units(), new.get_size().as_units())
                if u'DeleteRequest' in operation:
                    old = table.delete_item(operation[u'DeleteRequest'][u'Key'], {})
                    units += old.get_size().as_units()
            push_write_throughput(tablename, units)
            ret[tablename][u'ConsumedCapacityUnits'] = units

        return ret

# reference instance
dynamodb = DynamoDB()

# -*- coding: utf-8 -*-

from .key import Key, PrimaryKey
from .item import Item, ItemSize
from .storage import Store
from collections import defaultdict, namedtuple
from threading import Timer, Lock
from ddbmock import config
from ddbmock.errors import ValidationException, LimitExceededException, ResourceInUseException
import time, copy, datetime

# All validations are performed on *incomming* data => already done :)

# items: array
# size: ItemSize
Results = namedtuple('Results', ['items', 'size', 'last_key', 'scanned'])

class Table(object):
    def __init__(self, name, rt, wt, hash_key, range_key, status='CREATING'):
        self.name = name
        self.rt = rt
        self.wt = wt
        self.hash_key = hash_key
        self.range_key = range_key
        self.status = status

        self.store = Store(name)
        self.write_lock = Lock()

        self.creation_time = time.time()
        self.last_increase_time = 0
        self.last_decrease_time = 0
        self.count = 0

        Timer(config.DELAY_CREATING, self.activate).start()

    def delete(self, callback):
        """
        Delete is really done when the timeout is exhausted, so we need a callback
        for this
        In Python, this table is not actually destroyed until all references are
        dead. So, we shut down the links with the databases but not the table itself
        until all requests are done. This is the reason why the lock is not acquired
        here. Indeed, this would probably dead-lock the server !

        :ivar callback: real delete function
        """
        if self.status != "ACTIVE":
            raise ResourceInUseException("Table {} is in {} state. Can not UPDATE.".format(self.name, self.status))

        self.status = "DELETING"

        Timer(config.DELAY_DELETING, callback, [self.name]).start()

    def activate(self):
        self.status = "ACTIVE"

    def update_throughput(self, rt, wt):
        if self.status != "ACTIVE":
            raise ResourceInUseException("Table {} is in {} state. Can not UPDATE.".format(self.name, self.status))

        # is decrease ?
        if self.rt > rt or self.wt > wt:
            current_time = time.time()
            current_date = datetime.date.fromtimestamp(current_time)
            last_decrease = datetime.date.fromtimestamp(self.last_decrease_time)
            if (current_date - last_decrease).days < config.MIN_TP_DEC_INTERVAL:
                last = datetime.datetime.fromtimestamp(self.last_decrease_time)
                current = datetime.datetime.fromtimestamp(current_time)
                raise LimitExceededException("Subscriber limit exceeded: Provisioned throughput can be decreased only once within the {} day. Last decrease time: Tuesday, {}. Request time: {}".format(config.MIN_TP_DEC_INTERVAL, last, current))
            self.last_decrease_time = current_time

        # is increase ?
        if self.rt < rt or self.wt < wt:
            if (rt - self.rt)/float(self.rt)*100 > config.MAX_TP_INC_CHANGE:
                raise LimitExceededException('Requested provisioned throughput change is not allowed. The ReadCapacityUnits change must be at most {} percent of current value. Current ReadCapacityUnits provisioned for the table: {}. Requested ReadCapacityUnits: {}.'.format(config.MAX_TP_INC_CHANGE, self.rt, rt))
            if (wt - self.wt)/float(self.wt)*100 > config.MAX_TP_INC_CHANGE:
                raise LimitExceededException('Requested provisioned throughput change is not allowed. The WriteCapacityUnits change must be at most {} percent of current value. Current WriteCapacityUnits provisioned for the table: {}. Requested WriteCapacityUnits: {}.'.format(config.MAX_TP_INC_CHANGE, self.wt, wt))
            self.last_increase_time = time.time()

        # real work
        self.status = "UPDATING"

        self.rt = rt
        self.wt = wt

        Timer(config.DELAY_UPDATING, self.activate).start()

    def delete_item(self, key, expected):
        key = Item(key)
        hash_key = key.read_key(self.hash_key, u'HashKeyElement')
        range_key = key.read_key(self.range_key, u'RangeKeyElement')

        with self.write_lock:
            try:
                old = self.store[hash_key, range_key]
            except KeyError:
                return Item()

            old.assert_match_expected(expected)
            del self.store[hash_key, range_key]

        self.count -= 1
        return old

    def update_item(self, key, actions, expected):
        key = Item(key)
        hash_key = key.read_key(self.hash_key, u'HashKeyElement', max_size=config.MAX_HK_SIZE)
        range_key = key.read_key(self.range_key, u'RangeKeyElement', max_size=config.MAX_RK_SIZE)

        with self.write_lock:
            # Need a deep copy as we will *modify* it
            try:
                old = self.store[hash_key, range_key]
                new = copy.deepcopy(old)
                old.assert_match_expected(expected)
            except KeyError:
                # Item was not in the DB yet
                old = Item()
                new = Item()
                self.count += 1
                # append the keys
                new[self.hash_key.name] = key['HashKeyElement']
                if self.range_key is not None:
                    new[self.range_key.name] = key['RangeKeyElement']


            # Make sure we are not altering a key
            if self.hash_key.name in actions:
                raise ValidationException("UpdateItem can not alter the hash_key.")
            if self.range_key is not None and self.range_key.name in actions:
                raise ValidationException("UpdateItem can not alter the range_key.")

            new.apply_actions(actions)
            self.store[hash_key, range_key] = new

            size = new.get_size()
            if size > config.MAX_ITEM_SIZE:
                self.store[hash_key, range_key] = old  # roll back
                raise ValidationException("Items must be smaller than {} bytes. Got {} after applying update".format(config.MAX_ITEM_SIZE, size))

        return old, new

    def put(self, item, expected):
        item = Item(item)

        if item.get_size() > config.MAX_ITEM_SIZE:
            raise ValidationException("Items must be smaller than {} bytes. Got {}".format(config.MAX_ITEM_SIZE, item.get_size()))

        hash_key = item.read_key(self.hash_key, max_size=config.MAX_HK_SIZE)
        range_key = item.read_key(self.range_key, max_size=config.MAX_RK_SIZE)

        with self.write_lock:
            try:
                old = self.store[hash_key, range_key]
                old.assert_match_expected(expected)
            except KeyError:
                # Item was not in the DB yet
                self.count += 1
                old = Item()

            self.store[hash_key, range_key] = item
            new = copy.deepcopy(item)

        return old, new

    def get(self, key, fields):
        key = Item(key)
        hash_key = key.read_key(self.hash_key, u'HashKeyElement')
        range_key = key.read_key(self.range_key, u'RangeKeyElement')

        if self.range_key is None and u'RangeKeyElement' in key:
            raise ValidationException("Table {} has no range_key".format(self.name))

        try:
            item = self.store[hash_key, range_key]
            return item.filter(fields)
        except KeyError:
            # Item was not in the DB yet
            return None

    def query(self, hash_key, rk_condition, fields, start, reverse, limit):
        """Scans all items at hash_key and return matches as well as last
        evaluated key if more than 1MB was scanned.

        :ivar hash_key: Element describing the hash_key, no type checkeing performed
        :ivar rk_condition: Condition which must be matched by the range_key. If None, all is returned.
        :ivar fields: return only these fields is applicable
        :ivar start: key structure. where to start iteration
        :ivar reverse: wether to scan the collection backward
        :ivar limit: max number of items to parse in this batch
        :return: Results(results, cumulated_size, last_key)
        """
        #FIXME: naive implementation
        #FIXME: what is an item disappears during the operation ?
        #TODO:
        # - size limit

        hash_value = self.hash_key.read(hash_key)
        rk_name = self.range_key.name
        size = ItemSize(0)
        good_item_count = 0
        results = []
        lek = None

        if start and start['HashKeyElement'] != hash_key:
            raise ValidationException("'HashKeyElement' element of 'ExclusiveStartKey' must be the same as the hash_key. Expected {}, got {}".format(hash_key, start['HashKeyElement']))

        data = self.store[hash_value, None]

        keys = sorted(data.keys())

        if reverse:
            keys.reverse()

        if start:
            first_key = self.range_key.read(start['RangeKeyElement'])
            index = keys.index(first_key) + 1  # May raise ValueError but that's OK
            keys = keys[index:]

        for key in keys:
            item = data[key]

            if item.field_match(rk_name, rk_condition):
                good_item_count += 1
                size += item.get_size()
                results.append(item.filter(fields))

            if good_item_count == limit:
                lek = {
                    u'HashKeyElement': hash_key,
                    u'RangeKeyElement': item[rk_name],
                }
                break

        return Results(results, size, lek, -1)

    def scan(self, scan_conditions, fields, start, limit):
        """Scans a whole table, no matter the structure, and return matches as
        well as the the last_evaluated key if applicable and the actually scanned
        item count.

        :ivar scan_conditions: Dict of key:conditions to match items against. If None, all is returned.
        :ivar fields: return only these fields is applicable
        :ivar start: key structure. where to start iteration
        :ivar limit: max number of items to parse in this batch
        :return: results, cumulated_scanned_size, last_key
        """
        #FIXME: naive implementation (too)
        #TODO:
        # - reverse
        # - esk
        # - limit
        # - size limit
        # - last evaluated key

        size = ItemSize(0)
        scanned = 0
        results = []

        for item in self.store:
            size += item.get_size()
            scanned += 1
            if item.match(scan_conditions):
                results.append(item.filter(fields))

        return Results(results, size, None, scanned)

    @classmethod
    def from_dict(cls, data):
        hash_key = PrimaryKey.from_dict(data[u'KeySchema'][u'HashKeyElement'])
        range_key = None
        if u'RangeKeyElement' in data[u'KeySchema']:
            range_key = PrimaryKey.from_dict(data[u'KeySchema'][u'RangeKeyElement'])

        return cls( data[u'TableName'],
                    data[u'ProvisionedThroughput'][u'ReadCapacityUnits'],
                    data[u'ProvisionedThroughput'][u'WriteCapacityUnits'],
                    hash_key,
                    range_key,
                  )

    def get_size(self):
        # TODO: update size only every 6 hours
        size = 0

        for item in self.store:
            size += item.get_size().with_indexing_overhead()

        return size

    def to_dict(self, verbose=True):
        """Serialize table metadata for the describe table method. ItemCount and
        TableSizeBytes are accurate but highly depends on CPython > 2.6. Do not
        rely on it to project the actual size on a real DynamoDB implementation.
        """

        ret = {
            "CreationDateTime": self.creation_time,
            "KeySchema": {
                "HashKeyElement": self.hash_key.to_dict(),
            },
            "ProvisionedThroughput": {
                "ReadCapacityUnits": self.rt,
                "WriteCapacityUnits": self.wt,
            },
            "TableName": self.name,
            "TableStatus": self.status
        }

        if verbose:
            ret[u'ItemCount'] = self.count
            ret[u'TableSizeBytes'] = self.get_size()

        if self.last_increase_time:
            ret[u'ProvisionedThroughput'][u'LastIncreaseDateTime'] = self.last_increase_time
        if self.last_decrease_time:
            ret[u'ProvisionedThroughput'][u'LastDecreaseDateTime'] = self.last_decrease_time

        if self.range_key is not None:
            ret[u'KeySchema'][u'RangeKeyElement'] = self.range_key.to_dict()

        return ret

    # these 2 functions helps to persist table schema (If store supports it)
    # please note that only the schema is persisted, not the state
    def __getstate__(self):
        return (
            self.name,
            self.rt,
            self.wt,
            self.hash_key,
            self.range_key,
            'ACTIVE',
        )

    def __setstate__(self, state):
        self.__init__(*state)  # quick and dirty (tm), but it does the job

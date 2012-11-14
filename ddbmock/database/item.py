# -*- coding: utf-8 -*-

from ddbmock.errors import ConditionalCheckFailedException, ValidationException
from ddbmock import config
from decimal import Decimal
from math import ceil
from . import comparison


def _decode_field(field):
    return field.items()[0]

class ItemSize(int):
    def __add__(self, value):
        return ItemSize(int.__add__(self, value))

    def as_units(self):
        """Get item size in terms of capacity units. This does *not* include the
        index overhead. Units can *not* be bellow 1 ie: a "delete" on a non
        existing item is *not* free
        """
        return max(1, int(ceil((self) / 1024.0)))

    def with_indexing_overhead(self):
        """Take the indexing overhead into account. this is especially usefull
        to compute the table disk size as DynamoDB would but it's not included
        in the capacity unit calculation.
        """
        return self + config.INDEX_OVERHEAD


class Item(dict):
    def __init__(self, dico={}):
        self.update(dico)
        self.size = None

    def filter(self, fields):
        """
        Return a dict containing only the keys specified in ``fields``. If
        ``fields`` evaluates to False (None, empty, ...), the original dict is
        returned untouched.

        :ivar fields: array of name of keys to keep
        :return: filtered ``item``
        """
        if fields:
            filtered = Item((k, v) for k, v in self.items() if k in fields)
            filtered.size = self.get_size()  # Filtered or not, you pay for actual size
            return filtered
        return self

    def _apply_action(self, fieldname, action):
        # Rewrite this function, it's disgustting code
        if action[u'Action'] == u"PUT":
            self[fieldname] = action[u'Value']

        if action[u'Action'] == u"DELETE": # Starts to be anoying
            if not fieldname in self:
                return  #shortcut
            if u'Value' not in action:
                del self[fieldname] # Nice and easy part
                return

            typename, value = _decode_field(action[u'Value'])
            ftypename, fvalue = _decode_field(self[fieldname])

            if len(ftypename) != 2:
                raise ValidationException(u"Can not DELETE elements from a non set type. Got {}".format(ftypename))
            if ftypename != typename:
                raise ValidationException(u"Expected type {t} for DELETE from type {t}. Got {}".format(typename, t=ftypename))

            # do the dirty work
            data = set(fvalue).difference(value)
            # if data empty => remove the key
            if not data:
                del self[fieldname]
            else:
                self[fieldname] = {ftypename: list(data)}

        if action[u'Action'] == u"ADD":  # Realy anoying to code :s
            #FIXME: not perfect, action should be different if the item was new
            typename, value = _decode_field(action[u'Value'])
            if fieldname in self:
                ftypename, fvalue = _decode_field(self[fieldname])

                if ftypename == u"N":
                    data = Decimal(value) + Decimal(fvalue)
                    self[fieldname][u"N"] = unicode(data)
                elif ftypename in [u"NS", u"SS", u"BS"]:
                    if ftypename != typename:
                        raise ValidationException(u"Expected type {t} for ADD in type {t}. Got {}".format(typename, t=ftypename))
                    data = set(fvalue).union(value)
                    self[fieldname][typename] = list(data)
                else:
                    raise ValidationException(u"Only N, NS, SS and BS types supports ADD operation. Got {}".format(ftypename))
            else:
                if typename not in [u"N", u"NS"]:
                    raise ValidationException(u"When performing ADD operation on new field, only Numbers or Numbers set are allowed. Got {} of type {}".format(value, typename))
                self[fieldname] = action[u'Value']

    def apply_actions(self, actions):
        map(self._apply_action, actions.keys(), actions.values())
        self.size = None  # reset cache

    def assert_match_expected(self, expected):
        """
        Raise ConditionalCheckFailedException if ``self`` does not match ``expected``
        values. ``expected`` schema is raw conditions as defined by DynamoDb.

        :ivar expected: conditions to validate
        :raises: ConditionalCheckFailedException
        """
        for fieldname, condition in expected.iteritems():
            if u'Exists' in condition and not condition[u'Exists']:
                if fieldname in self:
                    raise ConditionalCheckFailedException(
                        "Field '{}' should not exist".format(fieldname))
                # *IS* executed but coverage bug
                continue  # pragma: no cover
            if fieldname not in self:
                raise ConditionalCheckFailedException(
                    "Field '{}' should exist".format(fieldname))
            if self[fieldname] != condition[u'Value']:
                raise ConditionalCheckFailedException(
                    "Expected field '{}'' = '{}'. Got '{}'".format(
                    fieldname, condition[u'Value'], self[fieldname]))

    def match(self, conditions):
        for name, condition in conditions.iteritems():
            if not self.field_match(name, condition):
                return False

        return True

    def field_match(self, name, condition):
        """Check if a field matches a condition. Return False when field not
        found, or do not match. If condition is None, it is considered to match.

        :ivar name: name of the field to test
        :ivar condition: raw dict describing the condition {"OPERATOR": FIELDDEFINITION}
        :return: True on success
        """
        # Arcording to specif, no condition means match
        if condition is None:
            return True

        # read the item
        if name not in self:
            value = None
        else:
            value = self[name]

        # Load the test operator from the comparison module. Thamks to input
        # validation, no try/except required
        condition_operator = condition[u'ComparisonOperator'].lower()
        operator = getattr(comparison, condition_operator)
        return operator(value, *condition[u'AttributeValueList'])

    def read_key(self, key, name=None, max_size=0):
        """Provided ``key``, read field value at ``name`` or ``key.name`` if not
        specified. If the field does not exist, this is a "ValueError". In case
        it exists, also check the type compatibility. If it does not match, raise
        TypeError.

        :ivar key: ``Key`` or ``PrimaryKey`` to read
        :ivar name: override name field of key
        :ivar max_size: if specified, check that the item is bellow a treshold
        :return: field value
        """
        if key is None:
            return False
        if name is None:
            name = key.name

        try:
            field = self[name]
        except KeyError:
            raise ValidationException(u'Field {} not found'.format(name))

        if max_size:
            size = self.get_field_size(name)
            if size > max_size:
                raise ValidationException(u'Field {} is over {} bytes limit. Got {}'.format(name, max_size, size))

        return key.read(field)

    def _internal_item_size(self, base_type, value):
        if base_type == 'N': return 8 # assumes "double" internal type on ddb side
        if base_type == 'S': return len(value.encode('utf-8'))
        if base_type == 'B': return len(value.encode('utf-8'))*3/4 # base64 overead

    def get_field_size(self, key):
        """Return value size in bytes or 0 if not found"""
        if not key in self:
            return 0

        typename, value = _decode_field(self[key])
        base_type = typename[0]

        if len(typename) == 1:
            value_size = self._internal_item_size(base_type, value)
        else:
            value_size = 0
            for v in value:
                value_size += self._internal_item_size(base_type, v)

        return value_size

    def get_size(self):
        """Compute Item size as DynamoDB would. This is especially useful for
        enforcing the 64kb per item limit as well as the capacityUnit cost.

        note: the result is cached for efficiency. If you ever happend to directly
        edit values for any reason, do not forget to invalidate it: ``self.size=None``

        :return: the computed size
        """

        # Check cache and compute
        if self.size is None:
            size = 0

            for key in self.keys():
                size += self._internal_item_size('S', key)
                size += self.get_field_size(key)

            self.size = size

        return ItemSize(self.size)

    def __sub__(self, other):
        # Thanks mnoel :)
        return {k:v for k,v in self.iteritems() if k not in other or v != other[k]}

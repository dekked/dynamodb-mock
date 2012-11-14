# -*- coding: utf-8 -*-

# All validations are performed on *incomming* data => already done :)

from ddbmock.errors import ValidationException

class Key(object):
    def __init__(self, name, typename):
        self.name = name
        self.typename = typename

    def read(self, key):
        """Parse a key as specified by DynamoDB API and return its value as long as
            its typename matches self.typename
        """
        typename, value = key.items()[0]
        if self.typename != typename:
            raise ValidationException('Expected key type = {} for field {}. Got {}'.format(
                self.typename, self.name, typename))

        return value

    def to_dict(self):
        """Return the a dict form of the key, suitable for DynamoDb API
        """
        return {
            "AttributeName": self.name,
            "AttributeType": self.typename,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(data[u'AttributeName'], data[u'AttributeType'])

class PrimaryKey(Key):
    pass

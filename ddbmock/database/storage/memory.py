# -*- coding: utf-8 -*-

from collections import defaultdict

class Store(object):
    def __init__(self, name):
        """ Initialize the in-memory store
        :param name: Table name.
        """
        self.name = name
        self.data = defaultdict(dict)

    def truncate(self):
        """Perform a full table cleanup. Might be a good idea in tests :)"""
        self.data = defaultdict(dict)

    def __getitem__(self, (hash_key, range_key)):
        """Get item at (``hash_key``, ``range_key``) or the dict at ``hash_key`` if
        ``range_key``  is None.

        :param key: (``hash_key``, ``range_key``) Tuple. If ``range_key`` is None, all keys under ``hash_key`` are returned
        :return: Item or item dict

        :raise: KeyError
        """

        if hash_key not in self.data:
            raise KeyError('hash_key={} not found'.format(hash_key))
        if range_key is None:
            return self.data[hash_key]
        if range_key not in self.data[hash_key]:
            raise KeyError('range_key={} not found'.format(range_key))
        return self.data[hash_key][range_key]

    def __setitem__(self, (hash_key, range_key), item):
        """Set the item at (``hash_key``, ``range_key``). Both keys must be
        defined and valid. By convention, ``range_key`` may be ``False`` to
        indicate a ``hash_key`` only key.

        :param key: (``hash_key``, ``range_key``) Tuple.
        :param item: the actual ``Item`` data structure to store
        """

        self.data[hash_key][range_key] = item

    def __delitem__(self, (hash_key, range_key)):
        """Delete item at key (``hash_key``, ``range_key``)

        :raises: KeyError if not found
        """

        # Let this line throw KeyError if needed. Checks needs to be performed by the caller
        del self.data[hash_key][range_key]

    def __iter__(self):
        """ Iterate all over the table, abstracting the ``hash_key`` and
        ``range_key`` complexity. Mostly used for ``Scan`` implementation.
        """

        for outer in self.data.values():
            for item in outer.values():
                yield item

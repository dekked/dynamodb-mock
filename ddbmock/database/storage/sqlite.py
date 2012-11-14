# -*- coding: utf-8 -*-

from ..item import Item
from ddbmock import config
import sqlite3, cPickle as pickle

# I know, using global "variable" for this kind of state *is* bad. But it helps
# keeping execution times to a sane value. In particular, this allows to use
# in-memory version of sqlite
conn = sqlite3.connect(config.STORAGE_SQLITE_FILE)

class Store(object):
    def __init__(self, name):
        """ Initialize the sqlite store

        By contract, we know the table name will only contain alphanum chars,
        '_', '.' or '-' so that this is ~ safe

        :param name: Table name.
        """
        conn.execute('''CREATE TABLE IF NOT EXISTS `{}` (
          `hash_key` blob NOT NULL,
          `range_key` blob NOT NULL,
          `data` blob NOT NULL,
          PRIMARY KEY (`hash_key`,`range_key`)
        );'''.format(name))
        conn.commit()

        self.name = name

    def truncate(self):
        """Perform a full table cleanup. Might be a good idea in tests :)"""
        conn.execute('DELETE FROM `{}`'.format(self.name))
        conn.commit()

    def _get_by_hash_range(self, hash_key, range_key):
        request = conn.execute('''SELECT `data` FROM `{}`
                                    WHERE `hash_key`=? AND `range_key`=?'''
                                    .format(self.name),
                                    (hash_key, range_key))
        item = request.fetchone()
        if item is None:
            raise KeyError("No item found at ({}, {})".format(hash_key, range_key))

        return pickle.loads(str(item[0]))

    def _get_by_hash(self, hash_key):
        items = conn.execute('''SELECT * FROM `{}`
                                    WHERE `hash_key`=? '''.format(self.name),
                                    (hash_key, ))
        ret = {item[1]:pickle.loads(str(item[2])) for item in items}

        if not ret:
            raise KeyError("No item found at hash_key={}".format(hash_key))
        return ret

    def __getitem__(self, (hash_key, range_key)):
        """Get item at (``hash_key``, ``range_key``) or the dict at ``hash_key`` if
        ``range_key``  is None.

        :param key: (``hash_key``, ``range_key``) Tuple. If ``range_key`` is None, all keys under ``hash_key`` are returned
        :return: Item or item dict

        :raise: KeyError
        """

        if range_key is None:
            return self._get_by_hash(hash_key)
        return self._get_by_hash_range(hash_key, range_key)

    def __setitem__(self, (hash_key, range_key), item):
        """Set the item at (``hash_key``, ``range_key``). Both keys must be
        defined and valid. By convention, ``range_key`` may be ``False`` to
        indicate a ``hash_key`` only key.

        :param key: (``hash_key``, ``range_key``) Tuple.
        :param item: the actual ``Item`` data structure to store
        """
        db_item = buffer(pickle.dumps(item, 2))
        conn.execute('''INSERT OR REPLACE INTO `{}` (`hash_key`,`range_key`, `data`)
                     VALUES (?, ?, ?)'''.format(self.name),
                     (hash_key, range_key, db_item))
        conn.commit()

    def __delitem__(self, (hash_key, range_key)):
        """Delete item at key (``hash_key``, ``range_key``)

        :raises: KeyError if not found
        """
        conn.execute('DELETE FROM `{}` WHERE `hash_key`=? AND `range_key`=?'
                          .format(self.name), (hash_key, range_key))

    def __iter__(self):
        """ Iterate all over the table, abstracting the ``hash_key`` and
        ``range_key`` complexity. Mostly used for ``Scan`` implementation.
        """
        items = conn.execute('SELECT `data` FROM `{}`'.format(self.name))
        for item in items:
            yield pickle.loads(str(item[0]))

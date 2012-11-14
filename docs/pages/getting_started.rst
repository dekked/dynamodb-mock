##################################
Getting started with DynamoDB-Mock
##################################

.. include:: ../_include/intro.rst

Installation
============

::

    $ pip install ddbmock


Example usage
=============

Run as Regular client-server
----------------------------

Ideal for test environment. For stage and production I highly recommend using
DynamoDB servers. ddbmock comes with no warranty and *will* **loose your data(tm)**.

Launch the server

::

    $ pserve development.ini # launch the server on 0.0.0.0:6543

Start the client

::

    import boto
    from ddbmock import connect_boto_network

    # Use the provided helper to connect your *own* endpoint
    db = connect_boto_network()

    # Done ! just use it wherever in your project as usual.
    db.list_tables() # get list of tables (empty at this stage)

Note: if you do not want to import ddbmock only for the helper, here is a
reference implementation:

::

    def connect_boto_network(host='localhost', port=6543):
        import boto
        from boto.regioninfo import RegionInfo
        endpoint = '{}:{}'.format(host, port)
        region = RegionInfo(name='ddbmock', endpoint=endpoint)
        return boto.connect_dynamodb(region=region, port=port, is_secure=False)

Run as a standalone library
---------------------------

Ideal for unit testing or small scale automated functional tests. Nice to play
around with boto DynamoDB API too :)

::

    import boto
    from ddbmock import connect_boto_patch

    # Wire-up boto and ddbmock together
    db = connect_boto_patch()

    # Done ! just use it wherever in your project as usual.
    db.list_tables() # get list of tables (empty at this stage)

Note, to clean patches made in ``boto.dynamodb.layer1``, you can call
``clean_boto_patch()`` from  the same module.


Advanced usage
==============

A significant part of ddbmock is now configurable through ``ddbmock.config``
parameters. This includes the storage backend.

By default, ddbmock has no persitence and stores everything in-memory. Alternatively,
you can use the ``SQLite`` storage engine but be warned that it will be slower.
To switch the backend, you will to change a configuration variable *before* creating
the first table.

::

    from ddbmock import config

    # switch to sqlite backend
    config.STORAGE_ENGINE_NAME = 'sqlite'
    # define the database path. defaults to 'dynamo.db'
    config.STORAGE_SQLITE_FILE = '/tmp/my_database.sqlite'


Please note that ddbmock does not persist table metadata currently. As a
consequence, you will need to create the tables at each restart even with the
SQLite backend. This is hoped to be improved in future releases.

See https://bitbucket.org/Ludia/dynamodb-mock/src/tip/ddbmock/config.py for a full
list of parameters.

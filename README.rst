ddbmock -- a DynamoDB mock implementation.

Presentation
============

`DynamoDB <http://aws.amazon.com/dynamodb/>`_ is a minimalistic NoSQL engine
provided by Amazon as a part of their AWS product.

**DynamoDB** allows you to store documents composed of unicode, number or binary
data as well are sets. Each tables must define a ``hash_key`` and may define a
``range_key``. All other fields are optional.

**DynamoDB** is really awesome but is terribly slooooow with managment tasks.
This makes it completly unusable in test environements.

**ddbmock** brings a nice, tiny, in-memory (optionaly sqlite) implementation of
DynamoDB along with much better and detailed error messages. Among its niceties,
it features a double entry point:

 - regular network based entry-point with 1:1 correspondance with stock DynamoDB
 - **embeded entry-point** with seamless boto intergration 1, ideal to avoid spinning yet another server.

**ddbmock** is **not** intended for production use. It **will lose** your data.
you've been warned! I currently recommend the "boto extension" mode for unit-tests
and the "server" mode for functional tests.

Yes, ddbmock *can persist your data* using the optional "sqlite" backend. Bt still,
do *not* use it in production.

Installation
============

::

    $ pip install ddbmock


Developing
==========

::

    $ hg clone ssh://hg@bitbucket.org/Ludia/dynamodb-mock
    $ pip install nose nosexcover coverage mock webtests boto
    $ python setup.py develop
    $ nosetests # --no-skip to run boto integration tests too


What is ddbmock useful for ?
============================

- running unit test FAST. DONE
- running functional test FAST. DONE
- experiment with DynamoDB API. DONE
- plan throughput usage. DONE
- plan disk space requirements. DONE (describe table returns accurate size !)
- perform simulations with accurate limitations.

Current status
==============

- pass all boto integration tests
- support full table life-cycle
- support full item life-cycle
- support for all item limitations
- accurate size, throughput reporting
- ``Scan``, ``BatchGetItem`` and ``BatchWriteItem`` still lacks ``ExclusiveStartKey``
- no limits on concurent table operations
- no limits for request/response size nor item count in those

See http://ddbmock.readthedocs.org/en/latest/pages/status.html for detailed
up-to-date status.

History
=======

 - v0.4.1 (?): more analytics, schema persistence in sqlite, ...
 - v0.4.0: sqlite backend + throughput statistics + refactoring, more documentation, more tests
 - v0.3.2: batchWriteItem support + pass boto integration tests
 - v0.3.1: accuracy in item/table sizes + full test coverage
 - v0.3.0: first public release. Full table lifecycle + most items operations

(?) indicates a future release. These are only ideas or "nice to have".

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

Requirements
============

 - Python 2.7.x
 - Pyramid >= 1.3
 - Boto >= 2.5.0 (optional)
 - **NO** AWS account :)

Related Links
=============

ddbmock
-------

- **Full documentation**: https://ddbmock.readthedocs.org/en/latest
- **Report bugs**: https://bitbucket.org/Ludia/dynamodb-mock/issues
- **Download**: http://pypi.python.org/pypi/ddbmock

Dynamodb-mapper
---------------

- **Full documentation**: http://dynamodb-mapper.readthedocs.org/en/latest/
- **Report bugs**: https://bitbucket.org/Ludia/dynamodb-mapper/issues
- **Download**: http://pypi.python.org/pypi/dynamodb-mapper

Boto
----

- **Full documentation**: http://docs.pythonboto.org/en/latest/index.html
- **Report bugs**: https://github.com/boto/boto/issues
- **Download**: http://pypi.python.org/pypi/boto

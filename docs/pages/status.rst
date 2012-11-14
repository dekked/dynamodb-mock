##############
Current Status
##############

This documents reflects ddbmock status as of 5/11/2012. It may be outdated.

Some items are marked as "WONTFIX". These are throttling related. The goal of
ddbmock is to help you with tests and planification. It won't get in your way.

Methods support
===============

- ``CreateTable`` DONE
- ``DeleteTable`` DONE
- ``UpdateTable`` DONE
- ``DescribeTable`` DONE
- ``GetItem`` DONE
- ``PutItem`` DONE
- ``DeleteItem`` DONE
- ``UpdateItem`` ALMOST
- ``BatchGetItem`` DONE*
- ``BatchWriteItem`` DONE*
- ``Query`` DONE
- ``Scan`` DONE*

There basically are no support for ``ExclusiveStartKey``, and their associated
features at all in ddbmock. This affects all "*" operations. ``Query`` is the
only exception.

``UpdateItem`` has a different behavior when the target item did not exist prior
the update operation. In particular, the ``ADD`` operator will always behave as
though the item existed before.

Comparison Operators
====================

Some comparison might not work as expected on binary data as it is performed on
the base64 representation instead of the binary one. Please report a bug if this
is a problem for you, or, even better, open a pull request :)

All operators exists as lower case functions in ``ddbmock.database.comparison``.
This list can easily be extended to add new/custom operators.

Common to ``Query`` and ``Scan``
--------------------------------

- ``EQ`` DONE
- ``LE`` DONE
- ``LT`` DONE
- ``GE`` DONE
- ``GT`` DONE
- ``BEGINS_WITH`` DONE
- ``BETWEEN`` DONE

Specific to ``Scan``
--------------------

- ``NULL`` DONE
- ``NOT_NULL`` DONE
- ``CONTAINS`` DONE
- ``NOT_CONTAINS`` DONE
- ``IN`` DONE

``IN`` operator is the only that can not be imported directly as it overlaps
builtin ``in`` keyword. If you need it, either import it with ``getattr`` on the
module or as ``in_test`` which, anyway, is its internal name.

Return value specifications
---------------------------

- ``NONE`` DONE
- ``ALL_OLD`` DONE
- ``ALL_NEW`` DONE
- ``UPDATED_OLD`` DONE
- ``UPDATED_NEW`` DONE

Please note that only ``UpdateItem`` supports the 5. Other compatible nethods
understands only the 2 first.

Rates and size limitations
==========================

basically, none are supported yet

Request rate
------------

- Throttle read  operations when provisioned throughput exceeded. WONTFIX
- Throttle write operations when provisioned throughput exceeded. WONTFIX
- Throughput usage logging for planification purpose. DONE
- Maximum throughput is 10,000. DONE
- Minimum throughput is 1. DONE
- Report accurate throughput. DONE

Request size
------------

- Limit response size to 1MB. TODO
- Limit request size to 1MB. TODO
- Limit ``BatchGetItem`` to 100 per request. TODO
- Linit ``BatchWriteItem`` to 25 per request. TODO

Table managment
---------------

- No more than 256 tables. DONE
- No more than 10 ``CREATING`` tables. WONTFIX
- No more than 10 ``DELETING`` tables. WONTFIX
- No more than 10 ``UPDATING`` tables. WONTFIX

- No more than 1 Throughput decrease/calendar day. DONE
- No more than \*2 Throughput increase/update. DONE

Types and items Limitations
===========================

- Table names can only be between 3 and 255 bytes long. DONE
- Table names can only contains a-z, A-Z, 0-9, '_', '-', and '.'. DONE
- No more than 64kB/Item including fieldname but not indexing overhead. DONE
- Primary key names can only be between 1 and 255 bytes long. DONE
- Attribute value can *not* be Null. DONE
- ``hash_key``  value maximu 2048 bytes. DONE
- ``range_key`` value maximu 1024 bytes. DONE
- Numbers max 38 digits precision; between 10^-128 and 10^+126. DONE

Table description
=================

- item count. DONE
- data size. DONE
- date: creation. DONE
- date: last throughput increase. DONE
- date: last throughput decrease. DONE

Dates are represented as float timestamps using scientific notation by DynamoDB
but we only send them as plain number, not caring about the representation. Most
parsers won't do any difference anyway.

###########################
Planifications with ddbmock
###########################

DynamoDB-Mock has two main goals. Speeding up tests and helping you plan your
real DynamoDB usage. This includes both the throughput and the disk usage.

Getting disk usage
==================

To get per table disk usage, feedback, one can issue a call to ``DescribeTable``
method. the informations returned are accurate in the sense of DynamoDB but beware,
these are also by far *below* the real usage in ddbmock as there are asbsolutly
no optimisations done on our side.

Getting Throughput usage
========================

To get per table throughput usage you can rely on the dedicated logger
``utils.tp_logger``. By default, ``min``, ``max`` and ``average`` throughput are
logged every 5 minutes and at the end of the program via an atexit handler.

Note that the handler is hooked to ``NullHandler`` handler by default so that
there should not be any noise in the console.

To get statistics more often, you can change ``config.STAT_TP_AGGREG`` value
**before** issueing any requests to ddbmock. ``__init__`` may be a good place to
do so.

For example, if you want to get statistics to the console every 15 seconds, you
can use a code like this :

::

    from ddbmock import config
    from ddbmock.utils import tp_logger
    import logging

    config.STAT_TP_AGGREG = 15                     # every 15 sec
    tp_logger.addHandler(logging.StreamHandler())  # to console


Depending on how your your application scales, it may be interesting to run a
representative secnario with multiples users and se how the throughput proportions.
this will be a very valuable information when going live.

General logging
===============

Logger ``utils.req_logger`` traces request body, response and errors if
applicable. Each log entry starts with ``request_id=...``. This allows you to
keep track of each individual requests even in a higly concurent environnement.

By default, all is logged to ``NullHandler`` and you should at leaste hook a
``logging.StreamHandler`` to have a console output.


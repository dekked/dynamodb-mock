`DynamoDB <http://aws.amazon.com/dynamodb/>`_ is a minimalistic NoSQL engine
provided by Amazon as a part of their AWS product.

**DynamoDB** is great in production environement but sucks when testing your
application. Tables needs roughtly 1 min to be created, deleted or updated.
Items operation rates depends on how much you pay and tests will conflict if
2 developers run them at the same time.

**ddbmock** brings a tiny in-memory(tm) implementation of DynamoDB API. It can
either be run as a stand alone server or as a regular library helping you to
build lightning fast unit and functional tests :)

**ddbmock** is **not** intended for production use. It **will lose** your data.
you've been warned! I currently recommend the "boto extension" mode for unit-tests
and the "server" mode for functional tests.

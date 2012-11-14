# -*- coding: utf-8 -*-

import unittest, mock

class TestRouterBoto(unittest.TestCase):
    def test_routing_exception_translation(self):
        from ddbmock.router.boto import _ddbmock_exception_to_boto_exception
        from boto.exception import DynamoDBResponseError
        from ddbmock.errors import InternalFailure

        self.assertIsInstance(_ddbmock_exception_to_boto_exception(
                              InternalFailure('taratata')),
                              DynamoDBResponseError)

    def test_validation_exception_translation(self):
        from ddbmock.router.boto import _ddbmock_exception_to_boto_exception
        from boto.dynamodb.exceptions import DynamoDBValidationError
        from ddbmock.errors import ValidationException

        self.assertIsInstance(_ddbmock_exception_to_boto_exception(
                              ValidationException('taratata')),
                              DynamoDBValidationError)

    def test_conditions_exception_translation(self):
        from ddbmock.router.boto import _ddbmock_exception_to_boto_exception
        from boto.dynamodb.exceptions import DynamoDBConditionalCheckFailedError
        from ddbmock.errors import ConditionalCheckFailedException

        self.assertIsInstance(_ddbmock_exception_to_boto_exception(
                              ConditionalCheckFailedException('taratata')),
                              DynamoDBConditionalCheckFailedError)

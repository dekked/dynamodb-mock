# -*- coding: utf-8 -*-

import unittest
from decimal import Decimal

# tests
# - number validator
# - dynamodb_api_validate errors

ACTION_404 = "!~I bet this route won't ever exist~!"
POST = {"toto":"titi"}

class TestValidators(unittest.TestCase):
    def test_number_max_exp(self):
        from ddbmock.validators.types import Precision
        from onctuous import Invalid

        self.assertEqual(Decimal("382.1E4"), Precision(max_exp=3)(Decimal("382.1E4")))
        self.assertRaisesRegexp(Invalid, "bigger",
                                Precision(max_exp=3),
                                Decimal("395.1E5"))

    def test_number_min_exp(self):
        from ddbmock.validators.types import Precision
        from onctuous import Invalid

        self.assertEqual(Decimal("-50.52"), Precision(min_exp=-2)(Decimal("-50.52")))
        self.assertRaisesRegexp(Invalid, "smaller",
                                Precision(min_exp=-2),
                                Decimal("-50.521"))

    def test_number_max_digits(self):
        from ddbmock.validators.types import Precision
        from onctuous import Invalid

        self.assertEqual(Decimal("-1.21E50"), Precision(max_digits=3)(Decimal("-1.21E50")))
        self.assertRaisesRegexp(Invalid, "digits",
                                Precision(max_digits=3),
                                Decimal("-1.211E50"))

    def test_validator_not_found(self):
        from ddbmock.validators import dynamodb_api_validate

        self.assertEqual(POST, dynamodb_api_validate(ACTION_404, POST))

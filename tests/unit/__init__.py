# -*- coding: utf-8 -*-

# hack for boto integration tests to run
# the test module expects to find `unitest` loaded as part of tests.unit
# and, as we have the same name (collisions happiness), I cam not use regular
# and easy import. :')

import unittest

# -*- coding: utf-8 -*-

import unittest, mock

# tests
# - update throughput

NAME = "tabloid"
RT = 100
WT = 100
RT2 = 120
WT2 = 120
RT3 = 20
WT3 = 20
RT4 = 2
WT4 = 2
RT10 = 109
WT10 = 109
RT100 = 201
WT100 = 201
CREATION = 2*24*3600  # day 2 of our era (UNIX) (avoids stupid side effects of 0 in the test)

class TestTable(unittest.TestCase):
    def setUp(self):
        from ddbmock.database.table import Table
        self.table = Table(NAME, RT, WT, None, None, status="ACTIVE")

    def tearDown(self):
        self.table = None

    def test_update_throughput_nominal(self):
        self.table.update_throughput(RT2, WT2)

        self.assertEqual(RT2, self.table.rt)
        self.assertEqual(WT2, self.table.wt)

    def test_increase_throughtput_max_100_percents(self):
        from ddbmock.errors import LimitExceededException

        # Try on RT
        self.assertRaisesRegexp(LimitExceededException,
                                "ReadCapacityUnits .* at most 100",
                                self.table.update_throughput,
                                RT100, WT)
        self.assertEqual(RT, self.table.rt)
        self.assertEqual(WT, self.table.wt)

        # Try on WT
        self.assertRaisesRegexp(LimitExceededException,
                                "WriteCapacityUnits .* at most 100",
                                self.table.update_throughput,
                                RT, WT100)
        self.assertEqual(RT, self.table.rt)
        self.assertEqual(WT, self.table.wt)

    @mock.patch("ddbmock.database.table.time")
    def test_decrease_max_once_a_day(self, m_time):
        from ddbmock.errors import LimitExceededException

        # 1st decrease 1 hour after creation (ok)
        m_time.time.return_value = CREATION + 1*3600
        self.table.update_throughput(RT3, WT3)
        self.assertEqual(RT3, self.table.rt)
        self.assertEqual(WT3, self.table.wt)

        # bypass the timer
        self.table.status = "ACTIVE"

        # 2nd decrease 2 hour after creation (fail)
        m_time.time.return_value = CREATION + 2*3600
        self.assertRaisesRegexp(LimitExceededException,
                                "once .* day",
                                self.table.update_throughput,
                                RT4, WT4)
        self.assertEqual(RT3, self.table.rt)
        self.assertEqual(WT3, self.table.wt)





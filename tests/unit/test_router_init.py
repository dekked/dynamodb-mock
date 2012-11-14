# -*- coding: utf-8 -*-

import unittest, mock

ACTION = "CreateTable"
ACTION_404 = "!~I bet this route won't ever exist~!"
ROUTE = "create_table"
POST = {"toto":"titi"}

class TestRouterInit(unittest.TestCase):
    @mock.patch("ddbmock.router.import_module")
    @mock.patch("ddbmock.router.dynamodb_api_validate")
    def test_do_request_nominal(self, m_validate, m_import):
        from ddbmock.router import router

        m_module = m_import.return_value
        m_route = m_module.create_table
        m_route.return_value = {}
        m_validated = m_validate.return_value

        router(ACTION, POST)

        m_import.assert_called_with("ddbmock.operations.{}".format(ROUTE))
        m_validate.assert_called_with(ROUTE, POST)
        m_route.assert_called_with(m_validated)

    def test_do_request_route_404(self):
        from ddbmock.router import router
        from ddbmock.errors import InternalFailure

        self.assertRaisesRegexp(InternalFailure,
                                'exist',
                                router,
                                ACTION_404, POST)

    @mock.patch("ddbmock.router.import_module")
    @mock.patch("ddbmock.router.dynamodb_api_validate")
    def test_internal_server_error(self, m_validate, m_import):
        from ddbmock.router import router
        from ddbmock.errors import InternalFailure

        m_module = m_import.return_value
        m_route = m_module.create_table
        m_route.return_value = {}
        m_route.side_effect = ValueError
        m_validated = m_validate.return_value

        self.assertRaisesRegexp(InternalFailure,
                                'ValueError',
                                router,
                                ACTION, POST)

        m_import.assert_called_with("ddbmock.operations.{}".format(ROUTE))
        m_validate.assert_called_with(ROUTE, POST)
        m_route.assert_called_with(m_validated)

import unittest

import mock

from vcl_client import cfg
from vcl_client import utils
from tests import fakes

class TestAuthCheck(unittest.TestCase):
    @mock.patch('vcl_client.cfg.get_password')
    @mock.patch('vcl_client.cfg.get_conf')
    def test_auth_check(self, mock_get_conf, mock_get_password):
        mock_get_conf.return_value = fakes.USERNAME
        mock_get_password.return_value = fakes.PASSWORD

        utils.auth_check()

        mock_get_conf.assert_called_with(cfg.USERNAME_KEY)
        mock_get_password.assert_called()

    @mock.patch('sys.exit')
    @mock.patch('click.echo')
    @mock.patch('vcl_client.cfg.get_password')
    @mock.patch('vcl_client.cfg.get_conf')
    def test_auth_check_no_creds(self, mock_get_conf, mock_get_password,
                                 mock_echo, mock_sys):
        mock_get_conf.return_value = None
        mock_get_password.return_value = None

        utils.auth_check()

        mock_echo.assert_called_with('Credentials not found. Run `vcl config`.')
        mock_sys.assert_called_with(1)

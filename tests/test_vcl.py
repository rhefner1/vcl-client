import unittest

import mock
from click import testing

from vcl_client import vcl
from vcl_client import cfg
from tests import fakes


class TestAuthCheck(unittest.TestCase):
    @mock.patch('vcl_client.cfg.get_password')
    @mock.patch('vcl_client.cfg.get_conf')
    def test_auth_check(self, mock_get_conf, mock_get_password):
        mock_get_conf.return_value = fakes.USERNAME
        mock_get_password.return_value = fakes.PASSWORD

        vcl.auth_check()

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

        vcl.auth_check()

        mock_echo.assert_called_with('Credentials not found. Run `vcl config`.')
        mock_sys.assert_called_with(1)


class TestConfig(unittest.TestCase):
    @mock.patch('keyring.set_password')
    @mock.patch('vcl_client.cfg.write_conf')
    def test_config(self, mock_write_conf, mock_set_pass):
        runner = testing.CliRunner()
        inputs = (fakes.USERNAME, fakes.PASSWORD, fakes.ENDPOINT)
        runner.invoke(vcl.config, input='%s\n%s\n%s\n' % inputs)

        calls = [
            mock.call(cfg.USERNAME_KEY, fakes.USERNAME, write=False),
            mock.call(cfg.ENDPOINT_KEY, fakes.ENDPOINT)
        ]

        mock_write_conf.assert_has_calls(calls)
        mock_set_pass.assert_called_with('system', fakes.USERNAME,
                                         fakes.PASSWORD)


class TestImages(unittest.TestCase):
    @mock.patch('click.echo')
    @mock.patch('vcl_client.cfg.get_conf')
    @mock.patch('vcl_client.vcl.auth_check')
    def test_images(self, mock_auth, mock_get_conf, mock_echo):
        mock_get_conf.return_value = fakes.JSON_RETURN

        runner = testing.CliRunner()
        runner.invoke(vcl.images, [None, False])

        mock_auth.assert_called()
        mock_echo.assert_called()


if __name__ == '__main__':
    unittest.main()

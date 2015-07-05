import unittest

import mock
from click import testing

from vcl_client import cli
from vcl_client import cfg
from tests import fakes


class TestConfig(unittest.TestCase):
    @mock.patch('vcl_client.cfg.set_password')
    @mock.patch('vcl_client.cfg.set_conf')
    @mock.patch('vcl_client.utils.validate_credentials')
    def test_config(self, mock_valid, mock_set_conf, mock_set_pass):
        runner = testing.CliRunner()
        inputs = (fakes.USERNAME, fakes.PASSWORD, fakes.ENDPOINT)
        runner.invoke(cli.config, input='%s\n%s\n%s\n' % inputs)

        calls = [
            mock.call(cfg.USERNAME_KEY, fakes.USERNAME),
            mock.call(cfg.ENDPOINT_KEY, fakes.ENDPOINT)
        ]

        mock_valid.assert_called()
        mock_set_conf.assert_has_calls(calls)
        mock_set_pass.assert_called_with(fakes.PASSWORD)


class TestImages(unittest.TestCase):
    @mock.patch('click.echo')
    @mock.patch('vcl_client.cfg.get_conf')
    @mock.patch('vcl_client.api.auth_check')
    def test_images(self, mock_auth, mock_get_conf, mock_echo):
        mock_get_conf.return_value = fakes.JSON_RETURN

        runner = testing.CliRunner()
        runner.invoke(cli.images, [None, False])

        mock_auth.assert_called()
        mock_echo.assert_called()


if __name__ == '__main__':
    unittest.main()

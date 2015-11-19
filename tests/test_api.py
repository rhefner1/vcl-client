import unittest
import mock
from vcl_client import api
from vcl_client import cfg
from tests import fakes


class TestCallApi(unittest.TestCase):
    @mock.patch('urllib2.urlopen')
    @mock.patch('keyring.get_password')
    @mock.patch('vcl_client.cfg.get_conf')
    def test_call_api(self, mock_get_conf, mock_keyring, mock_urlopen):
        endpoint = fakes.ENDPOINT
        params = ('key1', 'param1')
        mock_get_conf.return_value = fakes.USERNAME
        mock_keyring.return_value = 'password'
        mock_urlopen_read = mock.Mock()
        mock_urlopen_read.read.return_value = fakes.XML_RETURN
        mock_urlopen.return_value = mock_urlopen_read

        response = api.call_api(endpoint, params)

        mock_get_conf.assert_called_with(cfg.USERNAME_KEY)
        self.assertEqual(fakes.XML_PARSED, response)


class TestAuthCheck(unittest.TestCase):
    @mock.patch('vcl_client.cfg.get_password')
    @mock.patch('vcl_client.cfg.get_conf')
    def test_auth_check(self, mock_get_conf, mock_get_password):
        mock_get_conf.return_value = fakes.USERNAME
        mock_get_password.return_value = fakes.PASSWORD

        api.auth_check()

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

        api.auth_check()

        mock_echo.assert_called_with('Credentials not found. Run `vcl config`.')
        mock_sys.assert_called_with(1)


if __name__ == '__main__':
    unittest.main()

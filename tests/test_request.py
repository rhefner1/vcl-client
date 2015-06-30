import unittest

import mock

from vcl_client import request
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

        response = request.call_api(endpoint, params)

        mock_get_conf.assert_called_with(cfg.USERNAME_KEY)
        self.assertEqual(fakes.XML_PARSED, response)


if __name__ == '__main__':
    unittest.main()

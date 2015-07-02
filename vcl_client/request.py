"""Handles the XMLRPC server communication"""

import urllib2
import xmlrpclib

from vcl_client import cfg

BOOT_ENDPOINT = 'XMLRPCaddRequest'
IMAGES_ENDPOINT = 'XMLRPCgetImages'
REQUEST_LIST_ENDPOINT = 'XMLRPCgetRequestIds'


def call_api(endpoint, params):
    """Calls the API."""
    base_url = cfg.get_conf(cfg.BASE_URL_KEY)
    username = cfg.get_conf(cfg.USERNAME_KEY)
    data = xmlrpclib.dumps(params, endpoint)
    headers = {
        'Content-Type': 'text/xml',
        'X-User': username,
        'X-Pass': cfg.get_password(),
        'X-APIVERSION': '2'
    }

    req = urllib2.Request(base_url, data, headers)
    response = urllib2.urlopen(req)
    raw_xml = response.read()
    return xmlrpclib.loads(raw_xml)


def boot(params):
    """Calls the APi and throws an error if request isn't successful."""
    response = call_api(BOOT_ENDPOINT, params)
    status = response[0][0]['status']

    if status != 'success':
        raise RuntimeError("Got unknown status: %s. Full response: %s."
                           % (status, response))


def images():
    """Calls the API and returns a list of images."""
    response = call_api(IMAGES_ENDPOINT, ())
    return response[0][0]


def request_list():
    """Calls the API and returns a list of requests."""
    response = call_api(REQUEST_LIST_ENDPOINT, ())
    return response[0][0]['requests']

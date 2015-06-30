"""Handles the XMLRPC server communication"""

import urllib2
import xmlrpclib

import keyring

from vcl_client import cfg


def call_api(endpoint, params):
    """Calls the API."""
    base_url = cfg.get_conf(cfg.BASE_URL_KEY)
    username = cfg.get_conf(cfg.USERNAME_KEY)
    data = xmlrpclib.dumps(params, endpoint)
    headers = {
        'Content-Type': 'text/xml',
        'X-User': cfg.get_conf(cfg.USERNAME_KEY),
        'X-Pass': keyring.get_password('system', username),
        'X-APIVERSION': '2'
    }

    req = urllib2.Request(base_url, data, headers)
    response = urllib2.urlopen(req)
    raw_xml = response.read()
    return xmlrpclib.loads(raw_xml)

"""Handles the XMLRPC server communication"""

import json
import sys
import urllib2
import xmlrpclib

import click

from vcl_client import cfg

REQUEST_START = 'now'
REQUEST_LENGTH = 480

REQUEST_CONNECTION = 'XMLRPCgetRequestConnectData'
REQUEST_ADD = 'XMLRPCaddRequest'
REQUEST_STATUS = 'XMLRPCgetRequestStatus'
IMAGES_ENDPOINT = 'XMLRPCgetImages'
REQUEST_LIST_ENDPOINT = 'XMLRPCgetRequestIds'
TEST_ENDPOINT = 'XMLRPCtest'

IP_ADDR_SERVER = 'https://api.ipify.org'


def auth_check():
    """Checks if user/pass exist."""
    username = cfg.get_conf(cfg.USERNAME_KEY)
    password = cfg.get_password()

    if not username or not password:
        click.echo('Credentials not found. Run `vcl config`.')
        sys.exit(1)


def call_api(endpoint, params):
    """Calls the API."""
    auth_check()

    base_url = cfg.get_conf(cfg.ENDPOINT_KEY)
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
    return xmlrpclib.loads(raw_xml)[0][0]


def images(filter_term=None, refresh=False):
    """Calls the API and returns a list of images."""
    cached_image_list = cfg.get_conf(cfg.IMAGE_LIST_KEY)

    if refresh or not cached_image_list:
        response = call_api(IMAGES_ENDPOINT, ())
        all_images = [[i['id'], i['name']] for i in response]

        # Caching response for subsequent queries
        cfg.set_conf(cfg.IMAGE_LIST_KEY, json.dumps(all_images), write=True)
    else:
        all_images = json.loads(cached_image_list)

    if filter_term:
        filtered_images = [image for image in all_images
                           if filter_term.lower() in image[1].lower()]

        if not filtered_images:
            raise ValueError('No matches found for that filter.')

        return filtered_images

    return all_images


def request(image_id):
    """Calls the API and throws an error if request isn't successful."""
    params = (image_id, REQUEST_START, REQUEST_LENGTH)
    response = call_api(REQUEST_ADD, params)
    status = response['status']

    if status != 'success':
        raise RuntimeError("%s." % response['errormsg'])

    return response['requestid']


def request_details(request_id):
    """Requests connection details for a request."""
    remote_ip = urllib2.urlopen(IP_ADDR_SERVER).read()
    params = (request_id, remote_ip)
    response = call_api(REQUEST_CONNECTION, params)
    status = response['status']

    if status == 'ready':
        ip_addr = response['serverIP']
        user = response['user']
        password = response['password'] if response['password'] else None
        connect_methods = response['connectMethods']

        return ip_addr, user, password, connect_methods
    elif status == 'notready':
        raise RuntimeError("Request isn't ready to connect.")
    else:
        raise RuntimeError("%s" % response['errormsg'])


def request_list():
    """Calls the API and returns a list of requests."""
    response = call_api(REQUEST_LIST_ENDPOINT, ())
    all_request_data = response['requests']

    if all_request_data:
        return [
            [
                r['imageid'],
                r['imagename'],
                r['state'],
                r['ostype'],
                r['OS'],
                r['requestid']
            ]
            for r in all_request_data
        ]
    else:
        return None


def request_status(request_id):
    """Checks the status of a request."""
    params = (request_id,)
    response = call_api(REQUEST_STATUS, params)
    status = response['status']

    try:
        time_left = response['time']
    except KeyError:
        time_left = None

    return status, time_left


def test_call():
    """Calls a test API method."""
    response = call_api(TEST_ENDPOINT, ())
    status = response['status']

    if status != 'success':
        raise ValueError

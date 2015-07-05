"""Handles the XMLRPC server communication"""

import json
import sys
import urllib2
import xmlrpclib

import click

from vcl_client import cfg

REQUEST_ENDPOINT = 'XMLRPCaddRequest'
IMAGES_ENDPOINT = 'XMLRPCgetImages'
REQUEST_LIST_ENDPOINT = 'XMLRPCgetRequestIds'
TEST_ENDPOINT = 'XMLRPCtest'


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
    return xmlrpclib.loads(raw_xml)


def request(image_id, start, length, timeout):
    """Calls the API and throws an error if request isn't successful."""
    params = (image_id, start, length, timeout)
    response = call_api(REQUEST_ENDPOINT, params)
    status = response[0][0]['status']

    if status != 'success':
        raise RuntimeError("Got unknown status: %s. Full response: %s."
                           % (status, response))


def images(filter_term=None, refresh=False):
    """Calls the API and returns a list of images."""
    cached_image_list = cfg.get_conf(cfg.IMAGE_LIST_KEY)

    if refresh or not cached_image_list:
        response = call_api(IMAGES_ENDPOINT, ())
        all_image_data = response[0][0]
        all_images = [[i['id'], i['name']] for i in all_image_data]

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


def request_list():
    """Calls the API and returns a list of requests."""
    response = call_api(REQUEST_LIST_ENDPOINT, ())
    all_request_data = response[0][0]['requests']

    if all_request_data:
        return [
            [
                r['imageid'],
                r['imagename'],
                r['state'],
                r['ostype'],
                r['OS']
            ]
            for r in all_request_data
        ]
    else:
        return None


def test_call():
    """Calls a test API method."""
    response = call_api(TEST_ENDPOINT, ())
    status = response[0][0]['status']

    if status != 'success':
        raise ValueError

"""Helper functions for the rest of the client."""

import os
import time
import socket
import sys
import xmlrpclib

import click
import paramiko
import tabulate

from lib import interactive
from vcl_client import api
from vcl_client import cfg

ACTIVE_STATES = ['reserved', 'inuse']
CHECK_TIMEOUT = 15
HEADERS = {
    'image': ['ID', 'Name'],
    'request': ['Image ID', 'Name', 'State', 'OS Type', 'OS', 'Request ID'],
    'activerequest': ['Request ID', 'Name']
}
REQUEST_STATE_IDX = 2
REQUEST_NAME_IDX = 1
REQUEST_ID_IDX = 5
SSH_TIMEOUT = 2


def auto_connect(request_id):
    """Connects to the request given the connection details."""
    ip_addr, user, _, connect_methods = api.request_details(request_id)
    connect_method = choose_connect_method(connect_methods)
    click.echo('Connecting to %s via %s...' % (ip_addr, connect_method))

    if connect_method == 'SSH (Secure Shell) on Port 22':
        if os.name == 'nt':
            click.secho("Auto SSH connections aren't supported on Windows.")
            print_connection_details(request_id)
            return

        click.echo('Checking if request is available...')
        # Retry until IP is available
        for _ in range(5):
            try:
                initialize_ssh(ip_addr, user)
                break
            except socket.error as error:
                if 'No route to host' in error.strerror:
                    time.sleep(SSH_TIMEOUT)
                else:
                    handle_error(error.strerror)
    else:
        raise RuntimeError(
            "Connection method '%s' is unsupported." % connect_method)


def check_request_status(request_id):
    """Checks the status of a request and reports when it is ready."""
    while True:
        click.echo('Checking status...   ', nl=False)
        status, time_left = api.request_status(request_id)

        if status == 'ready':
            click.secho('Request is ready!\n', fg='green')
            break
        elif status == 'loading':
            minute = minute_spelling(time_left)
            click.secho("%s %s left." % (time_left, minute), fg='cyan')
        else:
            handle_error("Received status '%s'." % status)

        time.sleep(CHECK_TIMEOUT)


def choose_active_request():
    """Gets active requests and prompts user to choose one."""
    try:
        active_requests = get_active_requests()
    except RuntimeError as error:
        handle_error(error.message)
        return

    if len(active_requests) == 1:
        request_id = active_requests[0][0]
    else:
        click.echo('Active requests:')
        for idx, request in enumerate(active_requests, start=1):
            click.echo("  %s. %s (id: %s)" % (idx, request[1], request[0]))
        selected_request = click.prompt('Enter a number', type=int)
        request_id = active_requests[selected_request - 1][0]

    return request_id


def choose_connect_method(connect_methods):
    """Returns a connection method to use for connecting to a request."""
    if len(connect_methods) == 1:
        return connect_methods[0]['description']

    click.echo('\nAvailable connection methods:')
    for key in connect_methods:
        click.echo("  %s. %s" % (key, connect_methods[key]['description']))

    selected_method = click.prompt('Enter a number', type=int)
    return connect_methods[str(selected_method)]['description']


def cli_print_table(to_print, data_type):
    """Formats a list into a table suitable for CLI output."""
    if data_type not in HEADERS:
        raise ValueError("Header '%s' not recognized." % data_type)

    table = tabulate.tabulate(to_print, headers=HEADERS[data_type])
    click.echo(table)


def get_active_requests():
    """Gets list of requests that can be connected to."""
    all_requests = api.request_list()

    if not all_requests:
        raise RuntimeError('No active requests to connect to.')

    active_requests = [
        [
            r[REQUEST_ID_IDX],
            r[REQUEST_NAME_IDX]
        ]
        for r in all_requests if r[REQUEST_STATE_IDX] in ACTIVE_STATES
        ]

    if not active_requests:
        raise RuntimeError('No active requests to connect to.')

    return active_requests


def get_image_id(image):
    """Returns the image ID given either the ID itself or an image name."""
    if is_number(image):
        return image

    try:
        possible_images = api.images(filter_term=image)
    except ValueError as error:
        click.echo("Error: %s" % error.message)
        return

    if len(possible_images) == 1:
        image = possible_images[0][0]
    else:
        cli_print_table(possible_images, 'image')
        image = click.prompt(
            '\nMultiple matches found. Please enter image ID', type=int)

    return image


def get_ssh_client(ip_addr, user):
    """Returns an SSH client to either execute commands are enter session."""
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ip_addr, username=user, password=cfg.get_password())

    return client


def handle_error(message):
    """Prints error message and exits with an error code."""
    click.secho("ERROR: %s" % message, err=True, fg='red')
    sys.exit(1)


def initialize_ssh(ip_addr, user):
    """Initializes an SSH connection to a given host."""
    click.clear()

    client = get_ssh_client(ip_addr, user)
    channel = client.invoke_shell()

    interactive.interactive_shell(channel)

    # Clean up
    channel.close()
    client.close()


def is_number(string):
    """Returns true if a string can be successfully cast into a number."""
    try:
        float(string)
        return True
    except ValueError:
        return False


def minute_spelling(time_left):
    """If there is only 1 minute left, don't pluralize 'minute'."""
    if time_left == 1:
        return 'minute'
    else:
        return 'minutes'


def print_connection_details(request_id):
    """Prints request connection details."""
    ip_addr, user, password, _ = api.request_details(request_id)
    password = '(your campus password)' if not password else password

    click.echo('\nConnection details:')
    click.echo(' - IP address: %s' % ip_addr)
    click.echo(' - Username: %s' % user)
    click.echo(' - Password: %s' % password)


def validate_credentials():
    """Calls a test API method to validate credentials."""
    try:
        api.test_call()
    except (xmlrpclib.Fault, ValueError):
        raise ValueError('Endpoint did not accept credentials.')
    except:
        raise ValueError('Credentials or endpoint invalid.')

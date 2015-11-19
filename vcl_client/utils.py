"""Helper functions for the rest of the client."""

import time
import sys
import xmlrpclib
import click
import tabulate
from vcl_client import api

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
        raise RuntimeError('No active requests found.')

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


def handle_error(message):
    """Prints error message and exits with an error code."""
    click.secho("ERROR: %s" % message, err=True, fg='red')
    sys.exit(1)


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
    ssh_connect_string = 'ssh -XC %s@%s' % (user, ip_addr)

    click.echo('\nConnection details:')
    click.echo(' - IP address: %s' % ip_addr)
    click.echo(' - Username: %s' % user)
    click.echo(' - Password: %s' % password)
    click.echo('\nFor SSH: %s' % ssh_connect_string)


def validate_credentials():
    """Calls a test API method to validate credentials."""
    try:
        api.test_call()
    except (xmlrpclib.Fault, ValueError):
        raise ValueError('Endpoint did not accept credentials.')
    except:
        raise ValueError('Credentials or endpoint invalid.')

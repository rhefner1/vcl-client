"""Helper functions for the rest of the client."""

import time
import sys
import xmlrpclib

import click
import tabulate

from vcl_client import api

CHECK_TIMEOUT = 15
HEADERS = {
    'image': ['ID', 'Name'],
    'request': ['Image ID', 'Name', 'State', 'OS Type', 'OS', 'Request ID']
}


def check_request_status(request_id):
    """Checks the status of a request and reports when it is ready."""
    while True:
        click.echo('Checking status...   ', nl=False)
        status, time_left = api.request_status(request_id)

        if status == 'ready':
            click.secho('Request is ready!', fg='green')
            print_connection_details(request_id)
            break
        elif status == 'loading':
            minute = minute_spelling(time_left)
            click.secho("%s %s left." % (time_left, minute), fg='cyan')
        else:
            handle_error("Received status '%s'." % status)

        time.sleep(CHECK_TIMEOUT)


def cli_print_table(to_print, data_type):
    """Formats a list into a table suitable for CLI output."""
    if data_type not in HEADERS:
        raise ValueError("Header '%s' not recognized." % data_type)

    table = tabulate.tabulate(to_print, headers=HEADERS[data_type])
    click.echo(table)


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
    click.echo('Retrieving connection details...')

    ip_address, user, password = api.request_details(request_id)
    click.echo('\nConnection details:')
    click.echo(' - IP address: %s' % ip_address)
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

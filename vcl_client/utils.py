"""Helper functions for the rest of the client."""

import os
import time
import sys
import xmlrpclib

import click
import tabulate

from vcl_client import api

CHECK_TIMEOUT = 15
SSH_TIMEOUT = 2

HEADERS = {
    'image': ['ID', 'Name'],
    'request': ['Image ID', 'Name', 'State', 'OS Type', 'OS', 'Request ID']
}
SSH_NIX = "ssh -YC {user}@{ip_addr}"


def auto_connect(request_id):
    """Connects to the request given the connection details."""
    ip_addr, user, _, connect_methods = api.request_details(request_id)
    connect_method = choose_connect_method(connect_methods)

    if connect_method == 'SSH (Secure Shell) on Port 22':
        if os.name == 'nt':
            click.secho("Auto SSH connections aren't supported on Windows.")
            print_connection_details(request_id)
            return

        click.echo('\nConnecting to %s via %s.' % (ip_addr, connect_method))
        click.echo('Waiting for IP address to become available...')

        # Retry until IP is available
        while True:
            ssh_command = SSH_NIX.format(user=user, ip_addr=ip_addr)
            response = os.system(ssh_command)
            if response == 0:
                break
            else:
                time.sleep(SSH_TIMEOUT)
    else:
        raise RuntimeError(
            "Connection method '%s' is unsupported." % connect_method)

def check_request_status(request_id):
    """Checks the status of a request and reports when it is ready."""
    while True:
        click.echo('Checking status...   ', nl=False)
        status, time_left = api.request_status(request_id)

        if status == 'ready':
            click.secho('Request is ready!', fg='green')
            break
        elif status == 'loading':
            minute = minute_spelling(time_left)
            click.secho("%s %s left." % (time_left, minute), fg='cyan')
        else:
            handle_error("Received status '%s'." % status)

        time.sleep(CHECK_TIMEOUT)


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

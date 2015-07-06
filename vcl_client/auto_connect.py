"""Helper functions to connect to a request."""

import click

from vcl_client import api
from vcl_client.connect_methods import rdp
from vcl_client.connect_methods import ssh
from vcl_client import utils


def auto_connect(request_id):
    """Connects to a request via a chosen method."""
    ip_addr, user, password, connect_methods = api.request_details(request_id)
    connect_method = choose_connect_method(connect_methods)
    click.echo('Connecting to %s via %s...' % (ip_addr, connect_method))

    if connect_method == 'SSH (Secure Shell) on Port 22':
        try:
            ssh.handle_ssh(ip_addr, user)
        except RuntimeError as error:
            print_connection_details(request_id)
            utils.handle_error(error.message)
    elif connect_method == 'Remote Desktop':
        try:
            rdp.handle_rdp(request_id, ip_addr, user, password)
        except RuntimeError as error:
            print_connection_details(request_id)
            utils.handle_error(error.message)
    else:
        raise RuntimeError(
            "Connection method '%s' is unsupported." % connect_method)


def choose_connect_method(connect_methods):
    """Returns a connection method to use for connecting to a request."""
    if len(connect_methods) == 1:
        return connect_methods[0]['description']

    click.echo('\nAvailable connection methods:')
    for key in connect_methods:
        click.echo("  %s. %s" % (key, connect_methods[key]['description']))

    selected_method = click.prompt('Enter a number', type=int)
    return connect_methods[str(selected_method)]['description']


def print_connection_details(request_id):
    """Prints request connection details."""
    ip_addr, user, password, _ = api.request_details(request_id)
    password = '(your campus password)' if not password else password

    click.echo('\nConnection details:')
    click.echo(' - IP address: %s' % ip_addr)
    click.echo(' - Username: %s' % user)
    click.echo(' - Password: %s' % password)

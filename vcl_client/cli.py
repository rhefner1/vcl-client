"""Entry point for CLI access."""

import click

from vcl_client import api
from vcl_client import cfg
from vcl_client import auto_connect
from vcl_client import utils


@click.group()
def vcl():
    """Creates and manages VMs hosted by the Apache VCL service."""


@vcl.command(name='request')
@click.argument('image')
@click.option('--no-status',
              is_flag=True,
              help='Do not check status of request.')
@click.option('--no-connect',
              is_flag=True,
              help='Do not automatically connect to request.')
def request_instance(image, no_status, no_connect):
    """Creates a new request for resources."""
    image_id = utils.get_image_id(image)

    try:
        request_id = api.request(image_id)
        click.echo('Request is starting now.\n')
    except RuntimeError as error:
        utils.handle_error(error.message)
        return

    if no_status:
        return

    # If this doesn't raise an exception, request is ready
    utils.check_request_status(request_id)

    if no_connect:
        auto_connect.print_connection_details(request_id)
        return

    try:
        auto_connect.auto_connect(request_id)
    except RuntimeError as error:
        utils.handle_error(error.message)
        return


@vcl.command()
@click.option('--request-id',
              help='ID of the request to connect to.')
@click.option('--details',
              is_flag=True,
              help='Only show the connection details.')
def connect(request_id, details):
    """Establishes a connection with a request."""
    if not request_id:
        request_id = utils.choose_active_request()

    if details:
        auto_connect.print_connection_details(request_id)
        return

    try:
        auto_connect.auto_connect(request_id)
    except RuntimeError as error:
        utils.handle_error(error.message)
        return


@vcl.command()
@click.option('filter_term', '--filter',
              default=None,
              help='Filters by name of image.')
@click.option('--refresh',
              is_flag=True,
              help='Requests a refreshed image list from server.')
def images(filter_term, refresh):
    """Lists all of the images available in VCL."""
    to_print = api.images(filter_term=filter_term, refresh=refresh)
    utils.cli_print_table(to_print, 'image')


@vcl.command(name='list')
def request_list():
    """Lists the currently running requests."""
    requests = api.request_list()

    if requests:
        utils.cli_print_table(requests, 'request')
    else:
        click.echo('No requests found.')


@vcl.command()
@click.option('--request-id',
              help='ID of the request to connect to.')
def delete(request_id):
    """Deletes a request."""
    if not request_id:
        request_id = utils.choose_active_request()

    msg = "Are you sure you want to delete request %s?" % request_id
    if not click.confirm(msg):
        return

    try:
        api.delete(request_id)
        click.echo("Request %s deleted successfully." % request_id)
    except RuntimeError as error:
        utils.handle_error(error.message)


@vcl.command()
@click.argument('extend_time')
@click.option('--request-id',
              help='ID of the request to connect to.')
def extend(extend_time, request_id):
    """Extends the reservation time on a request."""
    if not request_id:
        request_id = utils.choose_active_request()

    try:
        api.extend(request_id, extend_time)
        click.echo("Request %s extended successfully." % request_id)
    except RuntimeError as error:
        utils.handle_error(error.message)


@vcl.command()
@click.option('--username', prompt=True)
@click.option('--password', prompt=True, hide_input=True)
@click.option('--endpoint', prompt=True, default=cfg.DEFAULT_ENDPOINT)
def config(username, password, endpoint):
    """Initial setup of VCL settings."""
    try:
        cfg.vcl_conf(username, password, endpoint)
        utils.validate_credentials()
    except ValueError as error:
        utils.handle_error(error.message)

    click.echo('Credentials and endpoint validated and recorded.')


if __name__ == '__main__':
    vcl()

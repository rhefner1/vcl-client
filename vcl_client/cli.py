"""Entry point for CLI access."""

import click

from vcl_client import api
from vcl_client import cfg
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
        click.echo('\nRequest is starting now.')
    except RuntimeError as error:
        utils.handle_error(error.message)
        return

    if no_status:
        return

    # If this doesn't raise an exception, request is ready
    utils.check_request_status(request_id)

    if no_connect:
        utils.print_connection_details(request_id)
        return

    try:
        utils.auto_connect(request_id)
    except RuntimeError as error:
        utils.handle_error(error.message)
        return


def ssh():
    """Establishes an SSH connection with a request."""
    pass


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


def delete():
    """Deletes a request."""
    pass


def extend():
    """Extends the reservation time on a request."""
    pass


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

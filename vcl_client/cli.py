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
@click.option('--start',
              default='now',
              help='UNIX timestamp for the start of the reservation.')
@click.option('--length',
              default=480,
              help='Length of the reservation in minutes.')
@click.option('--timeout',
              default=True,
              help='Timeout if user inactivity is detected.')
def request_instance(image, start, length, timeout):
    """Creates a new request for virtual computing resources."""
    image_id = utils.get_image_id(image)
    params = (image_id, start, length, 0 if timeout else 1)
    try:
        api.request(params)
    except RuntimeError as error:
        click.echo("ERROR: %s" % error.message)

    click.echo('Success: Request is starting now.')


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
        click.echo("Error: %s" % error.message)

    click.echo('Credentials and endpoint validated and recorded.')


if __name__ == '__main__':
    vcl()

"""Entry point for CLI access."""

import click
import tabulate
import keyring

from vcl_client import cfg
from vcl_client import request
from vcl_client import utils

IMAGE_HEADERS = ['ID', 'Name']
REQUEST_HEADERS = ['Image ID', 'Name', 'State', 'OS Type', 'OS']


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
    utils.auth_check()

    if not utils.is_number(image):
        try:
            possible_images = request.images(filter_term=image)
        except ValueError as error:
            click.echo("Error: %s" % error.message)
            return

        if len(possible_images) == 1:
            image = possible_images[0][0]
        else:
            click.echo(tabulate.tabulate(possible_images,
                                         headers=IMAGE_HEADERS))
            image = click.prompt(
                '\nMultiple matches found. Please enter image ID', type=int)

    params = (image, start, length, 0 if timeout else 1)
    try:
        request.boot(params)
        click.echo('Success: Request is starting now.')
    except RuntimeError as error:
        click.echo("ERROR: %s" % error.message)


@vcl.command()
def ssh():
    """Establishes an SSH connection with a request."""
    pass


@vcl.command()
@click.option('--username', prompt=True)
@click.option('--password', prompt=True, hide_input=True)
@click.option('--endpoint', prompt=True, default=cfg.DEFAULT_ENDPOINT)
def config(username, password, endpoint):
    """Initial setup of VCL settings."""
    cfg.set_conf(cfg.USERNAME_KEY, username)
    keyring.set_password('system', username, password)
    cfg.set_conf(cfg.ENDPOINT_KEY, endpoint)

    try:
        request.validate_credentials()
        cfg.write_conf()

        click.echo('Credentials and endpoint validated and recorded.')
    except ValueError as error:
        click.echo("Error: %s" % error.message)


@vcl.command(name='list')
def request_list():
    """Lists the currently running requests."""
    utils.auth_check()
    requests = request.request_list()

    if requests:
        requests = [
            [
                r['imageid'],
                r['imagename'],
                r['state'],
                r['ostype'],
                r['OS']
            ]
            for r in requests
        ]
        click.echo(tabulate.tabulate(requests, headers=REQUEST_HEADERS))
    else:
        click.echo('No requests found.')


def extend():
    """Extends the reservation time on a request."""
    pass


def delete():
    """Deletes a request."""
    pass


@vcl.command()
@click.option('filter_term', '--filter',
              default=None,
              help='Filters by name of image.')
@click.option('--refresh',
              is_flag=True,
              help='Requests a fresh image list from server.')
def images(filter_term, refresh):
    """Lists all of the images available in VCL."""
    utils.auth_check()

    to_print = request.images(filter_term=filter_term, refresh=refresh)
    click.echo(tabulate.tabulate(to_print, headers=IMAGE_HEADERS))


if __name__ == '__main__':
    vcl()

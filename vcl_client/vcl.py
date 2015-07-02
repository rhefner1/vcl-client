"""Entry point for CLI access."""

import json
import sys

import click
import tabulate
import keyring

from vcl_client import request
from vcl_client import cfg


def auth_check():
    """On authenticated calls, checks is user/pass exist."""
    username = cfg.get_conf(cfg.USERNAME_KEY)
    password = cfg.get_password()
    if not username or not password:
        click.echo('Credentials not found. Run `vcl login`.')
        sys.exit(1)


@click.group()
def vcl():
    """Creates and manages VMs hosted by the Apache VCL service."""


@vcl.command()
@click.argument('image_id')
@click.option('--start',
              default='now',
              help='UNIX timestamp for the start of the reservation.')
@click.option('--length',
              default=480,
              help='Length of the reservation in minutes.')
@click.option('--timeout',
              default=True,
              help='Timeout if user inactivity is detected.')
def boot(image_id, start, length, timeout):
    """Starts a request."""
    auth_check()
    params = (image_id,
              start,
              length,
              0 if timeout else 1)
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
def login(username, password):
    """Stores username in conf file and password in memory."""
    cfg.write_conf(cfg.USERNAME_KEY, username)
    keyring.set_password('system', username, password)


@vcl.command(name='list')
def request_list():
    """Lists the currently running requests."""
    requests = request.request_list()

    if requests:
        headers = ['Image ID', 'Name', 'State', 'OS Type', 'OS']
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
        click.echo(tabulate.tabulate(requests, headers=headers))
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
    auth_check()
    cached_image_list = cfg.get_conf(cfg.IMAGE_LIST_KEY)

    if refresh or not cached_image_list:
        all_images = request.images()
        to_print = [[i['id'], i['name']] for i in all_images]

        # Caching response for subsequent queries
        cfg.write_conf(cfg.IMAGE_LIST_KEY, json.dumps(to_print))
    else:
        to_print = json.loads(cached_image_list)

    if filter_term:
        to_print = [image for image in to_print
                    if filter_term.lower() in image[1].lower()]

    headers = ['ID', 'Name']
    click.echo(tabulate.tabulate(to_print, headers=headers))


if __name__ == '__main__':
    vcl()

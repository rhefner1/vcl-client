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


def boot():
    """Starts an instance."""
    pass


def ssh():
    """Establishes an SSH connection with an instance."""
    pass


@vcl.command()
@click.option('--username', prompt=True)
@click.option('--password', prompt=True, hide_input=True)
def login(username, password):
    """Stores username in conf file and password in memory."""
    cfg.write_conf(cfg.USERNAME_KEY, username)
    keyring.set_password('system', username, password)


@vcl.command(name='list')
def instance_list():
    """Lists the currently running instances."""
    instances = request.instance_list()

    if instances:
        headers = ['Image ID', 'Name', 'State', 'OS Type', 'OS']
        instances = [
            [
                r['imageid'],
                r['imagename'],
                r['state'],
                r['ostype'],
                r['OS']
            ] for r in instances]
        click.echo(tabulate.tabulate(instances, headers=headers))
    else:
        click.echo('No instances found.')


def extend():
    """Extends the reservation time on an instance."""
    pass


def delete():
    """Deletes an instance."""
    pass


@vcl.command()
@click.option('--search',
              default=None,
              help='Filters by name of image.')
@click.option('--refresh',
              is_flag=True,
              help='Requests a fresh image list from server.')
def images(search, refresh):
    """Lists all of the images available in VCL."""
    auth_check()
    cached_image_list = cfg.get_conf(cfg.IMAGE_LIST_KEY)

    if refresh or not cached_image_list:
        endpoint = 'XMLRPCgetImages'
        response = request.call_api(endpoint, ())
        all_images = response[0][0]
        to_print = [{'ID': i['id'], 'Name': i['name']} for i in all_images]

        # Caching response for subsequent queries
        cfg.write_conf(cfg.IMAGE_LIST_KEY, json.dumps(to_print))
    else:
        to_print = json.loads(cached_image_list)

    if search:
        to_print = [image for image in to_print
                    if search.lower() in image['Name'].lower()]

    click.echo(tabulate.tabulate(to_print, headers='keys'))


if __name__ == '__main__':
    vcl()

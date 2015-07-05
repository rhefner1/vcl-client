"""Helper functions for the rest of the client."""

import xmlrpclib

import click
import tabulate

from vcl_client import api

HEADERS = {
    'image': ['ID', 'Name'],
    'request': ['Image ID', 'Name', 'State', 'OS Type', 'OS']
}


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


def is_number(string):
    """Returns true if a string can be successfully cast into a number."""
    try:
        float(string)
        return True
    except ValueError:
        return False


def cli_print_table(to_print, data_type):
    """Formats a list into a table suitable for CLI output."""
    if data_type not in HEADERS:
        raise ValueError("Header '%s' not recognized." % data_type)

    table = tabulate.tabulate(to_print, headers=HEADERS[data_type])
    click.echo(table)


def validate_credentials():
    """Calls a test API method to validate credentials."""
    try:
        api.test_call()
    except (xmlrpclib.Fault, ValueError):
        raise ValueError('Endpoint did not accept credentials.')
    except:
        raise ValueError('Credentials or endpoint invalid.')

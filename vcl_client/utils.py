"""Helper functions for the rest of the client."""

import sys

import click

from vcl_client import cfg


def auth_check():
    """On authenticated calls, checks is user/pass exist."""
    username = cfg.get_conf(cfg.USERNAME_KEY)
    password = cfg.get_password()
    if not username or not password:
        click.echo('Credentials not found. Run `vcl config`.')
        sys.exit(1)

def is_number(string):
    """Returns true if a string can be successfully cast into a number."""
    try:
        float(string)
        return True
    except ValueError:
        return False

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

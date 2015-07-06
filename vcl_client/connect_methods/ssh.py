"""Implements the SSH connection method."""

import platform
import time
import socket

import click
import paramiko

from lib import interactive
from vcl_client import cfg

SSH_TIMEOUT = 2


def get_ssh_client(ip_addr, user):
    """Returns an SSH client to either execute commands are enter session."""
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ip_addr, username=user, password=cfg.get_password())

    return client


def handle_ssh(ip_addr, user):
    """Handles the SSH connection method."""
    if platform.system() == 'Windows':
        msg = "SSH connections aren't supported on Windows."
        raise RuntimeError(msg)

    click.echo('Checking if request is available...')
    # Retry until IP is available
    for _ in range(5):
        try:
            start_ssh_shell(ip_addr, user)
            break
        except socket.error as error:
            if 'No route to host' in error.strerror:
                time.sleep(SSH_TIMEOUT)
            else:
                raise


def start_ssh_shell(ip_addr, user):
    """Initializes an SSH interactive shell to a given host."""
    if not click.confirm('Ready to start SSH connection?'):
        return

    click.clear()

    client = get_ssh_client(ip_addr, user)
    channel = client.invoke_shell()

    interactive.interactive_shell(channel)

    # Clean up
    channel.close()
    client.close()

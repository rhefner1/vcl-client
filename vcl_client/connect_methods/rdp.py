"""Implements the RDP connection method."""

import os
import platform
import subprocess

import click

REMMINA_LAUNCH = "remmina -c {path}"
REMMINA_FILE = """
[remmina]
sound=off
sharefolder=
name=VCL
cert_ignore=0
console=0
ssh_enabled=0
exec=
clientname=
colordepth=32
server={ip_addr}
ssh_auth=0
group=
sharesmartcard=0
quality=0
username={user}
ssh_charset=
ssh_loopback=0
password=
ssh_username=
gateway_server=
disablepasswordstoring=0
execpath=
gateway_usage=0
resolution=
security=
domain=
precommand=
ssh_server=
shareprinter=0
protocol=RDP
disableclipboard=0
ssh_privatekey=
window_maximize=1
viewmode=1
"""


def clean_rdp_files():
    """Removes the temporary RDP files."""
    subprocess.call('rm -f ~/.vcl_*.remmina', shell=True)


def handle_rdp(request_id, ip_addr, user, password):
    """Handles the RDP connection method."""
    clean_rdp_files()
    path = write_rdp_file(request_id, ip_addr, user, password)
    launch_rdp(path, password)


def launch_rdp(path, password):
    """Launches RDP file in OS-specific program."""
    confirm_msg = "Login password is: %s  Ready to start RDP connection?"
    if not click.confirm(confirm_msg % password):
        return

    host_os = platform.system()

    if host_os == 'Linux':
        launch_cmd = REMMINA_LAUNCH.format(path=path)
    else:
        raise RuntimeError("RDP not supported on OS: '%s'" % host_os)

    subprocess.Popen(launch_cmd, shell=True)


def write_rdp_file(request_id, ip_addr, user, password):
    """Writes an RDP file and returns the path."""
    host_os = platform.system()
    replacements = {
        'ip_addr': ip_addr,
        'user': user,
        'password': password
    }

    if host_os == 'Linux':
        contents = REMMINA_FILE.format(**replacements)
    else:
        raise RuntimeError("RDP not supported on OS: '%s'" % host_os)

    path = os.path.expanduser('~/.vcl_%s.remmina' % request_id)
    with open(path, 'w') as rdp_file:
        rdp_file.write(contents)
        rdp_file.close()

    return path

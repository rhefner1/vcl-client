"""Handles reading and writing to the config file."""

import ConfigParser
import os

import keyring

CONFIG_FILE_PATH = os.path.expanduser('~/.vcl.conf')
CONF_SECTION = 'vcl'
DEFAULT_ENDPOINT = 'https://vcl.ncsu.edu/scheduling/index.php?mode=xmlrpccall'
ENDPOINT_KEY = 'xmlrpc_base_url'
IMAGE_LIST_KEY = 'image_list'
USERNAME_KEY = 'username'

CONF = ConfigParser.ConfigParser()
CONF.read(CONFIG_FILE_PATH)


def vcl_conf(username, password, endpoint):
    """Sets the initial VCL config options."""
    if not CONF.has_section(CONF_SECTION):
        CONF.add_section(CONF_SECTION)

    set_conf(USERNAME_KEY, username)
    set_password(password)
    set_conf(ENDPOINT_KEY, endpoint)

    write_conf()


def get_conf(key):
    """Gets a key from the config file"""
    try:
        return CONF.get(CONF_SECTION, key)
    except (ConfigParser.NoOptionError, ConfigParser.NoSectionError):
        return None


def set_conf(key, data, write=False):
    """Writes key:data to the config file."""
    CONF.set(CONF_SECTION, key, data)

    if write:
        write_conf()


def write_conf():
    """Writes configuration changes to the filesystem."""
    config_file = open(CONFIG_FILE_PATH, 'w')
    CONF.write(config_file)
    config_file.close()


def get_password():
    """Gets the password from the keyring."""
    try:
        return keyring.get_password('system', get_conf(USERNAME_KEY))
    except AttributeError:
        return None


def set_password(password):
    """Stores the password in the keyring."""
    username = get_conf(USERNAME_KEY)
    if not username:
        raise ValueError('Cannot set password without a username specified.')

    keyring.set_password('system', username, password)

"""Handles reading and writing to the config file."""

import ConfigParser
import os

import keyring

CONFIG_FILE_PATH = os.path.expanduser('~/.vcl.conf')
CONF_SECTION = 'vcl'

DEFAULT_ENDPOINT = 'https://vcl.ncsu.edu/scheduling/index.php?mode=xmlrpccall'
BASE_URL_KEY = 'xmlrpc_base_url'
IMAGE_LIST_KEY = 'image_list'
USERNAME_KEY = 'username'

CONF = ConfigParser.ConfigParser()
CONF.read(CONFIG_FILE_PATH)


def initialize_config():
    """Sets the initial config file options."""
    if not CONF.has_section(CONF_SECTION):
        CONF.add_section(CONF_SECTION)
        write_conf(BASE_URL_KEY, DEFAULT_ENDPOINT)


def get_conf(key):
    """Gets a key from the config file"""
    try:
        return CONF.get(CONF_SECTION, key)
    except ConfigParser.NoOptionError:
        return None


def write_conf(key, data):
    """Writes key:data to the config file."""
    config_file = open(CONFIG_FILE_PATH, 'w')

    CONF.set(CONF_SECTION, key, data)
    CONF.write(config_file)
    config_file.close()


def get_password():
    """Gets the password from the keyring."""
    try:
        return keyring.get_password('system', get_conf(USERNAME_KEY))
    except AttributeError:
        return None


initialize_config()

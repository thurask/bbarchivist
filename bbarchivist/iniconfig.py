#!/usr/bin/env python3
"""This module is used for generic configuration parsing."""

import configparser  # config parsing, duh
import os  # path work

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "2016-2017 Thurask"


def config_emptysection(config, section):
    """
    Create empty configuration section.

    :param config: Configuration dictionary.
    :type config: configparser.ConfigParser

    :param section: Section of ini file to return.
    :type section: str
    """
    if not config.has_section(section):
        config[section] = {}
    return config


def config_homepath(homepath):
    """
    Fix path for ini file.

    :param homepath: Path to ini file.
    :type homepath: str
    """
    if homepath is None:
        homepath = os.path.expanduser("~")
    return homepath


def config_conffile(conffile):
    """
    Create ini file if it doesn't exist.

    :param conffile: Path to config ini file.
    :type conffile: str
    """
    if not os.path.exists(conffile):
        open(conffile, 'w').close()


def config_location(homepath=None):
    """
    Return config location.

    :param homepath: Folder containing ini file. Default is user directory.
    :type homepath: str
    """
    homepath = config_homepath(homepath)
    conffile = os.path.join(homepath, "bbarchivist.ini")
    return conffile


def generic_preamble(section, homepath=None):
    """
    Read a ConfigParser file, return whole config.

    :param section: Section of ini file to return.
    :type section: str

    :param homepath: Folder containing ini file. Default is user directory.
    :type homepath: str
    """
    config = configparser.ConfigParser()
    conffile = config_location(homepath)
    config_conffile(conffile)
    config.read(conffile)
    config = config_emptysection(config, section)
    return config


def generic_loader(section, homepath=None):
    """
    Read a ConfigParser file, return section.

    :param section: Section of ini file to return.
    :type section: str

    :param homepath: Folder containing ini file. Default is user directory.
    :type homepath: str
    """
    config = generic_preamble(section, homepath)
    ini = config[section]
    return ini


def generic_writer(section, resultdict, homepath=None):
    """
    Write a ConfigParser file.

    :param section: Section of ini file to write.
    :type section: str

    :param resultdict: Dictionary of configs: {key: value}
    :type resultdict: dict({str, bool})

    :param homepath: Folder containing ini file. Default is user directory.
    :type homepath: str
    """
    config = generic_preamble(section, homepath)
    for key, value in resultdict.items():
        config.set(section, key, str(value))
    conffile = config_location(homepath)
    with open(conffile, "w") as configfile:
        config.write(configfile)

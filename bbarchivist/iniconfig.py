#!/usr/bin/env python3
"""This module is used for generic configuration parsing."""

import configparser  # config parsing, duh
import os  # path work
import shutil  # moving
from appdirs import AppDirs  # folders

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "2016-2018 Thurask"


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


def config_homepath(homepath, logpath=False):
    """
    Fix path for ini file.

    :param homepath: Path to ini file.
    :type homepath: str

    :param logpath: True if processing log folder, False if processing data files. Default is False.
    :type logpath: bool
    """
    if homepath is None:
        rawpath = config_rawdir(homepath, logpath)
        homepath = process_homepath(rawpath, logpath)
    return homepath


def config_rawdir(homepath, logpath=False):
    """
    Get new config dir.

    :param homepath: Path to data directory.
    :type homepath: str

    :param logpath: True if processing log folder, False if processing data files. Default is False.
    :type logpath: bool
    """
    apdi = AppDirs("bbarchivist", "bbarchivist")
    if logpath:
        rawpath = apdi.user_log_dir
    else:
        rawpath = apdi.user_data_dir
    return rawpath


def process_homepath(homepath, logpath=False):
    """
    Prepare homepath if it doesn't exist.

    :param homepath: Path to data directory.
    :type homepath: str

    :param logpath: True if processing log folder, False if processing data files. Default is False.
    :type logpath: bool
    """
    if not os.path.exists(homepath):
        os.makedirs(homepath)
    if logpath:
        migrate_logs(homepath)
    else:
        migrate_files(homepath)
    return homepath


def migrate_files(homepath):
    """
    Prepare ini file and SQL DB for new homepath.

    :param homepath: Path to data directory.
    :type homepath: str
    """
    files = ("bbarchivist.ini", "bbarchivist.db")
    for file in files:
        oldfile = os.path.join(os.path.expanduser("~"), file)
        newfile = os.path.join(homepath, file)
        conditional_move(oldfile, newfile)


def migrate_logs(homepath):
    """
    Prepare log directory for new homepath.

    :param homepath: Path to data directory.
    :type homepath: str
    """
    olddir = os.path.join(os.path.expanduser("~"), "lookuplogs")
    if os.path.exists(olddir):
        log_move(olddir, homepath)
        shutil.rmtree(olddir)


def conditional_move(oldfile, newfile):
    """
    Migrate from user directory to dedicated appdata/.local dir.

    :param oldfile: Path to old config file.
    :type oldfile: str

    :param newfile: Path to new config file.
    :type newfile: str
    """
    if os.path.exists(oldfile):
        if os.path.exists(newfile):
            os.remove(oldfile)  # remove old
        else:
            shutil.move(oldfile, newfile)  # migrate to new


def log_move(olddir, homepath):
    """
    Migrate logs from user directory subfolder to dedicated appdata/.local dir.

    :param olddir: Path to old log dir.
    :type olddir: str

    :param homepath: Path to new log directory.
    :type homepath: str
    """
    oldlogs = [os.path.join(olddir, logfile) for logfile in os.listdir(olddir)]
    if oldlogs:
        for log in oldlogs:
            shutil.move(log, os.path.abspath(homepath))


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

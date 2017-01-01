#!/usr/bin/env python3
"""This module is used for JSON tools."""

import os  # path work
try:
    import simplejson as json
except ImportError:
    import json
import glob  # filenames
import sys  # frozen status
from bbarchivist import bbconstants  # file location
from bbarchivist import decorators  # enter to exit
from bbarchivist import utilities  # lprint

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "2015-2017 Thurask"


def grab_json():
    """
    Figure out where JSON is, local or system-supplied.
    """
    jfile = None
    try:
        jfile = glob.glob(os.path.join(os.getcwd(), "bbconstants.json"))[0]
    except IndexError:
        jfile = bbconstants.JSONFILE
    return os.path.abspath(jfile)


def load_json(table, jfile=None):
    """
    Load JSON file, return specific table (dict or list).

    :param table: Name of sub-structure to return.
    :type table: str

    :param jfile: Path to JSON file.
    :type jfile: str
    """
    if jfile is None:
        jfile = grab_json()
    with open(jfile) as thefile:
        data = json.load(thefile)
    return data[table]


def extract_cert(table, device):
    """
    Extract PTCRB info from a list of dicts.

    :param table: List of device entries.
    :type table: list(dict)

    :param device: HWID, FCCID or name of device.
    :type device: str
    """
    for key in table:
        keylist = key['hwid'], key['fccid'], key['ptcrbid']
        not_secret = device in key['name'] and 'secret' not in key
        if (device in keylist or not_secret) and key['ptcrbid']:
            device = key['device']
            name = key['name']
            ptcrbid = key['ptcrbid']
            hwid = key['hwid']
            fccid = key['fccid']
            break
    else:
        fubar("NO PTCRBID!")
    return name, ptcrbid, hwid, fccid


def list_available_certs(table):
    """
    List all certified devices in a device table.

    :param table: List of device entries.
    :type table: list(dict)
    """
    for key in table:
        if key['ptcrbid']:
            hwid = "NO HWID" if not key['hwid'] else key['hwid']
            print("{0} {1} - {2} - {3}".format(key['device'], key['name'], hwid, key['fccid']))


def list_devices(table):
    """
    List all devices, certified or not, in a device table.

    :param table: List of device entries.
    :type table: list(dict)
    """
    for key in table:
        hwid = "NO HWID" if not key['hwid'] else key['hwid']
        fccid = "NO FCCID" if not key['fccid'] else key['fccid']
        print("{0} {1} - {2} - {3}".format(key['device'], key['name'], hwid, fccid))


def certchecker_prep(table, device):
    """
    Extract model, family and HWID from a device table.

    :param table: List of device entries.
    :type table: list(dict)

    :param device: HWID, FCCID or name of device.
    :type device: str
    """
    for key in table:
        if 'secret' not in key and key['name'] == device:
            model = key['device']
            family = key['family']
            hwid = key['hwid']
            break
    else:
        fubar("INVALID DEVICE!")
    return model, family, hwid


def read_family(table, device):
    """
    Get all devices of a given family in a device table.

    :param table: List of device entries.
    :type table: list(dict)

    :param device: HWID, FCCID or name of device.
    :type device: str
    """
    famlist = [key['fccid'] for key in table if key['ptcrbid'] and key['device'] == device]
    return famlist


def list_family(table):
    """
    List all valid (certified) families in a device table.

    :param table: List of device entries.
    :type table: list(dict)
    """
    famlist = list({key['device'] for key in table if 'secret' not in key and key['ptcrbid']})
    utilities.lprint(famlist)


def fubar(message):
    """
    What to do when things go bad.

    :param message: Error message.
    :type message: str
    """
    print(message)
    decorators.enter_to_exit(True)
    if not getattr(sys, 'frozen', False):
        raise SystemExit

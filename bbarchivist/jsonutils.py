#!/usr/bin/env python3
#pylint: disable = I0011, R0201, W0613, C0301, R0913, R0912, R0914, R0915
"""This module is used for JSON tools."""

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "2015 Thurask"

import os  # path work
import json  # duh
import glob  # filenames
from bbarchivist import bbconstants  # file location

def grab_json():
    """
    Figure out where JSON is, local or system-supplied.
    """
    jfile = None
    try:
        jfile = glob.glob(os.path.join(os.getcwd(), "bbconstants.json"))[0]  # local JSON
    except IndexError:
        jfile = bbconstants.JSONFILE  # system JSON
    return os.path.abspath(jfile)


def load_json(table, jfile=None):
    """
    Load JSON file, return specific table as dict.

    :param table: Name of sub-structure to return
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
        if (device in (keylist) or (device in key['name'] and 'secret' not in key)) and key['ptcrbid']:
            device = key['device']
            name = key['name']
            ptcrbid = key['ptcrbid']
            hwid = key['hwid']
            fccid = key['fccid']
            break
    else:
        print("NO PTCRB ID!")
        raise SystemExit
    return name, ptcrbid, hwid, fccid


def list_available_certs(table):
    """
    List all certified devices in a device table.

    :param table: List of device entries.
    :type table: list(dict)
    """
    for key in table:
        if key['ptcrbid']:
            if not key['hwid']:
                hwid = "NO HWID"
            else:
                hwid = key['hwid']
            print("{0} {1} - {2} - {3}".format(key['device'], key['name'], hwid, key['fccid']))


def list_devices(table):
    """
    Lists all devices, certified or not, in a device table.

    :param table: List of device entries.
    :type table: list(dict)
    """
    for key in table:
        if not key['hwid']:
            hwid = "NO HWID"
        else:
            hwid = key['hwid']
        if not key['fccid']:
            fccid = "NO FCCID"
        else:
            fccid = key['fccid']
        print("{0} {1} - {2} - {3}".format(key['device'], key['name'], hwid, fccid))

#!/usr/bin/env python3
"""This module is used for JSON tools."""

import glob  # filenames
import os  # path work
import sys  # frozen status

from bbarchivist import bbconstants  # file location
from bbarchivist import decorators  # enter to exit
from bbarchivist import utilities  # lprint

try:
    import simplejson as json
except ImportError:
    import json

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "2015-2019 Thurask"


def grab_json(filename):
    """
    Figure out where JSON is, local or system-supplied.

    :param filename: Desired JSON database name.
    :type filename: str
    """
    jfile = None
    try:
        jfile = glob.glob(os.path.join(os.getcwd(), "json"))[0]
    except IndexError:
        jfile = bbconstants.JSONDIR
    jfile = os.path.join(jfile, "{0}.json".format(filename))
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
        jfile = grab_json(table)
    with open(jfile) as thefile:
        data = json.load(thefile)
    return data[table]


def extract_cert_secret(key, device):
    """
    Check if device is marked as secret.

    :param key: Device entry.
    :type key: dict

    :param device: HWID, FCCID or name of device.
    :param device: str
    """
    not_secret = device in key['name'] and 'secret' not in key
    return not_secret


def extract_cert_check(key, device, not_secret):
    """
    Check function for extracting PTCRB info.

    :param key: Device entry.
    :type key: dict

    :param device: HWID, FCCID or name of device.
    :type device: str

    :param not_secret: If device is not market as secret.
    :type not_secret: bool
    """
    keylist = key['hwid'], key['fccid'], key['ptcrbid']
    goforit = (device in keylist or not_secret) and key['ptcrbid']
    return goforit


def extract_cert(table, device):
    """
    Extract PTCRB info from a list of dicts.

    :param table: List of device entries.
    :type table: list(dict)

    :param device: HWID, FCCID or name of device.
    :type device: str
    """
    for key in table:
        not_secret = extract_cert_secret(key, device)
        goforit = extract_cert_check(key, device, not_secret)
        if goforit:
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


def list_prds(table):
    """
    List all PRDs in a PRD table.

    :param table: Dictionary of device : PRD list pairs.
    :type table: dict(str: list)
    """
    for key in table.keys():
        print("~{0}~".format(key))
        for prd in table[key]:
            print(prd)


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

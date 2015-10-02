#!/usr/bin/env python3
#pylint: disable = I0011, R0201, W0613, C0301, R0913, R0912, R0914, R0915
"""Checks certifications for a given device."""

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "2015 Thurask"

from bbarchivist import bbconstants  # versions/constants
from bbarchivist import networkutils  # check function
from bbarchivist import utilities  # json
from json import load  # read json
import argparse  # parse arguments
import sys  # load arguments


def grab_args():
    """
    Parse arguments from argparse/questionnaire.

    Invoke :func:`certchecker.certchecker_main` with arguments.
    """
    if len(sys.argv) > 1:
        parser = argparse.ArgumentParser(
            prog="bb-certchecker",
            description="Checks certifications for a given device.",
            epilog="http://github.com/thurask/bbarchivist")
        parser.add_argument(
            "-v",
            "--version",
            action="version",
            version="%(prog)s " + bbconstants.VERSION)
        parser.add_argument("device", help="FCCID/HWID/model number")
        parser.set_defaults()
        args = parser.parse_args(sys.argv[1:])
        certchecker_main(args.device)
    else:
        device = input("DEVICE (SXX100-#/FCCID/HWID): ")
        print(" ")
        certchecker_main(device)
        smeg = input("Press Enter to exit")
        if smeg or not smeg:
            raise SystemExit


def certchecker_main(device):
    """
    Wrap around :mod:`bbarchivist.networkutils` certification checking.

    :param device: Hardware ID, PTCRB ID, FCC ID or model number.
    :type device: str
    """
    with open(utilities.grab_json()) as thefile:
        data = load(thefile)
    data = data['devices']
    device = device.upper()
    for key in data:
        keylist = key['hwid'], key['fccid'], key['ptcrbid']
        if (device in (keylist) or (device in key['name'] and 'secret' not in key)) and key['ptcrbid']:
            device = key['device']
            name = key['name']
            ptcrbid = key['ptcrbid']
            break
    else:
        print("NO PTCRB ID!")
        raise SystemExit
    print("~~~CERTCHECKER VERSION", bbconstants.VERSION + "~~~")
    print("DEVICE:", device.upper())
    print("VARIANT:", name.upper())
    print("\nCHECKING CERTIFICATIONS...\n")
    certlist = networkutils.ptcrb_scraper(ptcrbid)
    for item in certlist:
        print(item)

if __name__ == "__main__":
    grab_args()

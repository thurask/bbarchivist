#!/usr/bin/env python3
#pylint: disable = I0011, R0201, W0613, C0301, R0913, R0912, R0914, R0915
"""Checks certifications for a given device."""

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "2015 Thurask"

from bbarchivist import bbconstants  # versions/constants
from bbarchivist import networkutils  # check function
from bbarchivist import jsonutils  # json
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
        parser.add_argument(
            "device",
            help="FCCID/HWID/model number",
            nargs="?",
            default=None)
        fgroup = parser.add_mutually_exclusive_group()
        fgroup.add_argument(
            "-l",
            "--list",
            dest="list",
            help="List all devices in database",
            action="store_true",
            default=False)
        fgroup.add_argument(
            "-c",
            "--certs",
            dest="certs",
            help="List certified devices in database",
            action="store_true",
            default=False)
        parser.set_defaults()
        args = parser.parse_args(sys.argv[1:])
        if args.list:
            jsonutils.list_devices(jsonutils.load_json('devices'))
        elif args.certs:
            jsonutils.list_available_certs(jsonutils.load_json('devices'))
        elif args.device is None:
            print("NO DEVICE SPECIFIED!")
            raise SystemExit
        else:
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
    data = jsonutils.load_json('devices')
    device = device.upper()
    name, ptcrbid, hwid, fccid = jsonutils.extract_cert(data, device)
    print("~~~CERTCHECKER VERSION", bbconstants.VERSION + "~~~")
    print("DEVICE: {0}".format(device.upper()))
    print("VARIANT: {0}".format(name.upper()))
    if hwid:
        print("HARDWARE ID: {0}".format(hwid.upper()))
    if fccid:
        print("FCC ID: {0}".format(fccid.upper()))
    print("\nCHECKING CERTIFICATIONS...\n")
    certlist = networkutils.ptcrb_scraper(ptcrbid)
    for item in certlist:
        print(item)

if __name__ == "__main__":
    grab_args()

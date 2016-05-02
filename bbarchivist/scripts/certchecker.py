#!/usr/bin/env python3
"""Checks certifications for a given device."""

import sys  # load arguments
from bbarchivist import networkutils  # check function
from bbarchivist import jsonutils  # json
from bbarchivist import scriptutils  # default parser

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "Copyright 2015-2016 Thurask"


def grab_args():
    """
    Parse arguments from argparse/questionnaire.

    Invoke :func:`certchecker.certchecker_main` with arguments.
    """
    if len(sys.argv) > 1:
        datafile = jsonutils.load_json('devices')
        parser = scriptutils.default_parser("bb-certchecker", "Certification scraper")
        parser.add_argument(
            "device",
            help="FCCID/HWID/model #, or family",
            nargs="?",
            default=None)
        parser.add_argument(
            "-f",
            "--family",
            dest="family",
            help="Return all certs of a device family",
            action="store_true",
            default=False)
        fgroup = parser.add_mutually_exclusive_group()
        fgroup.add_argument(
            "-d",
            "--database",
            dest="database",
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
        fgroup.add_argument(
            "-l",
            "--list",
            dest="list",
            help="List families in database",
            action="store_true",
            default=False)
        parser.set_defaults()
        args = parser.parse_args(sys.argv[1:])
        if args.database:
            jsonutils.list_devices(datafile)
        elif args.certs:
            jsonutils.list_available_certs(datafile)
        elif args.list:
            jsonutils.list_family(datafile)
        elif args.family:
            family = jsonutils.read_family(datafile, args.device.upper())
            for ptcrbid in family:
                certchecker_main(ptcrbid)
                print("")
        elif args.device is None:
            print("NO DEVICE SPECIFIED!")
            raise SystemExit
        else:
            certchecker_main(args.device)
    else:
        device = input("DEVICE (SXX100-#/FCCID/HWID): ")
        if not device:
            print("NO DEVICE SPECIFIED!")
            scriptutils.enter_to_exit(True)
            if not getattr(sys, 'frozen', False):
                raise SystemExit
        print(" ")
        certchecker_main(device)
        scriptutils.enter_to_exit(True)


def certchecker_main(device):
    """
    Wrap around :mod:`bbarchivist.networkutils` certification checking.

    :param device: Hardware ID, PTCRB ID, FCC ID or model number.
    :type device: str
    """
    data = jsonutils.load_json('devices')
    device = device.upper()
    name, ptcrbid, hwid, fccid = jsonutils.extract_cert(data, device)
    scriptutils.slim_preamble("CERTCHECKER")
    print("DEVICE: {0}".format(device.upper()))
    print("VARIANT: {0}".format(name.upper()))
    if hwid:
        print("HARDWARE ID: {0}".format(hwid.upper()))
    if fccid:
        print("FCC ID: {0}".format(fccid.upper()))
    print("\nCHECKING CERTIFICATIONS...\n")
    certlist = networkutils.ptcrb_scraper(ptcrbid)
    scriptutils.lprint(certlist)

if __name__ == "__main__":
    grab_args()

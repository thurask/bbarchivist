#!/usr/bin/env python3
"""Checks certifications for a given device."""

import sys  # load arguments
from bbarchivist import decorators  # enter to exit
from bbarchivist import networkutils  # check function
from bbarchivist import jsonutils  # json
from bbarchivist import scriptutils  # default parser
from bbarchivist import utilities  # lprint

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "2015-2017 Thurask"


def grab_args():
    """
    Parse arguments from argparse/questionnaire.

    Invoke :func:`certchecker.certchecker_main` with arguments.
    """
    datafile = jsonutils.load_json('devices')
    if len(sys.argv) > 1:
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
        execute_args(args, datafile)
    else:
        device = scriptutils.questionnaire_device("DEVICE (XXX100-#/FCCID/HWID): ")
        print(" ")
        certchecker_main(device, datafile)
        decorators.enter_to_exit(True)


def execute_args(args, datafile):
    """
    Get args and decide what to do with them.

    :param args: Arguments.
    :type args: argparse.Namespace

    :param datafile: List of device entries.
    :type datafile: list(dict)
    """
    if args.database:
        jsonutils.list_devices(datafile)
    elif args.certs:
        jsonutils.list_available_certs(datafile)
    elif args.list:
        jsonutils.list_family(datafile)
    else:
        execute_args_end(args, datafile)


def execute_args_end(args, datafile):
    """
    Continue the first half.

    :param args: Arguments.
    :type args: argparse.Namespace

    :param datafile: List of device entries.
    :type datafile: list(dict)
    """
    if args.family:
        certchecker_family(args, datafile)
    elif args.device is None:
        print("NO DEVICE SPECIFIED!")
        raise SystemExit
    else:
        certchecker_main(args.device, datafile)


def certchecker_family(args, datafile):
    """
    Output all devices in a family.

    :param args: Arguments.
    :type args: argparse.Namespace

    :param datafile: List of device entries.
    :type datafile: list(dict)
    """
    family = jsonutils.read_family(datafile, args.device.upper())
    for ptcrbid in family:
        certchecker_main(ptcrbid, datafile)
        if len(family) > 1:
            print("")


def certchecker_main(device, data):
    """
    Wrap around :mod:`bbarchivist.networkutils` certification checking.

    :param device: Hardware ID, PTCRB ID, FCC ID or model number.
    :type device: str

    :param data: List of device entries.
    :type data: list(dict)
    """
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
    utilities.lprint(sorted(certlist, reverse=True))


if __name__ == "__main__":
    grab_args()

#!/usr/bin/env python3
"""Check Android autoloader files."""

import sys  # load arguments

import requests  # session
from bbarchivist import argutils  # arguments
from bbarchivist import decorators  # Ctrl+C wrapping
from bbarchivist import jsonutils  # json
from bbarchivist import networkutils  # lookup
from bbarchivist import utilities  # argument filters

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "2015-2018 Thurask"


def grab_args():
    """
    Parse arguments from argparse/questionnaire.

    Invoke :func:`droidlookup.droidlookup_main` with those arguments.
    """
    if len(sys.argv) > 1:
        parser = argutils.default_parser("bb-droidlookup", "Get Android autoloaders")
        parser.add_argument(
            "branch",
            help="OS branch, 3 letters")
        parser.add_argument(
            "floor",
            help="Start of search range",
            default=0,
            nargs="?",
            type=int,
            choices=range(0, 999),
            metavar="floor")
        parser.add_argument(
            "-d",
            "--device",
            dest="device",
            help="Device to check",
            nargs="?",
            type=argutils.droidlookup_devicetype,
            default=None)
        parser.add_argument(
            "-c",
            "--ceiling",
            dest="ceil",
            help="End of search range",
            default=999,
            nargs="?",
            type=int,
            choices=range(1, 1000),
            metavar="ceil")
        parser.add_argument(
            "-t",
            "--type",
            help="Check SHA256/512 hashes instead",
            default=None,
            type=argutils.droidlookup_hashtype)
        parser.add_argument(
            "-s",
            "--single",
            dest="single",
            help="Only scan one OS build",
            action="store_true",
            default=False)
        parser.add_argument(
            "-a",
            "--all-devices",
            dest="alldevices",
            help="Scan all devices, not just known ones",
            action="store_true",
            default=False)
        args = parser.parse_args(sys.argv[1:])
        parser.set_defaults()
        execute_args(args)
    else:
        questionnaire()


def execute_args(args):
    """
    Get args and decide what to do with them.

    :param args: Arguments.
    :type args: argparse.Namespace
    """
    if args.single:
        args.ceil = args.floor  # range(x, x+1) == x
    famlist = jsonutils.load_json("droidfamilies")
    cleanlist = famlist[:4]  # Priv/DTEK50/DTEK60/KEYone
    if args.device is None:
        if not args.alldevices:
            famlist = cleanlist
        droidlookup_main(famlist, args.branch, args.floor, args.ceil, args.type)
    elif args.device not in cleanlist:
        print("Selected device {0} has unknown autoloader scheme!".format(args.device))
    else:
        droidlookup_main(args.device, args.branch, args.floor, args.ceil, args.type)


def questionnaire_single():
    """
    What to ask if only one lookup is needed.
    """
    while True:
        scanos = input("OS (ex. AAD250): ")
        branch = scanos[:3]
        floor = scanos[3:6]
        quants = [len(scanos) == 6, branch.isalpha(), floor.isdigit()]
        if not all(quants):
            print("OS MUST BE 3 LETTERS AND 3 NUMBERS, TRY AGAIN")
            continue
        else:
            floor = int(floor)
            ceil = floor
            break
    return branch, floor, ceil


def questionnaire_branch():
    """
    Ask about lookup branch.
    """
    while True:
        branch = input("BRANCH (ex. AAD): ")
        if len(branch) != 3 or not branch.isalpha():
            print("BRANCH MUST BE 3 LETTERS, TRY AGAIN")
            continue
        else:
            break
    return branch


def parse_floor(floor):
    """
    Check if floor value is OK.

    :param floor: Starting OS version.
    :type floor: int
    """
    return parse_extreme(floor, 0, 998, "INITIAL < 0, TRY AGAIN", "INITIAL > 998, TRY AGAIN")


def parse_ceiling(ceil, floor):
    """
    Check if ceiling value is OK.

    :param ceil: Ending OS version.
    :type ceil: int

    :param floor: Starting OS version.
    :type floor: int
    """
    return parse_extreme(ceil, floor, 999, "FINAL < INITIAL, TRY AGAIN", "FINAL > 999, TRY AGAIN")


def questionnaire_initial():
    """
    Ask about lookup start.
    """
    while True:
        try:
            floor = int(input("INITIAL OS (0-998): "))
        except ValueError:
            continue
        else:
            if parse_floor(floor):
                break
            else:
                continue
    return floor


def parse_extreme(starter, minim, maxim, mintext, maxtext):
    """
    Check if floor/ceiling value is OK.

    :param starter: Minimum/maximum OS version.
    :type starter: int

    :param minim: Minimum value for starter.
    :type minim: int

    :param maxim: Maximum value for starter.
    :type maxim: int

    :param mintext: What to print if starter < minim.
    :type mintext: str

    :param maxtext: What to print if starter > maxim.
    :type maxtext: str
    """
    okay = False
    if starter < minim:
        print(mintext)
    elif starter > maxim:
        print(maxtext)
    else:
        okay = True
    return okay


def questionnaire_final(floor):
    """
    Ask about lookup end.

    :param floor: Starting OS version.
    :type floor: int
    """
    while True:
        try:
            ceil = int(input("FINAL OS (1-999): "))
        except ValueError:
            ceil = 999
        else:
            if parse_ceiling(ceil, floor):
                break
            else:
                continue
    return ceil


def questionnaire():
    """
    Questions to ask if no arguments given.
    """
    single = utilities.i2b("SINGLE OS (Y/N)?: ")
    if single:
        branch, floor, ceil = questionnaire_single()
    else:
        branch = questionnaire_branch()
        floor = questionnaire_initial()
        ceil = questionnaire_final(floor)
    famlist = jsonutils.load_json("droidfamilies")  # same here
    droidlookup_main(famlist[:2], branch, floor, ceil)
    decorators.enter_to_exit(True)


@decorators.wrap_keyboard_except
def droidlookup_main(device, branch, floor=0, ceil=999, method=None):
    """
    Check the existence of Android factory images, in a range.

    :param device: Device to check.
    :type device: str

    :param branch: OS version, 3 letters.
    :type branch: str

    :param floor: Starting OS version, padded to 3 numbers. Default is 0.
    :type floor: int

    :param ceil: Ending OS version, padded to 3 numbers. Default is 999.
    :type ceil: int

    :param method: None for regular OS links, "hash256/512" for SHA256 or 512 hash.
    :type method: str
    """
    argutils.slim_preamble("DROIDLOOKUP")
    text = "DEVICE: ALL" if isinstance(device, list) else "DEVICE: {0}".format(device.upper())
    print(text)
    sess = requests.Session()
    for ver in range(floor, ceil + 1):
        build = "{0}{1}".format(branch.upper(), str(ver).zfill(3))
        print("NOW SCANNING: {0}".format(build), end="\r")
        results = networkutils.droid_scanner(build, device, method, sess)
        if results is not None:
            for result in results:
                print("{0} AVAILABLE! {1}\n".format(build, result), end="\r")


if __name__ == "__main__":
    grab_args()

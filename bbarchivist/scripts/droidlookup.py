#!/usr/bin/env python3
"""Check Android autoloader files."""

import sys  # load arguments
from bbarchivist import networkutils  # lookup
from bbarchivist import decorators  # Ctrl+C wrapping
from bbarchivist import jsonutils  # json
from bbarchivist import utilities  # argument filters
from bbarchivist import scriptutils  # default parser

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "Copyright 2015-2016 Thurask"


def grab_args():
    """
    Parse arguments from argparse/questionnaire.

    Invoke :func:`droidlookup.droidlookup_main` with those arguments.
    """
    if len(sys.argv) > 1:
        parser = scriptutils.default_parser("bb-droidlookup", "Get Android autoloaders")
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
            type=utilities.droidlookup_devicetype,
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
            type=utilities.droidlookup_hashtype)
        parser.add_argument(
            "-s",
            "--single",
            dest="single",
            help="Only scan one OS build",
            action="store_true",
            default=False)
        args = parser.parse_args(sys.argv[1:])
        parser.set_defaults()
        if args.single:
            args.ceil = args.floor  # range(x, x+1) == x
        if args.device is None:
            famlist = jsonutils.load_json("droidfamilies")  # make sure to skip DTEK60 for now
            droidlookup_main(famlist[:2], args.branch, args.floor, args.ceil, args.type)
        else:
            droidlookup_main(args.device, args.branch, args.floor, args.ceil, args.type)
    else:
        questionnaire()


def questionnaire():
    """
    Questions to ask if no arguments given.
    """
    single = utilities.s2b(input("SINGLE OS (Y/N)?: "))
    if single:
        while True:
            scanos = input("OS (ex. AAD250): ")
            if len(scanos) != 6:
                print("OS MUST BE 3 LETTERS AND 3 NUMBERS, TRY AGAIN")
                continue
            branch = scanos[:3]
            if not branch.isalpha():
                print("OS MUST BE 3 LETTERS AND 3 NUMBERS, TRY AGAIN")
                continue
            floor = scanos[3:6]
            if not floor.isdigit():
                print("OS MUST BE 3 LETTERS AND 3 NUMBERS, TRY AGAIN")
                continue
            floor = int(floor)
            ceil = floor
            break
    else:
        while True:
            branch = input("BRANCH (ex. AAD): ")
            if len(branch) != 3 or not branch.isalpha():
                print("BRANCH MUST BE 3 LETTERS, TRY AGAIN")
                continue
            else:
                break
        while True:
            try:
                floor = int(input("INITIAL OS (0-998): "))
            except ValueError:
                continue
            else:
                if floor < 0:
                    print("INITIAL < 0, TRY AGAIN")
                    continue
                elif floor > 998:
                    print("INITIAL > 998, TRY AGAIN")
                    continue
                else:
                    break
        while True:
            try:
                ceil = int(input("FINAL OS (1-999): "))
            except ValueError:
                ceil = 999
            else:
                if ceil < floor:
                    print("FINAL < INITIAL, TRY AGAIN")
                    continue
                elif ceil > 999:
                    print("FINAL > 999, TRY AGAIN")
                    continue
                else:
                    break
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
    scriptutils.slim_preamble("DROIDLOOKUP")
    if isinstance(device, list):
        print("DEVICE: ALL")
    else:
        print("DEVICE: {0}".format(device.upper()))
    for ver in range(floor, ceil + 1):
        build = "{0}{1}".format(branch.upper(), str(ver).zfill(3))
        print("NOW SCANNING: {0}".format(build), end="\r")
        results = networkutils.droid_scanner(build, device, method)
        if results is not None:
            for result in results:
                print("{0} AVAILABLE! {1}\n".format(build, result), end="\r")


if __name__ == "__main__":
    grab_args()

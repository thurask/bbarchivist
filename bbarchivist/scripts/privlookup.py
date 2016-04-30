#!/usr/bin/env python3
"""Check Priv autoloader files."""

import sys  # load arguments
from bbarchivist import networkutils  # lookup
from bbarchivist import utilities  # Ctrl+C wrapping
from bbarchivist import scriptutils  # default parser

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "Copyright 2015-2016 Thurask"


def grab_args():
    """
    Parse arguments from argparse/questionnaire.

    Invoke :func:`privlookup.privlookup_main` with those arguments."""
    if len(sys.argv) > 1:
        parser = scriptutils.default_parser("bb-privlookup", "Get Priv autoloaders")
        parser.add_argument(
            "branch",
            help="OS branch, 3 letters")
        parser.add_argument(
            "floor",
            help="Start of search range",
            default=0,
            type=int,
            choices=range(0, 999),
            metavar="INT")
        parser.add_argument(
            "ceil",
            help="End of search range",
            default=999,
            type=int,
            choices=range(1, 1000),
            metavar="INT")
        parser.add_argument(
            "-t",
            "--type",
            help="Check SHA256/512 hashes instead",
            default=None,
            type=utilities.privlookup_hashtype)
        args = parser.parse_args(sys.argv[1:])
        parser.set_defaults()
        privlookup_main(args.branch, args.floor, args.ceil, args.type)
    else:
        questionnaire()


def questionnaire():
    """
    Questions to ask if no arguments given.
    """
    while True:
        branch = input("BRANCH (ex. AAD): ")
        if len(branch) != 3:
            print("BRANCH MUST BE 3 LETTERS, TRY AGAIN")
            continue
        else:
            break
    while True:
        try:
            floor = int(input("INITIAL OS (0-998): "))
        except ValueError:
            floor = 0
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
    privlookup_main(branch, floor, ceil)
    scriptutils.enter_to_exit(True)


@utilities.wrap_keyboard_except
def privlookup_main(branch, floor=0, ceil=999, type=None):
    """
    Check the existence of Priv factory images, in a range.

    :param branch: OS version, 3 letters.
    :type branch: str

    :param floor: Starting OS version, padded to 3 numbers. Default is 0.
    :type floor: int

    :param ceil: Ending OS version, padded to 3 numbers. Default is 999.
    :type ceil: int

    :param type: None for regular OS links, "hash256/512" for SHA256 or 512 hash.
    :type type: str
    """
    for ver in range(floor, ceil + 1):
        build = "{0}{1}".format(branch.upper(), str(ver).zfill(3))
        print("NOW SCANNING: {0}".format(build), end="\r")
        results = networkutils.priv_scanner(build, type)
        if results is not None:
            for result in results:
                print("\r\n{0} AVAILABLE!\n{1}".format(build, result))


if __name__ == "__main__":
    grab_args()

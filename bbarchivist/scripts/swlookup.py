#!/usr/bin/env python3
"""Check BB10 software releases."""

import sys  # load arguments

from bbarchivist import argutils  # arguments
from bbarchivist import decorators  # Ctrl+C wrapping
from bbarchivist import networkutils  # lookup
from bbarchivist import utilities  # argument filters

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "2016-2019 Thurask"


def grab_args():
    """
    Parse arguments from argparse/questionnaire.
    """
    if len(sys.argv) > 1:
        parser = argutils.default_parser("bb-swlookup", "Check software releases")
        parser.add_argument("sw", help="Software version, 10.x.y.zzzz")
        parser.add_argument(
            "-l", "--loop",
            dest="recurse",
            help="Loop lookup, CTRL-C to quit",
            action="store_true",
            default=False)
        parser.add_argument(
            "-c", "--ceiling",
            dest="ceiling",
            help="When to stop script, default = 9999",
            default=9999,
            type=int,
            choices=range(1, 10000),
            metavar="INT")
        args = parser.parse_args(sys.argv[1:])
        parser.set_defaults()
        swlookup_main(
            args.sw,
            args.recurse,
            args.ceiling)
    else:
        swrel = input("SOFTWARE RELEASE: ")
        recurse = utilities.i2b("LOOP (Y/N)?: ")
        if recurse:
            print("Press Ctrl+C to stop loop")
        print(" ")
        swlookup_main(
            swrel,
            recurse,
            9999)
        decorators.enter_to_exit(True)


def terminator(swversion, ceiling, loop=None):
    """
    Handle KeyboardInterrupt calling.

    :param swversion: Software version, 10.x.y.zzzz.
    :type swversion: str

    :param loop: Whether or not to automatically lookup. Default is None.
    :type loop: bool

    :param ceiling: When to stop loop. Default is 9999 (i.e. 10.x.y.9999).
    :type ceiling: int
    """
    goloop = True if loop is None else loop
    if goloop and int(swversion.split(".")[3]) > ceiling:
        raise KeyboardInterrupt


@decorators.wrap_keyboard_except
def swlookup_main(swversion, loop=False, ceiling=9999):
    """
    Check if a software release exists.

    :param swversion: Software version, 10.x.y.zzzz.
    :type swversion: str

    :param loop: Whether or not to automatically lookup. Default is false.
    :type loop: bool

    :param ceiling: When to stop loop. Default is 9999 (i.e. 10.x.y.9999).
    :type ceiling: int
    """
    argutils.slim_preamble("SWLOOKUP")
    while True:
        terminator(swversion, ceiling, loop)
        print("NOW SCANNING: {0}".format(swversion), end="\r")
        baseurl = utilities.create_base_url(swversion)
        avail = networkutils.availability(baseurl)
        if avail:
            print("SW {0} AVAILABLE!".format(swversion))
        if not loop:
            raise KeyboardInterrupt  # hack, but whatever
        else:
            terminator(swversion, ceiling)
            swversion = utilities.increment(swversion, 1)
            continue


if __name__ == "__main__":
    grab_args()

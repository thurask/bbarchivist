#!/usr/bin/env python3
"""Generate Dev Alpha autoloader URLs."""

import sys  # load arguments

import requests  # session
from bbarchivist import argutils  # arguments
from bbarchivist import decorators  # wrap Ctrl+C
from bbarchivist import jsonutils  # json
from bbarchivist import networkutils  # check function
from bbarchivist import textgenerator  # export
from bbarchivist import utilities  # filesize

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "2015-2019 Thurask"


def grab_args():
    """
    Parse arguments from argparse/questionnaire.

    Invoke :func:`devloader.devloader_main` with arguments.
    """
    if len(sys.argv) > 1:
        parser = argutils.default_parser("bb-devloader", "Dev Alpha URL generator")
        parser.add_argument(
            "os",
            help="OS version, 10.x.y.zzzz")
        parser.add_argument(
            "-l", "--loop",
            dest="recurse",
            help="Loop lookup, CTRL-C to quit",
            action="store_true",
            default=False)
        parser.add_argument(
            "-e", "--export",
            dest="export",
            help="Export links to files",
            action="store_true",
            default=False)
        parser.add_argument(
            "-i", "--increment",
            dest="increment",
            help="Loop increment, default = 3",
            default=3,
            type=argutils.positive_integer,
            metavar="INT")
        parser.add_argument(
            "-c", "--ceiling",
            dest="ceiling",
            help="When to stop script, default = 9996",
            default=9999,
            type=int,
            choices=range(1, 10000),
            metavar="INT")
        parser.set_defaults()
        args = parser.parse_args(sys.argv[1:])
        devloader_main(args.os, args.export, args.recurse, args.ceiling, args.increment)
    else:
        osversion = input("OS VERSION: ")
        export = utilities.i2b("EXPORT TO FILE (Y/N)?: ")
        print(" ")
        devloader_main(osversion, export)
        decorators.enter_to_exit(True)


def devloader_exporter(osversion, export, urls):
    """
    Handle exporting links to text/stdout.

    :param osversion: OS version.
    :type osversion: str

    :param export: If we write URLs to file. Default is false.
    :type export: bool

    :param urls: List of Dev Alpha URLs.
    :type urls: list(str)
    """
    if export:
        print("EXPORTING...")
        textgenerator.export_devloader(osversion, urls)
    else:
        utilities.lprint(urls.keys())


@decorators.wrap_keyboard_except
def devloader_main(osversion, export=False, loop=False, ceiling=9999, inc=3):
    """
    Wrap around :mod:`bbarchivist.networkutils` Dev Alpha autoloader searching.

    :param osversion: OS version.
    :type osversion: str

    :param export: If we write URLs to file. Default is false.
    :type export: bool

    :param loop: Whether or not to automatically lookup. Default is false.
    :type loop: bool

    :param ceiling: When to stop loop. Default is 9999 (i.e. 10.x.y.9999).
    :type ceiling: int

    :param inc: Lookup increment. Default is 3.
    :type inc: int
    """
    skels = jsonutils.load_json('devskeletons')
    argutils.slim_preamble("DEVLOADER")
    sess = requests.Session()
    while True:
        if loop and int(osversion.split(".")[3]) > ceiling:
            break
        print("OS VERSION: {0}".format(osversion), end="\r")
        urls = networkutils.devalpha_urls_bootstrap(osversion, skels, sess)
        if urls:
            urls = networkutils.dev_dupe_cleaner(urls)
            print("{0} AVAILABLE!    \n".format(osversion), end="\r")  # spaces to clear line
            devloader_exporter(osversion, export, urls)
            if not loop:
                break
        else:
            if not loop:
                print("NOT FOUND!                ", end="\r")
                break
        if loop:
            osversion = utilities.increment(osversion, inc)
            continue

if __name__ == "__main__":
    grab_args()

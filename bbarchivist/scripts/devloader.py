#!/usr/bin/env python3
"""Generate Dev Alpha autoloader URLs."""

import sys  # load arguments
from bbarchivist import networkutils  # check function
from bbarchivist import jsonutils  # json
from bbarchivist import scriptutils  # default parser
from bbarchivist import textgenerator  # export
from bbarchivist import utilities  # filesize

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "Copyright 2015-2016 Thurask"


def grab_args():
    """
    Parse arguments from argparse/questionnaire.

    Invoke :func:`devloader.devloader_main` with arguments.
    """
    if len(sys.argv) > 1:
        parser = scriptutils.default_parser("bb-devloader", "Dev Alpha URL generator")
        parser.add_argument(
            "os",
            help="OS version, 10.x.y.zzzz")
        parser.add_argument(
            "-e", "--export",
            dest="export",
            help="Export links to files",
            action="store_true",
            default=False)
        parser.set_defaults()
        args = parser.parse_args(sys.argv[1:])
        devloader_main(args.os, args.export)
    else:
        osversion = input("OS VERSION: ")
        export = utilities.s2b(input("EXPORT TO FILE?: "))
        print(" ")
        devloader_main(osversion, export)
        scriptutils.enter_to_exit(True)


def devloader_main(osversion, export=False):
    """
    Wrap around :mod:`bbarchivist.networkutils` Dev Alpha autoloader searching.

    :param osversion: OS version.
    :type osversion: str

    :param export: If we write URLs to file. Default is false.
    :type export: bool
    """
    skels = jsonutils.load_json('devskeletons')
    scriptutils.slim_preamble("DEVLOADER")
    print("OS VERSION: {0}".format(osversion))
    print("\nGENERATING...\n")
    urls = networkutils.devalpha_urls(osversion, skels)
    urls = networkutils.dev_dupe_cleaner(urls)
    if export:
        print("EXPORTING...")
        textgenerator.export_devloader(osversion, urls)
    else:
        scriptutils.lprint(urls.keys())

if __name__ == "__main__":
    grab_args()

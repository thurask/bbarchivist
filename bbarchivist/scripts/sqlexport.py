﻿#!/usr/bin/env python3
#pylint: disable = I0011, R0201, W0613, C0301, R0913, R0912, R0914, R0915
"""Export SQL database to CSV."""

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "2015 Thurask"

import argparse  # parse arguments
import sys  # load arguments
from bbarchivist import bbconstants  # versions/constants
from bbarchivist import sqlutils  # the export function


def sqlexport_main():
    """
    Wrapper around CSV export function.

    Invoke :func:`bbarchivist.sqlutils.export_sql_db`.
    """
    parser = argparse.ArgumentParser(
        prog="bb-sqlexport",
        description="Export SQL database to CSV.",
        epilog="http://github.com/thurask/bbarchivist")
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version="%(prog)s " + bbconstants.VERSION)
    parser.add_argument(
        "-p",
        "--pop",
        dest="popsw",
        help="Pop this OS and SW from the database",
        nargs=2,
        metavar=("OS", "SW"),
        default=False)
    parser.add_argument(
        "-l",
        "--list",
        dest="list",
        help="List entries in database",
        action="store_true",
        default=False)
    parser.set_defaults()
    args = parser.parse_args(sys.argv[1:])
    if args.list:
        args.popsw = False
    if not args.popsw and not args.list:
        sqlutils.export_sql_db()
    elif args.popsw:
        sqlutils.pop_sw_release(*args.popsw)
        print("POPPED: OS {0} - SW {1}".format(*args.popsw))
    else:
        rellist = sqlutils.list_sw_releases()
        if rellist is not None:
            for rel in rellist:
                if rel[2] == "available":
                    affix = "  "
                else:
                    affix = ""
                print("OS {0} - SR {1} - {2} - {3}".format(
                    rel[0], rel[1], (rel[2] + affix), rel[3]))

if __name__ == "__main__":
    sqlexport_main()

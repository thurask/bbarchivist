#!/usr/bin/env python3
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
        metavar="OS SW",
        default=False)
    parser.set_defaults()
    args = parser.parse_args(sys.argv[1:])
    if not args.popsw:
        sqlutils.export_sql_db()
    else:
        sqlutils.pop_sw_release(*args.popsw)
        print("POPPED: OS {0} - SW {1}".format(*args.popsw))
if __name__ == "__main__":
    sqlexport_main()

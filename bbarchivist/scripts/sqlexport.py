#!/usr/bin/env python3
"""Export SQL database to CSV."""

import sys  # load arguments
from bbarchivist import sqlutils  # the export function
from bbarchivist import scriptutils  # default parser

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "Copyright 2015-2016 Thurask"


def sqlexport_main():
    """
    Wrapper around CSV export function.

    Invoke :func:`bbarchivist.sqlutils.export_sql_db`.
    """
    parser = scriptutils.default_parser("bb-sqlexport",
                                        "SQL-related tools")
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

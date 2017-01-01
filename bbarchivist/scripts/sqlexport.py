#!/usr/bin/env python3
"""Export SQL database to CSV."""

import sys  # load arguments
from bbarchivist import sqlutils  # the export function
from bbarchivist import scriptutils  # default parser

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "2015-2017 Thurask"


def grab_args():
    """
    Parse arguments from argparse/questionnaire.
    """
    parser = scriptutils.default_parser("bb-sqlexport", "SQL-related tools")
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
    parser.add_argument(
        "-a",
        "--available",
        dest="avail",
        help="List only available entries in database (implies -l)",
        action="store_true",
        default=False)
    parser.set_defaults()
    args = parser.parse_args(sys.argv[1:])
    if args.list or args.avail:
        args.popsw = False
    sqlexport_main(args.list, args.avail, args.popsw)


def pprint(avail):
    """
    Pretty print the release list.

    :param avail: List only available entries in database (implies listing in the first place).
    :type avail: bool
    """
    rellist = sqlutils.list_sw_releases(avail)
    if rellist is not None:
        for rel in rellist:
            affix = "  " if rel[2] == "available" else ""
            print("OS {0} - SR {1} - {2} - {3}".format(
                rel[0], rel[1], (rel[2] + affix), rel[3]))


def sqlexport_main(listed, avail, popsw):
    """
    Wrapper around CSV export function/other SQL-related stuff.

    :param listed: List entries in database.
    :type listed: bool

    :param avail: List only available entries in database (implies listing in the first place).
    :type avail: bool

    :param popsw: If we're popping a software release: False if not, ("OS", "SW") tuple if we are.
    :type popsw: tuple
    """
    if not popsw and not listed and not avail:
        sqlutils.export_sql_db()
    elif popsw:
        sqlutils.pop_sw_release(*popsw)
        print("POPPED: OS {0} - SW {1}".format(*popsw))
    else:
        pprint(avail)


if __name__ == "__main__":
    grab_args()

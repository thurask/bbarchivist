#!/usr/bin/env python3
"""Check for new PRDs for TCL API devices."""

import sys  # load arguments
from bbarchivist import jsonutils  # json
from bbarchivist import scriptutils  # default parser

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "2017 Thurask"


def grab_args():
    """
    Parse arguments from argparse/questionnaire.

    Invoke a function with those arguments.
    """
    parser = scriptutils.default_parser("bb-tclnewprd", "Check for new PRDs for TCL devices")
    parser.add_argument("prd", help="Only scan one/custom PRD root", default=None, nargs="?")
    parser.add_argument(
        "-f", "--floor",
        dest="floor",
        help="When to start, default=1",
        default=1,
        type=int,
        choices=range(0, 998),
        metavar="INT")
    parser.add_argument(
        "-c", "--ceiling",
        dest="ceiling",
        help="When to stop, default=60",
        default=None,
        type=int,
        choices=range(1, 999),
        metavar="INT")
    args = parser.parse_args(sys.argv[1:])
    parser.set_defaults()
    execute_args(args)


def execute_args(args):
    """
    Get args and decide what to do with them.

    :param args: Arguments.
    :type args: argparse.Namespace
    """
    if args.ceiling is None:
        args.ceiling = args.floor + 59  # default range
    if args.ceiling < args.floor:
        print("INVALID RANGE!")
        raise SystemExit
    args.ceiling += 1  # because range() is a half-open interval
    tclnewprd_main(args.prd, args.floor, args.ceiling)


def tclnewprd_main(prd=None, floor=1, ceiling=60):
    """
    Scan every PRD and produce latest versions.

    :param prd: Specific PRD to check, None if we're checking all variants in database. Default is None.
    :type prd: str

    :param floor: When to start. Default is 1.
    :type floor: int

    :param ceiling: When to stop. Default is 60.
    :type ceiling: int
    """
    scriptutils.slim_preamble("TCLNEWPRD")
    prdbase = jsonutils.load_json("prds")
    prddict = scriptutils.tcl_findprd_prepdict(prdbase)
    prddict = scriptutils.tcl_findprd_checkfilter(prddict, prd)
    scriptutils.tcl_findprd(prddict, floor, ceiling)


if __name__ == "__main__":
    grab_args()

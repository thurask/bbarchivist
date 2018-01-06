#!/usr/bin/env python3
"""Check for new PRDs for TCL API devices."""

import sys  # load arguments
from bbarchivist import decorators  # enter to exit
from bbarchivist import jsonutils  # json
from bbarchivist import scriptutils  # default parser
from bbarchivist import utilities  # bool

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "2017-2018 Thurask""


def grab_args():
    """
    Parse arguments from argparse/questionnaire.

    Invoke a function with those arguments.
    """
    if getattr(sys, "frozen", False) and len(sys.argv) == 1:
        questionnaire()
    else:
        parser = scriptutils.default_parser("bb-tclnewprd", "Check for new PRDs for TCL devices")
        parser.add_argument("prds", help="Only scan space separated list of PRDs", default=None, nargs="*")
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
        parser.add_argument(
            "-x",
            "--export",
            dest="export",
            help="Write XML to logs folder",
            action="store_true",
            default=False)
        args = parser.parse_args(sys.argv[1:])
        parser.set_defaults()
        execute_args(args)


def questionnaire():
    """
    Questions to ask if no arguments given.
    """
    prds = questionnaire_prds()
    tclnewprd_main(prds=prds, floor=1, ceiling=61)
    decorators.enter_to_exit(True)


def questionnaire_prds():
    """
    Ask about individual versus full scanning.
    """
    selectbool = utilities.i2b("SCAN SELECTED PRDS (Y/N)?: ")
    if selectbool:
        prdin = input("ENTER PRD(S) TO SCAN (ex. 63116 63734 63737): ")
        prds = prdin.split(" ")
    else:
        prds = None
    return prds


def execute_args(args):
    """
    Get args and decide what to do with them.

    :param args: Arguments.
    :type args: argparse.Namespace
    """
    if not args.prds:
        args.prds = None
    if args.ceiling is None:
        args.ceiling = args.floor + 59  # default range
    if args.ceiling < args.floor:
        print("INVALID RANGE!")
        raise SystemExit
    args.ceiling += 1  # because range() is a half-open interval
    tclnewprd_main(args.prds, args.floor, args.ceiling, args.export)


def tclnewprd_main(prds=None, floor=1, ceiling=60, export=False):
    """
    Scan every PRD and produce latest versions.

    :param prds: Specific PRD(s) to check, None if we're checking all variants in database. Default is None.
    :type prds: list(str)

    :param floor: When to start. Default is 1.
    :type floor: int

    :param ceiling: When to stop. Default is 60.
    :type ceiling: int

    :param export: Whether to export XML response to file. Default is False.
    :type export: bool
    """
    scriptutils.slim_preamble("TCLNEWPRD")
    prdbase = jsonutils.load_json("prds")
    prddict = scriptutils.tcl_findprd_prepdict(prdbase)
    prddict = scriptutils.tcl_findprd_checkfilter(prddict, prds)
    scriptutils.tcl_findprd(prddict, floor, ceiling, export)


if __name__ == "__main__":
    grab_args()

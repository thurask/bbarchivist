#!/usr/bin/env python3
"""Check latest update for TCL API devices."""

import sys  # load arguments
import requests  # session
from bbarchivist import decorators  # enter to exit
from bbarchivist import jsonutils  # json
from bbarchivist import networkutils  # lookup
from bbarchivist import scriptutils  # default parser
from bbarchivist import utilities  # bool

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "2017 Thurask"


def grab_args():
    """
    Parse arguments from argparse/questionnaire.

    Invoke a function with those arguments.
    """
    if len(sys.argv) > 1:
        parser = scriptutils.default_parser("bb-tclscan", "Check for updates for TCL devices")
        parser.add_argument("prd", help="Only scan one PRD", default=None, nargs="?")
        parser.add_argument(
            "-l",
            "--list",
            dest="printlist",
            help="List PRDs in database",
            action="store_true",
            default=False)
        parser.add_argument(
            "-d",
            "--download",
            dest="download",
            help="Download update, assumes single PRD",
            action="store_true",
            default=False)
        parser.add_argument(
            "-o",
            "--ota-version",
            dest="otaver",
            help="Query OTA updates from a given version instead of full OS",
            default=None)
        args = parser.parse_args(sys.argv[1:])
        parser.set_defaults()
        execute_args(args)
    else:
        questionnaire()


def execute_args(args):
    """
    Get args and decide what to do with them.

    :param args: Arguments.
    :type args: argparse.Namespace
    """
    if args.printlist:
        prddict = jsonutils.load_json("prds")
        jsonutils.list_prds(prddict)
    elif args.prd is not None:
        tclscan_single(args.prd, args.download, args.otaver)
    else:
        tclscan_main(args.otaver)


def questionnaire_ota():
    """
    Ask about OTA versus full scanning.
    """
    otabool = utilities.i2b("CHECK OTA VERSION (Y/N)?: ")
    if otabool:
        otaver = input("ENTER OTA VERSION (ex. AAO472): ")
    else:
        otaver = None
    return otaver


def questionnaire_single():
    """
    Ask about single versus full scanning.
    """
    singlebool = utilities.i2b("SCAN SINGLE OS (Y/N)?: ")
    if singlebool:
        singleprd = input("ENTER PRD TO SCAN (ex. PRD-63116-001): ")
    else:
        singleprd = None
    return singleprd


def questionnaire():
    """
    Questions to ask if no arguments given.
    """
    singleprd = questionnaire_single()
    otaver = questionnaire_ota()
    if singleprd is not None:
        tclscan_single(singleprd, ota=otaver)
    else:
        tclscan_main(otaver)
    decorators.enter_to_exit(True)


def tclscan_single(curef, download=False, ota=None):
    """
    Scan one PRD and produce download URL and filename.

    :param curef: PRD of the phone variant to check.
    :type curef: str

    :param download: If we'll download the file that this returns. Default is False.
    :type download: bool

    :param ota: The starting version if we're checking OTA updates, None if we're not. Default is None.
    :type ota: str
    """
    mode, fvver = scriptutils.tcl_prep_otaver(ota)
    scriptutils.tcl_prd_scan(curef, False, mode=mode, fvver=fvver)
    if download:
        print("LARGE DOWNLOAD DOESN'T WORK YET")


def tclscan_main(ota=None):
    """
    Scan every PRD and produce latest versions.

    :param ota: The starting version if we're checking OTA updates, None if we're not. Default is None.
    :type ota: str
    """
    mode, fvver = scriptutils.tcl_prep_otaver(ota)
    scriptutils.tcl_mainscan_preamble(ota)
    prddict = jsonutils.load_json("prds")
    sess = requests.Session()
    for device in prddict.keys():
        print("~{0}~".format(device))
        for curef in prddict[device]:
            checktext = networkutils.tcl_check(curef, sess, mode=mode, fvver=fvver)
            if checktext is None:
                continue
            else:
                tvver, firmwareid, filename, fsize, fhash = networkutils.parse_tcl_check(checktext)
                del firmwareid, filename, fsize, fhash
                scriptutils.tcl_mainscan_printer(curef, tvver, ota)


if __name__ == "__main__":
    grab_args()

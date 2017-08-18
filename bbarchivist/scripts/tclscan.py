#!/usr/bin/env python3
"""Check latest update for TCL API devices."""

import sys  # load arguments
import requests  # session
from bbarchivist import networkutils  # lookup
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
    if len(sys.argv) > 1:
        parser = scriptutils.default_parser("bb-tclscan", "Check for updates for TCL devices")
        parser.add_argument(
            "-p",
            "--prd",
            dest="prd",
            help="Only scan one PRD",
            default=None)
        parser.add_argument(
            "-l",
            "--list",
            dest="printlist",
            help="List PRDs in database",
            action="store_true",
            default=False)
        args = parser.parse_args(sys.argv[1:])
        parser.set_defaults()
        if args.printlist:
            prddict = jsonutils.load_json("prds")
            jsonutils.list_prds(prddict)
        elif args.prd is not None:
            tclscan_single(args.prd)
        else:
            tclscan_main()
    else:
        tclscan_main()


def tclscan_single(curef):
    """
    Scan one PRD and produce download URL and filename.

    :param curef: PRD of the phone variant to check.
    :type curef: str
    """
    sess = requests.Session()
    ctext = networkutils.tcl_check(curef, sess)
    if ctext is None:
        raise SystemExit
    tvver, firmwareid, filename, fsize, fhash = networkutils.parse_tcl_check(ctext)
    del fsize, fhash
    salt = networkutils.tcl_salt()
    vkhsh = networkutils.vkhash(curef, tvver, firmwareid, salt)
    updatetext = networkutils.tcl_download_request(curef, tvver, firmwareid, salt, vkhsh, sess)
    downloadurl = networkutils.parse_tcl_download_request(updatetext)
    print("{0}: HTTP {1}".format(filename, networkutils.getcode(downloadurl, sess)))
    print(downloadurl)


def tclscan_main():
    """
    Scan every PRD and produce latest versions.
    """
    scriptutils.slim_preamble("TCLSCAN")
    prddict = jsonutils.load_json("prds")
    sess = requests.Session()
    for device in prddict.keys():
        print("~{0}~".format(device))
        for curef in prddict[device]:
            checktext = networkutils.tcl_check(curef, sess)
            tvver, firmwareid, filename, fsize, fhash = networkutils.parse_tcl_check(checktext)
            del firmwareid, filename, fsize, fhash
            print("{0}: {1}".format(curef, tvver))


if __name__ == "__main__":
    grab_args()

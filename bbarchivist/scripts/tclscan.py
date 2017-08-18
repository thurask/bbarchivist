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

    Invoke :func:`droidlookup.droidlookup_main` with those arguments.
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
            "-s",
            "--serid",
            dest="serid",
            help="Specify serial number",
            default="543212345000000")
        args = parser.parse_args(sys.argv[1:])
        parser.set_defaults()
        if args.prd is not None:
            tclscan_single(args.prd, args.serid)
        else:
            tclscan_main(args.serid)
    else:
        tclscan_main()


def tclscan_single(curef, serid):
    """
    Scan one PRD and produce download URL and filename.

    :param curef: PRD of the phone variant to check.
    :type curef: str

    :param curef: Serial number of the phone to check.
    :type curef: str
    """
    ctext = networkutils.tcl_check(curef)
    tvver, firmwareid, filename, fsize, fhash = networkutils.parse_tcl_check(ctext)
    del fsize, fhash
    slt = networkutils.tcl_salt()
    vkh = networkutils.vkhash(serid, curef, tvver, firmwareid, slt)
    updatetext = update_request(sess, serid, curef, tvver, firmwareid, slt, vkh)
    downloadurl = parse_request(updatetext)
    print("{0}: HTTP {1}".format(filename, networkutils.getcode(sess, downloadurl)))
    print(downloadurl)


def tclscan_main(serid="543212345000000"):
    """
    Scan every PRD and produce latest versions.

    :param curef: Serial number of the phone to check, filled in by default.
    :type curef: str
    """
    scriptutils.slim_preamble("TCLSCAN")
    prddict = jsonutils.load_json("prds")
    sess = requests.Session()
    for device in prddict.keys():
        print("~{0}~".format(device))
        for curef in prddict[device]:
            checktext = check(sess, serid, curef)
            tvver, firmwareid, filename, fsize, fhash = networkutils.parse_tcl_check(checktext)
            del firmwareid, filename, fsize, fhash
            print("{0}: {1}".format(curef, tvver))


if __name__ == "__main__":
    grab_args()

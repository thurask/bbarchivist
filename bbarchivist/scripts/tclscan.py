#!/usr/bin/env python3
"""Check latest update for TCL API devices."""

import os  # file work
import sys  # load arguments
import requests  # session
from bbarchivist import hashutils  # hash work
from bbarchivist import jsonutils  # json
from bbarchivist import networkutils  # lookup
from bbarchivist import scriptutils  # default parser
from bbarchivist import utilities  # filesize

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "2017 Thurask"


def grab_args():
    """
    Parse arguments from argparse/questionnaire.

    Invoke a function with those arguments.
    """
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
    parser.add_argument(
        "-d",
        "--download",
        dest="download",
        help="Download update, assumes -p",
        action="store_true",
        default=False)
    args = parser.parse_args(sys.argv[1:])
    parser.set_defaults()
    if args.printlist:
        prddict = jsonutils.load_json("prds")
        jsonutils.list_prds(prddict)
    elif args.prd is not None:
        tclscan_single(args.prd, args.download)
    else:
        tclscan_main()


def tclscan_single(curef, download=False):
    """
    Scan one PRD and produce download URL and filename.

    :param curef: PRD of the phone variant to check.
    :type curef: str
    """
    sess = requests.Session()
    ctext = networkutils.tcl_check(curef, sess)
    if ctext is None:
        raise SystemExit
    tvver, firmwareid, filename, filesize, filehash = networkutils.parse_tcl_check(ctext)
    salt = networkutils.tcl_salt()
    vkhsh = networkutils.vkhash(curef, tvver, firmwareid, salt)
    updatetext = networkutils.tcl_download_request(curef, tvver, firmwareid, salt, vkhsh, sess)
    downloadurl = networkutils.parse_tcl_download_request(updatetext)
    statcode = networkutils.getcode(downloadurl, sess)
    print("{0}: HTTP {1}".format(filename, statcode))
    print(downloadurl)
    if statcode == 200 and download:
        #tclscan_download(downloadurl, filename, filesize, filehash)
        print("DOWNLOAD DOESN'T WORK YET!!!")


def tclscan_download(downloadurl, filename, filesize, filehash):
    """
    Download autoloader file, rename, and verify.

    :param downloadurl: Download URL.
    :type downloadurl: str

    :param filename: Name of autoloader file.
    :type filename: str

    :param filesize: Size of autoloader file.
    :type filesize: str

    :param filehash: SHA-1 hash of autoloader file.
    :type filehash: str
    """
    print("FILENAME: {0}".format(filename))
    print("LENGTH: {0}".format(utilities.fsizer(filesize)))
    networkutils.download(downloadurl)
    print("DOWNLOAD COMPLETE")
    os.rename(downloadurl.split("/")[-1], filename)
    method = hashutils.get_engine("sha1")
    shahash = hashutils.hashlib_hash(filename, method)
    if shahash == filehash:
        print("HASH CHECK OK")
    else:
        print(shahash)
        print("HASH FAILED!")


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

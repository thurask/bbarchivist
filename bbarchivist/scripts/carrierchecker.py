#!/usr/bin/env python3
"""Checks a carrier for an OS version, can download."""

import sys  # load arguments
import os  # file/path operations
import webbrowser  # code list
import requests  # session
from bbarchivist import decorators  # enter to exit
from bbarchivist import bbconstants  # versions/constants
from bbarchivist import networkutils  # check function
from bbarchivist import utilities  # input validation
from bbarchivist import jsonutils  # json
from bbarchivist import scriptutils  # default parser

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "Copyright 2015-2016 Thurask"


def grab_args():
    """
    Parse arguments from argparse/questionnaire.

    Invoke :func:`carrierchecker.carrierchecker_main` with those arguments.
    """
    if len(sys.argv) > 1:
        parser = scriptutils.default_parser("bb-cchecker", "Carrier info checking")
        parser.add_argument("mcc",
                            help="1-3 digit country code",
                            type=utilities.valid_carrier,
                            nargs="?",
                            default=None)
        parser.add_argument("mnc",
                            help="1-3 digit carrier code",
                            type=utilities.valid_carrier,
                            nargs="?",
                            default=None)
        parser.add_argument("device",
                            help="'STL100-1', 'SQW100-3', etc.",
                            nargs="?",
                            default=None)
        parser.add_argument(
            "-c", "--codes",
            dest="codes",
            help="Open browser for MCC/MNC list",
            action="store_true",
            default=False)
        parser.add_argument(
            "-a", "--available-bundles",
            dest="bundles",
            help="Check available bundles",
            action="store_true",
            default=False)
        parser.add_argument(
            "-d", "--download",
            dest="download",
            help="Download files after checking",
            action="store_true",
            default=False)
        parser.add_argument(
            "-e", "--export",
            dest="export",
            help="Export links to files",
            action="store_true",
            default=False)
        parser.add_argument(
            "-r", "--repair",
            dest="upgrade",
            help="Debrick instead of upgrade bars",
            action="store_false",
            default=True)
        parser.add_argument(
            "-f", "--folder",
            dest="folder",
            help="Working folder",
            default=None,
            metavar="DIR")
        parser.add_argument(
            "-b", "--blitz",
            dest="blitz",
            help="Create blitz package",
            action="store_true",
            default=False)
        parser.add_argument(
            "--selective",
            dest="selective",
            help="Skip Nuance/retaildemo",
            action="store_true",
            default=False)
        fgroup = parser.add_mutually_exclusive_group()
        fgroup.add_argument(
            "-s", "--software-release",
            dest="forcedsw",
            help="Force SW release (check bundles first!)",
            default=None,
            metavar="SWRELEASE")
        fgroup.add_argument(
            "-o", "--os",
            dest="forcedos",
            help="Force OS (check bundles first!)",
            default=None,
            metavar="OS")
        parser.set_defaults()
        args = parser.parse_args(sys.argv[1:])
        if args.codes:
            webbrowser.open("https://en.wikipedia.org/wiki/Mobile_country_code")
        else:
            if args.folder is None:
                args.folder = os.getcwd()
            if args.blitz:
                args.download = True
                args.upgrade = True  # blitz takes precedence
            if args.bundles:
                args.download = False
                args.upgrade = False
                args.export = False
                args.blitz = False
            if args.forcedos is not None and args.forcedsw is None:
                avail = networkutils.sr_lookup(args.forcedos,
                                               bbconstants.SERVERS['p'])
                forced = avail if avail != "SR not in system" else None
            elif args.forcedos is None and args.forcedsw is not None:
                forced = args.forcedsw
            else:
                forced = None
            carrierchecker_main(
                args.mcc,
                args.mnc,
                args.device,
                args.download,
                args.upgrade,
                args.folder,
                args.export,
                args.blitz,
                args.bundles,
                forced,
                args.selective)
    else:
        questionnaire()
    decorators.enter_to_exit(True)


def questionnaire_3digit(message):
    """
    Get MCC/MNC from questionnaire.
    """
    while True:
        try:
            trip = int(input("{0}: ".format(message)))
        except ValueError:
            continue
        else:
            if trip == utilities.valid_carrier(trip):
                return trip


def questionnaire():
    """
    Questions to ask if no arguments given.
    """
    mcc = questionnaire_3digit("MCC")
    mnc = questionnaire_3digit("MNC")
    device = scriptutils.questionnaire_device()
    bundles = utilities.s2b(input("CHECK BUNDLES?: "))
    if bundles:
        download = False
        upgrade = False
        export = False
        blitz = False
    else:
        export = utilities.s2b(input("EXPORT TO FILE?: "))
        download = utilities.s2b(input("DOWNLOAD?: "))
        upgrade = False if not download else utilities.s2b(input("Y=UPGRADE BARS, N=DEBRICK BARS?: "))
        blitz = False if not download else (utilities.s2b(input("CREATE BLITZ?: ")) if upgrade else False)
    directory = os.getcwd()
    print(" ")
    carrierchecker_main(
        mcc,
        mnc,
        device,
        download,
        upgrade,
        directory,
        export,
        blitz,
        bundles,
        None,
        False)


def carrierchecker_argfilter(mcc, mnc, device, directory):
    """
    Filter arguments.

    :param mcc: Country code.
    :type mcc: int

    :param mnc: Network code.
    :type mnc: int

    :param device: Device ID (SXX100-#)
    :type device: str

    :param directory: Where to store files. Default is local directory.
    :type directory: str
    """
    if mcc is None:
        print("INVALID MCC!")
        raise SystemExit
    elif mnc is None:
        print("INVALID MNC!")
        raise SystemExit
    elif device is None:
        print("INVALID DEVICE!")
        raise SystemExit
    device = device.upper()
    directory = os.getcwd() if directory is None else directory
    return device, directory


def carrierchecker_jsonprepare(mcc, mnc, device):
    """
    Prepare JSON data.

    :param mcc: Country code.
    :type mcc: int

    :param mnc: Network code.
    :type mnc: int

    :param device: Device ID (SXX100-#).
    :type device: str
    """
    data = jsonutils.load_json("devices")
    model, family, hwid = jsonutils.certchecker_prep(data, device)
    country, carrier = networkutils.carrier_checker(mcc, mnc)
    return model, family, hwid, country, carrier


def carrierchecker_bundles(mcc, mnc, hwid):
    """
    :param mcc: Country code.
    :type mcc: int

    :param mnc: Network code.
    :type mnc: int

    :param hwid: Device hardware ID.
    :type hwid: str
    """
    releases = networkutils.available_bundle_lookup(mcc, mnc, hwid)
    print("\nAVAILABLE BUNDLES:")
    utilities.lprint(releases)


def carrierchecker_selective(files, selective=False):
    """
    Filter useless bar files.

    :param files: List of files.
    :type files: list(str)

    :param selective: Whether or not to exclude Nuance/other dross. Default is false.
    :type selective: bool
    """
    if selective:
        craplist = jsonutils.load_json("apps_to_remove")
        files = scriptutils.clean_barlist(files, craplist)
    return files


def carrierchecker_export(mcc, mnc, files, hwid, osv, radv, swv, export=False, upgrade=False, forced=None):
    """
    Export files to file.

    :param mcc: Country code.
    :type mcc: int

    :param mnc: Network code.
    :type mnc: int

    :param files: List of files.
    :type files: list(str)

    :param hwid: Device hardware ID.
    :type hwid: str

    :param osv: OS version, 10.x.y.zzzz.
    :type osv: str

    :param radv: Radio version, 10.x.y.zzzz.
    :type radv: str

    :param swv: Software release, 10.x.y.zzzz.
    :type swv: str

    :param export: Whether or not to write URLs to a file. Default is false.
    :type export: bool

    :param upgrade: Whether or not to use upgrade files. Default is false.
    :type upgrade: bool

    :param forced: Force a software release. None to go for latest.
    :type forced: str
    """
    if export:
        print("\nEXPORTING...")
        npc = networkutils.return_npc(mcc, mnc)
        scriptutils.export_cchecker(files, npc, hwid, osv, radv, swv, upgrade, forced)


def carrierchecker_download(files, directory, osv, radv, swv, family, download=False, blitz=False, session=None):
    """
    Download files, create blitz if specified.

    :param files: List of files.
    :type files: list(str)

    :param directory: Where to store files. Default is local directory.
    :type directory: str

    :param osv: OS version, 10.x.y.zzzz.
    :type osv: str

    :param radv: Radio version, 10.x.y.zzzz.
    :type radv: str

    :param swv: Software release, 10.x.y.zzzz.
    :type swv: str

    :param family: Device family.
    :type family: str

    :param download: Whether or not to download. Default is false.
    :type download: bool

    :param blitz: Whether or not to create a blitz package. Default is false.
    :type blitz: bool

    :param session: Requests session object, default is created on the fly.
    :type session: requests.Session()
    """
    if download:
        suffix = "-BLITZ" if blitz else "-{0}".format(family)
        bardir = os.path.join(directory, "{0}{1}".format(swv, suffix))
        if not os.path.exists(bardir):
            os.makedirs(bardir)
        if blitz:
            files = scriptutils.generate_blitz_links(files, osv, radv, swv)
        print("\nDOWNLOADING...")
        networkutils.download_bootstrap(files, outdir=bardir, session=session)
        scriptutils.test_bar_files(bardir, files)
        if blitz:
            scriptutils.package_blitz(bardir, swv)
        print("\nFINISHED!!!")


def carrierchecker_main(mcc, mnc, device,
                        download=False, upgrade=True,
                        directory=None,
                        export=False,
                        blitz=False,
                        bundles=False,
                        forced=None,
                        selective=False):
    """
    Wrap around :mod:`bbarchivist.networkutils` carrier checking.

    :param mcc: Country code.
    :type mcc: int

    :param mnc: Network code.
    :type mnc: int

    :param device: Device ID (SXX100-#).
    :type device: str

    :param download: Whether or not to download. Default is false.
    :type download: bool

    :param upgrade: Whether or not to use upgrade files. Default is false.
    :type upgrade: bool

    :param directory: Where to store files. Default is local directory.
    :type directory: str

    :param export: Whether or not to write URLs to a file. Default is false.
    :type export: bool

    :param blitz: Whether or not to create a blitz package. Default is false.
    :type blitz: bool

    :param bundles: Whether or not to check software bundles. Default is false.
    :type bundles: bool

    :param forced: Force a software release. None to go for latest.
    :type forced: str

    :param selective: Whether or not to exclude Nuance/other dross. Default is false.
    :type selective: bool
    """
    device, directory = carrierchecker_argfilter(mcc, mnc, device, directory)
    model, family, hwid, country, carrier = carrierchecker_jsonprepare(mcc, mnc, device)
    scriptutils.slim_preamble("CARRIERCHECKER")
    print("COUNTRY: {0}".format(country.upper()))
    print("CARRIER: {0}".format(carrier.upper()))
    print("DEVICE: {0}".format(model.upper()))
    print("VARIANT: {0}".format(device.upper()))
    print("HARDWARE ID: {0}".format(hwid.upper()))
    print("\nCHECKING CARRIER...")
    if bundles:
        carrierchecker_bundles(mcc, mnc, hwid)
    else:
        npc = networkutils.return_npc(mcc, mnc)
        swv, osv, radv, files = networkutils.carrier_query(npc, hwid, upgrade, blitz, forced)
        print("SOFTWARE RELEASE: {0}".format(swv))
        print("OS VERSION: {0}".format(osv))
        print("RADIO VERSION: {0}".format(radv))
        files = carrierchecker_selective(files, selective)
        carrierchecker_export(mcc, mnc, files, hwid, osv, radv, swv, export, upgrade, forced)
        sess = requests.Session()
        carrierchecker_download(files, directory, osv, radv, swv, family, download, blitz, sess)


if __name__ == "__main__":
    grab_args()

#!/usr/bin/env python3
"""Checks a carrier for an OS version, can download."""

import sys  # load arguments
import os  # file/path operations
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

    Invoke :func:`carrierchecker.carrierchecker_main` with those arguments."""
    if len(sys.argv) > 1:
        parser = scriptutils.default_parser("bb-cchecker",
                                            "Carrier info checking")
        parser.add_argument("mcc",
                            help="1-3 digit country code",
                            type=utilities.valid_carrier)
        parser.add_argument("mnc",
                            help="1-3 digit carrier code",
                            type=utilities.valid_carrier)
        parser.add_argument("device", help="'STL100-1', 'SQW100-3', etc.")
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
            if avail != "SR not in system":
                forced = avail
            else:
                forced = None
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
    scriptutils.enter_to_exit(True)


def questionnaire():
    """
    Questions to ask if no arguments given.
    """
    while True:
        mcc = int(input("MCC: "))
        if mcc == utilities.valid_carrier(mcc):
            break
    while True:
        mnc = int(input("MNC: "))
        if mnc == utilities.valid_carrier(mnc):
            break
    device = input("DEVICE (SXX100-#): ")
    if not device:
        print("NO DEVICE SPECIFIED!")
        scriptutils.enter_to_exit(True)
        if not getattr(sys, 'frozen', False):
            raise SystemExit
    bundles = utilities.s2b(input("CHECK BUNDLES?: "))
    if bundles:
        download = False
        upgrade = False
        export = False
        blitz = False
    else:
        export = utilities.s2b(input("EXPORT TO FILE?: "))
        download = utilities.s2b(input("DOWNLOAD?: "))
        if download:
            upgrade = utilities.s2b(input("Y=UPGRADE BARS, N=DEBRICK BARS?: "))
            if upgrade:
                blitz = utilities.s2b(input("CREATE BLITZ?: "))
            else:
                blitz = False
        else:
            upgrade = False
            blitz = False
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

    :param device: Device ID (SXX100-#)
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
    device = device.upper()
    if directory is None:
        directory = os.getcwd()
    data = jsonutils.load_json('devices')
    model, family, hwid = jsonutils.certchecker_prep(data, device)
    print("~~~CARRIERCHECKER VERSION {0}~~~".format(bbconstants.VERSION))
    country, carrier = networkutils.carrier_checker(mcc, mnc)
    print("COUNTRY:", country.upper())
    print("CARRIER:", carrier.upper())
    print("DEVICE:", model.upper())
    print("VARIANT:", device.upper())
    print("HARDWARE ID:", hwid.upper())
    print("\nCHECKING CARRIER...")
    if bundles:
        releases = networkutils.available_bundle_lookup(mcc, mnc, hwid)
        print("\nAVAILABLE BUNDLES:")
        for bundle in releases:
            print(bundle)
    else:
        npc = networkutils.return_npc(mcc, mnc)
        swv, osv, radv, files = networkutils.carrier_query(npc, hwid, upgrade, blitz, forced)
        print("SOFTWARE RELEASE:", swv)
        print("OS VERSION:", osv)
        print("RADIO VERSION:", radv)
        if selective:
            files = scriptutils.purge_dross(files)
        if export:
            print("\nEXPORTING...")
            npc = networkutils.return_npc(mcc, mnc)
            scriptutils.export_cchecker(files, npc, hwid, osv, radv, swv, upgrade, forced)
        if download:
            if blitz:
                bardir = os.path.join(directory, swv + "-BLITZ")
            else:
                bardir = os.path.join(directory, swv + "-" + family)
            if not os.path.exists(bardir):
                os.makedirs(bardir)
            if blitz:
                files = scriptutils.generate_blitz_links(files, osv, radv, swv)
            print("\nDOWNLOADING...")
            networkutils.download_bootstrap(files, outdir=bardir)
            scriptutils.test_bar_files(bardir, files)
            if blitz:
                scriptutils.package_blitz(bardir, swv)
            print("\nFINISHED!!!")


if __name__ == "__main__":
    grab_args()

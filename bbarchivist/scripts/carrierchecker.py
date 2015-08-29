#!/usr/bin/env python3
#pylint: disable = I0011, R0201, W0613, C0301, R0913, R0912, R0914, R0915
"""Checks a carrier for an OS version, can download."""

from bbarchivist import bbconstants  # versions/constants
from bbarchivist import networkutils  # check function
from bbarchivist import barutils  # file/folder operations
from bbarchivist import textgenerator  # text work
from bbarchivist import utilities  # input validation
import argparse  # parse arguments
import sys  # load arguments
import os  # file/path operations
import shutil  # folder removal
import json  # db work


def grab_args():
    """
    Parse arguments from argparse/questionnaire.

    Invoke :func:`carrierchecker.carrierchecker_main` with those arguments."""
    if len(sys.argv) > 1:
        parser = argparse.ArgumentParser(
            prog="bb-cchecker",
            description="Checks a carrier for an OS version, can download.",
            epilog="http://github.com/thurask/bbarchivist")
        parser.add_argument(
            "-v",
            "--version",
            action="version",
            version="%(prog)s " +
            bbconstants.VERSION)
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
            avail = networkutils.software_release_lookup(args.forcedos, bbconstants.SERVERS['p'])
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
            forced)
    else:
        while True:
            mcc = int(input("MCC: "))
            if mcc == utilities.valid_carrier(mcc):
                break
        while True:
            mnc = int(input("MNC: "))
            if mnc == utilities.valid_carrier(mnc):
                break
        device = input("DEVICE (SXX100-#): ")
        bundles = utilities.str2bool(input("CHECK BUNDLES?: "))
        if bundles:
            download = False
            upgrade = False
            export = False
            blitz = False
        else:
            export = utilities.str2bool(input("EXPORT TO FILE?: "))
            download = utilities.str2bool(input("DOWNLOAD?: "))
            if download:
                upgrade = utilities.str2bool(input("UPGRADE BARS?: "))
                if upgrade:
                    blitz = utilities.str2bool(input("CREATE BLITZ?: "))
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
            None)
        smeg = input("Press Enter to exit")
        if smeg or not smeg:
            raise SystemExit


def carrierchecker_main(mcc, mnc, device,
                        download=False, upgrade=True,
                        directory=None,
                        export=False,
                        blitz=False,
                        bundles=False,
                        forced=None):
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
    """
    device = device.upper()
    if directory is None:
        directory = os.getcwd()
    with open(bbconstants.JSONFILE) as thefile:
        data = json.load(thefile)
    data = data['devices']
    for key in data:
        if 'secret' not in key:
            if key['name'] == device:
                model = key['device']
                family = key['family']
                hwid = key['hwid']
                break
    else:
        print("INVALID DEVICE!")
        raise SystemExit
    version = bbconstants.VERSION
    print("~~~CARRIERCHECKER VERSION", version + "~~~")
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
        swv, osv, radv, files = networkutils.carrier_update_request(npc,
                                                                    hwid,
                                                                    upgrade,
                                                                    blitz,
                                                                    forced)
        print("SOFTWARE RELEASE:", swv)
        print("OS VERSION:", osv)
        print("RADIO VERSION:", radv)
        if export:
            print("\nEXPORTING...")
            if files:
                if not upgrade:
                    npc = networkutils.return_npc(mcc, mnc)
                    newfiles = networkutils.carrier_update_request(npc, hwid, True, False, forced)
                    newfiles = newfiles[3]
                else:
                    newfiles = files
                osurls, coreurls, radiourls = textgenerator.url_generator(osv, radv, swv)
                finalfiles = []
                stoppers = ["8960", "8930", "8974", "m5730", "winchester"]
                for link in newfiles:
                    if all(word not in link for word in stoppers):
                        finalfiles.append(link)
                textgenerator.write_links(swv, osv, radv,
                                          osurls, coreurls, radiourls,
                                          True, True, finalfiles)
                print("\nFINISHED!!!")
            else:
                print("CANNOT EXPORT, NO SOFTWARE RELEASE")
        if download:
            if blitz:
                bardir = os.path.join(directory, swv + "-BLITZ")
            else:
                bardir = os.path.join(directory, swv + "-" + family)
            if not os.path.exists(bardir):
                os.makedirs(bardir)
            if blitz:
                baseurl = networkutils.create_base_url(swv)
                coreurls = [baseurl + "/winchester.factory_sfi-" +
                            osv + "-nto+armle-v7+signed.bar",
                            baseurl + "/qc8960.factory_sfi-" +
                            osv + "-nto+armle-v7+signed.bar",
                            baseurl + "/qc8960.factory_sfi_hybrid_qc8x30-" +
                            osv + "-nto+armle-v7+signed.bar",
                            baseurl + "/qc8960.factory_sfi_hybrid_qc8974-" +
                            osv + "-nto+armle-v7+signed.bar"]
                for i in coreurls:
                    files.append(i)
                # List of radio urls
                radiourls = [baseurl + "/m5730-" + radv +
                             "-nto+armle-v7+signed.bar",
                             baseurl + "/qc8960-" + radv +
                             "-nto+armle-v7+signed.bar",
                             baseurl + "/qc8960.wtr-" + radv +
                             "-nto+armle-v7+signed.bar",
                             baseurl + "/qc8960.wtr5-" +
                             radv + "-nto+armle-v7+signed.bar",
                             baseurl + "/qc8930.wtr5-" + radv +
                             "-nto+armle-v7+signed.bar",
                             baseurl + "/qc8974.wtr2-" + radv +
                             "-nto+armle-v7+signed.bar"]
                for i in radiourls:
                    files.append(i)
            print("\nDOWNLOADING...")
            networkutils.download_bootstrap(files, outdir=bardir)
            # integrity check
            brokenlist = []
            print("\nTESTING...")
            for file in os.listdir(bardir):
                if file.endswith(".bar"):
                    print("TESTING:", file)
                    thepath = os.path.abspath(os.path.join(bardir, file))
                    brokens = barutils.bar_tester(thepath)
                    if brokens is not None:
                        os.remove(brokens)
                        for url in files:
                            if brokens in url:
                                brokenlist.append(url)
            if brokenlist:
                if len(brokenlist) > 5:
                    workers = 5
                else:
                    workers = len(brokenlist)
                print("\nREDOWNLOADING BROKEN FILES...")
                networkutils.download_bootstrap(brokenlist,
                                                outdir=bardir,
                                                lazy=False,
                                                workers=workers)
                for file in os.listdir(bardir):
                    if file.endswith(".bar"):
                        thepath = os.path.abspath(os.path.join(bardir, file))
                        brokens = barutils.bar_tester(thepath)
                        if brokens is not None:
                            print(file, "STILL BROKEN")
                            raise SystemExit
            else:
                print("\nALL FILES DOWNLOADED OK")
            if blitz:
                print("\nCREATING BLITZ...")
                barutils.create_blitz(bardir, swv)
                print("\nTESTING BLITZ...")
                zipver = barutils.zip_verify("Blitz-" + swv + '.zip')
                if not zipver:
                    print("BLITZ FILE IS BROKEN")
                    raise SystemExit
                else:
                    shutil.rmtree(bardir)
            print("\nFINISHED!!!")

if __name__ == "__main__":
    grab_args()

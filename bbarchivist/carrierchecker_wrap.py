#!/usr/bin/env python3

import argparse  # parse arguments
import sys  # load arguments
import os  # folder operations
from . import carrierchecker  # main program
from . import bbconstants  # constants/versions
from . import utilities  # input validation


def main():
    """
    Parse arguments from argparse/questionnaire.

    Invoke :func:`bbarchivist.carrierchecker.do_magic` with those arguments.
    """
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
        parser.add_argument("mcc", help="1-3 digit country code")
        parser.add_argument("mnc", help="1-3 digit carrier code")
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
        comps = parser.add_argument_group("bartypes", "File types")
        compgroup = comps.add_mutually_exclusive_group()
        compgroup.add_argument(
            "-u", "--upgrade",
            dest="upgrade",
            help="Upgrade instead of debrick bars",
            action="store_true",
            default=False),
        compgroup.add_argument(
            "-r", "--repair",
            dest="upgrade",
            help="Debrick instead of upgrade bars",
            action="store_false",
            default=False),
        parser.add_argument(
            "-f",
            "--folder",
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
        parser.set_defaults(upgrade=False)
        args = parser.parse_args(sys.argv[1:])
        if args.folder is None:
            args.folder = os.getcwd()
        if args.blitz:
            args.upgrade = True  # blitz takes precedence
        carrierchecker.do_magic(
            args.mcc,
            args.mnc,
            args.device,
            args.download,
            args.upgrade,
            args.folder,
            args.export,
            args.blitz,
            args.bundles)
    else:
        mcc = int(input("MCC: "))
        mnc = int(input("MNC: "))
        device = input("DEVICE (SXX100-#): ")
        bundles = utilities.str2bool(input("CHECK BUNDLES?: "))
        if bundles:
            download = False
            upgrade = False
            export = False
            blitz = False
        else:
            download = utilities.str2bool(input("DOWNLOAD?: "))
            upgrade = utilities.str2bool(input("UPGRADE BARS?: "))
            export = utilities.str2bool(input("EXPORT TO FILE?: "))
            if download:
                if upgrade:
                    blitz = utilities.str2bool(input("CREATE BLITZ?: "))
                else:
                    blitz = False
            else:
                blitz = False
        directory = os.getcwd()
        print(" ")
        carrierchecker.do_magic(
            mcc,
            mnc,
            device,
            download,
            upgrade,
            directory,
            export,
            blitz)
        smeg = input("Press Enter to exit")
        if smeg or not smeg:
            raise SystemExit

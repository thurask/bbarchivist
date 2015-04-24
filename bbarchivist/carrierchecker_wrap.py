#!/usr/bin/env python3

import argparse
import sys
import os
from . import carrierchecker
from . import bbconstants
from . import utilities


def main():
    """
    Parse arguments from argparse/questionnaire.

    Invoke `carrierchecker.doMagic()` with those arguments.
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
            bbconstants._version)
        parser.add_argument("mcc", help="1-3 digit country code")
        parser.add_argument("mnc", help="1-3 digit carrier code")
        parser.add_argument("device", help="'STL100-1', 'SQW100-3', etc.")
        parser.add_argument(
            "-d", "--download",
            dest="download",
            type=str.lower(),
            help="Download files after checking",
            action="store_true",
            default=False)
        comps = parser.add_argument_group("bartypes", "File types")
        compgroup = comps.add_mutually_exclusive_group()
        compgroup.add_argument(
            "-u", "--upgrade",
            dest="upgrade",
            type=str.lower(),
            help="Upgrade instead of debrick bars",
            action="store_true",
            default=False),
        compgroup.add_argument(
            "-r", "--repair",
            dest="upgrade",
            type=str.lower(),
            help="Debrick instead of upgrade bars",
            action="store_false",
            default=False),
        parser.add_argument(
            "-f",
            "--folder",
            dest="folder",
            help="Working folder",
            default=os.getcwd(),
            metavar="DIR")
        parser.set_defaults(upgrade=False)
        args = parser.parse_args(sys.argv[1:])
        if not args.download:
            args.upgrade = False
        carrierchecker.doMagic(
            args.mcc,
            args.mnc,
            args.device,
            args.download,
            args.upgrade,
            args.folder)
    else:
        mcc = int(input("MCC: "))
        mnc = int(input("MNC: "))
        device = input("DEVICE (SXX100-#): ")
        download = utilities.str2bool(input("DOWNLOAD?: "))
        upgrade = utilities.str2bool(input("UPGRADE BARS?: "))
        directory = os.getcwd()
        print(" ")
        carrierchecker.doMagic(
            mcc,
            mnc,
            device,
            download,
            upgrade,
            directory)
        smeg = input("Press Enter to exit")  # @UnusedVariable

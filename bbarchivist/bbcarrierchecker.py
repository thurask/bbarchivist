import argparse
import sys
from . import carrierchecker
from . import bbconstants


def main():
    """
    Parse arguments from argparse/questionnaire.

    Invoke `carrierchecker.doMagic()` with those arguments.
    """
    if len(sys.argv) > 1:
        parser = argparse.ArgumentParser(
            prog="bb-cchecker",
            description="Checks a carrier for an OS version",
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
        args = parser.parse_args(sys.argv[1:])
        carrierchecker.doMagic(
            args.mcc,
            args.mnc,
            args.device)
    else:
        mcc = int(input("MCC: "))
        mnc = int(input("MNC: "))
        device = input("DEVICE (SXX100-#): ")
        print(" ")
        carrierchecker.doMagic(
            mcc,
            mnc,
            device)

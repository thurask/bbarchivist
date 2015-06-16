#!/usr/bin/env python3

import argparse  # parse arguments
import sys  # load arguments
from bbarchivist import autolookup  # main program
from bbarchivist import bbconstants  # versions/constants
from bbarchivist import utilities  # input validation


def main():
    """
    Parse arguments from argparse/questionnaire.

    Invoke :func:`bbarchivist.autolookup.do_magic` with those arguments.
    """
    if len(sys.argv) > 1:
        parser = argparse.ArgumentParser(
            prog="bb-autolookup",
            description="Get software release for one/many OS versions.",
            epilog="http://github.com/thurask/bbarchivist")
        parser.add_argument(
            "-v",
            "--version",
            action="version",
            version="%(prog)s " +
            bbconstants.VERSION)
        parser.add_argument("os", help="OS version, 10.x.y.zzzz")
        parser.add_argument(
            "-l", "--loop",
            dest="recurse",
            help="Loop lookup, CTRL-C to quit",
            action="store_true",
            default=False)
        parser.add_argument(
            "-o", "--output",
            dest="log",
            help="Output to file",
            action="store_true",
            default=False)
        parser.add_argument(
            "-a", "--autogen",
            dest="autogen",
            help="Generate links for availables",
            action="store_true",
            default=False)
        args = parser.parse_args(sys.argv[1:])
        parser.set_defaults()
        autolookup.do_magic(
            args.os,
            args.recurse,
            args.log,
            args.autogen)
    else:
        osversion = input("OS VERSION: ")
        recurse = utilities.str2bool(input("LOOP?: "))
        print(" ")
        autolookup.do_magic(
            osversion,
            recurse,
            True,
            False)
        smeg = input("Press Enter to exit")
        if smeg or not smeg:
            raise SystemExit

if __name__ == "__main__":
    main()

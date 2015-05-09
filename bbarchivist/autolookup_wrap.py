#!/usr/bin/env python3

import argparse
import sys
from . import autolookup
from . import bbconstants
from . import utilities


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
            help="Loop lookup; CTRL-C to quit",
            action="store_true",
            default=False)
        args = parser.parse_args(sys.argv[1:])
        autolookup.do_magic(
            args.os,
            args.recurse)
    else:
        osversion = input("OS VERSION: ")
        recurse = utilities.str2bool(input("LOOP?: "))
        print(" ")
        autolookup.do_magic(
            osversion,
            recurse)
        smeg = input("Press Enter to exit")  # @UnusedVariable

#!/usr/bin/env python3

import argparse
import sys
try:
    from . import linkgen  # @UnusedImport
except SystemError:
    import linkgen  # @UnresolvedImport @Reimport
try:
    from . import bbconstants  # @UnusedImport
except SystemError:
    import bbconstants  # @UnresolvedImport @Reimport


def main():
    """
    Parse arguments from argparse/questionnaire.

    Invoke :func:`bbarchivist.linkgen.do_magic` with those arguments.
    """
    if len(sys.argv) > 1:
        parser = argparse.ArgumentParser(
            prog="bb-linkgen",
            description="Generate links from OS/radio/software.",
            epilog="http://github.com/thurask/bbarchivist")
        parser.add_argument(
            "-v",
            "--version",
            action="version",
            version="%(prog)s " +
            bbconstants._version)
        parser.add_argument("os", help="OS version, 10.x.y.zzzz")
        parser.add_argument("radio", help="Radio version, 10.x.y.zzzz")
        parser.add_argument("swrelease", help="Software version, 10.x.y.zzzz")
        args = parser.parse_args(sys.argv[1:])
        linkgen.do_magic(
            args.os,
            args.radio,
            args.swrelease)
    else:
        osversion = input("OS VERSION: ")
        radioversion = input("RADIO VERSION: ")
        softwareversion = input("SOFTWARE RELEASE: ")
        print(" ")
        linkgen.do_magic(
            osversion,
            radioversion,
            softwareversion)
        smeg = input("Press Enter to exit")  # @UnusedVariable

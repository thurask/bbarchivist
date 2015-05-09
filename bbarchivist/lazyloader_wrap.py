#!/usr/bin/env python3

import argparse
import sys
import os
from . import lazyloader
from . import bbconstants
from . import utilities


def main():
    """
    Parse arguments from argparse/questionnaire.

    Invoke :func:`bbarchivist.lazyloader.do_magic` with those arguments.
    """
    if len(sys.argv) > 1:
        parser = argparse.ArgumentParser(
            prog="bb-lazyloader",
            description="Create one autoloader for personal use.",
            epilog="http://github.com/thurask/bbarchivist")
        parser.add_argument(
            "-v",
            "--version",
            action="version",
            version="%(prog)s " +
            bbconstants.VERSION)
        parser.add_argument("os", help="OS version, 10.x.y.zzzz")
        parser.add_argument("radio", help="Radio version, 10.x.y.zzzz")
        parser.add_argument("swrelease", help="Software version, 10.x.y.zzzz")
        devgroup = parser.add_argument_group(
            "devices",
            "Device to load (one required)")
        compgroup = devgroup.add_mutually_exclusive_group(required=True)
        compgroup.add_argument(
            "--stl100-1",
            dest="device",
            help="STL100-1",
            action="store_const",
            const=0)
        compgroup.add_argument(
            "--stl100-x",
            dest="device",
            help="STL100-2/3, P'9982",
            action="store_const",
            const=1)
        compgroup.add_argument(
            "--stl100-4",
            dest="device",
            help="STL100-4",
            action="store_const",
            const=2)
        compgroup.add_argument(
            "--q10",
            dest="device",
            help="Q10, Q5, P'9983",
            action="store_const",
            const=3)
        compgroup.add_argument(
            "--z30",
            dest="device",
            help="Z30, Classic, Leap",
            action="store_const",
            const=4)
        compgroup.add_argument(
            "--z3",
            dest="device",
            help="Z3",
            action="store_const",
            const=5)
        compgroup.add_argument(
            "--passport",
            dest="device",
            help="Passport",
            action="store_const",
            const=6)
        parser.add_argument(
            "--run-loader",
            dest="autoloader",
            help="Run autoloader after creation",
            action="store_true",
            default=False)
        parser.add_argument(
            "-f",
            "--folder",
            dest="folder",
            help="Working folder",
            default=os.getcwd(),
            metavar="DIR")
        args = parser.parse_args(sys.argv[1:])
        if not utilities.is_windows():
            args.autoloader = False
        lazyloader.do_magic(
            args.os,
            args.radio,
            args.swrelease,
            args.device,
            args.folder,
            args.autoloader)
    else:
        localdir = os.getcwd()
        osversion = input("OS VERSION: ")
        radioversion = input("RADIO VERSION: ")
        softwareversion = input("SOFTWARE RELEASE: ")
        device = int(input(
            """SELECTED DEVICE (0=STL100-1; 1=STL100-2/3/P9983; 2=STL100-4; 3=Q10/Q5/P9983;
4=Z30/CLASSIC/LEAP; 5=Z3; 6=PASSPORT): """))
        if utilities.is_windows():
            autoloader = utilities.str2bool(
                input("RUN AUTOLOADER (WILL WIPE YOUR DEVICE!)(Y/N)?: "))
        else:
            autoloader = False
        print(" ")
        lazyloader.do_magic(
            osversion,
            radioversion,
            softwareversion,
            device,
            localdir,
            autoloader)
        smeg = input("Press Enter to exit")  # @UnusedVariable

#!/usr/bin/env python3

import argparse  # parse arguments
import sys  # load arguments
import os  # path work
from bbarchivist import lazyloader  # main program
from bbarchivist import bbconstants  # constants/versions
from bbarchivist import utilities  # input validation


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
        parser.add_argument(
                            "os",
                            help="OS version, 10.x.y.zzzz")
        parser.add_argument(
                            "radio",
                            help="Radio version, 10.x.y.zzzz",
                            nargs="?",
                            default=None)
        parser.add_argument(
                            "swrelease",
                            help="Software version, 10.x.y.zzzz",
                            nargs="?",
                            default=None)
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
            default=None,
            metavar="DIR")
        args = parser.parse_args(sys.argv[1:])
        if args.folder is None:
            args.folder = os.getcwd()
        if not utilities.is_windows():
            args.autoloader = False
        lazyloader.do_magic(
            args.device,
            args.os,
            args.radio,
            args.swrelease,
            args.folder,
            args.autoloader)
    else:
        localdir = os.getcwd()
        osversion = input("OS VERSION: ")
        radioversion = input("RADIO VERSION (PRESS ENTER TO GUESS): ")
        if not radioversion:
            radioversion = None
        softwareversion = input("SOFTWARE RELEASE (PRESS ENTER TO GUESS): ")
        if not softwareversion:
            softwareversion = None
        while True:
            try:
                device = int(input(
                """SELECTED DEVICE (0=STL100-1; 1=STL100-2/3/P9983; 2=STL100-4; 3=Q10/Q5/P9983;
4=Z30/CLASSIC/LEAP; 5=Z3; 6=PASSPORT): """))
            except ValueError:
                continue
            else:
                break
        if utilities.is_windows():
            autoloader = utilities.str2bool(
                input("RUN AUTOLOADER (WILL WIPE YOUR DEVICE!)(Y/N)?: "))
        else:
            autoloader = False
        print(" ")
        lazyloader.do_magic(
            device,
            osversion,
            radioversion,
            softwareversion,
            localdir,
            autoloader)
        smeg = input("Press Enter to exit")
        if smeg or not smeg:
            raise SystemExit

if __name__ == "__main__":
    main()

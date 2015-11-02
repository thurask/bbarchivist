﻿#!/usr/bin/env python3
"""Create one autoloader for personal use."""

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "Copyright 2015 Thurask"

import argparse  # parse arguments
import sys  # load arguments
import os  # path work
import subprocess  # autoloader running
import pprint  # pretty printing
from bbarchivist import scriptutils  # script stuff
from bbarchivist import utilities  # input validation
from bbarchivist import barutils  # file operations
from bbarchivist import bbconstants  # constants/versions
from bbarchivist import networkutils  # download/lookup
from bbarchivist import loadergen  # cap wrapper


def grab_args():
    """
    Parse arguments from argparse/questionnaire.

    Invoke :func:`lazyloader.lazyloader_main` with arguments.
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
            version="%(prog)s " + bbconstants.VERSION)
        parser.add_argument(
            "os",
            help="OS version, 10.x.y.zzzz",
            nargs="?",
            default=None)
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
        compgroup = devgroup.add_mutually_exclusive_group()
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
        parser.add_argument(
            "-n",
            "--no-download",
            dest="download",
            help="Don't download files",
            action="store_false",
            default=True)
        parser.add_argument(
            "-r",
            "--radiosw",
            dest="altsw",
            metavar="SW",
            help="Radio software version; use without software to guess",
            nargs="?",
            const="checkme",
            default=None)
        parser.add_argument(
            "-c",
            "--core",
            dest="core",
            help="Make core/radio loader",
            default=False,
            action="store_true")
        parser.set_defaults(device=None)
        args = parser.parse_args(sys.argv[1:])
        if args.folder is None:
            args.folder = os.getcwd()
        if not utilities.is_windows():
            args.autoloader = False
        else:
            if args.os is None:
                raise argparse.ArgumentError(argument=None,
                                             message="No OS specified!")
            if args.device is None:
                raise argparse.ArgumentError(argument=None,
                                             message="No device specified!")
            else:
                lazyloader_main(args.device,
                                args.os,
                                args.radio,
                                args.swrelease,
                                args.folder,
                                args.autoloader,
                                args.download,
                                args.altsw,
                                args.core)
    else:
        questionnaire()


def questionnaire():
    """
    Questions to ask if no arguments given.
    """
    localdir = os.getcwd()
    while True:
        osversion = input("OS VERSION: ")
        if osversion:
            break
    print("OS:", osversion)
    radioversion = input("RADIO VERSION (PRESS ENTER TO GUESS): ")
    if not radioversion:
        radioversion = None
    else:
        print("RADIO:", radioversion)
    softwareversion = input("SOFTWARE RELEASE (PRESS ENTER TO GUESS): ")
    if not softwareversion:
        softwareversion = None
    else:
        print("SOFTWARE RELEASE:", softwareversion)
    altcheck = utilities.s2b(input("HYBRID AUTOLOADER (Y/N)?: "))
    if altcheck:
        print("CREATING HYBRID AUTOLOADER")
        altsw = input("RADIO SOFTWARE RELEASE (PRESS ENTER TO GUESS): ")
        if altsw:
            print("RADIO SOFTWARE RELEASE:", altsw)
        else:
            altsw = "checkme"
    else:
        altsw = None
    print("DEVICES:")
    inputlist = ["0=STL100-1",
                    "1=STL100-2/3/P9982",
                    "2=STL100-4",
                    "3=Q10/Q5/P9983",
                    "4=Z30/CLASSIC/LEAP",
                    "5=Z3",
                    "6=PASSPORT"]
    pprint.pprint(inputlist)
    while True:
        device = int(input("SELECTED DEVICE: "))
        if not (0 <= device <= len(inputlist) - 1):
            continue
        else:
            print("DEVICE:", bbconstants.DEVICES[device])
            break
    if utilities.is_windows():
        autoloader = utilities.s2b(
            input("RUN AUTOLOADER (WILL WIPE YOUR DEVICE!)(Y/N)?: "))
        if autoloader:
            print("RUN AUTOLOADER AFTER CREATION")
    else:
        autoloader = False
    print(" ")
    lazyloader_main(
        device,
        osversion,
        radioversion,
        softwareversion,
        localdir,
        autoloader,
        True,
        altsw,
        False)
    smeg = input("Press Enter to exit")
    if smeg or not smeg:
        raise SystemExit


def lazyloader_main(device, osversion, radioversion=None,
                    softwareversion=None, localdir=None, autoloader=False,
                    download=True, altsw=None, core=False):
    """
    Wrap the tools necessary to make one autoloader.

    :param device: Device family to create loader for.
    :type device: int

    :param osversion: OS version, 10.x.y.zzzz.
    :type osversion: str

    :param radioversion: Radio version, 10.x.y.zzzz.
    :type radioversion: str

    :param softwareversion: Software version, 10.x.y.zzzz.
    :type softwareversion: str

    :param localdir: Working path. Default is local dir.
    :type localdir: str

    :param autoloader: Whether to run loader. Default is false. Windows-only.
    :type autoloader: bool

    :param download: Whether to download files. Default is true.
    :type download: bool

    :param altsw: Radio software release, if not the same as OS.
    :type altsw: str

    :param core: Whether to create a core/radio loader. Default is false.
    :type core: bool
    """
    if (osversion or device) is None:
        raise SystemExit
    swc = False  # if we checked SW release already
    if altsw:
        altchecked = False
    radioversion = scriptutils.return_radio_version(osversion,
                                                    radioversion)
    softwareversion, swc = scriptutils.return_sw_checked(softwareversion,
                                                         osversion)
    if altsw == "checkme":
        altsw, altchecked = scriptutils.return_radio_sw_checked(altsw,
                                                                radioversion)
    print("~~~LAZYLOADER VERSION", bbconstants.VERSION + "~~~")
    print("OS VERSION:", osversion)
    print("SOFTWARE VERSION:", softwareversion)
    print("RADIO VERSION:", radioversion)
    if altsw is not None:
        print("RADIO SOFTWARE VERSION:", altsw)
    print("DEVICE:", bbconstants.DEVICES[device])

    # Make dirs
    bd_o, bd_r, ld_o, ld_r, zd_o, zd_r = barutils.make_dirs(localdir,
                                                            osversion,
                                                            radioversion)
    osurl = radiourl = None

    # Create download URLs
    if download:
        baseurl = networkutils.create_base_url(softwareversion)
        if altsw:
            alturl = networkutils.create_base_url(altsw)
        osurl, radiourl = utilities.generate_lazy_urls(baseurl,
                                                       osversion,
                                                       radioversion,
                                                       device)
        if altsw:
            radiourl = radiourl.replace(baseurl, alturl)
        if core:
            osurl = osurl.replace(".desktop", "")

        # Check availability of software releases
        scriptutils.check_sw(baseurl, softwareversion, swc)
        if altsw:
            scriptutils.check_radio_sw(alturl, altsw, altchecked)

        # Check availability of OS, radio
        scriptutils.check_os_single(osurl, osversion, device)
        radiourl, radioversion = scriptutils.check_radio_single(radiourl,
                                                                radioversion)

    dllist = [osurl, radiourl]

    # Download files
    if download:
        print("DOWNLOADING...")
        networkutils.download_bootstrap(dllist,
                                        outdir=localdir,
                                        lazy=True,
                                        workers=2)

    # Test bar files
    scriptutils.test_bar_files(localdir, dllist, download)

    # Extract bar files
    print("EXTRACTING...")
    barutils.extract_bars(localdir)

    # Test signed files
    scriptutils.test_signed_files(localdir)

    # Move bar files
    print("MOVING BAR FILES...")
    barutils.move_bars(localdir, bd_o, bd_r)

    # Generate loader
    if altsw:
        altradio = radioversion
    else:
        altradio = None
    loadergen.generate_lazy_loader(osversion, device,
                                   localdir=localdir,
                                   altradio=altradio,
                                   core=core)

    # Test loader
    suffix = loadergen.format_suffix(bool(altradio), altradio, core)
    loadername = loadergen.generate_filename(device, osversion, suffix)
    scriptutils.test_single_loader(loadername)

    # Remove signed files
    print("REMOVING SIGNED FILES...")
    barutils.remove_signed_files(localdir)

    # Move loaders
    print("MOVING LOADERS...")
    barutils.move_loaders(localdir, ld_o, ld_r, zd_o, zd_r)
    loadername = os.path.join(ld_o, loadername)

    # Delete empty folders
    print("REMOVING EMPTY FOLDERS...")
    barutils.remove_empty_folders(localdir)

    if autoloader:
        subprocess.call(loadername)
    print("\nFINISHED!!!")

if __name__ == "__main__":
    grab_args()

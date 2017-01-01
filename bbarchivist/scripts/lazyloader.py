#!/usr/bin/env python3
"""Create one autoloader for personal use."""

import argparse  # parse arguments
import sys  # load arguments
import os  # path work
import subprocess  # autoloader running
import requests  # session
from bbarchivist import scriptutils  # script stuff
from bbarchivist import decorators  # timer
from bbarchivist import utilities  # input validation
from bbarchivist import barutils  # file operations
from bbarchivist import bbconstants  # constants/versions
from bbarchivist import networkutils  # download/lookup
from bbarchivist import loadergen  # cap wrapper

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "2015-2017 Thurask"


@decorators.timer
def grab_args():
    """
    Parse arguments from argparse/questionnaire.

    Invoke :func:`lazyloader.lazyloader_main` with arguments.
    """
    if len(sys.argv) > 1:
        parser = scriptutils.default_parser("bb-lazyloader", "Create one autoloader",
                                            ("folder", "osr"))
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
        args.folder = scriptutils.generate_workfolder(args.folder)
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
        osversion = input("OS VERSION (REQUIRED): ")
        if osversion:
            break
    radioversion = input("RADIO VERSION (PRESS ENTER TO GUESS): ")
    softwareversion = input("OS SOFTWARE RELEASE (PRESS ENTER TO GUESS): ")
    if not softwareversion:
        softwareversion = None
    if not radioversion:
        radioversion = None
        altcheck = False
        altsw = None
    else:
        altcheck = utilities.s2b(input("USING ALTERNATE RADIO (Y/N)?: "))
        if altcheck:
            altsw = input("RADIO SOFTWARE RELEASE (PRESS ENTER TO GUESS): ")
            if not altsw:
                altsw = "checkme"
    print("DEVICES:")
    devlist = ["0=STL100-1",
               "1=STL100-2/3/P9982",
               "2=STL100-4",
               "3=Q10/Q5/P9983",
               "4=Z30/CLASSIC/LEAP",
               "5=Z3",
               "6=PASSPORT"]
    utilities.lprint(devlist)
    while True:
        device = int(input("SELECTED DEVICE: "))
        if not 0 <= device <= len(devlist) - 1:
            continue
        else:
            break
    if utilities.is_windows():
        autoloader = utilities.s2b(
            input("RUN AUTOLOADER - WILL WIPE YOUR DEVICE! (Y/N)?: "))
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
    radioversion = scriptutils.return_radio_version(osversion, radioversion)
    softwareversion, swc = scriptutils.return_sw_checked(softwareversion, osversion)
    if altsw == "checkme":
        altsw, altchecked = scriptutils.return_radio_sw_checked(altsw, radioversion)
    scriptutils.standard_preamble("lazyloader", osversion, softwareversion, radioversion, altsw)
    print("DEVICE: {0}".format(bbconstants.DEVICES[device]))

    # Make dirs
    bd_o, bd_r, ld_o, ld_r, zd_o, zd_r = barutils.make_dirs(localdir, osversion, radioversion)
    osurl = radiourl = None

    # Create download URLs
    baseurl = utilities.create_base_url(softwareversion)
    if altsw:
        alturl = utilities.create_base_url(altsw)
    osurl, radiourl = utilities.generate_lazy_urls(softwareversion, osversion, radioversion, device)
    if altsw:
        radiourl = radiourl.replace(baseurl, alturl)
    if core:
        osurl = osurl.replace(".desktop", "")

    if download:
        # Check availability of software releases
        scriptutils.check_sw(baseurl, softwareversion, swc)
        if altsw:
            scriptutils.check_radio_sw(alturl, altsw, altchecked)

        # Check availability of OS, radio
        scriptutils.check_os_single(osurl, osversion, device)
        radiourl, radioversion = scriptutils.check_radio_single(radiourl, radioversion)
    dllist = [osurl, radiourl]

    # Check cached
    osfile = os.path.join(localdir, bd_o, os.path.basename(osurl))
    radfile = os.path.join(localdir, bd_r, os.path.basename(radiourl))

    if download:
        # Download files
        print("DOWNLOADING...")
        sess = requests.Session()
        networkutils.download_bootstrap(dllist, outdir=localdir, workers=2, session=sess)
    elif all(os.path.exists(x) for x in [osfile, radfile]):
        # Already downloaded in previous session
        print("USING CACHED OS/RADIO...")
        barutils.replace_bar_pair(localdir, osfile, radfile)

    # Test bar files
    scriptutils.test_bar_files(localdir, dllist)

    # Extract bar files
    print("EXTRACTING...")
    barutils.extract_bars(localdir)

    # Test signed files
    scriptutils.test_signed_files(localdir)

    # Move bar files
    print("MOVING BAR FILES...")
    barutils.move_bars(localdir, bd_o, bd_r)

    # Generate loader
    altradio = radioversion if altsw else None
    loadergen.generate_lazy_loader(osversion, device, os.path.abspath(localdir), altradio, core)

    # Test loader
    suffix = loadergen.format_suffix(bool(altradio), altradio, core)
    loadername = loadergen.generate_filename(device, osversion, suffix)
    loaderpath = os.path.join(localdir, loadername)
    scriptutils.test_single_loader(loaderpath)

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
    decorators.enter_to_exit(True)

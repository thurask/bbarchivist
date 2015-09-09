#!/usr/bin/env python3
#pylint: disable = I0011, R0201, W0613, C0301, R0913, R0912, R0914, R0915, W0703
"""Create one autoloader for personal use."""

import argparse  # parse arguments
import sys  # load arguments
import os  # path work
import glob  # filename matching
import subprocess  # autoloader running
import json  # db work
import pprint  # pretty printing
from bbarchivist import scriptutils  # script stuff
from bbarchivist import utilities  # input validation
from bbarchivist import barutils  # file operations
from bbarchivist import bbconstants  # constants/versions
from bbarchivist import networkutils  # download/lookup
from bbarchivist import loadergen  # cap wrapper
try:
    import easygui as eg  # gui
except Exception:
    GUI_AVAILABLE = False
else:
    GUI_AVAILABLE = True


def start_gui(osv=None, radv=None, swv=None, dev=None, aut=None,
              fol=None, dow=None, alt=None):
    """
    Either passes straight through to the main function,
    or uses the GUI to prompt for variables.

    :param osv: OS version.
    :type osv: str

    :param radv: Radio version.
    :type radv: str

    :param swv: Software version.
    :type swv: str

    :param dev: Device index, as an integer.
    :type dev: int

    :param aut: Run autoloader or not. Windows only.
    :type aut: bool

    :param fol: Folder to download to.
    :type fol: str

    :param dow: Download files or not.
    :type dow: bool

    :param alt: Alternate software release, for alternate radio.
    :type alt: str
    """
    if osv is None:
        while True:
            osentry = eg.enterbox(msg="OS version")
            if osentry:
                break
    else:
        osentry = osv
    if swv is None:
        swentry = eg.enterbox(msg="Software version, click Cancel to guess")
        if not swentry:
            swentry = None
    else:
        swentry = swv
    if radv is None:
        radentry = eg.enterbox(msg="Radio version, click Cancel to guess")
        if not radentry:
            radentry = None
    else:
        radentry = radv
    if alt is None:
        altcheck = eg.boolbox(msg="Are you making a hybrid autoloader?",
                              default_choice="No")
        if altcheck:
            altentry = eg.enterbox(msg="Software version for radio")
            if not altentry:
                altentry = None
        else:
            altentry = None
    else:
        altentry = alt
    if dev is None:
        deventry = eg.choicebox(msg="Device", choices=bbconstants.DEVICES)
        for idx, device in enumerate(bbconstants.DEVICES):
            if device == deventry:
                devint = idx
    else:
        devint = dev
    if utilities.is_windows():
        if aut is None:
            autoentry = eg.boolbox(msg="Run autoloader?")
        else:
            autoentry = aut
    else:
        autoentry = False
    if fol is None:
        fol = os.getcwd()
    if dow is None:
        dow = True
    lazyloader_main(devint, osentry, radentry, swentry,
                    fol, autoentry, dow, altentry)


def grab_args():
    """
    Parse arguments from argparse/questionnaire.

    Invoke :func:`lazyloader.lazyloader_main` with arguments.
    """
    if len(sys.argv) > 1 or getattr(sys, 'frozen', False):
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
        guigroup = parser.add_mutually_exclusive_group()
        guigroup.add_argument(
            "-g",
            "--gui",
            dest="gui",
            help="Use GUI",
            default=False,
            action="store_true")
        guigroup.add_argument(
            "-ng",
            "--no-gui",
            dest="gui",
            help="Don't use GUI",
            default=False,
            action="store_false")
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
            help="Radio software version, if not same as OS",
            nargs="?",
            default=None)
        if getattr(sys, 'frozen', False):
            frozen = True
        else:
            frozen = False
        parser.set_defaults(device=None, gui=frozen)
        args = parser.parse_args(sys.argv[1:])
        if args.folder is None:
            args.folder = os.getcwd()
        if not utilities.is_windows():
            args.autoloader = False
        if not GUI_AVAILABLE:
            args.gui = False
        if args.gui:
            start_gui(args.os,
                      args.radio,
                      args.swrelease,
                      args.device,
                      args.autoloader,
                      args.folder,
                      args.download,
                      args.altsw)
        else:
            if not args.os:
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
                                args.altsw)
    else:
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
        altcheck = utilities.str2bool(input("HYBRID AUTOLOADER (Y/N)?: "))
        if altcheck:
            print("CREATING HYBRID AUTOLOADER")
            while True:
                altsw = input("RADIO SOFTWARE RELEASE: ")
                if altsw:
                    break
            print("RADIO SOFTWARE RELEASE:", altsw)
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
            try:
                device = int(input("SELECTED DEVICE: "))
                derp = inputlist[device]
            except (ValueError, IndexError):
                continue
            else:
                print("DEVICE:", bbconstants.DEVICES[device])
                del derp
                break
        if utilities.is_windows():
            autoloader = utilities.str2bool(
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
            altsw)
        smeg = input("Press Enter to exit")
        if smeg or not smeg:
            raise SystemExit


def lazyloader_main(device, osversion, radioversion=None,
                    softwareversion=None, localdir=None, autoloader=False,
                    download=True, altsw=None):
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

    :param autoloader: Whether to run loaders. Default is false. Windows-only.
    :type autoloader: bool

    :param download: Whether to download files. Default is true.
    :type download: bool

    :param altsw: Radio software release, if not the same as OS.
    :type altsw: str
    """
    if (osversion or device) is None:
        raise SystemExit
    swchecked = False  # if we checked SW release already
    radioversion = scriptutils.return_radio_version(osversion, radioversion)
    softwareversion, swchecked = scriptutils.return_sw_checked(softwareversion, osversion)
    print("~~~LAZYLOADER VERSION", bbconstants.VERSION + "~~~")
    print("OS VERSION:", osversion)
    print("SOFTWARE VERSION:", softwareversion)
    print("RADIO VERSION:", radioversion)
    if altsw is not None:
        print("RADIO SOFTWARE VERSION:", altsw)
    print("DEVICE:", bbconstants.DEVICES[device])

    # Make dirs
    bd_o, bd_r, ld_o, ld_r, zd_o, zd_r = barutils.make_dirs(localdir, osversion, radioversion)
    osurl = radiourl = None
    if download:
        baseurl = networkutils.create_base_url(softwareversion)
        if altsw:
            alturl = networkutils.create_base_url(altsw)
        osurl, radiourl = utilities.generate_lazy_urls(baseurl, osversion, radioversion, device)
        if altsw:
            radiourl = radiourl.replace(baseurl, alturl)

        # Check availability of software releases
        scriptutils.check_sw(baseurl, softwareversion, swchecked)
        if altsw:
            scriptutils.check_radio_sw(alturl, altsw)

        # Check availability of OS, radio
        scriptutils.check_os_single(osurl, osversion, device)
        radiourl, radioversion = scriptutils.check_radio_single(radiourl, radioversion)

    dllist = [osurl, radiourl]
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

    if altsw:
        altradio = radioversion
    else:
        altradio = None
    loadergen.generate_lazy_loader(osversion, device,
                                   localdir=localdir, altradio=altradio)

    print("REMOVING SIGNED FILES...")
    barutils.remove_signed_files(localdir)

    print("MOVING LOADERS...")
    barutils.move_loaders(localdir, ld_o, ld_r, zd_o, zd_r)

    # Delete empty folders
    print("REMOVING EMPTY FOLDERS...")
    barutils.remove_empty_folders(localdir)

    if autoloader:
        os.chdir(ld_o)
        with open(utilities.grab_json()) as thefile:
            data = json.load(thefile)
        data = data['integermap']
        for key in data:
            if key['id'] == device:
                fname = key['parts'][0]+"*"+key['parts'][1]+"*"
                break
        try:
            loaderfile = str(glob.glob(fname)[0])
        except IndexError:
            loaderfile = None
        if loaderfile is not None:
            print("\nSTARTING LOADER...")
            subprocess.call(loaderfile)
            print("\nFINISHED!!!")
        else:
            print("Error!")
            raise SystemExit
    else:
        print("\nFINISHED!!!")

if __name__ == "__main__":
    grab_args()

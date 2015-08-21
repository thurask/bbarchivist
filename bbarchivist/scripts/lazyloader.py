#!/usr/bin/env python3

import argparse  # parse arguments
import sys  # load arguments
import os  # path work
import glob  # filename matching
import shutil  # folder removal
import subprocess  # autoloader running
import json  # db work
from bbarchivist import utilities  # input validation
from bbarchivist import barutils  # file operations
from bbarchivist import bbconstants  # constants/versions
from bbarchivist import networkutils  # download/lookup
from bbarchivist import loadergen  # cap wrapper
import easygui as eg  # gui


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
    if not osv:
        osentry = eg.enterbox(msg="OS version")
    else:
        osentry = osv
    if not swv:
        swentry = eg.enterbox(msg="Software version, click Cancel to guess")
    else:
        swentry = swv
    if not radv:
        radentry = eg.enterbox(msg="Radio version, click Cancel to guess")
    else:
        radentry = radv
    if not alt:
        altcheck = eg.boolbox(msg="Are you making a hybrid autoloader?",
                              default_choice="No")
        if altcheck:
            altentry = eg.enterbox(msg="Software version for radio")
        else: altentry = None
    else:
        altentry = alt
    choicelist = ["STL100-1", "STL100-2/3/P9982", "STL100-4", "Q10/Q5/P9983",
                  "Z30/CLASSIC/LEAP", "Z3", "PASSPORT"]
    if dev is None:
        deventry = eg.choicebox(msg="Device", choices=choicelist)
        for idx, device in enumerate(choicelist):
            if device == deventry:
                devint = idx
    else:
        devint = dev
    if utilities.is_windows():
        if not aut:
            autoentry = eg.boolbox(msg="Run autoloader?")
        else:
            autoentry = aut
    else:
        autoentry = False
    if not fol:
        fol = os.getcwd()
    if not dow:
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
            version="%(prog)s " +
            bbconstants.VERSION)
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
            mu = True
        else:
            mu = False
        parser.set_defaults(device=None, gui=mu)
        args = parser.parse_args(sys.argv[1:])
        if args.folder is None:
            args.folder = os.getcwd()
        if not utilities.is_windows():
            args.autoloader = False
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
        osversion = input("OS VERSION: ")
        radioversion = input("RADIO VERSION (PRESS ENTER TO GUESS): ")
        if not radioversion:
            radioversion = None
        softwareversion = input("SOFTWARE RELEASE (PRESS ENTER TO GUESS): ")
        if not softwareversion:
            softwareversion = None
        altcheck = utilities.str2bool(input("HYBRID AUTOLOADER (Y/N)?: "))
        if altcheck:
            altsw = input("RADIO SOFTWARE RELEASE: ")
        else:
            altsw = None
        while True:
            inputlist = ["0=STL100-1",
                         "1=STL100-2/3/P9982",
                         "2=STL100-4",
                         "3=Q10/Q5/P9983",
                         "\n4=Z30/CLASSIC/LEAP",
                         "5=Z3",
                         "6=PASSPORT"]
            try:
                device = int(input(
                                   "SELECTED DEVICE (" +
                                   "; ".join(inputlist) +
                                   "): ")
                             )
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
    swchecked = False  # if we checked sw release already
    if radioversion is None:
        radioversion = utilities.version_incrementer(osversion, 1)
    if softwareversion is None:
        serv = bbconstants.SERVERS["p"]
        softwareversion = networkutils.software_release_lookup(osversion, serv)
        if softwareversion == "SR not in system":
            print("SOFTWARE RELEASE NOT FOUND")
            cont = utilities.str2bool(input("INPUT MANUALLY? Y/N: "))
            if cont:
                softwareversion = input("SOFTWARE RELEASE: ")
                swchecked = False
            else:
                print("\nEXITING...")
                raise SystemExit  # bye bye
        else:
            swchecked = True
    devicelist = ["STL100-1",
                  "STL100-2/3/P9982",
                  "STL100-4",
                  "Q10/Q5/P9983",
                  "Z30/CLASSIC/LEAP",
                  "Z3",
                  "PASSPORT"]
    print("~~~LAZYLOADER VERSION", bbconstants.VERSION + "~~~")
    print("OS VERSION:", osversion)
    print("SOFTWARE VERSION:", softwareversion)
    print("RADIO VERSION:", radioversion)
    if altsw is not None:
        print("RADIO SOFTWARE VERSION:", altsw)
    print("DEVICE:", devicelist[device])

    if download:
        baseurl = networkutils.create_base_url(softwareversion)
        if altsw:
            alturl = networkutils.create_base_url(altsw)
        osurl, radiourl = utilities.generate_lazy_urls(baseurl, osversion, radioversion, device)
        if altsw:
            radiourl = radiourl.replace(baseurl, alturl)

        # Check availability of software release
        if not swchecked:
            avlty = networkutils.availability(baseurl)
            if avlty:
                print("SOFTWARE RELEASE", softwareversion, "EXISTS")
            else:
                print("SOFTWARE RELEASE", softwareversion, "NOT FOUND")
                cont = utilities.str2bool(input("CONTINUE? Y/N: "))
                if cont:
                    pass
                else:
                    print("\nEXITING...")
                    raise SystemExit
        else:
            print("SOFTWARE RELEASE", softwareversion, "EXISTS")

        if altsw:
            print("\nCHECKING RADIO SOFTWARE RELEASE...")
            altavlty = networkutils.availability(alturl)
            if altavlty:
                print("SOFTWARE RELEASE", altsw, "EXISTS")
            else:
                print("SOFTWARE RELEASE", altsw, "NOT FOUND")
                cont = utilities.str2bool(input("CONTINUE? Y/N: "))
                if cont:
                    pass
                else:
                    print("\nEXITING...")
                    raise SystemExit

        # Check availability of specific OS
        osav = networkutils.availability(osurl)
        if not osav:
            print(osversion, "NOT AVAILABLE FOR", devicelist[device])
            cont = utilities.str2bool(input("CONTINUE? Y/N: "))
            if cont:
                pass
            else:
                print("\nEXITING...")
                raise SystemExit

        # Check availability of specific radio
        radav = networkutils.availability(radiourl)
        if not radav:
            print("RADIO VERSION NOT FOUND")
            cont = utilities.str2bool(input("INPUT MANUALLY? Y/N: "))
            if cont:
                rad2 = input("RADIO VERSION: ")
                radiourl = radiourl.replace(radioversion, rad2)
                radioversion = rad2
            else:
                going = utilities.str2bool(input("KEEP GOING? Y/N: "))
                if going:
                    pass
                else:
                    print("\nEXITING...")
                    raise SystemExit

        print("\nDOWNLOADING...")
        dllist = [osurl, radiourl]
        networkutils.download_bootstrap(dllist,
                                        outdir=localdir,
                                        lazy=True,
                                        workers=2)
    brokenlist = []
    print("\nTESTING BAR FILES...")
    for file in os.listdir(localdir):
        if file.endswith(".bar"):
            print("TESTING:", file)
            thepath = os.path.abspath(os.path.join(localdir, file))
            brokens = barutils.bar_tester(thepath)
            if brokens is not None:
                os.remove(brokens)
                for url in dllist:
                    if brokens in url:
                        brokenlist.append(url)
    if brokenlist:
        print("\nREDOWNLOADING BROKEN FILES...")
        networkutils.download_bootstrap(brokenlist,
                                        outdir=localdir,
                                        lazy=True,
                                        workers=len(brokenlist))
        for file in os.listdir(localdir):
            if file.endswith(".bar"):
                thepath = os.path.abspath(os.path.join(localdir, file))
                brokens = barutils.bar_tester(thepath)
                if brokens is not None:
                    print(file, "STILL BROKEN")
                    raise SystemExit
    else:
        print("ALL FILES DOWNLOADED OK")

    print("\nEXTRACTING...")
    barutils.extract_bars(localdir)

    print("\nTESTING SIGNED FILES...")
    for file in os.listdir(localdir):
        if file.endswith(".bar"):
            print("TESTING:", file)
            signname, signhash = barutils.retrieve_sha512(file)
            sha512ver = barutils.verify_sha512(signname, signhash)
            if not sha512ver:
                print("{0} IS BROKEN".format((file)))
                raise SystemExit
    print("ALL FILES EXTRACTED OK")

    # Make dirs
    bardir_os, bardir_radio, loaderdir_os, lr, zo, zr = barutils.make_dirs(localdir, osversion, radioversion)

    print("\nMOVING BAR FILES...")
    barutils.move_bars(localdir, bardir_os, bardir_radio)

    if altsw:
        altradio = radioversion
    else:
        altradio = None
    loadergen.generate_lazy_loader(osversion, device,
                                   localdir=localdir, altradio=altradio)

    print("\nREMOVING SIGNED FILES...")
    for file in os.listdir(localdir):
        if file.endswith(".signed"):
            print("REMOVING: " + file)
            os.remove(file)

    print("\nMOVING LOADERS...")
    barutils.move_loaders(localdir, loaderdir_os, lr, zo, zr)

    # Delete empty folders
    print("\nREMOVING EMPTY FOLDERS...")
    barutils.remove_empty_folders(localdir)

    if autoloader:
        os.chdir(loaderdir_os)
        with open(bbconstants.JSONFILE) as thefile:
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

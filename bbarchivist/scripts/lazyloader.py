#!/usr/bin/env python3

import argparse  # parse arguments
import sys  # load arguments
import os  # path work
import glob  # filename matching
import shutil  # folder removal
import subprocess  # autoloader running
from bbarchivist import utilities  # input validation
from bbarchivist import barutils  # file operations
from bbarchivist import bbconstants  # constants/versions
from bbarchivist import networkutils  # download/lookup
from bbarchivist import loadergen  # cap wrapper


def main():
    """
    Parse arguments from argparse/questionnaire.

    Invoke :func:`bbarchivist.scripts.lazyloader.do_magic` with those arguments.
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
        parser.add_argument(
            "-n",
            "--no-download",
            dest="download",
            help="Don't download files",
            action="store_false",
            default=True)
        args = parser.parse_args(sys.argv[1:])
        if args.folder is None:
            args.folder = os.getcwd()
        if not utilities.is_windows():
            args.autoloader = False
        do_magic(
            args.device,
            args.os,
            args.radio,
            args.swrelease,
            args.folder,
            args.autoloader,
            args.download)
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
        do_magic(
            device,
            osversion,
            radioversion,
            softwareversion,
            localdir,
            autoloader,
            True)
        smeg = input("Press Enter to exit")
        if smeg or not smeg:
            raise SystemExit

if __name__ == "__main__":
    main()


def do_magic(device, osversion, radioversion=None,
             softwareversion=None, localdir=None, autoloader=False,
             download=True):
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
    print("RADIO VERSION:", radioversion)
    print("SOFTWARE VERSION:", softwareversion)
    print("DEVICE:", devicelist[device])

    if download:
        baseurl = networkutils.create_base_url(softwareversion)
        splitos = osversion.split(".")
        splitos = [int(i) for i in splitos]

        if device == 0:
            osurl = baseurl + "/winchester.factory_sfi.desktop-"
            osurl += osversion + "-nto+armle-v7+signed.bar"
            radiourl = baseurl + "/m5730-"
            radiourl += radioversion + "-nto+armle-v7+signed.bar"
        elif device == 1:
            osurl = baseurl + "/qc8960.factory_sfi.desktop-"
            osurl += osversion + "-nto+armle-v7+signed.bar"
            radiourl = baseurl + "/qc8960-"
            radiourl += radioversion + "-nto+armle-v7+signed.bar"
        elif device == 2:
            osurl = baseurl + "/qc8960.verizon_sfi.desktop-"
            osurl += osversion + "-nto+armle-v7+signed.bar"
            radiourl = baseurl + "/qc8960.omadm-"
            radiourl += radioversion + "-nto+armle-v7+signed.bar"
        elif device == 3:
            osurl = baseurl + "/qc8960.factory_sfi.desktop-"
            osurl += osversion + "-nto+armle-v7+signed.bar"
            radiourl = baseurl + "/qc8960.wtr-"
            radiourl += radioversion + "-nto+armle-v7+signed.bar"
        elif device == 4:
            osurl = baseurl + "/qc8960.factory_sfi.desktop-"
            osurl += osversion + "-nto+armle-v7+signed.bar"
            radiourl = baseurl + "/qc8960.wtr5-"
            radiourl += radioversion + "-nto+armle-v7+signed.bar"
        elif device == 5:
            osurl = baseurl + "/qc8960.factory_sfi.desktop-"
            osurl += osversion + "-nto+armle-v7+signed.bar"
            radiourl = baseurl + "/qc8930.wtr5-"
            radiourl += radioversion + "-nto+armle-v7+signed.bar"
            if (splitos[1] >= 4) or (splitos[1] == 3 and splitos[2] >= 1):
                osurl = osurl.replace("qc8960.factory_sfi",
                                      "qc8960.factory_sfi_hybrid_qc8x30")
        elif device == 6:
            osurl = baseurl + "/qc8974.factory_sfi.desktop-"
            osurl += osversion + "-nto+armle-v7+signed.bar"
            radiourl = baseurl + "/qc8974.wtr2-"
            radiourl += radioversion + "-nto+armle-v7+signed.bar"
            if (splitos[1] >= 4) or (splitos[1] == 3 and splitos[2] >= 1):
                osurl = osurl.replace("qc8974.factory_sfi",
                                      "qc8960.factory_sfi_hybrid_qc8974")
        else:
            return

        # Check availability of software release
        if not swchecked:
            avlty = networkutils.availability(baseurl)
            if avlty:
                print("\nSOFTWARE RELEASE", softwareversion, "EXISTS")
            else:
                print("\nSOFTWARE RELEASE", softwareversion, "NOT FOUND")
                cont = utilities.str2bool(input("CONTINUE? Y/N: "))
                if cont:
                    pass
                else:
                    print("\nEXITING...")
                    raise SystemExit
        else:
            print("\nSOFTWARE RELEASE", softwareversion, "EXISTS")

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
    print("\nTESTING...")
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
        print("\nALL FILES DOWNLOADED OK")

    print("\nEXTRACTING...")
    barutils.extract_bars(localdir)

    # Make dirs
    if not os.path.exists(localdir):
        os.makedirs(localdir)

    if not os.path.exists(os.path.join(localdir, 'bars')):
        os.mkdir(os.path.join(localdir, 'bars'))
    bardir = os.path.join(localdir, 'bars')
    if not os.path.exists(os.path.join(bardir, osversion)):
        os.mkdir(os.path.join(bardir, osversion))
    bardir_os = os.path.join(bardir, osversion)
    if not os.path.exists(os.path.join(bardir, radioversion)):
        os.mkdir(os.path.join(bardir, radioversion))
    bardir_radio = os.path.join(bardir, radioversion)

    if not os.path.exists(os.path.join(localdir, 'loaders')):
        os.mkdir(os.path.join(localdir, 'loaders'))
    loaderdir = os.path.join(localdir, 'loaders')
    if not os.path.exists(os.path.join(loaderdir, osversion)):
        os.mkdir(os.path.join(loaderdir, osversion))
    loaderdir_os = os.path.join(loaderdir, osversion)

    print("\nMOVING .bar FILES...")
    for files in os.listdir(localdir):
        if files.endswith(".bar"):
            print("MOVING: " + files)
            bardest_os = os.path.join(bardir_os, files)
            bardest_radio = os.path.join(bardir_radio, files)
            if os.path.getsize(files) > 90000000:
                try:
                    shutil.move(files, bardir_os)
                except shutil.Error:
                    os.remove(bardest_os)
            else:
                try:
                    shutil.move(files, bardir_radio)
                except shutil.Error:
                    os.remove(bardest_radio)

    loadergen.generate_lazy_loader(osversion, device,
                                   cap=utilities.grab_cap(),
                                   localdir=localdir)

    print("\nREMOVING .signed FILES...")
    for file in os.listdir(localdir):
        if file.endswith(".signed"):
            print("REMOVING: " + file)
            os.remove(file)

    print("\nMOVING LOADERS...")
    for files in os.listdir(localdir):
        if files.endswith(
            (".exe")
        ) and files.startswith(
                ("Q10", "Z10", "Z30", "Z3", "Passport")):
            loaderdest_os = os.path.join(loaderdir_os, files)
            print("MOVING: " + files)
            try:
                shutil.move(files, loaderdir_os)
            except shutil.Error:
                os.remove(loaderdest_os)

    print("\nCREATION FINISHED!")
    if autoloader:
        os.chdir(loaderdir_os)
        if device == 0:
            loaderfile = str(glob.glob("Z10*STL100-1*")[0])
        elif device == 1:
            loaderfile = str(glob.glob("Z10*STL100-2-3*")[0])
        elif device == 2:
            loaderfile = str(glob.glob("Z10*STL100-4*")[0])
        elif device == 3:
            loaderfile = str(glob.glob("Q10*")[0])
        elif device == 4:
            loaderfile = str(glob.glob("Z30*")[0])
        elif device == 5:
            loaderfile = str(glob.glob("Z3*")[0])
        elif device == 6:
            loaderfile = str(glob.glob("Passport*")[0])
        else:
            loaderfile = None
        if loaderfile is not None:
            subprocess.call(loaderfile)
            print("\nFINISHED!!!")
        else:
            print("Error!")
            raise SystemExit
    else:
        print("\nFINISHED!!!")

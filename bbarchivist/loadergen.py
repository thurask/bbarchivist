#!/usr/bin/env python3

"""This module is used for creation of autoloaders. 
A higher level interface for :mod:`bbarchivist.pseudocap`."""

__author__ = "Thurask"
__license__ = "Do whatever"
__copyright__ = "2015 Thurask"

import os  # path work
import glob  # filename matching
from bbarchivist import pseudocap  # implement cap
from bbarchivist import utilities  # cap location


def generate_loaders(
        osversion, radioversion, radios=True,
        localdir=None, altradio=False):
    """
    Create and label autoloaders for :mod:`bbarchivist.scripts.archivist`.

    :param osversion: OS version, 10.x.y.zzzz.
    :type osversion: str

    :param radioversion: Radio version, 10.x.y.zzzz.
    :type radioversion: str

    :param radios: Whether to make radios or not. True by default.
    :type radios: bool

    :param localdir: Working path. Default is local dir.
    :type localdir: str

    :param altradio: If we're using an alternate radio. Default is false.
    :type altradio: bool
    """
    # default parsing
    if localdir is None:
        localdir = os.getcwd()
    # OS Images
    print("GETTING FILENAMES...")
    # 8960
    try:
        os_8960 = glob.glob(
            os.path.join(
                localdir,
                "*qc8960*_sfi.desktop*.signed"))[0]
    except IndexError:
        os_8960 = None
        print("No 8960 image found")
    # 8x30 (10.3.1 MR+)
    try:
        os_8x30 = glob.glob(
            os.path.join(
                localdir,
                "*qc8x30*desktop*.signed"))[0]
    except IndexError:
        try:
            os_8x30 = glob.glob(
                os.path.join(
                    localdir,
                    "*qc8960*_sfi.desktop*.signed"))[0]
        except IndexError:
            os_8x30 = None
            print("No 8x30 image found")
    # 8974
    try:
        os_8974 = glob.glob(
            os.path.join(
                localdir,
                "*qc8974*desktop*.signed"))[0]
    except IndexError:
        os_8974 = None
        print("No 8974 image found")
    # OMAP (incl. 10.3.1)
    try:
        os_ti = glob.glob(os.path.join(localdir, "*winchester*.signed"))[0]
    except IndexError:
        try:
            os_ti = glob.glob(os.path.join(localdir,
                                           "*os.factory_sfi.*.signed"))[0]
        except IndexError:
            os_ti = None
            print("No OMAP image found")
    # Radio files
    # STL100-1
    try:
        radio_z10_ti = glob.glob(
            os.path.join(
                localdir,
                "*radio.m5730*.signed"))[0]
    except IndexError:
        radio_z10_ti = None
        print("No OMAP radio found")
    # STL100-X
    try:
        radio_z10_qcm = glob.glob(
            os.path.join(
                localdir,
                "*radio.qc8960.BB*.signed"))[0]
    except IndexError:
        radio_z10_qcm = None
        print("No 8960 radio found")
    # STL100-4
    try:
        radio_z10_vzw = glob.glob(
            os.path.join(
                localdir,
                "*radio.qc8960*omadm*.signed"))[0]
    except IndexError:
        radio_z10_vzw = None
        print("No Verizon 8960 radio found")
    # Q10/Q5
    try:
        radio_q10 = glob.glob(os.path.join(localdir, "*8960*wtr.*.signed"))[0]
    except IndexError:
        radio_q10 = None
        print("No Q10/Q5 radio found")
    # Z30/Classic
    try:
        radio_z30 = glob.glob(os.path.join(localdir, "*8960*wtr5*.signed"))[0]
    except IndexError:
        radio_z30 = None
        print("No Z30/Classic radio found")
    # Z3
    try:
        radio_z3 = glob.glob(os.path.join(localdir, "*8930*wtr5*.signed"))[0]
    except IndexError:
        radio_z3 = None
        print("No Z3 radio found")
    # Passport
    try:
        radio_8974 = glob.glob(os.path.join(localdir, "*8974*wtr2*.signed"))[0]
    except IndexError:
        radio_8974 = None
        print("No Passport radio found")
    # Pretty format names
    # 10.x.y.zzz becomes 10.x.0y.0zzz
    splitos = osversion.split(".")
    if len(splitos[2]) == 1:
        splitos[2] = "0" + splitos[2]
    if len(splitos[3]) < 4:
        splitos[3] = splitos[3].rjust(4, '0')
    osversion = ".".join(splitos)
    splitrad = radioversion.split(".")
    if len(splitrad[2]) == 1:
        splitrad[2] = "0" + splitrad[2]
    if len(splitrad[3]) < 4:
        splitrad[3] = splitrad[3].rjust(4, '0')
    radioversion = ".".join(splitrad)
    if altradio:
        suffix = "_R"+radioversion
    else:
        suffix = ""
    # Generate loaders
    print("\nCREATING LOADERS...")
    # STL100-1
    if os_ti is not None and radio_z10_ti is not None:
        try:
            print("\nCreating OMAP Z10 OS...")
            pseudocap.make_autoloader(
                filename="Z10_" +
                osversion +
                suffix + 
                "_STL100-1.exe",
                firstfile=os_ti,
                secondfile=radio_z10_ti,
                folder=localdir)
        except Exception as exc:
            print(str(exc))
            print("Could not create STL100-1 OS/radio loader")
    if radios:
        if radio_z10_ti is not None:
            print("Creating OMAP Z10 radio...")
            try:
                pseudocap.make_autoloader(
                    "Z10_" +
                    radioversion +
                    "_STL100-1.exe",
                    firstfile=radio_z10_ti,
                    folder=localdir)
            except Exception as exc:
                print(str(exc))
                print("Could not create STL100-1 radio loader")
    # STL100-X
    if os_8960 is not None and radio_z10_qcm is not None:
        try:
            print("\nCreating Qualcomm Z10 OS...")
            pseudocap.make_autoloader(
                "Z10_" +
                osversion +
                suffix + 
                "_STL100-2-3.exe",
                firstfile=os_8960,
                secondfile=radio_z10_qcm,
                folder=localdir)
        except Exception as exc:
            print(str(exc))
            print("Could not create Qualcomm Z10 OS/radio loader")
    if radios:
        if radio_z10_qcm is not None:
            print("Creating Qualcomm Z10 radio...")
            try:
                pseudocap.make_autoloader(
                    "Z10_" +
                    radioversion +
                    "_STL100-2-3.exe",
                    firstfile=radio_z10_qcm,
                    folder=localdir)
            except Exception as exc:
                print(str(exc))
                print("Could not create Qualcomm Z10 radio loader")
    # STL100-4
    if os_8960 is not None and radio_z10_vzw is not None:
        try:
            print("\nCreating Verizon Z10 OS...")
            pseudocap.make_autoloader(
                "Z10_" +
                osversion +
                suffix + 
                "_STL100-4.exe",
                firstfile=os_8960,
                secondfile=radio_z10_vzw,
                folder=localdir)
        except Exception as exc:
            print(str(exc))
            print("Could not create Verizon Z10 OS/radio loader")
    if radios:
        if radio_z10_vzw is not None:
            print("Creating Verizon Z10 radio...")
            try:
                pseudocap.make_autoloader(
                    "Z10_" +
                    radioversion +
                    "_STL100-4.exe",
                    firstfile=radio_z10_vzw,
                    folder=localdir)
            except Exception as exc:
                print(str(exc))
                print("Could not create Verizon Z10 radio loader")
    # Q10/Q5
    if os_8960 is not None and radio_q10 is not None:
        try:
            print("\nCreating Q10/Q5 OS...")
            pseudocap.make_autoloader(
                "Q10_" +
                osversion +
                suffix + 
                "_SQN100-1-2-3-4-5.exe",
                firstfile=os_8960,
                secondfile=radio_q10,
                folder=localdir)
        except Exception as exc:
            print(str(exc))
            print("Could not create Q10/Q5 OS/radio loader")
    if radios:
        if radio_q10 is not None:
            print("Creating Q10/Q5 radio...")
            try:
                pseudocap.make_autoloader(
                    "Q10_" +
                    radioversion +
                    "_SQN100-1-2-3-4-5.exe",
                    firstfile=radio_q10,
                    folder=localdir)
            except Exception as exc:
                print(str(exc))
                print("Could not create Q10/Q5 radio loader")
    # Z30/Classic
    if os_8960 is not None and radio_z30 is not None:
        try:
            print("\nCreating Z30/Classic OS...")
            pseudocap.make_autoloader(
                "Z30_" +
                osversion +
                suffix + 
                "_STA100-1-2-3-4-5-6.exe",
                firstfile=os_8960,
                secondfile=radio_z30,
                folder=localdir)
        except Exception as exc:
            print(str(exc))
            print("Could not create Z30/Classic OS/radio loader")
    if radios:
        if radio_z30 is not None:
            print("Creating Z30/Classic radio...")
            try:
                pseudocap.make_autoloader(
                    "Z30_" +
                    radioversion +
                    "_STA100-1-2-3-4-5-6.exe",
                    firstfile=radio_z30,
                    folder=localdir)
            except Exception as exc:
                print(str(exc))
                print("Could not create Z30/Classic radio loader")
    # Z3
    if os_8x30 is not None and radio_z3 is not None:
        try:
            print("\nCreating Z3 OS...")
            pseudocap.make_autoloader(
                "Z3_" +
                osversion +
                suffix + 
                "_STJ100-1-2.exe",
                firstfile=os_8x30,
                secondfile=radio_z3,
                folder=localdir)
        except Exception as exc:
            print(str(exc))
            print("Could not create Z3 OS/radio loader")
    if radios:
        if radio_z3 is not None:
            print("Creating Z3 radio...")
            try:
                pseudocap.make_autoloader(
                    "Z3_" +
                    radioversion +
                    "_STJ100-1-2.exe",
                    firstfile=radio_z3,
                    folder=localdir)
            except Exception as exc:
                print(str(exc))
                print("Could not create Z3 radio loader")
    # Passport
    if os_8974 is not None and radio_8974 is not None:
        try:
            print("\nCreating Passport OS...")
            pseudocap.make_autoloader(
                "Passport_" +
                osversion +
                suffix + 
                "_SQW100-1-2-3-4.exe",
                firstfile=os_8974,
                secondfile=radio_8974,
                folder=localdir)
        except Exception as exc:
            print(str(exc))
            print("Could not create Passport OS/radio loader")
    if radios:
        if radio_8974 is not None:
            print("Creating Passport radio...")
            try:
                pseudocap.make_autoloader(
                    "Passport_" +
                    radioversion +
                    "_SQW100-1-2-3-4.exe",
                    firstfile=radio_8974,
                    folder=localdir)
            except Exception as exc:
                print(str(exc))
                print("Could not create Passport radio loader")


def generate_lazy_loader(
        osversion, device,
        localdir=None, altradio=None):
    """
    Create and label autoloaders for :mod:`bbarchivist.scripts.lazyloader`.
    :func:`generate_loaders`, but for making one OS/radio loader.

    :param osversion: OS version, 10.x.y.zzzz.
    :type osversion: str

    :param device: Selected device, from
    :type device: int

    :param localdir: Working path. Default is local dir.
    :type localdir: str

    :param altradio: The alternate radio in use, if there is one.
    :type altradio: str
    """
    # default parsing
    if localdir is None:
        localdir = os.getcwd()
    print("\nCREATING LOADER...")
    if altradio:
        suffix = "_R"+altradio
    else:
        suffix = ""
    try:
        osfile = str(glob.glob("*desktop*.signed")[0])
    except IndexError:
        print("No OS found")
        return
    try:
        rset = set(glob.glob("*.signed")) - set(glob.glob("*desktop*.signed"))
        radiofile = str(list(rset)[0])
    except IndexError:
        print("No radio found")
        return
    if device == 0:
        loadername = "Z10_" + osversion + suffix + "_STL100-1.exe"
    elif device == 1:
        loadername = "Z10_" + osversion + suffix + "_STL100-2-3.exe"
    elif device == 2:
        loadername = "Z10_" + osversion + suffix + "_STL100-4.exe"
    elif device == 3:
        loadername = "Q10_" + osversion + suffix + "_SQN100-1-2-3-4-5.exe"
    elif device == 4:
        loadername = "Z30_" + osversion + suffix + "_STA100-1-2-3-4-5-6.exe"
    elif device == 5:
        loadername = "Z3_" + osversion + suffix + "_STJ100-1-2.exe"
    elif device == 6:
        loadername = "Passport_" + osversion + suffix + "_SQW100-1-2-3-4.exe"
    else:
        print("Invalid device")
        return
    try:
        pseudocap.make_autoloader(
            filename=loadername,
            firstfile=osfile,
            secondfile=radiofile,
            folder=localdir)
    except Exception as exc:
        print(str(exc))
        print("Could not create autoloader")
        return

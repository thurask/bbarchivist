#!/usr/bin/env python3
#pylint: disable = I0011, R0201, W0613, C0301, R0913, R0912, R0914, R0915
"""This module is used for creation of autoloaders.
A higher level interface for :mod:`bbarchivist.pseudocap`."""

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "2015 Thurask"

import os  # path work
import glob  # filename matching
import json  # db work
from bbarchivist import pseudocap  # implement cap
from bbarchivist import utilities  # json


def read_files(localdir):
    """
    Read list of signed files, return name assignments.

    :param localdir: Directory to use.
    :type localdir: str
    """
    oslist = read_os_files(localdir)
    radlist = read_radio_files(localdir)
    pairdict = {}
    # [radio_ti, radio_z10, radio_z10_vzw, radio_q10, radio_z30, radio_z3, radio_8974]
    for idx, rad in enumerate(radlist):
        if idx == 0:
            pairdict[rad] = oslist[3]
        elif idx == 5:
            pairdict[rad] = oslist[1]
        elif idx == 6:
            pairdict[rad] = oslist[2]
        else:
            pairdict[rad] = oslist[0]
    filtdict = dict((k, v) for k, v in pairdict.items() if k)  # pop None
    return filtdict


def read_os_files(localdir):
    """
    Read list of OS signed files, return name assignments.

    :param localdir: Directory to use.
    :type localdir: str
    """
    # 8960
    try:
        os_8960 = glob.glob(
            os.path.join(
                localdir,
                "*qc8960.*_sfi.desktop*.signed"))[0]
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
                    "*qc8960.*_sfi.desktop*.signed"))[0]
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
    # OMAP
    try:
        os_ti = glob.glob(os.path.join(localdir, "*winchester*.signed"))[0]
    except IndexError:
        try:
            os_ti = glob.glob(os.path.join(localdir, "*os.factory_sfi.*.signed"))[0]
        except IndexError:
            os_ti = None
            print("No OMAP image found")
    return [os_8960, os_8x30, os_8974, os_ti]


def read_radio_files(localdir):
    """
    Read list of radio signed files, return name assignments.

    :param localdir: Directory to use.
    :type localdir: str
    """
    # STL100-1
    try:
        radio_ti = glob.glob(
            os.path.join(
                localdir,
                "*radio.m5730*.signed"))[0]
    except IndexError:
        radio_ti = None
        print("No OMAP radio found")
    # STL100-X
    try:
        radio_z10 = glob.glob(
            os.path.join(
                localdir,
                "*radio.qc8960.BB*.signed"))[0]
    except IndexError:
        radio_z10 = None
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
        radio_q10 = glob.glob(os.path.join(localdir, "*radio.qc8960*wtr.*signed"))[0]
    except IndexError:
        radio_q10 = None
        print("No Q10/Q5 radio found")
    # Z30/Classic
    try:
        radio_z30 = glob.glob(os.path.join(localdir, "*radio.qc8960*wtr5*.signed"))[0]
    except IndexError:
        radio_z30 = None
        print("No Z30/Classic radio found")
    # Z3
    try:
        radio_z3 = glob.glob(os.path.join(localdir, "*radio.qc8930*wtr5*.signed"))[0]
    except IndexError:
        radio_z3 = None
        print("No Z3 radio found")
    # Passport
    try:
        radio_8974 = glob.glob(os.path.join(localdir, "*radio.qc8974*wtr2*.signed"))[0]
    except IndexError:
        radio_8974 = None
        print("No Passport radio found")
    return [radio_ti, radio_z10, radio_z10_vzw, radio_q10, radio_z30, radio_z3, radio_8974]


def pretty_formatter(osversion, radioversion):
    """
    Format OS/radio versions to cope with systems with poor sorting.

    :param osversion: OS version, 10.x.y.zzzz.
    :type osversion: str

    :param radioversion: Radio version, 10.x.y.zzzz.
    :type radioversion: str
    """
    # 10.x.y.zzz becomes 10.x.0y.0zzz
    splitos = osversion.split(".")
    if len(splitos[2]) == 1:
        splitos[2] = "0" + splitos[2]
    if len(splitos[3]) < 4:
        splitos[3] = splitos[3].rjust(4, '0')
    the_os = ".".join(splitos)
    splitrad = radioversion.split(".")
    if len(splitrad[2]) == 1:
        splitrad[2] = "0" + splitrad[2]
    if len(splitrad[3]) < 4:
        splitrad[3] = splitrad[3].rjust(4, '0')
    the_radio = ".".join(splitrad)
    return the_os, the_radio


def format_suffix(altradio=None, radioversion=None):
    """
    Formulate suffix for hybrid autoloaders.

    :param altradio: If a hybrid autoloader is being made.
    :type altradio: bool

    :param radioversion: The hybrid radio version, if applicable.
    :type radioversion: str
    """
    if altradio and radioversion:
        suffix = "_R"+radioversion
    else:
        suffix = ""
    return suffix


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
    print("GETTING FILENAMES...")
    filedict = read_files(localdir)
    osversion, radioversion = pretty_formatter(osversion, radioversion)
    suffix = format_suffix(altradio, radioversion)
    # Generate loaders
    print("CREATING LOADERS...")
    filtrad = [rad for rad in filedict.keys() if rad]  # pop None
    for radval in filtrad:
        device = generate_device(radval)
        osname = generate_filename(device, osversion, suffix)
        osfile = filedict[radval]
        if osfile is not None:
            wrap_pseudocap(osname, localdir, osfile, radval)
        if radios:
            radname = generate_filename(device, radioversion, "")
            wrap_pseudocap(radname, localdir, radval)


def wrap_pseudocap(filename, folder, first, second=None):
    """
    A filtered, excepting wrapper for pseudocap.

    :param filename: The title of the new loader.
    :type filename: str

    :param folder: The folder to create the loader in.
    :type folder: str

    :param first: The first signed file, required.
    :type first: str

    :param second: The second signed file, optional.
    :type second: str
    """
    if first is None:
        raise SystemError
    try:
        pseudocap.make_autoloader(filename, first, second, folder=folder)
    except (OSError, IndexError, SystemError) as exc:
        print(str(exc))
        print("Could not create", filename)


def generate_skeletons():
    """
    Read JSON to get a dict of all filename components.
    """
    namelist = {}
    for idx in range(0, 7):
        namelist[idx] = None
    with open(utilities.grab_json()) as thefile:
        data = json.load(thefile)
    data = data['integermap']
    for key in data:
        if key['id'] in namelist:
            namelist[key['id']] = key['parts']
            namelist[key['id']].append(".exe")
    return namelist


def generate_device(radio):
    """
    Read JSON to get the device integer ID from device radio.

    :param radio: The radio filename to look up.
    :type radio: str
    """
    with open(utilities.grab_json()) as thefile:
        data = json.load(thefile)
    data = data['integermap']
    for key in data:
        if not key['special'] and key['radtype'] in radio:
            idx = int(key['id'])
            break
        else:
            targs = (key['special'], key['radtype'])
            if all(idx in radio for idx in targs):
                idx = int(key['id'])
                break
    return idx


def generate_filename(device, version, suffix=None):
    """
    Use skeleton dict to create loader filenames.

    :param device: Device to use.
    :type device: int

    :param version: OS or radio version.
    :type version: str

    :param suffix: Alternate radio, or blank.
    :type suffix: str
    """
    thed = generate_skeletons()
    if device < 0:
        return None
    dev = thed[device]
    if suffix is None:
        suffix = ""
    return dev[0] + version + suffix + dev[1] + dev[2]



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
    print("CREATING LOADER...")
    suffix = format_suffix(bool(altradio), altradio)
    try:
        osfile = str(glob.glob("*desktop*.signed")[0])
    except IndexError:
        print("No OS found")
        raise SystemExit
    else:
        try:
            rset = set(glob.glob("*.signed")) - set(glob.glob("*desktop*.signed"))
            radiofile = str(list(rset)[0])
        except IndexError:
            print("No radio found")
            raise SystemExit
        else:
            loadername = generate_lazy_filename(osversion, suffix, device)
            wrap_pseudocap(loadername, localdir, osfile, radiofile)


def generate_lazy_filename(osversion, suffix, device):
    """
    Read JSON to formulate a single filename.

    :param osversion: OS version.
    :type osversion: str

    :param suffix: Alternate radio, or just blank.
    :type suffix: str

    :param device: Device to use.
    :type device: int
    """
    with open(utilities.grab_json()) as thefile:
        data = json.load(thefile)
    data = data['integermap']
    for key in data:
        if key['id'] == device:
            fname = key['parts']
            break
    return fname[0] + osversion + suffix + fname[1] + ".exe"

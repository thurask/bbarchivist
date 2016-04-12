#!/usr/bin/env python3
"""This module is used for creation of autoloaders.
A higher level interface for :mod:`bbarchivist.pseudocap`."""

import os  # path work
import glob  # filename matching
from bbarchivist import pseudocap  # implement cap
from bbarchivist import jsonutils  # json

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "Copyright 2015-2016 Thurask"


def read_files(localdir, core=False):
    """
    Read list of signed files, return name assignments.

    :param localdir: Directory to use.
    :type localdir: str

    :param core: If we're using a core OS image. Default is false.
    :type core: bool
    """
    oslist = read_os_files(localdir, core)
    radlist = read_radio_files(localdir)
    pairdict = {}
    # [ti, z10, z10_vzw, q10, z30, z3, 8974]
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


def find_signed_file(match, localdir, title, silent=False):
    """
    Use pattern matching to find a signed file in a directory.

    :param match: Match pattern to use.
    :type match: str

    :param localdir: Directory to use.
    :type localdir: str

    :param title: File type, in case it isn't found.
    :type title: str

    :param silent: Don't print that a file wasn't found. Default is False.
    :type silent: bool
    """
    try:
        signedfile = glob.glob(os.path.join(localdir, match))[0]
    except IndexError:
        signedfile = None
        if not silent:
            print("No {0} found".format(title))
    return signedfile


def read_os_files(localdir, core=False):
    """
    Read list of OS signed files, return name assignments.

    :param localdir: Directory to use.
    :type localdir: str

    :param core: If we're using a core OS image. Default is false.
    :type core: bool
    """
    if core:
        fix8960 = "*qc8960.*_sfi.BB*.signed"
        fixomap_new = "*winchester.*_sfi.BB*.signed"
        fixomap_old = "*os.factory_sfi.BB*.signed"
        fix8930 = "*qc8x30.BB*.signed"
        fix8974_new = "*qc8974.BB*.signed"
        fix8974_old = "*qc8974.*_sfi.BB*.signed"
    else:
        fix8960 = "*qc8960.*_sfi.desktop.BB*.signed"
        fixomap_new = "*winchester.*_sfi.desktop.BB*.signed"
        fixomap_old = "*os.factory_sfi.desktop.BB*.signed"
        fix8930 = "*qc8x30.desktop.BB*.signed"
        fix8974_new = "*qc8974.desktop.BB*.signed"
        fix8974_old = "*qc8974.*_sfi.desktop.BB*.signed"
    # 8960
    os_8960 = find_signed_file(fix8960, localdir, "8960 OS")
    # 8x30 (10.3.1 MR+)
    os_8x30 = find_signed_file(fix8930, localdir, "8x30 OS", True)
    if os_8x30 is None:
        os_8x30 = find_signed_file(fix8960, localdir, "8x30 OS")
    # 8974
    os_8974 = find_signed_file(fix8974_new, localdir, "8974 OS", True)
    if os_8974 is None:
        os_8974 = find_signed_file(fix8974_old, localdir, "8974 OS")
    # OMAP
    os_ti = find_signed_file(fixomap_new, localdir, "OMAP OS", True)
    if os_ti is None:
        os_ti = find_signed_file(fixomap_old, localdir, "OMAP OS")
    return [os_8960, os_8x30, os_8974, os_ti]


def read_radio_files(localdir):
    """
    Read list of radio signed files, return name assignments.

    :param localdir: Directory to use.
    :type localdir: str
    """
    # STL100-1
    radio_ti = find_signed_file("*radio.m5730*.signed", localdir, "OMAP radio")
    # STL100-X
    radio_z10 = find_signed_file("*radio.qc8960.BB*.signed", localdir, "8960 radio")
    # STL100-4
    radio_z10_vzw = find_signed_file("*radio.qc8960*omadm*.signed", localdir, "VZW 8960 radio")
    # Q10/Q5
    radio_q10 = find_signed_file("*radio.qc8960*wtr.*signed", localdir, "Q10/Q5 radio")
    # Z30/Classic
    radio_z30 = find_signed_file("*radio.qc8960*wtr5*.signed", localdir, "Z30/Classic radio")
    # Z3
    radio_z3 = find_signed_file("*radio.qc8930*wtr5*.signed", localdir, "Z3 radio")
    # Passport
    radio_8974 = find_signed_file("*radio.qc8974*wtr2*.signed", localdir, "Passport radio")
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


def format_suffix(altradio=None, radioversion=None, core=False):
    """
    Formulate suffix for hybrid autoloaders.

    :param altradio: If a hybrid autoloader is being made.
    :type altradio: bool

    :param radioversion: The hybrid radio version, if applicable.
    :type radioversion: str

    :param core: If we're using a core OS image. Default is false.
    :type core: bool
    """
    suffix = "_R{0}".format(radioversion) if altradio and radioversion else ""
    if core:
        suffix += "_CORE"
    return suffix


def generate_loaders(
        osversion, radioversion, radios=True,
        localdir=None, altradio=False, core=False):
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

    :param core: If we're using a core OS image. Default is false.
    :type core: bool
    """
    # default parsing
    if localdir is None:
        localdir = os.getcwd()
    print("GETTING FILENAMES...")
    filedict = read_files(localdir, core)
    osversion, radioversion = pretty_formatter(osversion, radioversion)
    suffix = format_suffix(altradio, radioversion, core)
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
        print("No OS!")
        raise SystemError
    try:
        pseudocap.make_autoloader(filename, [first, second], folder=folder)
    except (OSError, IndexError, SystemError) as exc:
        print(str(exc))
        print("Could not create {0}".format(filename))


def generate_skeletons():
    """
    Read JSON to get a dict of all filename components.
    """
    namelist = {}
    for idx in range(0, 7):
        namelist[idx] = None
    data = jsonutils.load_json('integermap')
    for key in data:
        if key['id'] in namelist:
            namelist[key['id']] = (key['parts'])
            namelist[key['id']].append(".exe")
    return namelist


def generate_device(radio):
    """
    Read JSON to get the device integer ID from device radio.

    :param radio: The radio filename to look up.
    :type radio: str
    """
    data = jsonutils.load_json('integermap')
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
    return "{0}{1}{2}{3}{4}".format(dev[0], version, suffix, dev[1], dev[2])


def generate_lazy_loader(
        osversion, device,
        localdir=None, altradio=None, core=False):
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

    :param core: If we're using a core OS image. Default is false.
    :type core: bool
    """
    # default parsing
    if localdir is None:
        localdir = os.getcwd()
    print("CREATING LOADER...")
    suffix = format_suffix(bool(altradio), altradio, core)
    osfile = radiofile = None
    try:
        osfile = str(glob.glob("*_sfi*.signed")[0])
    except IndexError:
        print("No OS found")
    else:
        try:
            sset = set(glob.glob("*.signed"))
            rset = sset - set(glob.glob("*desktop*.signed"))
            radiofile = str(list(rset)[0])
        except IndexError:
            print("No radio found")
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
    data = jsonutils.load_json('integermap')
    for key in data:
        if key['id'] == device:
            fname = key['parts']
            break
    return "{0}{1}{2}{3}.exe".format(fname[0], osversion, suffix, fname[1])

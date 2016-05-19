#!/usr/bin/env python3
"""This module is used to operate with bar files."""

import os  # filesystem read
import zipfile  # zip extract, zip compresssion
import shutil  # folder operations
import base64  # encoding for hashes
import hashlib   # get hashes
from bbarchivist import utilities  # platform determination
from bbarchivist import bbconstants  # premade stuff

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "Copyright 2015-2016 Thurask"


def extract_bars(filepath):
    """
    Extract .signed files from .bar files.
    Use system zlib.

    :param filepath: Path to bar file directory.
    :type filepath: str
    """
    try:
        for file in os.listdir(filepath):
            if file.endswith(".bar"):
                print("EXTRACTING: {0}".format(file))
                zfile = zipfile.ZipFile(file, 'r')
                names = zfile.namelist()
                for name in names:
                    if str(name).endswith(".signed"):
                        zfile.extract(name, filepath)
    except (RuntimeError, OSError) as exc:
        print("EXTRACTION FAILURE")
        print(str(exc))
        print("DID IT DOWNLOAD PROPERLY?")


def retrieve_sha512(filename):
    """
    Get the premade, Base64 encoded SHA512 hash of a signed file in a bar.

    :param filename: Bar file to check.
    :type filename: str
    """
    try:
        zfile = zipfile.ZipFile(filename, 'r')
        names = zfile.namelist()
        manifest = None
        for name in names:
            if name.endswith("MANIFEST.MF"):
                manifest = name
                break
        if manifest is None:
            raise SystemExit
        manf = zfile.read(manifest).splitlines()
        alist = []
        for idx, line in enumerate(manf):
            if line.endswith(b"signed"):
                alist.append(manf[idx])
                alist.append(manf[idx + 1])
        assetname = alist[0].split(b": ")[1]
        assethash = alist[1].split(b": ")[1]
        return assetname, assethash  # (b"blabla.signed", b"somehash")
    except (RuntimeError, OSError, zipfile.BadZipFile) as exc:
        print("EXTRACTION FAILURE")
        print(str(exc))
        print("DID IT DOWNLOAD PROPERLY?")


def verify_sha512(filename, inithash):
    """
    Compare the original hash value with the current.

    :param filename: Signed file to check.
    :type filename: str

    :param inithash: Original SHA512 hash, as bytestring.
    :type inithash: bytes
    """
    sha512 = hashlib.sha512()
    with open(filename, 'rb') as file:
        while True:
            data = file.read(16 * 1024 * 1024)
            if not data:
                break
            sha512.update(data)
    rawdigest = sha512.digest()  # must be bytestring, not hexadecimalized str
    b64h = base64.b64encode(rawdigest, altchars=b"-_")  # replace some chars
    b64h = b64h.strip(b"==")  # remove padding
    return b64h == inithash


def bar_tester(filepath):
    """
    Use zipfile in order to test a bar for errors.

    :param filepath: Path to bar file.
    :type filepath: str
    """
    try:
        with zipfile.ZipFile(filepath, "r") as zfile:
            brokens = zfile.testzip()
    except zipfile.BadZipFile:
        brokens = filepath
    return brokens


def remove_empty_folders(a_folder):
    """
    Remove empty folders in a given folder using os.walk().

    :param a_folder: Target folder.
    :type a_folder: str
    """
    for curdir, subdirs, files in os.walk(a_folder):
        while True:
            try:
                if not subdirs and not files:
                    os.rmdir(curdir)
            except OSError:
                continue
            except NotImplementedError:
                break
            break


def remove_signed_files(a_folder):
    """
    Remove signed files from a given folder.

    :param a_folder: Target folder.
    :type a_folder: str
    """
    files = [os.path.join(a_folder, file) for file in os.listdir(a_folder)]
    files = [os.path.abspath(file) for file in files]
    for file in files:
        if file.endswith(".signed") and os.path.exists(file):
            print("REMOVING: {0}".format(os.path.basename(file)))
            while True:
                try:
                    os.remove(os.path.abspath(file))
                except PermissionError:
                    continue
                else:
                    break


def remove_unpacked_loaders(osdir, raddir, radios):
    """
    Remove uncompressed loader folders.

    :param osdir: OS loader folder.
    :type osdir: str

    :param raddir: Radio loader folder.
    :type raddir: str

    :param radios: If we made radios this run.
    :type radios: bool
    """
    shutil.rmtree(osdir)
    if radios:
        shutil.rmtree(raddir)


def create_blitz(a_folder, swver):
    """
    Create a blitz file: a zipped archive of all app/core/radio bars.

    :param a_folder: Target folder.
    :type a_folder: str

    :param swver: Software version to title the blitz.
    :type swver: str
    """
    fname = "Blitz-{0}.zip".format(swver)
    with zipfile.ZipFile(fname, 'w', zipfile.ZIP_DEFLATED, allowZip64=True) as zfile:
        for root, dirs, files in os.walk(a_folder):
            del dirs
            for file in files:
                print("ZIPPING: {0}".format(utilities.stripper(file)))
                abs_filename = os.path.join(root, file)
                abs_arcname = os.path.basename(abs_filename)
                zfile.write(abs_filename, abs_arcname)


def move_loaders(a_dir,
                 exedir_os, exedir_rad,
                 zipdir_os, zipdir_rad):
    """
    Move autoloaders to zipped and loaders directories in localdir.

    :param a_dir: Local directory, containing files you wish to move.
    :type a_dir: str

    :param exedir_os: Large autoloader .exe destination.
    :type exedir_os: str

    :param exedir_rad: Small autoloader .exe destination.
    :type exedir_rad: str

    :param zipdir_os: Large autoloader archive destination.
    :type zipdir_os: str

    :param zipdir_rad: Small autoloader archive destination.
    :type zipdir_rad: str
    """
    arx = bbconstants.ARCS
    pfx = bbconstants.PREFIXES
    loaders = [file for file in os.listdir(a_dir) if utilities.prepends(file, pfx, ".exe")]
    for file in loaders:
        print("MOVING: {0}".format(file))
        exedest_os = os.path.join(exedir_os, file)
        exedest_rad = os.path.join(exedir_rad, file)
        loader_sorter(file, exedest_os, exedest_rad)
    zippeds = [file for file in os.listdir(a_dir) if utilities.prepends(file, pfx, arx)]
    for file in zippeds:
        print("MOVING: {0}".format(file))
        zipdest_os = os.path.join(zipdir_os, file)
        zipdest_rad = os.path.join(zipdir_rad, file)
        loader_sorter(file, zipdest_os, zipdest_rad)


def loader_sorter(file, osdir, raddir):
    """
    Sort loaders based on size.

    :param file: The file to sort. Absolute paths, please.
    :type file: str

    :param osdir: Large file destination.
    :type osdir: str

    :param raddir: Small file destination.
    :type raddir: str
    """
    if os.path.getsize(file) > 90000000:
        while True:
            try:
                shutil.move(file, osdir)
            except shutil.Error:
                os.remove(file)
                continue
            break
    else:
        while True:
            try:
                shutil.move(file, raddir)
            except shutil.Error:
                os.remove(file)
                continue
            break


def move_bars(localdir, osdir, radiodir):
    """
    Move bar files to subfolders of a given folder.

    :param localdir: Directory to use.
    :type localdir: str

    :param osdir: OS file directory (large bars).
    :type osdir: str

    :param radiodir: Radio file directory (small bars).
    :type radiodir: str
    """
    for files in os.listdir(localdir):
        if files.endswith(".bar"):
            print("MOVING: {0}".format(files))
            bardest_os = os.path.join(osdir, files)
            bardest_radio = os.path.join(radiodir, files)
            # even the fattest radio is less than 90MB
            if os.path.getsize(os.path.join(localdir, files)) > 90000000:
                try:
                    shutil.move(os.path.join(localdir, files), osdir)
                except shutil.Error:
                    os.remove(bardest_os)
            else:
                try:
                    shutil.move(os.path.join(localdir, files), radiodir)
                except shutil.Error:
                    os.remove(bardest_radio)


def make_dirs(localdir, osversion, radioversion):
    """
    Create the directory tree needed for archivist/lazyloader.

    :param localdir: Root folder.
    :type localdir: str

    :param osversion: OS version.
    :type osversion: str

    :param radioversion: Radio version.
    :type radioversion: str
    """
    os.makedirs(localdir, exist_ok=True)

    if not os.path.exists(os.path.join(localdir, 'bars')):
        os.makedirs(os.path.join(localdir, 'bars'), exist_ok=True)
    bardir = os.path.join(localdir, 'bars')
    if not os.path.exists(os.path.join(bardir, osversion)):
        os.makedirs(os.path.join(bardir, osversion), exist_ok=True)
    bardir_os = os.path.join(bardir, osversion)
    if not os.path.exists(os.path.join(bardir, radioversion)):
        os.makedirs(os.path.join(bardir, radioversion), exist_ok=True)
    bardir_radio = os.path.join(bardir, radioversion)

    if not os.path.exists(os.path.join(localdir, 'loaders')):
        os.makedirs(os.path.join(localdir, 'loaders'), exist_ok=True)
    loaderdir = os.path.join(localdir, 'loaders')
    if not os.path.exists(os.path.join(loaderdir, osversion)):
        os.makedirs(os.path.join(loaderdir, osversion), exist_ok=True)
    loaderdir_os = os.path.join(loaderdir, osversion)
    if not os.path.exists(os.path.join(loaderdir, radioversion)):
        os.makedirs(os.path.join(loaderdir, radioversion), exist_ok=True)
    loaderdir_radio = os.path.join(loaderdir, radioversion)

    if not os.path.exists(os.path.join(localdir, 'zipped')):
        os.makedirs(os.path.join(localdir, 'zipped'), exist_ok=True)
    zipdir = os.path.join(localdir, 'zipped')
    if not os.path.exists(os.path.join(zipdir, osversion)):
        os.makedirs(os.path.join(zipdir, osversion), exist_ok=True)
    zipdir_os = os.path.join(zipdir, osversion)
    if not os.path.exists(os.path.join(zipdir, radioversion)):
        os.makedirs(os.path.join(zipdir, radioversion), exist_ok=True)
    zipdir_radio = os.path.join(zipdir, radioversion)

    return (bardir_os, bardir_radio, loaderdir_os, loaderdir_radio, zipdir_os, zipdir_radio)


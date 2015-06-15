#!/usr/bin/env python3

import os  # filesystem read
import time  # time for downloader
import math  # rounding of floats
import subprocess  # invocation of 7z, cap
import zipfile  # zip extract, zip compresssion
import tarfile  # txz/tbz/tgz compression
import sys  # version info
import shutil  # folder operations
from bbarchivist import utilities  # platform determination


def extract_bars(filepath):
    """
    Extract .signed files from .bar files.
    Use system zlib.

    :param filepath: Path to bar file directory.
    :type filepath: str
    """
    for file in os.listdir(filepath):
        if file.endswith(".bar"):
            try:
                zfile = zipfile.ZipFile(file, 'r')
                names = zfile.namelist()
                for name in names:
                    if str(name).endswith(".signed"):
                        zfile.extract(name, filepath)
            except Exception as exc:
                print("EXTRACTION FAILURE")
                print(str(exc))
                print("DID IT DOWNLOAD PROPERLY?")
                return


def sz_compress(filepath, filename, szexe=None, strength=5):
    """
    Pack a file into a LZMA2 7z file.

    :param filepath: Basename of file, no extension.
    :type filepath: str

    :param filename: Name of file to pack.
    :type filename: str

    :param szexe: Path to 7z executable.
    :type szexe: str

    :param strength: Compression strength. 5 is normal, 9 is ultra.
    :type strength: int
    """
    starttime = time.clock()
    rawname = os.path.dirname(filepath)
    subprocess.call(
        szexe +
        " a -mx" +
        str(strength) +
        " -m0=lzma2 -mmt" +
        utilities.get_core_count() +
        " " +
        filepath +
        '.7z' +
        " " +
        os.path.join(
            rawname,
            filename),
        shell=True)
    endtime = time.clock() - starttime
    endtime_proper = math.ceil(endtime * 100) / 100
    print("COMPLETED IN " + str(endtime_proper) + " SECONDS")


def tgz_compress(filepath, filename, strength=5):
    """
    Pack a file into a gzip tarfile.

    :param filepath: Basename of file, no extension.
    :type filepath: str

    :param filename: Name of file to pack.
    :type filename: str

    :param strength: Compression strength. 5 is normal, 9 is ultra.
    :type strength: int
    """
    with tarfile.open(filepath + '.tar.gz',
                                 'w:gz',
                                 compresslevel=strength) as gzfile:
                    starttime = time.clock()
                    gzfile.add(filename, filter=None)
                    endtime = time.clock() - starttime
                    endtime_proper = math.ceil(endtime * 100) / 100
                    print("COMPLETED IN " + str(endtime_proper) + " SECONDS")


def tbz_compress(filepath, filename, strength=5):
    """
    Pack a file into a bzip2 tarfile.

    :param filepath: Basename of file, no extension.
    :type filepath: str

    :param filename: Name of file to pack.
    :type filename: str

    :param strength: Compression strength. 5 is normal, 9 is ultra.
    :type strength: int
    """
    with tarfile.open(filepath + '.tar.bz2',
                                 'w:bz2',
                                 compresslevel=strength) as bzfile:
                    starttime = time.clock()
                    bzfile.add(filename, filter=None)
                    endtime = time.clock() - starttime
                    endtime_proper = math.ceil(endtime * 100) / 100
                    print("COMPLETED IN " + str(endtime_proper) + " SECONDS")


def txz_compress(filepath, filename, strength=5):
    """
    Pack a file into a LZMA tarfile.

    :param filepath: Basename of file, no extension.
    :type filepath: str

    :param filename: Name of file to pack.
    :type filename: str

    :param strength: Compression strength. 5 is normal, 9 is ultra.
    :type strength: int
    """
    with tarfile.open(filepath + '.tar.xz',
                                 'w:xz') as xzfile:
                    starttime = time.clock()
                    xzfile.add(filename, filter=None)
                    endtime = time.clock() - starttime
                    endtime_proper = math.ceil(endtime * 100) / 100
                    print("COMPLETED IN " + str(endtime_proper) + " SECONDS")


def zip_compress(filepath, filename):
    """
    Pack a file into a DEFLATE zipfile.

    :param filepath: Basename of file, no extension.
    :type filepath: str

    :param filename: Name of file to pack.
    :type filename: str
    """
    with zipfile.ZipFile(filepath + '.zip',
                                    'w',
                                    zipfile.ZIP_DEFLATED,
                                    allowZip64=True) as zfile:
                    starttime = time.clock()
                    zfile.write(filename)
                    endtime = time.clock() - starttime
                    endtime_proper = math.ceil(endtime * 100) / 100
                    print("COMPLETED IN " + str(endtime_proper) + " SECONDS")


def compress(filepath, method="7z", szexe=None):
    """
    Compress all autoloader files in a given folder, with a given method.

    :param filepath: Working directory. Required.
    :type filepath: str

    :param method: Compression type. Default is "7z". Defined in source.
    :type method: str

    :param szexe: Path to 7z executable, if needed.
    :type szexe: str
    """
    if method == "7z" and szexe is None:
        ifexists = utilities.prep_seven_zip()  # see if 7z exists
        if not ifexists:
            method = "zip"  # fallback
        else:
            szexe = utilities.get_seven_zip(False)
    majver = sys.version_info[1]
    if majver < 3 and method == "txz":  # 3.2 and under
        method = "zip"  # fallback
    for file in os.listdir(filepath):
        if file.endswith(".exe") and file.startswith(
                ("Q10", "Z10", "Z30", "Z3", "Passport")):
            filename = os.path.splitext(os.path.basename(file))[0]
            fileloc = os.path.join(filepath, filename)
            print("COMPRESSING: " + filename + ".exe")
            if utilities.is_amd64():
                strength = 9  # ultra compression
            else:
                strength = 5  # normal compression
            if method == "7z":
                sz_compress(fileloc, file, szexe, strength)
            elif method == "tgz":
                tgz_compress(fileloc, file, strength)
            elif method == "txz":
                txz_compress(fileloc, file, strength)
            elif method == "tbz":
                tbz_compress(fileloc, file, strength)
            elif method == "zip":
                zip_compress(fileloc, file)
            else:
                print("INVALID METHOD")
                raise SystemExit


def remove_empty_folders(a_folder):
    """
    Remove empty folders in a given folder using os.walk().

    :param a_folder: Target folder.
    :type a_folder: str
    """
    for curdir, subdirs, files in os.walk(a_folder):
        while True:
            try:
                if len(subdirs) == 0 and len(files) == 0:
                    os.rmdir(curdir)
            except OSError:
                continue
            except NotImplementedError:
                break
            break


def create_blitz(a_folder, swver):
    """
    Create a blitz file: a zipped archive of all app/core/radio bars.

    :param a_folder: Target folder.
    :type a_folder: str

    :param swver: Software version to title the blitz.
    :type swver: str
    """
    with zipfile.ZipFile("Blitz-" + swver + '.zip',
                         'w',
                         zipfile.ZIP_DEFLATED,
                         allowZip64=True) as zfile:
        for root, dirs, files in os.walk(a_folder):  # @UnusedVariable
            del dirs
            for file in files:
                print("ZIPPING:", utilities.barname_stripper(file))
                zfile.write(os.path.join(root, file),
                            os.path.basename(os.path.join(root, file)))


def move_loaders(localdir,
                 exedir_os, exedir_rad,
                 zipdir_os, zipdir_rad):
    """
    Move autoloaders to zipped and loaders directories in localdir.

    :param localdir: Local directory, containing files you wish to move.
    :type localdir: str

    :param exedir_os: Large autoloader .exe destination.
    :type exedir_os: str

    :param exedir_rad: Small autoloader .exe destination.
    :type exedir_rad: str

    :param zipdir_os: Large autoloader archive destination.
    :type zipdir_os: str

    :param zipdir_rad: Small autoloader archive destination.
    :type zipdir_rad: str
    """
    for files in os.listdir(localdir):
        if files.endswith(".exe") and files.startswith(
                ("Q10", "Z10", "Z30", "Z3", "Passport")):
            print("MOVING: " + files)
            exedest_os = os.path.join(exedir_os, files)
            exedest_rad = os.path.join(exedir_rad, files)
            # even the fattest radio is less than 90MB
            if os.path.getsize(os.path.join(localdir, files)) > 90000000:
                while True:
                    try:
                        shutil.move(os.path.join(localdir, files), exedir_os)
                    except shutil.Error:
                        os.remove(exedest_os)
                        continue
                    break
            else:
                while True:
                    try:
                        shutil.move(os.path.join(localdir, files), exedir_rad)
                    except shutil.Error:
                        os.remove(exedest_rad)
                        continue
                    break
        if files.endswith(
            (".7z",
             ".tar.xz",
             ".tar.bz2",
             ".tar.gz",
             ".zip")
        ) and files.startswith(
            ("Q10",
             "Z10",
             "Z30",
             "Z3",
             "Passport")
        ):
            print("MOVING: " + files)
            zipdest_os = os.path.join(zipdir_os, files)
            zipdest_rad = os.path.join(zipdir_rad, files)
            # even the fattest radio is less than 90MB
            if os.path.getsize(os.path.join(localdir, files)) > 90000000:
                while True:
                    try:
                        shutil.move(os.path.join(localdir, files), zipdir_os)
                    except shutil.Error:
                        os.remove(zipdest_os)
                        continue
                    break
            else:
                while True:
                    try:
                        shutil.move(os.path.join(localdir, files), zipdir_rad)
                    except shutil.Error:
                        os.remove(zipdest_rad)
                        continue
                    break

#!/usr/bin/env python3

import os  # filesystem read
import time  # time for downloader
import math  # rounding of floats
import subprocess  # invocation of 7z, cap
import zipfile  # zip extract, zip compresssion
import tarfile  # txz/tbz/tgz compression
import sys
import shutil
from . import utilities


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
                z = zipfile.ZipFile(file, 'r')
                names = z.namelist()
                for name in names:
                    if str(name).endswith(".signed"):
                        z.extract(name, filepath)
            except Exception:
                print("EXTRACTION FAILURE")
                print("DID IT DOWNLOAD PROPERLY?")
                return


def reset(tarinfo):
    """
    Filter for TAR compression.

    :param tarinfo: TarInfo instance to use.
    :type tarinfo: TarInfo
    """
    tarinfo.uid = tarinfo.gid = 0
    tarinfo.uname = tarinfo.gname = "root"
    return tarinfo


def compress(filepath, method="7z", szexe="7za.exe"):
    """
    Compress all autoloader files in a given folder, with a given method.

    :param filepath: Working directory. Required.
    :type filepath: str

    :param method: Compression type. Default is "7z". Defined in source.
    :type method: str

    :param szexe: Path to 7z executable, if needed.
    :type szexe: str
    """
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
                starttime = time.clock()
                subprocess.call(
                    szexe +
                    " a -mx" +
                    str(strength) +
                    " -m0=lzma2 -mmt" +
                    utilities.get_core_count() +
                    " " +
                    fileloc +
                    '.7z' +
                    " " +
                    os.path.join(
                        filepath,
                        file),
                    shell=True)
                endtime = time.clock() - starttime
                endtime_proper = math.ceil(endtime * 100) / 100
                print("COMPLETED IN " + str(endtime_proper) + " SECONDS")
            elif method == "tgz":
                with tarfile.open(fileloc + '.tar.gz',
                                  'w:gz',
                                  compresslevel=strength) as gzfile:
                    starttime = time.clock()
                    gzfile.add(file, filter=reset)
                    endtime = time.clock() - starttime
                    endtime_proper = math.ceil(endtime * 100) / 100
                    print("COMPLETED IN " + str(endtime_proper) + " SECONDS")
            elif method == "txz":
                with tarfile.open(fileloc + '.tar.xz',
                                  'w:xz') as xzfile:
                    starttime = time.clock()
                    xzfile.add(file, filter=reset)
                    endtime = time.clock() - starttime
                    endtime_proper = math.ceil(endtime * 100) / 100
                    print("COMPLETED IN " + str(endtime_proper) + " SECONDS")
            elif method == "tbz":
                with tarfile.open(fileloc + '.tar.bz2',
                                  'w:bz2',
                                  compresslevel=strength) as bzfile:
                    starttime = time.clock()
                    bzfile.add(file, filter=reset)
                    endtime = time.clock() - starttime
                    endtime_proper = math.ceil(endtime * 100) / 100
                    print("COMPLETED IN " + str(endtime_proper) + " SECONDS")
            elif method == "zip":
                with zipfile.ZipFile(fileloc + '.zip',
                                     'w',
                                     zipfile.ZIP_DEFLATED) as zfile:
                    starttime = time.clock()
                    zfile.write(file)
                    endtime = time.clock() - starttime
                    endtime_proper = math.ceil(endtime * 100) / 100
                    print("COMPLETED IN " + str(endtime_proper) + " SECONDS")
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
            except:
                continue
            break


def create_blitz(a_folder, swver):
    """
    Create a blitz file: a zipped archive of all app/core/radio bars.

    :param a_folder: Target folder.
    :type a_folder: str

    :param swver: Software version to title the blitz.
    :type swver: str
    """
    shutil.make_archive("Blitz-" + swver,
                        format="zip",
                        root_dir=a_folder)


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
            (".7z", ".tar.xz", ".tar.bz2", ".tar.gz", ".zip")
        ) and files.startswith(
                ("Q10", "Z10", "Z30", "Z3", "Passport")):
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

#!/usr/bin/env python3
"""This module is used to operate with bar files and other archives."""

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "Copyright 2015 Thurask"

import os  # filesystem read
import time  # time for downloader
import math  # rounding of floats
import subprocess  # invocation of 7z, cap
import zipfile  # zip extract, zip compresssion
import tarfile  # txz/tbz/tgz compression
import sys  # version info
import shutil  # folder operations
import base64  # encoding for hashes
import hashlib   # get hashes
import configparser  # config parsing, duh
from bbarchivist import utilities  # platform determination
from bbarchivist import bbconstants  # premade stuff


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
                print("EXTRACTING:", file)
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
                alist.append(manf[idx+1])
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
            data = file.read(16*1024*1024)
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


def sz_compress(filepath, filename, szexe=None, strength=5, errors=False):
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

    :param errors: Print completion status message. Default is false.
    :type errors: bool
    """
    starttime = time.clock()
    strength = str(strength)
    rawname = os.path.dirname(filepath)
    cores = str(utilities.get_core_count())
    initfold = os.path.join(rawname, filename)
    cmd = '{0} a -mx{1} -m0=lzma2 -mmt{2} "{3}.7z" "{4}"'.format(szexe,
                                                                 strength,
                                                                 cores,
                                                                 filepath,
                                                                 initfold)
    with open(os.devnull, 'wb') as dnull:
        excode = subprocess.call(cmd, stdout=dnull, stderr=subprocess.STDOUT)
    endtime = time.clock() - starttime
    endtime_proper = math.ceil(endtime * 100) / 100
    print("COMPLETED IN " + str(endtime_proper) + " SECONDS")
    if errors:
        print(bbconstants.SZCODES[excode])


def sz_verify(filepath, szexe=None):
    """
    Verify that a .7z file is valid and working.

    :param filepath: Filename.
    :type filepath: str

    :param szexe: Path to 7z executable.
    :type szexe: str
    """
    filepath = os.path.abspath(filepath)
    cmd = '{0} t "{1}"'.format(szexe, filepath)
    with open(os.devnull, 'wb') as dnull:
        excode = subprocess.call(cmd, stdout=dnull, stderr=subprocess.STDOUT)
    return excode == 0


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
    with tarfile.open(filepath + '.tar.gz', 'w:gz',
                      compresslevel=strength) as gzfile:
        starttime = time.clock()
        gzfile.add(filename, filter=None)
        endtime = time.clock() - starttime
        endtime_proper = math.ceil(endtime * 100) / 100
        print("COMPLETED IN " + str(endtime_proper) + " SECONDS")


def tgz_verify(filepath):
    """
    Verify that a tar.gz file is valid and working.

    :param filepath: Filename.
    :type filepath: str
    """
    if tarfile.is_tarfile(filepath):
        with tarfile.open(filepath, "r:gz") as thefile:
            mems = thefile.getmembers()
        if not mems:
            return False
        else:
            return True
    else:
        return False


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
    with tarfile.open(filepath + '.tar.bz2', 'w:bz2',
                      compresslevel=strength) as bzfile:
        starttime = time.clock()
        bzfile.add(filename, filter=None)
        endtime = time.clock() - starttime
        endtime_proper = math.ceil(endtime * 100) / 100
        print("COMPLETED IN " + str(endtime_proper) + " SECONDS")


def tbz_verify(filepath):
    """
    Verify that a tar.bz2 file is valid and working.

    :param filepath: Filename.
    :type filepath: str
    """
    if tarfile.is_tarfile(filepath):
        with tarfile.open(filepath, "r:bz2") as thefile:
            mems = thefile.getmembers()
        if not mems:
            return False
        else:
            return True
    else:
        return False


def txz_compress(filepath, filename):
    """
    Pack a file into a LZMA tarfile.

    :param filepath: Basename of file, no extension.
    :type filepath: str

    :param filename: Name of file to pack.
    :type filename: str
    """
    with tarfile.open(filepath + '.tar.xz', 'w:xz') as xzfile:
        starttime = time.clock()
        xzfile.add(filename, filter=None)
        endtime = time.clock() - starttime
        endtime_proper = math.ceil(endtime * 100) / 100
        print("COMPLETED IN " + str(endtime_proper) + " SECONDS")


def txz_verify(filepath):
    """
    Verify that a tar.xz file is valid and working.

    :param filepath: Filename.
    :type filepath: str
    """
    if sys.version_info[1] <= 2:
        pass
    else:
        if tarfile.is_tarfile(filepath):
            with tarfile.open(filepath, "r:xz") as thefile:
                mems = thefile.getmembers()
            if not mems:
                return False
            else:
                return True
        else:
            return False


def zip_compress(filepath, filename):
    """
    Pack a file into a DEFLATE zipfile.

    :param filepath: Basename of file, no extension.
    :type filepath: str

    :param filename: Name of file to pack.
    :type filename: str
    """
    with zipfile.ZipFile(filepath + '.zip', 'w', zipfile.ZIP_DEFLATED,
                         allowZip64=True) as zfile:
        starttime = time.clock()
        zfile.write(filename)
        endtime = time.clock() - starttime
        endtime_proper = math.ceil(endtime * 100) / 100
        print("COMPLETED IN " + str(endtime_proper) + " SECONDS")


def zip_verify(filepath):
    """
    Verify that a .zip file is valid and working.

    :param filepath: Filename.
    :type filepath: str
    """
    if zipfile.is_zipfile(filepath):
        brokens = bar_tester(filepath)
        if brokens is None:
            return True
        else:
            return False
    else:
        return False


def filter_method(method, szexe=None):
    """
    Make sure methods are OK.

    :param method: Compression method to use.
    :type method: str

    :param szexe: Path to 7z executable, if needed.
    :type szexe: str
    """
    if sys.version_info[1] < 3 and method == "txz":
        method = "zip"  # fallback
    if method == "7z" and szexe is None:
        ifexists = utilities.prep_seven_zip()  # see if 7z exists
        if not ifexists:
            method = "zip"  # fallback
        else:
            szexe = utilities.get_seven_zip(False)
    return method


def calculate_strength():
    """
    Determine zip/gzip/bzip2 strength by OS bit setting.
    """
    if utilities.is_amd64():
        strength = 9  # ultra compression
    else:
        strength = 5  # normal compression
    return strength


def compress(filepath, method="7z", szexe=None, selective=False, errors=False):
    """
    Compress all autoloader files in a given folder, with a given method.

    :param filepath: Working directory. Required.
    :type filepath: str

    :param method: Compression type. Default is "7z".
    :type method: str

    :param szexe: Path to 7z executable, if needed.
    :type szexe: str

    :param selective: Only compress autoloaders. Default is false.
    :type selective: bool

    :param errors: Print completion status message. Default is false.
    :type errors: bool
    """
    method = filter_method(method, szexe)
    arx = bbconstants.ARCS
    pfx = bbconstants.PREFIXES
    files = [file for file in os.listdir(filepath) if not os.path.isdir(file)]
    if selective:
        filt0 = [file for file in files if prepends(file, pfx, "")]
        filt1 = [file for file in filt0 if not prepends(file, "", arx)]
        filt2 = [file for file in filt1 if prepends(file, "", ".exe")]
    else:
        filt2 = [file for file in files if not prepends(file, "", arx)]
    filt3 = [os.path.join(filepath, file) for file in filt2]
    for file in filt3:
        filename = os.path.splitext(os.path.basename(file))[0]
        fileloc = os.path.join(filepath, filename)
        print("COMPRESSING: " + filename + ".exe")
        strength = calculate_strength()
        if method == "7z":
            sz_compress(fileloc, file, szexe, strength, errors)
        elif method == "tgz":
            tgz_compress(fileloc, file, strength)
        elif method == "txz":
            txz_compress(fileloc, file)
        elif method == "tbz":
            tbz_compress(fileloc, file, strength)
        elif method == "zip":
            zip_compress(fileloc, file)
    return True


def verify(thepath, method="7z", szexe=None, selective=False):
    """
    Verify specific archive files in a given folder.

    :param thepath: Working directory. Required.
    :type thepath: str

    :param method: Compression type. Default is "7z". Defined in source.
    :type method: str

    :param szexe: Path to 7z executable, if needed.
    :type szexe: str

    :param selective: Only verify autoloaders. Default is false.
    :type selective: bool
    """
    method = filter_method(method, szexe)
    pathlist = [os.path.join(thepath, file) for file in os.listdir(thepath)]
    files = (file for file in pathlist if not os.path.isdir(file))
    for file in files:
        filt = file.endswith(bbconstants.ARCS)
        if selective:
            filt = filt and file.startswith(bbconstants.PREFIXES)
        if filt:
            print("VERIFYING:", file)
            if file.endswith(".7z") and szexe is not None:
                szver = sz_verify(os.path.abspath(file), szexe)
                if not szver:
                    print("{0} IS BROKEN!".format((file)))
                return szver
            elif file.endswith(".tar.gz"):
                tgver = tgz_verify(file)
                if not tgver:
                    print("{0} IS BROKEN!".format((file)))
                return tgver
            elif file.endswith(".tar.xz"):
                txver = txz_verify(file)
                if not txver:
                    print("{0} IS BROKEN!".format((file)))
                return txver
            elif file.endswith(".tar.bz2"):
                tbver = tbz_verify(file)
                if not tbver:
                    print("{0} IS BROKEN!".format((file)))
                return tbver
            elif file.endswith(".zip"):
                zver = zip_verify(file)
                if not zver:
                    print("{0} IS BROKEN!".format((file)))
                return zver


def compress_suite(filepath, method="7z", szexe=None, selective=False):
    """
    Wrap compression and verification into one.

    :param filepath: Working directory. Required.
    :type filepath: str

    :param method: Compression type. Default is "7z". Defined in source.
    :type method: str

    :param szexe: Path to 7z executable, if needed.
    :type szexe: str

    :param selective: Only compress autoloaders. Default is false.
    :type selective: bool
    """
    compress(filepath, method, szexe, selective)
    verify(filepath, method, szexe, selective)


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
            print("REMOVING: " + os.path.basename(file))
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
    with zipfile.ZipFile("Blitz-" + swver + '.zip',
                         'w',
                         zipfile.ZIP_DEFLATED,
                         allowZip64=True) as zfile:
        for root, dirs, files in os.walk(a_folder):
            del dirs
            for file in files:
                print("ZIPPING:", utilities.stripper(file))
                abs_filename = os.path.join(root, file)
                abs_arcname = os.path.basename(abs_filename)
                zfile.write(abs_filename, abs_arcname)


def prepends(file, pre, suf):
    """
    Check if filename starts with/ends with stuff.

    :param file: File to check.
    :type file: str

    :param pre: Prefix(es) to check.
    :type pre: str or list or tuple

    :param suf: Suffix(es) to check.
    :type suf: str or list or tuple
    """
    return file.startswith(pre) and file.endswith(suf)


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
    loaders = (file for file in os.listdir(a_dir) if prepends(file,
                                                              pfx,
                                                              ".exe"))
    for file in loaders:
        print("MOVING: " + file)
        exedest_os = os.path.join(exedir_os, file)
        exedest_rad = os.path.join(exedir_rad, file)
        loader_sorter(file, exedest_os, exedest_rad)
    zippeds = (file for file in os.listdir(a_dir) if prepends(file,
                                                              pfx,
                                                              arx))
    for file in zippeds:
        print("MOVING: " + file)
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
            print("MOVING: " + files)
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

    return (bardir_os,
            bardir_radio,
            loaderdir_os,
            loaderdir_radio,
            zipdir_os,
            zipdir_radio)


def compress_config_loader(homepath=None):
    """
    Read a ConfigParser file to get compression preferences.

    :param homepath: Folder containing ini file. Default is user directory.
    :type homepath: str
    """
    config = configparser.ConfigParser()
    if homepath is None:
        homepath = os.path.expanduser("~")
    conffile = os.path.join(homepath, "bbarchivist.ini")
    if not os.path.exists(conffile):
        open(conffile, 'w').close()
    config.read(conffile)
    if not config.has_section('compression'):
        config['compression'] = {}
    compini = config['compression']
    method = compini.get('method', fallback="7z")
    if sys.version_info[1] <= 2 and method == "txz":
        method = "zip"  # for 3.2 compatibility
    return method


def compress_config_writer(method=None, homepath=None):
    """
    Write a ConfigParser file to store compression preferences.

    :param method: Method to use.
    :type method: str

    :param homepath: Folder containing ini file. Default is user directory.
    :type homepath: str
    """
    if method is None:
        method = compress_config_loader()
    config = configparser.ConfigParser()
    if homepath is None:
        homepath = os.path.expanduser("~")
    conffile = os.path.join(homepath, "bbarchivist.ini")
    if not os.path.exists(conffile):
        open(conffile, 'w').close()
    config.read(conffile)
    if not config.has_section('compression'):
        config['compression'] = {}
    config['compression']['method'] = method
    with open(conffile, "w") as configfile:
        config.write(configfile)

#!/usr/bin/env python3
"""This module is used to operate with archives."""

import os  # filesystem read
import subprocess  # invocation of 7z, cap
import zipfile  # zip compresssion
import tarfile  # txz/tbz/tgz/tar compression
from bbarchivist import utilities  # platform determination
from bbarchivist import bbconstants  # premade stuff
from bbarchivist import decorators  # timer
from bbarchivist import iniconfig  # config parsing

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "Copyright 2015-2016 Thurask"


def smart_is_tarfile(filepath):
    """
    :func:`tarfile.is_tarfile` plus error handling.

    :param filepath: Filename.
    :type filepath: str
    """
    try:
        istar = tarfile.is_tarfile(filepath)
    except (OSError, IOError):
        return False
    else:
        return istar


@decorators.timer
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
    szcodes = {
        0: "NO ERRORS",
        1: "COMPLETED WITH WARNINGS",
        2: "FATAL ERROR",
        7: "COMMAND LINE ERROR",
        8: "OUT OF MEMORY ERROR",
        255: "USER STOPPED PROCESS"
    }
    strength = str(strength)
    rawname = os.path.dirname(filepath)
    thr = str(utilities.get_core_count())
    fold = os.path.join(rawname, filename)
    cmd = '{0} a -mx{1} -m0=lzma2 -mmt{2} "{3}.7z" "{4}"'.format(szexe, strength,
                                                                 thr, filepath, fold)
    with open(os.devnull, 'wb') as dnull:
        excode = subprocess.call(cmd, stdout=dnull, stderr=subprocess.STDOUT, shell=True)
    if errors:
        print(szcodes[excode])


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
        excode = subprocess.call(cmd, stdout=dnull, stderr=subprocess.STDOUT, shell=True)
    return excode == 0


@decorators.timer
def tar_compress(filepath, filename):
    """
    Pack a file into an uncompressed tarfile.

    :param filepath: Basename of file, no extension.
    :type filepath: str

    :param filename: Name of file to pack.
    :type filename: str
    """
    with tarfile.open("{0}.tar".format(filepath), 'w:') as tfile:
        tfile.add(filename, filter=None, arcname=os.path.basename(filename))


def tar_verify(filepath):
    """
    Verify that a tar file is valid and working.

    :param filepath: Filename.
    :type filepath: str
    """
    if smart_is_tarfile(filepath):
        with tarfile.open(filepath, "r:") as thefile:
            mems = thefile.getmembers()
        return False if not mems else True
    else:
        return False


@decorators.timer
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
    with tarfile.open("{0}.tar.gz".format(filepath), 'w:gz', compresslevel=strength) as gzfile:
        gzfile.add(filename, filter=None, arcname=os.path.basename(filename))


def tgz_verify(filepath):
    """
    Verify that a tar.gz file is valid and working.

    :param filepath: Filename.
    :type filepath: str
    """
    if smart_is_tarfile(filepath):
        with tarfile.open(filepath, "r:gz") as thefile:
            mems = thefile.getmembers()
        return False if not mems else True
    else:
        return False


@decorators.timer
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
    with tarfile.open("{0}.tar.bz2".format(filepath), 'w:bz2', compresslevel=strength) as bzfile:
        bzfile.add(filename, filter=None, arcname=os.path.basename(filename))


def tbz_verify(filepath):
    """
    Verify that a tar.bz2 file is valid and working.

    :param filepath: Filename.
    :type filepath: str
    """
    if smart_is_tarfile(filepath):
        with tarfile.open(filepath, "r:bz2") as thefile:
            mems = thefile.getmembers()
        return False if not mems else True
    else:
        return False


@decorators.timer
def txz_compress(filepath, filename):
    """
    Pack a file into a LZMA tarfile.

    :param filepath: Basename of file, no extension.
    :type filepath: str

    :param filename: Name of file to pack.
    :type filename: str
    """
    if not utilities.new_enough(3):
        pass
    else:
        with tarfile.open("{0}.tar.xz".format(filepath), 'w:xz') as xzfile:
            xzfile.add(filename, filter=None, arcname=os.path.basename(filename))


def txz_verify(filepath):
    """
    Verify that a tar.xz file is valid and working.

    :param filepath: Filename.
    :type filepath: str
    """
    if not utilities.new_enough(3):
        return None
    else:
        if smart_is_tarfile(filepath):
            with tarfile.open(filepath, "r:xz") as thefile:
                mems = thefile.getmembers()
            return False if not mems else True
        else:
            return False


@decorators.timer
def zip_compress(filepath, filename):
    """
    Pack a file into a DEFLATE zipfile.

    :param filepath: Basename of file, no extension.
    :type filepath: str

    :param filename: Name of file to pack.
    :type filename: str
    """
    with zipfile.ZipFile("{0}.zip".format(filepath), 'w', zipfile.ZIP_DEFLATED, allowZip64=True) as zfile:
        zfile.write(filename, arcname=os.path.basename(filename))


def zip_verify(filepath):
    """
    Verify that a .zip file is valid and working.

    :param filepath: Filename.
    :type filepath: str
    """
    if zipfile.is_zipfile(filepath):
        try:
            with zipfile.ZipFile(filepath, "r") as zfile:
                brokens = zfile.testzip()
        except zipfile.BadZipFile:
            brokens = filepath
        return brokens != filepath
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
    if not utilities.new_enough(3) and method == "txz":
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
    strength = 9 if utilities.is_amd64() else 5
    return strength


def filtercomp(files, criterion, critargs, boolfilt=True):
    """
    :param files: Files to work on.
    :type files: list(str)

    :param criterion: Function to use for evaluation.
    :type criterion: func

    :param critargs: Arguments for function, other than file.
    :type critargs: list

    :param boolfilt: True if comparing criterion, False if comparing not criterion.
    :type boolfilt: bool
    """
    if boolfilt:
        fx2 = [file for file in files if criterion(file, *critargs)]
    else:
        fx2 = [file for file in files if not criterion(file, *critargs)]
    return fx2


def compressfilter(filepath, selective=False):
    """
    Filter directory listing of working directory.

    :param filepath: Working directory. Required.
    :type filepath: str

    :param selective: Only compress autoloaders. Default is false.
    :type selective: bool/str
    """
    arx = bbconstants.ARCS
    pfx = bbconstants.PREFIXES
    files = [file for file in os.listdir(filepath) if not os.path.isdir(file)]
    if selective is None:
        filt2 = os.listdir(filepath)
    elif selective == "arcsonly":
        filt2 = filtercomp(files, utilities.prepends, ("", arx))
    elif selective:
        filt0 = filtercomp(files, utilities.prepends, (pfx, ""))
        filt1 = filtercomp(filt0, utilities.prepends, ("", arx), False)  # pop archives
        filt2 = filtercomp(filt1, utilities.prepends, ("", ".exe"))  # include exes
    else:
        filt2 = filtercomp(files, utilities.prepends, ("", arx), False)  # pop archives
    filt3 = [os.path.join(filepath, file) for file in filt2]
    return filt3


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
    files = compressfilter(filepath, selective)
    for file in files:
        fname = os.path.basename(file)
        filename = os.path.splitext(fname)[0]
        fileloc = os.path.join(filepath, filename)
        print("COMPRESSING: {0}".format(fname))
        if method == "7z":
            sz_compress(fileloc, file, szexe, calculate_strength(), errors)
        elif method == "tgz":
            tgz_compress(fileloc, file, calculate_strength())
        elif method == "txz":
            txz_compress(fileloc, file)
        elif method == "tbz":
            tbz_compress(fileloc, file, calculate_strength())
        elif method == "tar":
            tar_compress(fileloc, file)
        elif method == "zip":
            zip_compress(fileloc, file)
    return True


def tarzip_verifier(file):
    """
    Assign .tar.xxx, .tar and .zip verifiers.

    :param file: Filename.
    :type file: str
    """
    maps = {".tar.gz": tgz_verify, ".tar.xz": txz_verify,
            ".tar.bz2": tbz_verify, ".tar": tar_verify,
            ".zip": zip_verify, ".bar": zip_verify}
    for key, value in maps.items():
        if file.endswith(key):
            return value(file)


def decide_verifier(file, szexe=None):
    """
    Decide which verifier function to use.

    :param file: Filename.
    :type file: str

    :param szexe: Path to 7z executable, if needed.
    :type szexe: str
    """
    print("VERIFYING: {0}".format(file))
    if file.endswith(".7z") and szexe is not None:
        verif = sz_verify(os.path.abspath(file), szexe)
    else:
        verif = tarzip_verifier(file)
    if not verif:
        print("{0} IS BROKEN!".format(os.path.basename(file)))
    else:
        print("{0} OK".format(os.path.basename(file)))
    return verif


def verify(filepath, method="7z", szexe=None, selective=False):
    """
    Verify specific archive files in a given folder.

    :param filepath: Working directory. Required.
    :type filepath: str

    :param method: Compression type. Default is "7z". Defined in source.
    :type method: str

    :param szexe: Path to 7z executable, if needed.
    :type szexe: str

    :param selective: Only verify autoloaders. Default is false.
    :type selective: bool
    """
    method = filter_method(method, szexe)
    files = compressfilter(filepath, selective)
    for file in files:
        decide_verifier(file, szexe)


def compress_config_loader(homepath=None):
    """
    Read a ConfigParser file to get compression preferences.

    :param homepath: Folder containing ini file. Default is user directory.
    :type homepath: str
    """
    compini = iniconfig.generic_loader('compression', homepath)
    method = compini.get('method', fallback="7z")
    if not utilities.new_enough(3) and method == "txz":
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
    method = compress_config_loader() if method is None else method
    results = {"method": method}
    iniconfig.generic_writer("compression", results, homepath)

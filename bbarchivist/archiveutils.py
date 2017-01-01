#!/usr/bin/env python3
"""This module is used to operate with archives."""

import os  # filesystem read
import subprocess  # invocation of 7z, cap
import zipfile  # zip compresssion
import tarfile  # txz/tbz/tgz/tar compression
from bbarchivist import barutils  # zip tester
from bbarchivist import utilities  # platform determination
from bbarchivist import bbconstants  # premade stuff
from bbarchivist import decorators  # timer
from bbarchivist import iniconfig  # config parsing

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "2015-2017 Thurask"


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
    excode = sz_subprocess(cmd)
    if errors:
        print(szcodes[excode])


def sz_subprocess(cmd):
    """
    Subprocess wrapper for 7-Zip commands.

    :param cmd: Command to pass to subprocess.
    :type cmd: str
    """
    with open(os.devnull, 'wb') as dnull:
        output = subprocess.call(cmd, stdout=dnull, stderr=subprocess.STDOUT, shell=True)
    return output


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
    excode = sz_subprocess(cmd)
    return excode == 0


def generic_tarfile_verify(filepath, method):
    """
    Verify that a tar/tgz/tbz/txz file is valid and working.

    :param filepath: Filename.
    :type filepath: str

    :param method: Tarfile read method.
    :type method: str
    """
    if smart_is_tarfile(filepath):
        with tarfile.open(filepath, method) as thefile:
            mems = thefile.getmembers()
        return False if not mems else True
    else:
        return False


def generic_tarfile_compress(archivename, filename, method, strength=5):
    """
    Pack a file into an uncompressed/gzip/bzip2/LZMA tarfile.

    :param archivename: Archive name.
    :type archivename: str

    :param filename: Name of file to pack into archive.
    :type filename: str

    :param method: Tarfile compress method.
    :type method: str

    :param strength: Compression strength. 5 is normal, 9 is ultra.
    :type strength: int
    """
    nocomp = ["w:", "w:xz"]  # methods w/o compression: tar, tar.xz
    if method in nocomp:
        generic_nocompresslevel(archivename, filename, method)
    else:
        generic_compresslevel(archivename, filename, method, strength)


def generic_compresslevel(archivename, filename, method, strength=5):
    """
    Pack a file into a gzip/bzip2 tarfile.

    :param archivename: Archive name.
    :type archivename: str

    :param filename: Name of file to pack into archive.
    :type filename: str

    :param method: Tarfile compress method.
    :type method: str

    :param strength: Compression strength. 5 is normal, 9 is ultra.
    :type strength: int
    """
    with tarfile.open(archivename, method, compresslevel=strength) as afile:
        afile.add(filename, filter=None, arcname=os.path.basename(filename))


def generic_nocompresslevel(archivename, filename, method):
    """
    Pack a file into an uncompressed/LZMA tarfile.

    :param archivename: Archive name.
    :type archivename: str

    :param filename: Name of file to pack into archive.
    :type filename: str

    :param method: Tarfile compress method.
    :type method: str
    """
    with tarfile.open(archivename, method) as afile:
        afile.add(filename, filter=None, arcname=os.path.basename(filename))


@decorators.timer
def tar_compress(filepath, filename):
    """
    Pack a file into an uncompressed tarfile.

    :param filepath: Basename of file, no extension.
    :type filepath: str

    :param filename: Name of file to pack.
    :type filename: str
    """
    generic_tarfile_compress("{0}.tar".format(filepath), filename, "w:")


def tar_verify(filepath):
    """
    Verify that a tar file is valid and working.

    :param filepath: Filename.
    :type filepath: str
    """
    return generic_tarfile_verify(filepath, "r:")


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
    generic_tarfile_compress("{0}.tar.gz".format(filepath), filename, "w:gz", strength)


def tgz_verify(filepath):
    """
    Verify that a tar.gz file is valid and working.

    :param filepath: Filename.
    :type filepath: str
    """
    return generic_tarfile_verify(filepath, "r:gz")


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
    generic_tarfile_compress("{0}.tar.bz2".format(filepath), filename, "w:bz2", strength)


def tbz_verify(filepath):
    """
    Verify that a tar.bz2 file is valid and working.

    :param filepath: Filename.
    :type filepath: str
    """
    return generic_tarfile_verify(filepath, "r:bz2")


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
        generic_tarfile_compress("{0}.tar.xz".format(filepath), filename, "w:xz")


def txz_verify(filepath):
    """
    Verify that a tar.xz file is valid and working.

    :param filepath: Filename.
    :type filepath: str
    """
    if not utilities.new_enough(3):
        return None
    else:
        return generic_tarfile_verify(filepath, "r:xz")


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
        brokens = barutils.bar_tester(filepath)
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
    method = filter_method_nosz(method, szexe)
    return method


def filter_method_nosz(method, szexe=None):
    """
    Make sure 7-Zip is OK.

    :param method: Compression method to use.
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
    return method


def calculate_strength():
    """
    Determine zip/gzip/bzip2 strength by OS bit setting.
    """
    strength = 9 if utilities.is_amd64() else 5
    return strength


def filter_with_boolfilt(files, criterion, critargs):
    """
    Return everything that matches criterion.

    :param files: Files to work on.
    :type files: list(str)

    :param criterion: Function to use for evaluation.
    :type criterion: func

    :param critargs: Arguments for function, other than file.
    :type critargs: list
    """
    return [file for file in files if criterion(file, *critargs)]


def filter_without_boolfilt(files, criterion, critargs):
    """
    Return everything that doesn't match criterion.

    :param files: Files to work on.
    :type files: list(str)

    :param criterion: Function to use for evaluation.
    :type criterion: func

    :param critargs: Arguments for function, other than file.
    :type critargs: list
    """
    return [file for file in files if not criterion(file, *critargs)]


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
        fx2 = filter_with_boolfilt(files, criterion, critargs)
    else:
        fx2 = filter_without_boolfilt(files, criterion, critargs)
    return fx2


def compressfilter_select(filepath, files, selective=False):
    """
    :param filepath: Working directory. Required.
    :type filepath: str

    :param files: List of files in filepath.
    :type files: list(str)

    :param selective: Only compress autoloaders. Default is false.
    :type selective: bool/str
    """
    arx = bbconstants.ARCS
    pfx = bbconstants.PREFIXES
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
    return filt2


def compressfilter(filepath, selective=False):
    """
    Filter directory listing of working directory.

    :param filepath: Working directory. Required.
    :type filepath: str

    :param selective: Only compress autoloaders. Default is false.
    :type selective: bool/str
    """

    files = [file for file in os.listdir(filepath) if not os.path.isdir(file)]
    filt2 = compressfilter_select(filepath, files, selective)
    filt3 = [os.path.join(filepath, file) for file in filt2]
    return filt3


def prep_compress_function(method="7z", szexe=None, errors=False):
    """
    Prepare compression function and partial arguments.

    :param method: Compression type. Default is "7z".
    :type method: str

    :param szexe: Path to 7z executable, if needed.
    :type szexe: str

    :param errors: Print completion status message. Default is false.
    :type errors: bool
    """
    methods = {"7z": sz_compress, "tgz": tgz_compress, "txz": txz_compress, "tbz": tbz_compress,
               "tar": tar_compress, "zip": zip_compress}
    args = [szexe] if method == "7z" else []
    if method in ("7z", "tbz", "tgz"):
        args.append(calculate_strength())
    if method == "7z":
        args.append(errors)
    return methods[method], args


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
        compfunc, extargs = prep_compress_function(method, szexe, errors)
        compfunc(fileloc, file, *extargs)
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
    decide_verifier_printer(file, verif)
    return verif


def decide_verifier_printer(file, verif):
    """
    Print status of verifier function.

    :param file: Filename.
    :type file: str

    :param verif: If the file is OK or not.
    :type verif: bool
    """
    if not verif:
        print("{0} IS BROKEN!".format(os.path.basename(file)))
    else:
        print("{0} OK".format(os.path.basename(file)))


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

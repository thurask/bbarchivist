#!/usr/bin/env python3
"""This module is used to operate with bar files."""

import base64  # encoding for hashes
import hashlib  # get hashes
import os  # filesystem read
import shutil  # folder operations
import zipfile  # zip extract, zip compresssion

from bbarchivist import bbconstants  # premade stuff
from bbarchivist import exceptions  # exception handling
from bbarchivist import utilities  # platform determination

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "2015-2019 Thurask"


def extract_bars(filepath):
    """
    Extract .signed files from .bar files.
    Use system zlib.

    :param filepath: Path to bar file directory.
    :type filepath: str
    """
    try:
        for file in os.listdir(filepath):
            extract_individual_bar(file, filepath)
    except (RuntimeError, OSError) as exc:
        exceptions.handle_exception(exc, "EXTRACTION FAILURE", None)


def extract_individual_bar(file, filepath):
    """
    Generate bar file contents and extract signed files.

    :param file: Bar file to extract.
    :type file: str

    :param filepath: Path to bar file directory.
    :type filepath: str
    """
    if file.endswith(".bar"):
        print("EXTRACTING: {0}".format(file))
        zfile = zipfile.ZipFile(os.path.join(filepath, file), 'r')
        names = zfile.namelist()
        extract_signed_file(zfile, names, filepath)


def extract_signed_file(zfile, names, filepath):
    """
    Extract signed file from a provided bar.

    :param zfile: Open (!!!) ZipFile instance.
    :type zfile: zipfile.ZipFile

    :param names: List of bar file contents.
    :type names: list(str)

    :param filepath: Path to bar file directory.
    :type filepath: str
    """
    for name in names:
        if str(name).endswith(".signed"):
            zfile.extract(name, filepath)


def get_sha512_manifest(zfile):
    """
    Get MANIFEST.MF from a bar file.

    :param zfile: Open (!!!) ZipFile instance.
    :type zfile: zipfile.ZipFile
    """
    names = zfile.namelist()
    manifest = None
    for name in names:
        if name.endswith("MANIFEST.MF"):
            manifest = name
            break
    if manifest is None:
        raise SystemExit
    return manifest


def get_sha512_from_manifest(manf):
    """
    Retrieve asset name and hash from MANIFEST.MF file.

    :param manf: Content of MANIFEST.MF file, in bytes.
    :type manf: list(bytes)
    """
    alist = []
    for idx, line in enumerate(manf):
        if line.endswith(b"signed"):
            alist.append(manf[idx])
            alist.append(manf[idx + 1])
    assetname = alist[0].split(b": ")[1]
    assethash = alist[1].split(b": ")[1]
    return assetname, assethash


def retrieve_sha512(filename):
    """
    Get the premade, Base64 encoded SHA512 hash of a signed file in a bar.

    :param filename: Bar file to check.
    :type filename: str
    """
    try:
        zfile = zipfile.ZipFile(filename, 'r')
        manifest = get_sha512_manifest(zfile)
        manf = zfile.read(manifest).splitlines()
        assetname, assethash = get_sha512_from_manifest(manf)
        return assetname, assethash  # (b"blabla.signed", b"somehash")
    except (RuntimeError, OSError, zipfile.BadZipFile) as exc:
        exceptions.handle_exception(exc, "EXTRACTION FAILURE", None)


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


def remove_empty_folder(curdir, subdirs, files):
    """
    Remove a folder if it's empty.

    :param curdir: Target folder.
    :type curdir: str

    :param subdirs: Subdirectories inside target folder.
    :type subdirs: list(str)

    :param files: Files inside target folder.
    :type files: list(str)
    """
    while True:
        try:
            indiv_folder_remove(curdir, subdirs, files)
        except OSError:
            continue
        except NotImplementedError:
            break
        break


def indiv_folder_remove(curdir, subdirs, files):
    """
    Remove a folder if it's empty, the actual function.

    :param curdir: Target folder.
    :type curdir: str

    :param subdirs: Subdirectories inside target folder.
    :type subdirs: list(str)

    :param files: Files inside target folder.
    :type files: list(str)
    """
    if not subdirs and not files:
        os.rmdir(curdir)


def remove_empty_folders(a_folder):
    """
    Remove empty folders in a given folder using os.walk().

    :param a_folder: Target folder.
    :type a_folder: str
    """
    for curdir, subdirs, files in os.walk(a_folder):
        remove_empty_folder(curdir, subdirs, files)


def persistent_remove(afile):
    """
    Remove a file, and if it doesn't want to remove, keep at it.

    :param afile: Path to file you want terminated with extreme prejudice.
    :type afile: str
    """
    while True:
        try:
            os.remove(afile)
        except OSError:
            continue
        else:
            break


def remove_signed_files(a_folder):
    """
    Remove signed files from a given folder.

    :param a_folder: Target folder.
    :type a_folder: str
    """
    files = [os.path.abspath(os.path.join(a_folder, file)) for file in os.listdir(a_folder)]
    for afile in files:
        if afile.endswith(".signed") and os.path.exists(afile):
            print("REMOVING: {0}".format(os.path.basename(afile)))
            persistent_remove(afile)


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
    utilities.cond_do(shutil.rmtree, [osdir, raddir], condition=radios)


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


def move_loaders_prep(ldir, suf):
    """
    Prepare a list of filenames for moving loaders.

    :param ldir:
    :type ldir: str

    :param suf: Suffix(es) to check.
    :type suf: str or list or tuple
    """
    pfx = bbconstants.PREFIXES
    loaders = [os.path.join(ldir, file) for file in os.listdir(ldir) if utilities.prepends(file, pfx, suf)]
    return loaders


def move_loaders(ldir, exedir_os, exedir_rad, zipdir_os, zipdir_rad):
    """
    Move autoloaders to zipped and loaders directories in localdir.

    :param ldir: Local directory, containing files you wish to move.
    :type ldir: str

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
    loaders = move_loaders_prep(ldir, ".exe")
    move_loader_pairs(loaders, exedir_os, exedir_rad)
    zippeds = move_loaders_prep(ldir, arx)
    move_loader_pairs(zippeds, zipdir_os, zipdir_rad)


def move_loader_pairs(files, dir_os, dir_rad):
    """
    Move autoloaders to zipped/loaders directories.

    :param files: List of autoloader files.
    :type files: list(str)

    :param dir_os: Large autoloader destination.
    :type dir_os: str

    :param dir_rad: Small autoloader destination.
    :type dir_rad: str
    """
    for file in files:
        print("MOVING: {0}".format(os.path.basename(file)))
        dest_os = os.path.join(dir_os, os.path.basename(file))
        dest_rad = os.path.join(dir_rad, os.path.basename(file))
        loader_sorter(file, dest_os, dest_rad)


def dirsizer(file, osdir, raddir, maxsize=90 * 1000 * 1000):
    """
    Return output directory based in input filesize.

    :param file: The file to sort. Absolute paths, please.
    :type file: str

    :param osdir: Large file destination.
    :type osdir: str

    :param raddir: Small file destination.
    :type raddir: str

    :param maxsize: Return osdir if filesize > maxsize else raddir. Default is 90MB.
    :type maxsize: int
    """
    return osdir if os.path.getsize(file) > maxsize else raddir


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
    outdir = dirsizer(file, osdir, raddir)
    persistent_move(file, outdir)


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
            herefile = os.path.join(localdir, files)
            outdir = dirsizer(herefile, osdir, radiodir)
            atomic_move(herefile, outdir)


def persistent_move(infile, outdir):
    """
    Move file to given folder, removing file if it exists in folder.

    :param infile: Path to file to move.
    :type infile: str

    :param outdir: Directory to move to.
    :type outdir: str
    """
    while True:
        try:
            shutil.move(infile, outdir)
        except shutil.Error:
            os.remove(infile)
            continue
        break


def atomic_move(infile, outdir):
    """
    Move file to given folder, removing if things break.

    :param infile: Path to file to move.
    :type infile: str

    :param outdir: Directory to move to.
    :type outdir: str
    """
    try:
        shutil.move(infile, outdir)
    except shutil.Error:
        os.remove(os.path.join(outdir, infile))


def replace_bar_pair(localdir, osfile, radfile):
    """
    Move pair of OS and radio bars to a given folder.

    :param localdir: Final bar directory.
    :type localdir: str

    :param osfile: Path to OS file.
    :type osfile: str

    :param radfile: Path to radio file.
    :type radfile: str
    """
    shutil.move(osfile, localdir)
    shutil.move(radfile, localdir)


def replace_bars_bulk(localdir, barfiles):
    """
    Move set of OS and radio bars to a given folder.

    :param localdir: Final bar directory.
    :type localdir: str

    :param barfiles: List of OS/radio file paths.
    :type barfiles: list(str)
    """
    for barfile in barfiles:
        shutil.move(barfile, os.path.abspath(localdir))


def make_folder(localdir, root):
    """
    Make a folder if it doesn't exist.

    :param localdir: Top level folder.
    :type localdir: str

    :param root: Folder to create.
    :type root: str
    """
    if not os.path.exists(os.path.join(localdir, root)):
        os.makedirs(os.path.join(localdir, root), exist_ok=True)
    return os.path.join(localdir, root)


def make_dirpairs(localdir, root, osversion, radioversion):
    """
    Create a pair of directories, with OS/radio versions for names.

    :param localdir: Top level folder.
    :type localdir: str

    :param root: Name for folder containing OS/radio pairs.
    :type root: str

    :param osversion: OS version.
    :type osversion: str

    :param radioversion: Radio version.
    :type radioversion: str
    """
    rootdir = make_folder(localdir, root)
    osdir = make_folder(rootdir, osversion)
    radiodir = make_folder(rootdir, radioversion)
    return osdir, radiodir


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
    bardir_os, bardir_radio = make_dirpairs(localdir, "bars", osversion, radioversion)
    loaderdir_os, loaderdir_radio = make_dirpairs(localdir, "loaders", osversion, radioversion)
    zipdir_os, zipdir_radio = make_dirpairs(localdir, "zipped", osversion, radioversion)
    return (bardir_os, bardir_radio, loaderdir_os, loaderdir_radio, zipdir_os, zipdir_radio)

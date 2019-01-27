#!/usr/bin/env python3
"""This module is used to generate file PGP signatures."""

import concurrent.futures  # parallelization
import os  # path work

import gnupg  # interface b/w Python, GPG
from bbarchivist import bbconstants  # premade stuff
from bbarchivist import exceptions  # exceptions
from bbarchivist import hashutils  # filter stuff
from bbarchivist import iniconfig  # config parsing
from bbarchivist import utilities  # cores

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "2015-2019 Thurask"


def gpgrunner(workingdir, keyid=None, pword=None, selective=False):
    """
    Create ASCII-armored PGP signatures for all files in a given directory, in parallel.

    :param workingdir: Path containing files you wish to verify.
    :type workingdir: str

    :param keyid: Key to use. 8-character hexadecimal, with or without 0x.
    :type keyid: str

    :param pword: Passphrase for given key.
    :type pword: str

    :param selective: Filtering filenames/extensions. Default is false.
    :type selective: bool
    """
    try:
        gpg = gnupg.GPG(options=["--no-use-agent"])
    except ValueError:
        print("COULD NOT FIND GnuPG!")
        raise SystemExit
    else:
        gpgrunner_clean(gpg, workingdir, keyid, pword, selective)


def gpgfile(filepath, gpginst, key=None, pword=None):
    """
    Make ASCII-armored signature files with a given private key.
    Takes an instance of gnupg.GPG().

    :param filepath: File you wish to verify.
    :type filepath: str

    :param gpginst: Instance of Python GnuPG executable.
    :type gpginst: gnupg.GPG()

    :param key: Key ID. 0xABCDEF01
    :type key: str

    :param pword: Passphrase for key.
    :type pword: str
    """
    with open(filepath, "rb") as file:
        fname = file.name + ".asc"
        gpginst.sign_file(file, detach=True, keyid=key, passphrase=pword, output=fname)


def prep_gpgkeyid(keyid=None):
    """
    Prepare GPG key ID.

    :param keyid: Key to use. 8-character hexadecimal, with or without 0x.
    :type keyid: str
    """
    return "0x" + keyid.upper() if not keyid.startswith("0x") else keyid.upper().replace("X", "x")


def prep_gpgrunner(workingdir, keyid=None):
    """
    Prepare key and files for gpgrunner function.

    :param workingdir: Path containing files you wish to verify.
    :type workingdir: str

    :param keyid: Key to use. 8-character hexadecimal, with or without 0x.
    :type keyid: str
    """
    keyid = prep_gpgkeyid(keyid)
    dirlist = os.listdir(workingdir)
    files = [file for file in dirlist if hashutils.filefilter(file, workingdir)]
    return keyid, files


def gpgrunner_clean(gpg, workingdir, keyid=None, pword=None, selective=False):
    """
    Run GPG signature generation after filtering out errors.

    :param gpg: Instance of Python GnuPG executable.
    :type gpg: gnupg.GPG()

    :param workingdir: Path containing files you wish to verify.
    :type workingdir: str

    :param keyid: Key to use. 8-character hexadecimal, with or without 0x.
    :type keyid: str

    :param pword: Passphrase for given key.
    :type pword: str

    :param selective: Filtering filenames/extensions. Default is false.
    :type selective: bool
    """
    keyid, files = prep_gpgrunner(workingdir, keyid)
    with concurrent.futures.ThreadPoolExecutor(max_workers=utilities.cpu_workers(files)) as xec:
        for file in files:
            gpgwriter(gpg, xec, file, workingdir, selective, keyid, pword)


def gpg_supps(selective=False):
    """
    Prepare list of support files.

    :param selective: Filtering filenames/extensions. Default is false.
    :type selective: bool
    """
    sup = bbconstants.SUPPS + (".txt",) if selective else bbconstants.SUPPS
    return sup


def gpg_prepends(file, selective=False):
    """
    Check if file matches certain criteria.

    :param file: File inside workingdir that is being verified.
    :type file: str

    :param selective: Filtering filenames/extensions. Default is false.
    :type selective: bool
    """
    aps = bbconstants.ARCSPLUS
    pfx = bbconstants.PREFIXES
    sentinel = (utilities.prepends(file, pfx, aps)) if selective else True
    return sentinel


def gpgwriter(gpg, xec, file, workingdir, selective=False, keyid=None, pword=None):
    """
    Write individual GPG signatures.

    :param gpg: Instance of Python GnuPG executable.
    :type gpg: gnupg.GPG()

    :param xec: ThreadPoolExecutor instance.
    :type xec: concurrent.futures.ThreadPoolExecutor

    :param file: File inside workingdir that is being verified.
    :type file: str

    :param workingdir: Path containing files you wish to verify.
    :type workingdir: str

    :param selective: Filtering filenames/extensions. Default is false.
    :type selective: bool

    :param keyid: Key to use. 8-character hexadecimal, with or without 0x.
    :type keyid: str

    :param pword: Passphrase for given key.
    :type pword: str
    """
    sup = gpg_supps(selective)
    if not file.endswith(sup):
        if gpg_prepends(file, selective):
            gpgwriter_clean(gpg, xec, file, workingdir, keyid, pword)


def gpgwriter_clean(gpg, xec, file, workingdir, keyid=None, pword=None):
    """
    Write individual GPG signatures after filtering file list.

    :param gpg: Instance of Python GnuPG executable.
    :type gpg: gnupg.GPG()

    :param xec: ThreadPoolExecutor instance.
    :type xec: concurrent.futures.ThreadPoolExecutor

    :param file: File inside workingdir that is being verified.
    :type file: str

    :param workingdir: Path containing files you wish to verify.
    :type workingdir: str

    :param keyid: Key to use. 8-character hexadecimal, with or without 0x.
    :type keyid: str

    :param pword: Passphrase for given key.
    :type pword: str
    """
    print("VERIFYING:", os.path.basename(file))
    thepath = os.path.join(workingdir, file)
    try:
        xec.submit(gpgfile, thepath, gpg, keyid, pword)
    except Exception as exc:
        exceptions.handle_exception(exc)


def gpg_config_loader(homepath=None):
    """
    Read a ConfigParser file to get PGP key, password (optional)

    :param homepath: Folder containing ini file. Default is user directory.
    :type homepath: str
    """
    config = iniconfig.generic_loader('gpgrunner', homepath)
    gpgkey = config.get('key', fallback=None)
    gpgpass = config.get('pass', fallback=None)
    return gpgkey, gpgpass


def gpg_config_writer(key=None, password=None, homepath=None):
    """
    Write a ConfigParser file to store PGP key, password (optional)

    :param key: Key ID, leave as None to not write.
    :type key: str

    :param password: Key password, leave as None to not write.
    :type password: str

    :param homepath: Folder containing ini file. Default is user directory.
    :type homepath: str
    """
    results = {}
    if key is not None:
        results["key"] = key
    if password is not None:
        results["pass"] = password
    iniconfig.generic_writer("gpgrunner", results, homepath)

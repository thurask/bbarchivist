#!/usr/bin/env python3
"""This module is used to operate with 7Z archives."""

import os  # filesystem read
import subprocess  # invocation of 7z

from bbarchivist import decorators  # timer
from bbarchivist import utilities  # platform determination

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "2018 Thurask"


def szcodes():
    """
    Return dictionary of 7-Zip error codes.
    """
    szc = {
        0: "NO ERRORS",
        1: "COMPLETED WITH WARNINGS",
        2: "FATAL ERROR",
        7: "COMMAND LINE ERROR",
        8: "OUT OF MEMORY ERROR",
        255: "USER STOPPED PROCESS"
    }
    return szc


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
    strength = str(strength)
    szc = szcodes()
    rawname = os.path.dirname(filepath)
    thr = str(utilities.get_core_count())
    fold = os.path.join(rawname, filename)
    cmd = '{0} a -mx{1} -m0=lzma2 -mmt{2} "{3}.7z" "{4}"'.format(szexe, strength, thr, filepath, fold)
    excode = sz_subprocess(cmd)
    if errors:
        print(szc[excode])


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


def pack_tclloader_sz(dirname, filename, strength=5):
    """
    Compress Android autoloader folder into a 7z file.

    :param dirname: Target folder.
    :type dirname: str

    :param filename: File title, without extension.
    :type filename: str

    :param strength: Compression strength. 5 is normal, 9 is ultra.
    :type strength: int
    """
    szexe = utilities.get_seven_zip()
    thr = str(utilities.get_core_count())
    cmd = '{0} a -mx{1} -m0=lzma2 -mmt{2} "{3}.7z" "./{4}/*"'.format(szexe, strength, thr, filename, dirname)
    sz_subprocess(cmd)

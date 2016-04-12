#!/usr/bin/env python3
"""This module is the Python-ized implementation of cap.exe"""

import os  # path work
import binascii  # to hex and back again
import glob  # filename matching
import base64  # storage
from bbarchivist import bbconstants  # versions/constants
from bbarchivist import utilities  # finding cap

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "Copyright 2015-2016 Thurask"


def ghetto_convert(intsize):
    """
    Convert from decimal integer to little endian
    hexadecimal string, padded to 16 characters with zeros.

    :param intsize: Integer you wish to convert.
    :type intsize: int
    """
    if not isinstance(intsize, int):
        intsize = int(intsize)
    hexsize = format(intsize, '08x')  # '00AABBCC'
    newlist = [hexsize[i:i + 2] for i in range(0, len(hexsize), 2)]  # ['00', 'AA','BB','CC']
    newlist.reverse()
    ghetto_hex = "".join(newlist)  # 'CCBBAA'
    ghetto_hex = ghetto_hex.rjust(16, '0')
    if len(ghetto_hex) == 16:
        return binascii.unhexlify(bytes(ghetto_hex.upper(), 'ascii'))


def make_offset(files, folder=None):
    """
    Create magic offset file for use in autoloader creation.
    Cap.exe MUST match separator version.
    Version defined in :data:`bbarchivist.bbconstants.CAP.version`.

    :param files: List of 1-6 signed files.
    :type files: list(str)

    :param folder: Working folder. Optional. Default is local.
    :type folder: str
    """
    if folder is None:
        folder = os.getcwd()
    capfile = utilities.grab_cap()
    filelist = [file for file in files if file]
    filecount = len(filelist)
    fcount = b'0' + bytes(str(filecount), 'ascii')
    # immutable things
    scaff = b'at9dFE5LTEdOT0hHR0lTCxcKDR4MFFMtPiU6LT0zPjs6Ui88U05GTVFOSUdRTlFOT3BwcJzVxZec1cWXnNXFlw=='
    separator = base64.b64decode(scaff)
    password = binascii.unhexlify(b'0' * 160)
    pad = b'\x00'  # 1x, 2x or 8x
    filepad = binascii.unhexlify(fcount)  # 01-06
    trailers = binascii.unhexlify(b'00' * (7 - filecount))  # 00, 1-6x
    capsize = os.path.getsize(capfile)
    if not filecount:  # we need at least one file
        raise SystemExit
    first = str(glob.glob(filelist[0])[0])
    firstsize = os.path.getsize(first)  # required
    if filecount >= 2:
        second = str(glob.glob(filelist[1])[0])
        secondsize = os.path.getsize(second)
    if filecount >= 3:
        third = str(glob.glob(filelist[2])[0])
        thirdsize = os.path.getsize(third)
    if filecount >= 4:
        fourth = str(glob.glob(filelist[3])[0])
        fourthsize = os.path.getsize(fourth)
    if filecount >= 5:
        fifth = str(glob.glob(filelist[4])[0])
        fifthsize = os.path.getsize(fifth)
    # start of first file; length of cap + length of offset
    beginlength = len(separator) + len(password) + 64
    firstoffset = beginlength + capsize
    firststart = ghetto_convert(firstoffset)
    secondstart = thirdstart = fourthstart = fifthstart = sixthstart = pad * 8
    if filecount >= 2:
        secondoffset = firstoffset + firstsize  # start of second file
        secondstart = ghetto_convert(secondoffset)
    if filecount >= 3:
        thirdoffset = secondoffset + secondsize  # start of third file
        thirdstart = ghetto_convert(thirdoffset)
    if filecount >= 4:
        fourthoffset = thirdoffset + thirdsize  # start of fourth file
        fourthstart = ghetto_convert(fourthoffset)
    if filecount >= 5:
        fifthoffset = fourthoffset + fourthsize  # start of fifth file
        fifthstart = ghetto_convert(fifthoffset)
    if filecount == 6:
        sixthoffset = fifthoffset + fifthsize  # start of sixth file
        sixthstart = ghetto_convert(sixthoffset)
    makeuplen = 64 - 6 * len(pad * 8) - 2 * len(pad * 2) - 2 * \
        len(pad) - len(trailers) - len(filepad)
    makeup = b'\x00' * makeuplen  # pad to match offset begin
    with open(os.path.join(folder, "offset.hex"), "wb") as file:
        file.write(separator)
        file.write(password)
        file.write(filepad)
        file.write(pad * 2)
        file.write(pad)
        file.write(firststart)
        file.write(secondstart)
        file.write(thirdstart)
        file.write(fourthstart)
        file.write(fifthstart)
        file.write(sixthstart)
        file.write(pad)
        file.write(pad * 2)
        file.write(trailers)
        file.write(makeup)


def write_4k(infile, outfile):
    """
    Write a file from another file, 4k bytes at a time.

    :param infile: Filename. Input file.
    :type infile: str

    :param outfile: Open (!!!) file handle. Output file.
    :type outfile: str
    """
    with open(os.path.abspath(infile), "rb") as afile:
        print("WRITING FILE...\n{0}".format(os.path.basename(infile)))
        while True:
            chunk = afile.read(4096)  # 4k chunks
            if not chunk:
                break
            outfile.write(chunk)


def make_autoloader(filename, files, folder=None):
    """
    Write cap.exe, magic offset, signed files to a .exe file.
    :func:`make_offset` is used to create the offset.

    :param filename: Name of autoloader.
    :type filename: str

    :param files: List of 1-6 signed files.
    :type files: list(str)

    :param folder: Working folder. Optional. Default is local.
    :type folder: str
    """
    if folder is None:
        folder = os.getcwd()
    make_offset(files, folder)
    filelist = [os.path.abspath(file) for file in files if file]
    print("CREATING: {0}".format(filename))
    try:
        with open(os.path.join(os.path.abspath(folder), filename), "wb") as autoloader:
            with open(os.path.normpath(utilities.grab_cap()), "rb") as capfile:
                print("WRITING CAP VERSION {0}...".format(bbconstants.CAP.version))
                while True:
                    chunk = capfile.read(4096)  # 4k chunks
                    if not chunk:
                        break
                    autoloader.write(chunk)
            with open(os.path.join(folder, "offset.hex"), "rb") as offset:
                print("WRITING MAGIC OFFSET...")
                autoloader.write(offset.read())
            for file in filelist:
                write_4k(file, autoloader)
    except IOError as exc:
        print("Operation failed: {0}".format(exc.strerror))
    else:
        print("{0} FINISHED!".format(filename))
    os.remove(os.path.join(folder, "offset.hex"))

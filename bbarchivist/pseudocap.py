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
    newlist = [hexsize[i:i + 2]
               for i in range(0, len(hexsize), 2)]  # ['00', 'AA','BB','CC']
    newlist.reverse()
    ghetto_hex = "".join(newlist)  # 'CCBBAA'
    ghetto_hex = ghetto_hex.rjust(16, '0')
    if len(ghetto_hex) == 16:
        return binascii.unhexlify(bytes(ghetto_hex.upper(), 'ascii'))


def make_offset(firstfile, secondfile=None, thirdfile=None,
                fourthfile=None, fifthfile=None, sixthfile=None, folder=None):
    """
    Create magic offset file for use in autoloader creation.
    Cap.exe MUST match separator version.
    Version defined in :data:`bbarchivist.bbconstants.CAPVERSION`.

    :param firstfile: First signed file. Required.
    :type firstfile: str

    :param secondfile: Second signed file. Optional.
    :type secondfile: str

    :param thirdfile: Third signed file. Optional.
    :type thirdfile: str

    :param fourthfile: Fourth signed file. Optional.
    :type fourthfile: str

    :param fifthfile: Fifth signed file. Optional.
    :type fifthfile: str

    :param sixthfile: Sixth signed file. Optional.
    :type sixthfile: str

    :param folder: Working folder. Optional. Default is local.
    :type folder: str
    """
    if folder is None:
        folder = os.getcwd()
    cap = utilities.grab_cap()
    filelist = [
        firstfile,
        secondfile,
        thirdfile,
        fourthfile,
        fifthfile,
        sixthfile]
    filecount = len([file for file in filelist if file])
    fcount = b'0' + bytes(str(filecount), 'ascii')
    # immutable things
    scaff = b'at9dFE5LTEdOT0hHR0lTCxcKDR4MFFMtPiU6LT0zPj'
    scaff += b's6Ui88U05GTVFOSUdRTlFOT3BwcJzVxZec1cWXnNXFlw=='
    separator = base64.b64decode(scaff)
    password = binascii.unhexlify(b'0'*160)
    singlepad = b'\x00'
    doublepad = b'\x00\x00'
    signedpad = b'\x00\x00\x00\x00\x00\x00\x00\x00'
    filepad = binascii.unhexlify(fcount)  # 01-06
    trailers = binascii.unhexlify(b'00' * (7 - filecount))  # 00, 1-6x
    capfile = str(cap)
    capsize = os.path.getsize(capfile)
    if firstfile is None:  # we need at least one file
        raise SystemExit
    first = str(glob.glob(firstfile)[0])
    firstsize = os.path.getsize(first)  # required
    if filecount >= 2:
        second = str(glob.glob(secondfile)[0])
        secondsize = os.path.getsize(second)
    if filecount >= 3:
        third = str(glob.glob(thirdfile)[0])
        thirdsize = os.path.getsize(third)
    if filecount >= 4:
        fourth = str(glob.glob(fourthfile)[0])
        fourthsize = os.path.getsize(fourth)
    if filecount >= 5:
        fifth = str(glob.glob(fifthfile)[0])
        fifthsize = os.path.getsize(fifth)
    # start of first file; length of cap + length of offset
    beginlength = len(separator) + len(password) + 64
    firstoffset = beginlength + capsize
    firststart = ghetto_convert(firstoffset)
    secondstart = thirdstart = fourthstart = signedpad
    fifthstart = sixthstart = signedpad
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
    makeuplen = 64 - 6*len(signedpad)
    makeuplen -= 2*len(doublepad)
    makeuplen -= len(filepad)
    makeuplen -= 2*len(singlepad)
    makeuplen -= len(trailers)
    makeup = b'\x00'*makeuplen  # pad to match offset begin
    with open(os.path.join(folder, "offset.hex"), "wb") as file:
        file.write(separator)
        file.write(password)
        file.write(filepad)
        file.write(doublepad)
        file.write(singlepad)
        file.write(firststart)
        file.write(secondstart)
        file.write(thirdstart)
        file.write(fourthstart)
        file.write(fifthstart)
        file.write(sixthstart)
        file.write(singlepad)
        file.write(doublepad)
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


def make_autoloader(filename, firstfile, secondfile=None, thirdfile=None,
                    fourthfile=None, fifthfile=None, sixthfile=None,
                    folder=None):
    """
    Write cap.exe, magic offset, signed files to a .exe file.
    :func:`make_offset` is used to create the offset.

    :param filename: Name of autoloader.
    :type filename: str

    :param firstfile: First signed file. Required.
    :type firstfile: str

    :param secondfile: Second signed file. Optional.
    :type secondfile: str

    :param thirdfile: Third signed file. Optional.
    :type thirdfile: str

    :param fourthfile: Fourth signed file. Optional.
    :type fourthfile: str

    :param fifthfile: Fifth signed file. Optional.
    :type fifthfile: str

    :param sixthfile: Sixth signed file. Optional.
    :type sixthfile: str

    :param folder: Working folder. Optional. Default is local.
    :type folder: str
    """
    cap = utilities.grab_cap()
    if folder is None:
        folder = os.getcwd()
    make_offset(
        firstfile,
        secondfile,
        thirdfile,
        fourthfile,
        fifthfile,
        sixthfile,
        folder)
    filelist = [
        firstfile,
        secondfile,
        thirdfile,
        fourthfile,
        fifthfile,
        sixthfile]
    filelist = [os.path.abspath(file) for file in filelist if file]
    print("CREATING:", filename)
    try:
        with open(os.path.join(os.path.abspath(folder), filename), "wb") as autoloader:
            with open(os.path.normpath(cap), "rb") as capfile:
                print("WRITING CAP VERSION {0}...".format(bbconstants.CAPVERSION))
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
        print("Operation failed:", exc.strerror)
    else:
        print(filename, "FINISHED!")
    os.remove(os.path.join(folder, "offset.hex"))

#!/usr/bin/env python3
#pylint: disable = I0011, R0201, W0613, C0301, R0913, R0912, R0914, R0915
"""This module is the Python-ized implementation of cap.exe"""

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "2015 Thurask"

import os  # path work
import binascii  # to hex and back again
import glob  # filename matching
import base64  # storage
from bbarchivist import bbconstants  # versions/constants
from bbarchivist import utilities  # finding cap


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
    scaff = b'at9dFE5LTEdOT0hHR0lTCxcKDR4MFFMtPiU6LT0zPjs6Ui88U05GTVFOSUdRTlFOT3BwcJzVxZec1cWXnNXFlw=='
    separator = base64.b64decode(scaff)
    password = binascii.unhexlify(b'0'*160)
    singlepad = b'\x00'
    doublepad = b'\x00\x00'
    signedpad = b'\x00\x00\x00\x00\x00\x00\x00\x00'
    filepad = binascii.unhexlify(fcount)  # 01-06
    trailers = binascii.unhexlify(b'00' * (7 - filecount))# 00 repeated between 1 and 6 times
    capfile = str(cap)
    capsize = os.path.getsize(capfile)  # size of cap.exe, in bytes
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
    secondstart = thirdstart = fourthstart = fifthstart = sixthstart = signedpad
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
    makeuplen = 64 - (6*len(signedpad) + 2*len(doublepad) + len(filepad) + 2*len(singlepad) + len(trailers))
    makeup = b'\x00'*makeuplen  # pad to match offset begin and actual first file start
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


def make_autoloader(filename, firstfile, secondfile="", thirdfile="",
                    fourthfile="", fifthfile="", sixthfile="",
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
    filecount = 0
    filelist = [
        firstfile,
        secondfile,
        thirdfile,
        fourthfile,
        fifthfile,
        sixthfile]
    for i in filelist:
        if i:
            filecount += 1
    print("CREATING:", filename)
    try:
        with open(os.path.join(os.path.abspath(folder),
                               filename), "wb") as autoloader:
            try:
                with open(os.path.normpath(cap), "rb") as capfile:
                    print("WRITING CAP VERSION",
                          bbconstants.CAPVERSION + "...")
                    while True:
                        chunk = capfile.read(4096)  # 4k chunks
                        if not chunk:
                            break
                        autoloader.write(chunk)
            except IOError as exc:
                print("Operation failed:", exc.strerror)
            try:
                with open(os.path.join(folder, "offset.hex"), "rb") as offset:
                    print("WRITING MAGIC OFFSET...")
                    autoloader.write(offset.read())
            except IOError as exc:
                print("Operation failed:", exc.strerror)
            try:
                with open(firstfile, "rb") as first:
                    print(
                        "WRITING SIGNED FILE #1...\n",
                        os.path.basename(firstfile))
                    while True:
                        chunk = first.read(4096)  # 4k chunks
                        if not chunk:
                            break
                        autoloader.write(chunk)
            except IOError as exc:
                print("Operation failed:", exc.strerror)
            if filecount >= 2:
                try:
                    print(
                        "WRITING SIGNED FILE #2...\n",
                        os.path.basename(secondfile))
                    with open(secondfile, "rb") as second:
                        while True:
                            chunk = second.read(4096)  # 4k chunks
                            if not chunk:
                                break
                            autoloader.write(chunk)
                except IOError as exc:
                    print("Operation failed:", exc.strerror)
            if filecount >= 3:
                try:
                    print(
                        "WRITING SIGNED FILE #3...\n",
                        os.path.basename(thirdfile))
                    with open(thirdfile, "rb") as third:
                        while True:
                            chunk = third.read(4096)  # 4k chunks
                            if not chunk:
                                break
                            autoloader.write(chunk)
                except IOError as exc:
                    print("Operation failed:", exc.strerror)
            if filecount >= 4:
                try:
                    print(
                        "WRITING SIGNED FILE #5...\n",
                        os.path.basename(fourthfile))
                    with open(fourthfile, "rb") as fourth:
                        while True:
                            chunk = fourth.read(4096)  # 4k chunks
                            if not chunk:
                                break
                            autoloader.write(chunk)
                except IOError as exc:
                    print("Operation failed:", exc.strerror)
            if filecount >= 5:
                try:
                    print(
                        "WRITING SIGNED FILE #5...\n",
                        os.path.basename(fifthfile))
                    with open(fifthfile, "rb") as fifth:
                        while True:
                            chunk = fifth.read(4096)  # 4k chunks
                            if not chunk:
                                break
                            autoloader.write(chunk)
                except IOError as exc:
                    print("Operation failed:", exc.strerror)
            if filecount == 6:
                try:
                    print(
                        "WRITING SIGNED FILE #6...\n",
                        os.path.basename(sixthfile))
                    with open(sixthfile, "rb") as sixth:
                        while True:
                            chunk = sixth.read(4096)  # 4k chunks
                            if not chunk:
                                break
                            autoloader.write(chunk)
                except IOError as exc:
                    print("Operation failed:", exc.strerror)
            if filecount == 0 or filecount > 6:
                print("Invalid filecount")
                return
    except IOError as exc:
        print("Operation failed:", exc.strerror)
    print(filename, "FINISHED!")
    os.remove(os.path.join(folder, "offset.hex"))

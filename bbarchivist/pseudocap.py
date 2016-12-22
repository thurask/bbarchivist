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


def make_sizes(filelist):
    """
    Get sizes of list of signed files.

    :param filelist: List of 1-6 signed files.
    :type filelist: list(str)
    """
    first = str(glob.glob(filelist[0])[0])
    size1 = os.path.getsize(first)  # required
    size2 = size3 = size4 = size5 = 0
    if len(filelist) >= 2:
        second = str(glob.glob(filelist[1])[0])
        size2 = os.path.getsize(second)
    if len(filelist) >= 3:
        third = str(glob.glob(filelist[2])[0])
        size3 = os.path.getsize(third)
    if len(filelist) >= 4:
        fourth = str(glob.glob(filelist[3])[0])
        size4 = os.path.getsize(fourth)
    if len(filelist) >= 5:
        fifth = str(glob.glob(filelist[4])[0])
        size5 = os.path.getsize(fifth)
    return [size1, size2, size3, size4, size5]


def make_starts(beginlength, capsize, pad, sizes, filecount):
    """
    Get list of starting positions for each signed file.

    :param beginlength: Length of beginning offset.
    :type beginlength: int

    :param capsize: Size of cap executable.
    :type capsize: int

    :param pad: Padding character.
    :type pad: bytes

    :param sizes: List of signed file sizes.
    :type sizes: list(int)

    :param filecount: Number of signed files.
    :type filecount: int
    """
    firstoffset = beginlength + capsize
    start1 = ghetto_convert(firstoffset)
    start2 = start3 = start4 = start5 = start6 = pad * 8
    if filecount >= 2:
        secondoffset = firstoffset + sizes[0]  # start of second file
        start2 = ghetto_convert(secondoffset)
    if filecount >= 3:
        thirdoffset = secondoffset + sizes[1]  # start of third file
        start3 = ghetto_convert(thirdoffset)
    if filecount >= 4:
        fourthoffset = thirdoffset + sizes[2]  # start of fourth file
        start4 = ghetto_convert(fourthoffset)
    if filecount >= 5:
        fifthoffset = fourthoffset + sizes[3]  # start of fifth file
        start5 = ghetto_convert(fifthoffset)
    if filecount == 6:
        sixthoffset = fifthoffset + sizes[4]  # start of sixth file
        start6 = ghetto_convert(sixthoffset)
    return [start1, start2, start3, start4, start5, start6]


def make_offset(files, folder=None):
    """
    Create magic offset for use in autoloader creation.
    Cap.exe MUST match separator version.
    Version defined in :data:`bbarchivist.bbconstants.CAP.version`.

    :param files: List of 1-6 signed files.
    :type files: list(str)

    :param folder: Working folder. Optional. Default is local.
    :type folder: str
    """
    folder = os.getcwd() if folder is None else folder
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
    sizes = make_sizes(filelist)
    # start of first file; length of cap + length of offset
    beginlength = len(separator) + len(password) + 64
    starts = make_starts(beginlength, capsize, pad, sizes, filecount)
    makeuplen = 64 - 6 * len(pad * 8) - 2 * len(pad * 2) - 2 * \
        len(pad) - len(trailers) - len(filepad)
    makeup = b'\x00' * makeuplen  # pad to match offset begin
    magicoffset = [separator, password, filepad, pad, pad, pad, starts[0], starts[1], starts[2], starts[3], starts[4], starts[5], pad, pad, pad, trailers, makeup]
    return b"".join(magicoffset)


def write_offset(inbytes, outfile):
    """
    Write to a file from the offset bytestring.

    :param inbytes: Bytestring.
    :type inbytes: bytes

    :param outfile: Open (!!!) file handle. Output file.
    :type outfile: str
    """
    print("WRITING MAGIC OFFSET")
    outfile.write(inbytes)


def write_4k(infile, outfile, text="FILE"):
    """
    Write to a file from another file, 4k bytes at a time.

    :param infile: Filename. Input file.
    :type infile: str

    :param outfile: Open (!!!) file handle. Output file.
    :type outfile: str

    :param text: Writing <text>...
    :type text: str
    """
    with open(os.path.abspath(infile), "rb") as afile:
        print("WRITING {1}...\n{0}".format(os.path.basename(infile), text))
        while True:
            chunk = afile.read(4096)  # 4k chunks
            if not chunk:
                break
            outfile.write(chunk)


def make_autoloader(filename, files, folder=None):
    """
    Prepare for creation of autoloader.

    :param filename: Name of autoloader.
    :type filename: str

    :param files: List of 1-6 signed files to add into autoloader.
    :type files: list(str)

    :param folder: Working folder. Optional, default is local.
    :type folder: str
    """
    folder = os.getcwd() if folder is None else folder
    offset = make_offset(files, folder)
    filelist = [os.path.abspath(file) for file in files if file]
    print("CREATING: {0}".format(filename))
    try:
        write_autoloader(filename, folder, offset, filelist)
    except IOError as exc:
        print("Operation failed: {0}".format(exc.strerror))
    else:
        print("{0} FINISHED!".format(filename))


def write_autoloader(filename, folder, offset, filelist):
    """
    Write cap.exe, magic offset, and signed files to a .exe file.

    :param filename: Name of autoloader.
    :type filename: str

    :param folder: Working folder.
    :type folder: str

    :param offset: Offset bytestring.
    :type offset: bytes

    :param filelist: List of absolute filepaths to write into autoloader.
    :type filelist: list(str)
    """
    with open(os.path.join(os.path.abspath(folder), filename), "wb") as autoloader:
        capskel = "CAP VERSION {0}".format(bbconstants.CAP.version)
        write_4k(os.path.normpath(utilities.grab_cap()), autoloader, capskel)
        write_offset(offset, autoloader)
        for file in filelist:
            write_4k(file, autoloader)

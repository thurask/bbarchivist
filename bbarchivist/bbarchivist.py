#!/usr/bin/env python3

import sys  # arguments
import argparse  # argument parsing
import os
from . import utilities
from . import bbconstants
from . import archivist


def main():
    """
    Parse arguments from argparse/questionnaire.

    Invoke `archivist.doMagic()` with those arguments.
    """
    if len(sys.argv) > 1:
        parser = argparse.ArgumentParser(
            prog="bb-archivist",
            description="Download bar files, create autoloaders.",
            epilog="http://github.com/thurask/bbarchivist")
        parser.add_argument(
            "-v",
            "--version",
            action="version",
            version="%(prog)s " +
            bbconstants._version)
        parser.add_argument("os", help="OS version, 10.x.y.zzzz")
        parser.add_argument("radio", help="Radio version, 10.x.y.zzzz")
        parser.add_argument("swrelease", help="Software version, 10.x.y.zzzz")
        parser.add_argument(
            "-f",
            "--folder",
            type=utilities.file_exists,
            dest="folder",
            help="Working folder",
            default=os.getcwd(),
            metavar="DIR")
        parser.add_argument(
            "-c",
            "--cap",
            type=utilities.file_exists,
            dest="cappath",
            help="Path to cap.exe",
            default=os.path.join(
                os.getcwd(),
                bbconstants._caplocation),
            metavar="PATH")
        negategroup = parser.add_argument_group(
            "negators",
            "Disable program functionality")
        negategroup.add_argument(
            "-no",
            "--no-download",
            dest="download",
            help="Don't download files",
            action="store_false",
            default=True)
        negategroup.add_argument(
            "-nx",
            "--no-extract",
            dest="extract",
            help="Don't extract bar files",
            action="store_false",
            default=True)
        negategroup.add_argument(
            "-nl",
            "--no-loaders",
            dest="loaders",
            help="Don't create autoloaders",
            action="store_false",
            default=True)
        negategroup.add_argument(
            "-nr",
            "--no-radios",
            dest="radloaders",
            help="Don't make radio autoloaders",
            action="store_false",
            default=True)
        negategroup.add_argument(
            "-ns",
            "--no-rmsigned",
            dest="signed",
            help="Don't remove signed files",
            action="store_false",
            default=True)
        negategroup.add_argument(
            "-nc",
            "--no-compress",
            dest="compress",
            help="Don't compress loaders",
            action="store_false",
            default=True)
        negategroup.add_argument(
            "-nd",
            "--no-delete",
            dest="delete",
            help="Don't delete uncompressed loaders",
            action="store_false",
            default=True)
        negategroup.add_argument(
            "-nv",
            "--no-verify",
            dest="verify",
            help="Don't verify created loaders",
            action="store_false",
            default=True)
        hashgroup = parser.add_argument_group(
            "verifiers",
            "Verification methods")
        hashgroup.add_argument(
            "--crc32",
            dest="crc32",
            help="Enable CRC32 verification",
            action="store_true",
            default=False)
        hashgroup.add_argument(
            "--adler32",
            dest="adler32",
            help="Enable Adler-32 verification",
            action="store_true",
            default=False)
        hashgroup.add_argument(
            "--md4",
            dest="md4",
            help="Enable MD4 verification",
            action="store_true",
            default=False)
        hashgroup.add_argument(
            "--sha224",
            dest="sha224",
            help="Enable SHA-224 verification",
            action="store_true",
            default=False)
        hashgroup.add_argument(
            "--sha384",
            dest="sha384",
            help="Enable SHA-384 verification",
            action="store_true",
            default=False)
        hashgroup.add_argument(
            "--sha512",
            dest="sha512",
            help="Enable SHA-512 verification",
            action="store_true",
            default=False)
        hashgroup.add_argument(
            "--ripemd160",
            dest="ripemd160",
            help="Enable RIPEMD-160 verification",
            action="store_true",
            default=False)
        hashgroup.add_argument(
            "--no-sha1",
            dest="sha1",
            help="Disable SHA-1 verification",
            action="store_false",
            default=True)
        hashgroup.add_argument(
            "--no-sha256",
            dest="sha256",
            help="Disable SHA-256 verification",
            action="store_false",
            default=True)
        hashgroup.add_argument(
            "--no-md5",
            dest="md5",
            help="Disable MD5 verification",
            action="store_false",
            default=True)
        comps = parser.add_argument_group("compressors", "Compression methods")
        compgroup = comps.add_mutually_exclusive_group()
        compgroup.add_argument(
            "--7z",
            dest="compmethod",
            help="Compress with 7z, LZMA2",
            action="store_const",
            const="7z")
        compgroup.add_argument(
            "--tgz",
            dest="compmethod",
            help="Compress with tar, GZIP",
            action="store_const",
            const="tgz")
        compgroup.add_argument(
            "--tbz",
            dest="compmethod",
            help="Compress with tar, BZIP2",
            action="store_const",
            const="tbz")
        compgroup.add_argument(
            "--txz",
            dest="compmethod",
            help="Compress with tar, LZMA",
            action="store_const",
            const="txz")
        compgroup.add_argument(
            "--zip",
            dest="compmethod",
            help="Compress with zip, DEFLATE",
            action="store_const",
            const="zip")
        parser.set_defaults(compmethod="7z")
        args = parser.parse_args(sys.argv[1:])
        archivist.do_magic(args.os, args.radio, args.swrelease,
                           args.folder, args.radloaders,
                           args.compress, args.delete, args.verify,
                           args.crc32, args.adler32, args.sha1,
                           args.sha224, args.sha256,
                           args.sha384, args.sha512, args.md5,
                           args.md4, args.ripemd160,
                           args.cappath, args.download,
                           args.extract, args.loaders,
                           args.signed, args.compmethod)
    else:
        localdir = os.getcwd()
        osversion = input("OS VERSION: ")
        radioversion = input("RADIO VERSION: ")
        softwareversion = input("SOFTWARE RELEASE: ")
        radios = utilities.str2bool(input("CREATE RADIO LOADERS? Y/N: "))
        compressed = utilities.str2bool(input("COMPRESS LOADERS? Y/N: "))
        if compressed:
            deleted = utilities.str2bool(input("DELETE UNCOMPRESSED? Y/N: "))
        else:
            deleted = False
        hashed = utilities.str2bool(input("GENERATE HASHES? Y/N: "))
        print(" ")
        archivist.do_magic(osversion, radioversion, softwareversion,
                           localdir, radios, compressed, deleted, hashed,
                           False, False, True, False, False,
                           False, False, True, False, False,
                           "cap-3.11.0.18.dat", True, True, True, True, "7z")
    smeg = input("Press Enter to exit")  # @UnusedVariable

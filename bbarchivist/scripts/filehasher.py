#!/usr/bin/env python3

import argparse  # parse arguments
import sys  # load arguments
import os  # path operations
from bbarchivist import filehashtools  # main program
from bbarchivist import bbconstants  # constants/versions
from bbarchivist import utilities  # input validation


def main():
    """
    Parse arguments from argparse/questionnaire.

    Invoke :func:`bbarchivist.filehashtools.verifier` with those arguments.
    """
    if len(sys.argv) > 1:
        parser = argparse.ArgumentParser(
            prog="bb-filehasher",
            description="""Applies hash functions to files.
Default: SHA-1, SHA-256, MD5""",
            epilog="http://github.com/thurask/bbarchivist")
        parser.add_argument(
            "-v",
            "--version",
            action="version",
            version="%(prog)s " +
            bbconstants.VERSION)
        parser.add_argument(
            "folder",
            help="Working directory, default is local",
            nargs="?",
            default=None)
        parser.add_argument(
            "-b",
            "--block",
            dest="blocksize",
            help="Blocksize (bytes), default = 16777216 (16MB)",
            default=16777216,
            type=utilities.positive_integer,
            metavar="INT")
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
            "--whirlpool",
            dest="whirlpool",
            help="Enable Whirlpool verification",
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
        hashgroup.add_argument(
            "-a",
            "--all",
            dest="all",
            help="Use all methods",
            action="store_true",
            default=False)
        hashgroup.add_argument(
            "-o",
            "--one-file",
            dest="onefile",
            help="One checksum file per folder",
            action="store_true",
            default=False)
        parser.set_defaults()
        args = parser.parse_args(sys.argv[1:])
        if args.folder is None:
            args.folder = os.getcwd()
        if args.all is True:
            args.adler32 = True
            args.crc32 = True
            args.sha1 = True
            args.sha224 = True
            args.sha256 = True
            args.sha384 = True
            args.sha512 = True
            args.md5 = True
            args.md4 = True
            args.ripemd160 = True
            args.whirlpool = True
        filehashtools.verifier(args.folder,
                               args.blocksize,
                               args.crc32,
                               args.adler32,
                               args.sha1,
                               args.sha224,
                               args.sha256,
                               args.sha384,
                               args.sha512,
                               args.md5,
                               args.md4,
                               args.ripemd160,
                               args.whirlpool,
                               not args.onefile)
    else:
        folder = os.getcwd()
        blocksize = 16777216
        crc32 = utilities.str2bool(input("CRC32?: "))
        adler32 = utilities.str2bool(input("ADLER32?: "))
        sha1 = utilities.str2bool(input("SHA-1?: "))
        sha224 = utilities.str2bool(input("SHA-224?: "))
        sha256 = utilities.str2bool(input("SHA-256?: "))
        sha384 = utilities.str2bool(input("SHA-384?: "))
        sha512 = utilities.str2bool(input("SHA-512?: "))
        md5 = utilities.str2bool(input("MD5?: "))
        md4 = utilities.str2bool(input("MD4?: "))
        ripemd160 = utilities.str2bool(input("RIPEMD160?: "))
        whirlpool = utilities.str2bool(input("WHIRLPOOL?: "))
        onefile = utilities.str2bool(input("USE ONE CHECKSUM FILE?: "))
        print(" ")
        filehashtools.verifier(
            folder,
            blocksize,
            crc32,
            adler32,
            sha1,
            sha224,
            sha256,
            sha384,
            sha512,
            md5,
            md4,
            ripemd160,
            whirlpool,
            not onefile)
        smeg = input("Press Enter to exit")
        if smeg or not smeg:
            raise SystemExit

if __name__ == "__main__":
    main()
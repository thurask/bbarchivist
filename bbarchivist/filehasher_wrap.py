#!/usr/bin/env python3

import argparse
import sys
import os
from . import hashwrapper
from . import bbconstants
from . import utilities


def main():
    """
    Parse arguments from argparse/questionnaire.

    Invoke `hashwrapper.verifier()` with those arguments.
    """
    if len(sys.argv) > 1:
        parser = argparse.ArgumentParser(
            prog="bb-verifier",
            description="""Applies various hash functions to a group of files.
Default: SHA-1, SHA-256, MD5""",
            epilog="http://github.com/thurask/bbarchivist")
        parser.add_argument(
            "-v",
            "--version",
            type=str.lower(),
            action="version",
            version="%(prog)s " +
            bbconstants._version)
        parser.add_argument(
            "folder",
            help="Working directory, default is local",
            nargs="?",
            default=os.getcwd())
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
            type=str.lower(),
            help="Enable CRC32 verification",
            action="store_true",
            default=False)
        hashgroup.add_argument(
            "--adler32",
            dest="adler32",
            type=str.lower(),
            help="Enable Adler-32 verification",
            action="store_true",
            default=False)
        hashgroup.add_argument(
            "--md4",
            dest="md4",
            type=str.lower(),
            help="Enable MD4 verification",
            action="store_true",
            default=False)
        hashgroup.add_argument(
            "--sha224",
            dest="sha224",
            type=str.lower(),
            help="Enable SHA-224 verification",
            action="store_true",
            default=False)
        hashgroup.add_argument(
            "--sha384",
            dest="sha384",
            type=str.lower(),
            help="Enable SHA-384 verification",
            action="store_true",
            default=False)
        hashgroup.add_argument(
            "--sha512",
            dest="sha512",
            type=str.lower(),
            help="Enable SHA-512 verification",
            action="store_true",
            default=False)
        hashgroup.add_argument(
            "--ripemd160",
            dest="ripemd160",
            type=str.lower(),
            help="Enable RIPEMD-160 verification",
            action="store_true",
            default=False)
        hashgroup.add_argument(
            "--whirlpool",
            dest="whirlpool",
            type=str.lower(),
            help="Enable Whirlpool verification",
            action="store_true",
            default=False)
        hashgroup.add_argument(
            "--no-sha1",
            dest="sha1",
            type=str.lower(),
            help="Disable SHA-1 verification",
            action="store_false",
            default=True)
        hashgroup.add_argument(
            "--no-sha256",
            dest="sha256",
            type=str.lower(),
            help="Disable SHA-256 verification",
            action="store_false",
            default=True)
        hashgroup.add_argument(
            "--no-md5",
            dest="md5",
            type=str.lower(),
            help="Disable MD5 verification",
            action="store_false",
            default=True)
        hashgroup.add_argument(
            "-a",
            "--all",
            dest="all",
            type=str.lower(),
            help="Use all methods",
            action="store_true",
            default=False)
        parser.set_defaults()
        args = parser.parse_args(sys.argv[1:])
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
        hashwrapper.verifier(args.folder,
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
                             args.whirlpool)
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
        print(" ")
        hashwrapper.verifier(
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
            whirlpool)
        smeg = input("Press Enter to exit")  # @UnusedVariable

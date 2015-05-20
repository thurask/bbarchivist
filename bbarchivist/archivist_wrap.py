#!/usr/bin/env python3

import sys  # load arguments
import argparse  # parse arguments
import os  # filesystem utils
import configparser  # read ini file
import getpass  # invisible password
from . import archivist  # main program
from . import bbconstants  # versions/constants
from . import utilities  # input validation


def main():
    """
    Parse arguments from argparse/questionnaire.

    Invoke :func:`bbarchivist.archivist.do_magic` with those arguments.
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
            bbconstants.VERSION)
        parser.add_argument(
                            "os",
                            help="OS version, 10.x.y.zzzz")
        parser.add_argument(
                            "radio",
                            help="Radio version, 10.x.y.zzzz",
                            nargs="?",
                            default=None)
        parser.add_argument(
                            "swrelease",
                            help="Software version, 10.x.y.zzzz",
                            nargs="?",
                            default=None)
        parser.add_argument(
            "-f",
            "--folder",
            dest="folder",
            help="Working folder",
            default=None,
            metavar="DIR")
        parser.add_argument(
            "-c",
            "--cap",
            type=utilities.file_exists,
            dest="cappath",
            help="Path to cap.exe",
            default=None,
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
        parser.add_argument(
            "-g",
            "--gpg",
            dest="gpg",
            help="Enable GPG signing. Set up GnuPG.",
            action="store_true",
            default=False)
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
            help="Compress with tar, LZMA (py3.3+)",
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
        if args.folder is None:
            args.folder = os.getcwd()
        if args.cappath is None:
            args.cappath = bbconstants.CAPLOCATION
        majver = sys.version_info[1]
        if majver <= 2:  # 3.2 and under
            if args.compmethod == "txz":
                args.compmethod = "zip"  # fallback
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
        if args.gpg is True:
            config = configparser.ConfigParser()
            homepath = os.path.expanduser("~")
            conffile = os.path.join(homepath, "bbarchivist.ini")
            config.read(conffile)
            gpgkey = config.get('gpgrunner', 'key', fallback=None)
            gpgpass = config.get('gpgrunner', 'pass', fallback=None)
            if gpgkey is None or gpgpass is None:
                print("NO PGP KEY FOUND")
                cont = utilities.str2bool(input("CONTINUE (Y/N)?: "))
                if cont:
                    gpgkey = input("PGP KEY (0x12345678): ")
                    gpgpass = getpass.getpass(prompt="PGP PASSPHRASE: ")
                    config['gpgrunner'] = {}
                    config['gpgrunner']['key'] = gpgkey
                    config['gpgrunner']['pass'] = gpgpass
                    with open(conffile, "w") as configfile:
                        config.write(configfile)
                else:
                    args.gpg = False
        else:
            gpgkey = None
            gpgpass = None
        archivist.do_magic(args.os, args.radio, args.swrelease,
                           args.folder, args.radloaders,
                           args.compress, args.delete, args.verify,
                           args.crc32, args.adler32, args.sha1,
                           args.sha224, args.sha256,
                           args.sha384, args.sha512, args.md5,
                           args.md4, args.ripemd160, args.whirlpool,
                           args.cappath, args.download,
                           args.extract, args.loaders,
                           args.signed, args.compmethod,
                           args.gpg, gpgkey, gpgpass, args.onefile)
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
                           False, bbconstants.CAPLOCATION, True,
                           True, True, True, "7z", False,
                           False, None, None, False)
    smeg = input("Press Enter to exit")  # @UnusedVariable

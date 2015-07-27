#!/usr/bin/env python3

import os  # filesystem read
import shutil  # directory read/write
import time  # time for downloader
import math  # rounding of floats
import sys  # load arguments
import argparse  # parse arguments
import configparser  # read ini file
import getpass  # invisible password
from bbarchivist import bbconstants  # versions/constants
from bbarchivist import utilities  # input validation
from bbarchivist import barutils  # file/folder work
from bbarchivist import networkutils  # download/lookup
from bbarchivist import loadergen  # cap, in Python
from bbarchivist import filehashtools  # hashes, GPG


def grab_args():
    """
    Parse arguments from argparse/questionnaire.

    Invoke :func:`archivist.archivist_main` with those arguments.
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
            "-ni",
            "--no-integrity",
            dest="integrity",
            help="Don't test bar files after download",
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
        if args.download is False:
            args.integrity = False
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
        archivist_main(args.os, args.radio, args.swrelease,
                       args.folder, args.radloaders,
                       args.compress, args.delete, args.verify,
                       args.crc32, args.adler32, args.sha1,
                       args.sha224, args.sha256,
                       args.sha384, args.sha512, args.md5,
                       args.md4, args.ripemd160, args.whirlpool,
                       args.cappath, args.download,
                       args.extract, args.loaders,
                       args.signed, args.compmethod,
                       args.gpg, gpgkey, gpgpass, args.onefile,
                       args.integrity)
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
        archivist_main(osversion, radioversion, softwareversion,
                       localdir, radios, compressed, deleted, hashed,
                       False, False, True, False, False,
                       False, False, True, False, False,
                       False, bbconstants.CAPLOCATION, True,
                       True, True, True, "7z", False,
                       False, None, None, False, True)
    smeg = input("Press Enter to exit")
    if smeg or not smeg:
        raise SystemExit


def archivist_main(osversion, radioversion=None, softwareversion=None,
                   localdir=None, radios=True, compressed=True, deleted=True,
                   hashed=True, crc32=False, adler32=False,
                   sha1=True, sha224=False, sha256=False,
                   sha384=False, sha512=False, md5=True,
                   md4=False, ripemd160=False, whirlpool=False,
                   cappath=None, download=True, extract=True,
                   loaders=True, signed=True, compmethod="7z",
                   gpg=False, gpgkey=None, gpgpass=None,
                   onefile=False, integrity=True):
    """
    Wrap around multi-autoloader creation code.
    Some combination of creating, downloading, hashing,
    compressing and moving autoloaders.

    :param osversion: OS version, 10.x.y.zzzz.
    :type osversion: str

    :param radioversion: Radio version, 10.x.y.zzzz. Can be guessed.
    :type radioversion: str

    :param softwareversion: Software release, 10.x.y.zzzz. Can be guessed.
    :type softwareversion: str

    :param localdir: Working directory. Local by default.
    :type localdir: str

    :param radios: Whether to create radio autoloaders. True by default.
    :type radios: bool

    :param compressed: Whether to compress files. True by default.
    :type compressed: bool

    :param deleted: Whether to delete uncompressed files. True by default.
    :type deleted: bool

    :param hashed: Whether to hash files. True by default.
    :type hashed: bool

    :param crc32: Whether to use CRC32. False by default.
    :type crc32: bool

    :param adler32: Whether to use Adler-32. False by default.
    :type adler32: bool

    :param sha1: Whether to use SHA-1. True by default.
    :type sha1: bool

    :param sha224: Whether to use SHA-224. False by default.
    :type sha224: bool

    :param sha256: Whether to use SHA-256. False by default.
    :type sha256: bool

    :param sha384: Whether to use SHA-384. False by default.
    :type sha384: bool

    :param sha512: Whether to use SHA-512. False by default.
    :type sha512: bool

    :param md5: Whether to use MD5. True by default.
    :type md5: bool

    :param md4: Whether to use MD4. False by default.
    :type md4: bool

    :param ripemd160: Whether to use RIPEMD160. False by default.
    :type ripemd160: bool

    :param whirlpool: Whether to use Whirlpool. False by default.
    :type whirlpool: bool

    :param cappath: Path to cap.exe. Default is cap supplied with package.
    :type cappath: str

    :param download: Whether to download bar files. True by default.
    :type download: bool

    :param extract: Whether to extract bar files. True by default.
    :type extract: bool

    :param loaders: Whether to create autoloaders. True by default.
    :type loaders: bool

    :param signed: Whether to delete signed files. True by default.
    :type signed: bool

    :param compmethod: Compression method. Default is "7z" with fallback "zip".
    :type compmethod: str

    :param gpg: Whether to use GnuPG verification. False by default.
    :type gpg: bool

    :param gpgkey: Key to use with GnuPG verification.
    :type gpgkey: str

    :param gpgpass: Passphrase to use with GnuPG verification.
    :type gpgpass: str

    :param onefile: Whether to use one checksum file. False by default.
    :type onefile: bool

    :param integrity: Whether to test downloaded bar files. True by default.
    :type integrity: bool
    """
    starttime = time.clock()
    swchecked = False  # if we checked sw release already
    if radioversion is None:
        radioversion = utilities.version_incrementer(osversion, 1)
    if softwareversion is None:
        serv = bbconstants.SERVERS["p"]
        softwareversion = networkutils.software_release_lookup(osversion, serv)
        if softwareversion == "SR not in system":
            print("SOFTWARE RELEASE NOT FOUND")
            cont = utilities.str2bool(input("INPUT MANUALLY? Y/N: "))
            if cont:
                softwareversion = input("SOFTWARE RELEASE: ")
                swchecked = False
            else:
                print("\nEXITING...")
                raise SystemExit  # bye bye
        else:
            swchecked = True
    if cappath is None:
        cappath = utilities.grab_cap()
    if localdir is None:
        localdir = os.getcwd()
    print("~~~ARCHIVIST VERSION", bbconstants.VERSION + "~~~")
    print("OS VERSION:", osversion)
    print("RADIO VERSION:", radioversion)
    print("SOFTWARE VERSION:", softwareversion)

    if compmethod == "7z":
        print("\nCHECKING PRESENCE OF 7ZIP...")
        psz = utilities.prep_seven_zip()
        if psz:
            print("7ZIP OK")
            szexe = utilities.get_seven_zip()
        else:
            szexe = ""
            print("7ZIP NOT FOUND")
            cont = utilities.str2bool(input("CONTINUE? Y/N "))
            if cont:
                print("FALLING BACK TO ZIP...")
                compmethod = "zip"
            else:
                print("\nEXITING...")
                raise SystemExit  # bye bye
    else:
        szexe = ""

    baseurl = networkutils.create_base_url(softwareversion)
    splitos = osversion.split(".")
    splitos = [int(i) for i in splitos]

    # List of OS urls
    osurls = [baseurl + "/winchester.factory_sfi.desktop-" +
              osversion + "-nto+armle-v7+signed.bar",
              baseurl + "/qc8960.factory_sfi.desktop-" +
              osversion + "-nto+armle-v7+signed.bar",
              baseurl + "/qc8960.factory_sfi.desktop-" +
              osversion + "-nto+armle-v7+signed.bar",
              baseurl + "/qc8974.factory_sfi.desktop-" +
              osversion + "-nto+armle-v7+signed.bar"]
    if (splitos[1] >= 4) or (splitos[1] == 3 and splitos[2] >= 1):  # 10.3.1+
        osurls[2] = osurls[2].replace("qc8960.factory_sfi",
                                      "qc8960.factory_sfi_hybrid_qc8x30")
        osurls[3] = osurls[3].replace("qc8974.factory_sfi",
                                      "qc8960.factory_sfi_hybrid_qc8974")
    if not networkutils.availability(osurls[1]):
        osurls[1] = osurls[1].replace("qc8960.factory_sfi",
                                      "qc8960.verizon_sfi")  # verizon fallback
    osurls = list(set(osurls))  # pop duplicates
    # List of radio urls
    radiourls = [baseurl + "/m5730-" + radioversion +
                 "-nto+armle-v7+signed.bar",
                 baseurl + "/qc8960-" + radioversion +
                 "-nto+armle-v7+signed.bar",
                 baseurl + "/qc8960.omadm-" + radioversion +
                 "-nto+armle-v7+signed.bar",
                 baseurl + "/qc8960.wtr-" + radioversion +
                 "-nto+armle-v7+signed.bar",
                 baseurl + "/qc8960.wtr5-" + radioversion +
                 "-nto+armle-v7+signed.bar",
                 baseurl + "/qc8930.wtr5-" + radioversion +
                 "-nto+armle-v7+signed.bar",
                 baseurl + "/qc8974.wtr2-" + radioversion +
                 "-nto+armle-v7+signed.bar"]

    # Check availability of software release
    print("\nCHECKING SOFTWARE RELEASE AVAILABILITY...")
    if not swchecked:
        avlty = networkutils.availability(baseurl)
        if avlty:
            print("\nSOFTWARE RELEASE", softwareversion, "EXISTS")
        else:
            print("\nSOFTWARE RELEASE", softwareversion, "NOT FOUND")
            cont = utilities.str2bool(input("CONTINUE? Y/N: "))
            if cont:
                pass
            else:
                print("\nEXITING...")
                raise SystemExit
    else:
        print("\nSOFTWARE RELEASE", softwareversion, "EXISTS")

    for url in radiourls:
        radav = networkutils.availability(url)
        if radav:
            break
    else:
        print("RADIO VERSION NOT FOUND")
        cont = utilities.str2bool(input("INPUT MANUALLY? Y/N: "))
        if cont:
            rad2 = input("RADIO VERSION: ")
            radiourls = [url.replace(radioversion, rad2) for url in radiourls]
        else:
            going = utilities.str2bool(input("KEEP GOING? Y/N: "))
            if going:
                pass
            else:
                print("\nEXITING...")
                raise SystemExit

    # Make dirs
    if not os.path.exists(localdir):
        os.makedirs(localdir)

    if not os.path.exists(os.path.join(localdir, 'bars')):
        os.mkdir(os.path.join(localdir, 'bars'))
    bardir = os.path.join(localdir, 'bars')
    if not os.path.exists(os.path.join(bardir, osversion)):
        os.mkdir(os.path.join(bardir, osversion))
    bardir_os = os.path.join(bardir, osversion)
    if not os.path.exists(os.path.join(bardir, radioversion)):
        os.mkdir(os.path.join(bardir, radioversion))
    bardir_radio = os.path.join(bardir, radioversion)

    if not os.path.exists(os.path.join(localdir, 'loaders')):
        os.mkdir(os.path.join(localdir, 'loaders'))
    loaderdir = os.path.join(localdir, 'loaders')
    if not os.path.exists(os.path.join(loaderdir, osversion)):
        os.mkdir(os.path.join(loaderdir, osversion))
    loaderdir_os = os.path.join(loaderdir, osversion)
    if not os.path.exists(os.path.join(loaderdir, radioversion)):
        os.mkdir(os.path.join(loaderdir, radioversion))
    loaderdir_radio = os.path.join(loaderdir, radioversion)

    if not os.path.exists(os.path.join(localdir, 'zipped')):
        os.mkdir(os.path.join(localdir, 'zipped'))
    zipdir = os.path.join(localdir, 'zipped')
    if not os.path.exists(os.path.join(zipdir, osversion)):
        os.mkdir(os.path.join(zipdir, osversion))
    zipdir_os = os.path.join(zipdir, osversion)
    if not os.path.exists(os.path.join(zipdir, radioversion)):
        os.mkdir(os.path.join(zipdir, radioversion))
    zipdir_radio = os.path.join(zipdir, radioversion)

    # Download files
    if download:
        print("\nBEGIN DOWNLOADING...")
        networkutils.download_bootstrap(radiourls+osurls, localdir, workers=3)

    # Test bar files
    if integrity:
        brokenlist = []
        print("\nTESTING...")
        for file in os.listdir(localdir):
            if file.endswith(".bar"):
                print("TESTING:", file)
                thepath = os.path.abspath(os.path.join(localdir, file))
                brokens = barutils.bar_tester(thepath)
                if brokens is not None:
                    os.remove(brokens)
                    for url in radiourls+osurls:
                        if brokens in url:
                            brokenlist.append(url)
        if brokenlist:
            print("\nREDOWNLOADING BROKEN FILES...")
            if len(brokenlist) > 5:
                workers = 5
            else:
                workers = len(brokenlist)
            networkutils.download_bootstrap(brokenlist,
                                            outdir=localdir,
                                            lazy=False,
                                            workers=workers)
            for file in os.listdir(localdir):
                if file.endswith(".bar"):
                    thepath = os.path.abspath(os.path.join(localdir, file))
                    brokens = barutils.bar_tester(thepath)
                    if brokens is not None:
                        print(file, "STILL BROKEN")
                        raise SystemExit
        else:
            print("\nALL FILES DOWNLOADED OK")

    # Extract bar files
    if extract:
        print("\nEXTRACTING...")
        barutils.extract_bars(localdir)

    # Test signed files
    if integrity:
        print("\nTESTING...")
        for file in os.listdir(localdir):
            if file.endswith(".bar"):
                print("TESTING:", file)
                signname, signhash = barutils.retrieve_sha512(file)
                sha512ver = barutils.verify_sha512(signname, signhash)
                if not sha512ver:
                    print("{0} IS BROKEN".format((file)))
                    raise SystemExit
        print("\nALL FILES EXTRACTED OK")

    # Move bar files
    print("\nMOVING .bar FILES...")
    for files in os.listdir(localdir):
        if files.endswith(".bar"):
            print("MOVING: " + files)
            bardest_os = os.path.join(bardir_os, files)
            bardest_radio = os.path.join(bardir_radio, files)
            # even the fattest radio is less than 90MB
            if os.path.getsize(os.path.join(localdir, files)) > 90000000:
                try:
                    shutil.move(os.path.join(localdir, files), bardir_os)
                except shutil.Error:
                    os.remove(bardest_os)
            else:
                try:
                    shutil.move(os.path.join(localdir, files), bardir_radio)
                except shutil.Error:
                    os.remove(bardest_radio)

    # Create loaders
    if loaders:
        print("\nGENERATING LOADERS...")
        loadergen.generate_loaders(osversion,
                                   radioversion,
                                   radios,
                                   cappath,
                                   localdir)

    # Remove .signed files
    if signed:
        print("\nREMOVING .signed FILES...")
        for file in os.listdir(localdir):
            if os.path.join(localdir, file).endswith(".signed"):
                print("REMOVING: " + file)
                os.remove(os.path.join(localdir, file))

    # If compression = true, compress
    if compressed:
        print("\nCOMPRESSING...")
        barutils.compress(localdir, compmethod, szexe)
    else:
        pass

    if integrity:
        print("\nTESTING...")
        barutils.verify(localdir, szexe)

    # Move zipped/unzipped loaders
    print("\nMOVING...")
    barutils.move_loaders(localdir,
                          loaderdir_os, loaderdir_radio,
                          zipdir_os, zipdir_radio)

    # Get hashes (if specified)
    if hashed:
        print("\nHASHING LOADERS...")
        print(
            "ADLER32:",
            adler32,
            "CRC32:",
            crc32,
            "MD4:",
            md4,
            "\nMD5:",
            md5,
            "SHA1:",
            sha1,
            "SHA224:",
            sha224,
            "\nSHA256:",
            sha256,
            "SHA384:",
            sha384,
            "SHA512:",
            sha512,
            "\nRIPEMD160:",
            ripemd160,
            "WHIRLPOOL:",
            whirlpool,
            "\n")
        blocksize = 32 * 1024 * 1024
        if compressed:
            filehashtools.verifier(
                zipdir_os,
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
            if radios:
                filehashtools.verifier(
                    zipdir_radio,
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
        if not deleted:
            filehashtools.verifier(
                loaderdir_os,
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
            if radios:
                filehashtools.verifier(
                    loaderdir_radio,
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
    if gpg:
        if gpgpass is not None and gpgkey is not None:
            print("\nVERIFYING LOADERS...")
            print("KEY:", gpgkey)
            if compressed:
                filehashtools.gpgrunner(
                    zipdir_os,
                    gpgkey,
                    gpgpass,
                    True)
                if radios:
                    filehashtools.gpgrunner(
                        zipdir_radio,
                        gpgkey,
                        gpgpass,
                        True)
            if not deleted:
                filehashtools.gpgrunner(
                    loaderdir_os,
                    gpgkey,
                    gpgpass,
                    True)
                if radios:
                    filehashtools.gpgrunner(
                        loaderdir_radio,
                        gpgkey,
                        gpgpass,
                        True)
        else:
            print("\nNO KEY AND/OR PASS PROVIDED!")

    # Remove uncompressed loaders (if specified)
    if deleted:
        print("\nDELETING UNCOMPRESSED LOADERS...")
        if radios:
            shutil.rmtree(loaderdir_radio)
        if loaders:
            shutil.rmtree(loaderdir_os)

    # Delete empty folders
    print("\nREMOVING EMPTY FOLDERS...")
    barutils.remove_empty_folders(localdir)

    print("\nFINISHED!")
    endtime = time.clock() - starttime
    endtime_proper = math.ceil(endtime * 100) / 100
    print("\nCompleted in " + str(endtime_proper) + " seconds\n")

if __name__ == "__main__":
    grab_args()

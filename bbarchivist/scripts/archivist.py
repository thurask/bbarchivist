#!/usr/bin/env python3
"""Download bar files, create autoloaders."""

import os  # filesystem read
import sys  # load arguments
from bbarchivist import scriptutils  # script stuff
from bbarchivist import bbconstants  # versions/constants
from bbarchivist import utilities  # input validation
from bbarchivist import barutils  # file/folder work
from bbarchivist import networkutils  # download/lookup
from bbarchivist import loadergen  # cap, in Python
from bbarchivist import filehashtools  # hashes, GPG

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "Copyright 2015 Thurask"


@utilities.timer
def grab_args():
    """
    Parse arguments from argparse/questionnaire.

    Invoke :func:`archivist.archivist_main` with those arguments.
    """
    if len(sys.argv) > 1:
        parser = scriptutils.default_parser("bb-archivist",
                                            "Create many autoloaders")
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
        if not getattr(sys, 'frozen', False):
            parser.add_argument(
                "-g",
                "--gpg",
                dest="gpg",
                help="Enable GPG signing. Set up GnuPG.",
                action="store_true",
                default=False)
        parser.add_argument(
            "-r",
            "--radiosw",
            dest="altsw",
            metavar="SW",
            help="Radio software version; use without software to guess",
            nargs="?",
            const="checkme",
            default=None)
        parser.add_argument(
            "-m",
            "--method",
            dest="method",
            metavar="METHOD",
            help="Compression method",
            nargs="?",
            type=utilities.valid_method,
            default=None)
        parser.add_argument(
            "-c",
            "--core",
            dest="core",
            help="Make core/radio loaders",
            default=False,
            action="store_true")
        parser.set_defaults(compmethod="7z")
        args = parser.parse_args(sys.argv[1:])
        if args.folder is None:
            args.folder = os.getcwd()
        if getattr(sys, 'frozen', False):
            args.gpg = False
            hashdict = filehashtools.verifier_config_loader(os.getcwd())
            args.method = "7z"
        else:
            hashdict = filehashtools.verifier_config_loader()
        filehashtools.verifier_config_writer(hashdict)
        if args.method is None:
            compmethod = barutils.compress_config_loader()
            barutils.compress_config_writer(compmethod)
        else:
            compmethod = args.method
        archivist_main(args.os, args.radio, args.swrelease,
                       args.folder, args.radloaders,
                       args.compress, args.delete, args.verify,
                       hashdict, args.download,
                       args.extract, args.signed, compmethod,
                       args.gpg, args.integrity, args.altsw, args.core)
    else:
        questionnaire()


def questionnaire():
    """
    Questions to ask if no arguments given.
    """
    localdir = os.getcwd()
    osversion = input("OS VERSION: ")
    radioversion = input("RADIO VERSION: ")
    softwareversion = input("SOFTWARE RELEASE: ")
    altcheck = utilities.s2b(input("HYBRID AUTOLOADER (Y/N)?: "))
    if altcheck:
        altsw = input("RADIO SOFTWARE RELEASE (PRESS ENTER TO GUESS): ")
        if not altsw:
            altsw = "checkme"
    else:
        altsw = None
    radios = utilities.s2b(input("CREATE RADIO LOADERS? Y/N: "))
    compressed = utilities.s2b(input("COMPRESS LOADERS? Y/N: "))
    if compressed:
        deleted = utilities.s2b(input("DELETE UNCOMPRESSED? Y/N: "))
    else:
        deleted = False
    hashed = utilities.s2b(input("GENERATE HASHES? Y/N: "))
    if getattr(sys, 'frozen', False):
        args.gpg = False
        hashdict = filehashtools.verifier_config_loader(os.getcwd())
        compmethod = "7z"
    else:
        hashdict = filehashtools.verifier_config_loader()
        filehashtools.verifier_config_writer(hashdict)
        compmethod = barutils.compress_config_loader()
    download = True
    extract = True
    signed = True
    gpg = False
    integrity = True
    altsw = None
    core = False
    print(" ")
    archivist_main(osversion, radioversion, softwareversion,
                   localdir, radios, compressed, deleted, hashed,
                   hashdict, download,
                   extract, signed, compmethod, gpg,
                   integrity, altsw, core)


def archivist_main(osversion, radioversion=None, softwareversion=None,
                   localdir=None, radios=True, compressed=True, deleted=True,
                   hashed=True, hashdict=None, download=True,
                   extract=True, signed=True, compmethod="7z",
                   gpg=False, integrity=True, altsw=None,
                   core=False):
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

    :param hashdict: Dictionary of hash rules, in ~\bbarchivist.ini.
    :type hashdict: dict({str: bool})

    :param download: Whether to download bar files. True by default.
    :type download: bool

    :param extract: Whether to extract bar files. True by default.
    :type extract: bool

    :param signed: Whether to delete signed files. True by default.
    :type signed: bool

    :param compmethod: Compression method. Default is "7z", fallback "zip".
    :type compmethod: str

    :param gpg: Whether to use GnuPG verification. False by default.
    :type gpg: bool

    :param integrity: Whether to test downloaded bar files. True by default.
    :type integrity: bool

    :param altsw: Radio software release, if not the same as OS.
    :type altsw: str

    :param core: Whether to create a core/radio loader. Default is false.
    :type core: bool
    """
    swchecked = False  # if we checked sw release already
    if altsw:
        altchecked = False
    radioversion = scriptutils.return_radio_version(osversion, radioversion)
    softwareversion, swchecked = scriptutils.return_sw_checked(softwareversion,
                                                               osversion)
    if altsw == "checkme":
        altsw, altchecked = scriptutils.return_radio_sw_checked(altsw,
                                                                radioversion)
    if localdir is None:
        localdir = os.getcwd()
    if hashdict is None:
        hashdict = filehashtools.verifier_config_loader()
        filehashtools.verifier_config_writer(hashdict)
    print("~~~ARCHIVIST VERSION", bbconstants.VERSION + "~~~")
    print("OS VERSION:", osversion)
    print("OS SOFTWARE VERSION:", softwareversion)
    print("RADIO VERSION:", radioversion)
    if altsw is not None:
        print("RADIO SOFTWARE VERSION:", altsw)

    # Generate download URLs
    baseurl = networkutils.create_base_url(softwareversion)
    if altsw:
        alturl = networkutils.create_base_url(altsw)
    osurls, radiourls, cores = utilities.generate_urls(baseurl, osversion,
                                                       radioversion, True)
    if core:
        osurls = cores
    else:
        del cores
    for idx, url in enumerate(osurls):
        if "qc8960.factory_sfi" in url:
            vzwurl = url
            vzwindex = idx
            break
    if not networkutils.availability(vzwurl):
        osurls[vzwindex] = osurls[vzwindex].replace("qc8960.factory_sfi",
                                                    "qc8960.verizon_sfi")
    osurls = list(set(osurls))  # pop duplicates
    if altsw:
        radiourls2 = [x.replace(baseurl, alturl) for x in radiourls]
        radiourls = radiourls2
        del radiourls2

    # Check availability of software releases
    scriptutils.check_sw(baseurl, softwareversion, swchecked)
    if altsw:
        scriptutils.check_radio_sw(alturl, altsw, altchecked)

    # Check availability of OS, radio
    scriptutils.check_os_bulk(osurls)
    radiourls, radioversion = scriptutils.check_radio_bulk(radiourls,
                                                           radioversion)

    # Get 7z executable
    compmethod, szexe = scriptutils.get_sz_executable(compmethod)

    # Make dirs
    bd_o, bd_r, ld_o, ld_r, zd_o, zd_r = barutils.make_dirs(localdir,
                                                            osversion,
                                                            radioversion)

    # Download files
    if download:
        print("BEGIN DOWNLOADING...")
        networkutils.download_bootstrap(radiourls+osurls,
                                        localdir,
                                        workers=3)
        print("ALL FILES DOWNLOADED")

    # Test bar files
    if integrity:
        urllist = osurls+radiourls
        scriptutils.test_bar_files(localdir, urllist, download)

    # Extract bar files
    if extract:
        print("EXTRACTING...")
        barutils.extract_bars(localdir)

    # Test signed files
    if integrity:
        scriptutils.test_signed_files(localdir)

    # Move bar files
    print("MOVING BAR FILES...")
    barutils.move_bars(localdir, bd_o, bd_r)

    # Create loaders
    print("GENERATING LOADERS...")
    altradio = (altsw is not None)
    loadergen.generate_loaders(osversion,
                               radioversion,
                               radios,
                               localdir,
                               altradio,
                               core)

    # Test loader files
    if integrity:
        scriptutils.test_loader_files(localdir)

    # Remove .signed files
    if signed:
        print("REMOVING SIGNED FILES...")
        barutils.remove_signed_files(localdir)

    # If compression = true, compress
    if compressed:
        print("COMPRESSING...")
        barutils.compress(localdir, compmethod, szexe, True)

    if integrity and compressed:
        print("TESTING ARCHIVES...")
        barutils.verify(localdir, compmethod, szexe, True)

    # Move zipped/unzipped loaders
    print("MOVING LOADERS...")
    barutils.move_loaders(localdir,
                          ld_o, ld_r,
                          zd_o, zd_r)

    # Get hashes (if specified)
    if hashed:
        print("HASHING LOADERS...")
        if compressed:
            filehashtools.verifier(
                zd_o,
                hashdict)
            if radios:
                filehashtools.verifier(
                    zd_r,
                    hashdict)
        if not deleted:
            filehashtools.verifier(
                ld_o,
                hashdict)
            if radios:
                filehashtools.verifier(
                    ld_r,
                    hashdict)
    if gpg:
        gpgkey, gpgpass = scriptutils.verify_gpg_credentials()
        if gpgpass is not None and gpgkey is not None:
            print("VERIFYING LOADERS...")
            print("KEY:", gpgkey)
            if compressed:
                filehashtools.gpgrunner(
                    zd_o,
                    gpgkey,
                    gpgpass,
                    True)
                if radios:
                    filehashtools.gpgrunner(
                        zd_r,
                        gpgkey,
                        gpgpass,
                        True)
            if not deleted:
                filehashtools.gpgrunner(
                    ld_o,
                    gpgkey,
                    gpgpass,
                    True)
                if radios:
                    filehashtools.gpgrunner(
                        ld_r,
                        gpgkey,
                        gpgpass,
                        True)

    # Remove uncompressed loaders (if specified)
    if deleted:
        print("DELETING UNCOMPRESSED LOADERS...")
        barutils.remove_unpacked_loaders(ld_o, ld_r, radios)

    # Delete empty folders
    print("REMOVING EMPTY FOLDERS...")
    barutils.remove_empty_folders(localdir)

    print("\nFINISHED!")


if __name__ == "__main__":
    grab_args()
    scriptutils.enter_to_exit(False)

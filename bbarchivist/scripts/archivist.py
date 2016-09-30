#!/usr/bin/env python3
"""Download bar files, create autoloaders."""

import os  # filesystem read
import sys  # load arguments
from bbarchivist import scriptutils  # script stuff
from bbarchivist import utilities  # input validation
from bbarchivist import decorators  # timer
from bbarchivist import barutils  # file/folder work
from bbarchivist import archiveutils  # archive work
from bbarchivist import networkutils  # download/lookup
from bbarchivist import loadergen  # cap, in Python
from bbarchivist import hashutils  # hashes, GPG

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "Copyright 2015-2016 Thurask"


@decorators.timer
def grab_args():
    """
    Parse arguments from argparse/questionnaire.

    Invoke :func:`archivist.archivist_main` with those arguments.
    """
    if len(sys.argv) > 1:
        parser = scriptutils.default_parser("bb-archivist", "Create many autoloaders",
                                            ("folder", "osr"))
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
        parser.add_argument(
            "-o",
            "--old-style",
            dest="oldstyle",
            help="Make old-style checksum files",
            default=False,
            action="store_true")
        parser.set_defaults(compmethod="7z")
        args = parser.parse_args(sys.argv[1:])
        if args.folder is None:
            args.folder = os.getcwd()
        if getattr(sys, 'frozen', False):
            args.gpg = False
            hashdict = hashutils.verifier_config_loader(os.getcwd())
            args.method = "7z"
        else:
            hashdict = hashutils.verifier_config_loader()
        hashutils.verifier_config_writer(hashdict)
        if args.method is None:
            compmethod = archiveutils.compress_config_loader()
            archiveutils.compress_config_writer(compmethod)
        else:
            compmethod = args.method
        archivist_main(args.os, args.radio, args.swrelease,
                       os.path.abspath(args.folder), args.radloaders,
                       args.compress, args.delete, args.verify,
                       hashdict, args.download,
                       args.extract, args.signed, compmethod, args.gpg,
                       args.integrity, args.altsw, args.core, args.oldstyle)
    else:
        questionnaire()


def questionnaire():
    """
    Questions to ask if no arguments given.
    """
    localdir = os.getcwd()
    osversion = input("OS VERSION (REQUIRED): ")
    radioversion = input("RADIO VERSION (PRESS ENTER TO GUESS): ")
    radioversion = None if not radioversion else radioversion
    softwareversion = input("OS SOFTWARE RELEASE (PRESS ENTER TO GUESS): ")
    softwareversion = None if not softwareversion else softwareversion
    altcheck = utilities.s2b(input("USING ALTERNATE RADIO (Y/N)?: "))
    if altcheck:
        altsw = input("RADIO SOFTWARE RELEASE (PRESS ENTER TO GUESS): ")
        if not altsw:
            altsw = "checkme"
    else:
        altsw = None
    radios = utilities.s2b(input("CREATE RADIO LOADERS (Y/N)?: "))
    compressed = utilities.s2b(input("COMPRESS LOADERS (Y/N)?: "))
    deleted = utilities.s2b(input("DELETE UNCOMPRESSED LOADERS (Y/N)?: ")) if compressed else False
    hashed = utilities.s2b(input("GENERATE HASHES (Y/N)?: "))
    if getattr(sys, 'frozen', False):
        hashdict = hashutils.verifier_config_loader(os.getcwd())
        compmethod = "7z"
    else:
        hashdict = hashutils.verifier_config_loader()
        hashutils.verifier_config_writer(hashdict)
        compmethod = archiveutils.compress_config_loader()
    print(" ")
    archivist_main(osversion, radioversion, softwareversion,
                   localdir, radios, compressed, deleted, hashed,
                   hashdict, download=True, extract=True, signed=True,
                   compmethod=compmethod, gpg=False, integrity=True,
                   altsw=None, core=False, oldstyle=False)


def archivist_checksw(baseurl, softwareversion, swchecked):
    """
    Check availability of software releases.

    :param baseurl: Base URL for download links.
    :type baseurl: str

    :param softwareversion: Software release, 10.x.y.zzzz. Can be guessed.
    :type softwareversion: str

    :param swchecked: If we checked the sw release already.
    :type swchecked: bool
    """
    scriptutils.check_sw(baseurl, softwareversion, swchecked)


def archivist_download(download, osurls, radiourls, localdir):
    """
    Download function.

    :param download: Whether to download bar files. True by default.
    :type download: bool

    :param osurls: OS file list.
    :type osurls: list(str)

    :param radiourls: Radio file list.
    :type radiourls: list(str)

    :param localdir: Working directory. Local by default.
    :type localdir: str
    """
    if download:
        print("BEGIN DOWNLOADING...")
        networkutils.download_bootstrap(radiourls + osurls, localdir, 3)
        print("ALL FILES DOWNLOADED")


def archivist_integritybars(integrity, osurls, radiourls, localdir):
    """
    Check integrity of bar files, redownload if necessary.

    :param integrity: Whether to test downloaded files. True by default.
    :type integrity: bool

    :param osurls: OS file list.
    :type osurls: list(str)

    :param radiourls: Radio file list.
    :type radiourls: list(str)
    """
    if integrity:
        urllist = osurls + radiourls
        scriptutils.test_bar_files(localdir, urllist)


def archivist_extractbars(extract, localdir):
    """
    Extract signed files from bar files.

    :param extract: Whether to extract bar files. True by default.
    :type extract: bool

    :param localdir: Working directory. Local by default.
    :type localdir: str
    """
    if extract:
        print("EXTRACTING...")
        barutils.extract_bars(localdir)


def archivist_integritysigned(integrity, localdir):
    """
    Check integrity of signed files.

    :param integrity: Whether to test downloaded files. True by default.
    :type integrity: bool

    :param localdir: Working directory. Local by default.
    :type localdir: str
    """
    if integrity:
        scriptutils.test_signed_files(localdir)


def archivist_movebars(dirs, localdir):
    """
    Move bar files.

    :param dirs: List of OS/radio bar/loader/zipped folders.
    :type dirs: list(str)

    :param localdir: Working directory. Local by default.
    :type localdir: str
    """
    print("MOVING BAR FILES...")
    barutils.move_bars(localdir, dirs[0], dirs[1])


def archivist_generateloaders(osversion, radioversion, radios, localdir, altsw, core):
    """
    Generate loaders.

    :param osversion: OS version, 10.x.y.zzzz. Required.
    :type osversion: str

    :param radioversion: Radio version, 10.x.y.zzzz. Can be guessed.
    :type radioversion: str

    :param radios: Whether to create radio autoloaders. True by default.
    :type radios: bool

    :param localdir: Working directory. Local by default.
    :type localdir: str

    :param altsw: Radio software release, if not the same as OS.
    :type altsw: str

    :param core: Whether to create a core/radio loader. Default is false.
    :type core: bool
    """
    print("GENERATING LOADERS...")
    altradio = altsw is not None
    loadergen.generate_loaders(osversion, radioversion, radios, localdir, altradio, core)


def archivist_integrityloaders(integrity, localdir):
    """
    Check integrity of build loaders.

    :param integrity: Whether to test downloaded files. True by default.
    :type integrity: bool

    :param localdir: Working directory. Local by default.
    :type localdir: str
    """
    if integrity:
        scriptutils.test_loader_files(localdir)


def archivist_removesigned(signed, localdir):
    """
    Remove signed files.

    :param signed: Whether to delete signed files. True by default.
    :type signed: bool

    :param localdir: Working directory. Local by default.
    :type localdir: str
    """
    if signed:
        print("REMOVING SIGNED FILES...")
        barutils.remove_signed_files(localdir)


def archivist_compressor(compressed, integrity, localdir, compmethod, szexe):
    """
    Compress and optionally verify loaders.

    :param compressed: Whether to compress files. True by default.
    :type compressed: bool

    :param integrity: Whether to test downloaded files. True by default.
    :type integrity: bool

    :param localdir: Working directory. Local by default.
    :type localdir: str

    :param compmethod: Compression method. Default is "7z", fallback "zip".
    :type compmethod: str

    :param szexe: Path to 7z executable.
    :type szexe: str
    """
    if compressed:
        print("COMPRESSING...")
        archiveutils.compress(localdir, compmethod, szexe, True)
        if integrity:
            print("TESTING ARCHIVES...")
            archiveutils.verify(localdir, compmethod, szexe, True)


def archivist_moveloaders(dirs, localdir):
    """
    Move loaders.

    :param dirs: List of OS/radio bar/loader/zipped folders.
    :type dirs: list(str)

    :param localdir: Working directory. Local by default.
    :type localdir: str
    """
    print("MOVING LOADERS...")
    barutils.move_loaders(localdir, dirs[2], dirs[3], dirs[4], dirs[5])


def archivist_gethashes(dirs, hashed, compressed, deleted, radios, osversion, radioversion, softwareversion, oldstyle):
    """
    Make new-style info files.

    :param dirs: List of OS/radio bar/loader/zipped folders.
    :type dirs: list(str)

    :param hashed: Whether to hash files. True by default.
    :type hashed: bool

    :param compressed: Whether to compress files. True by default.
    :type compressed: bool

    :param deleted: Whether to delete uncompressed files. True by default.
    :type deleted: bool

    :param radios: Whether to create radio autoloaders. True by default.
    :type radios: bool

    :param osversion: OS version, 10.x.y.zzzz. Required.
    :type osversion: str

    :param radioversion: Radio version, 10.x.y.zzzz. Can be guessed.
    :type radioversion: str

    :param softwareversion: Software release, 10.x.y.zzzz. Can be guessed.
    :type softwareversion: str

    :param oldstyle: Whether to make old-style checksum files. Default is false.
    :type oldstyle: bool
    """
    if hashed and not oldstyle:
        scriptutils.bulk_info(dirs, osversion, compressed, deleted, radios,
                                  radioversion, softwareversion)

def archivist_getoldhashes(dirs, hashed, compressed, deleted, radios, hashdict, oldstyle):
    """
    Make old-style checksum files.

    :param dirs: List of OS/radio bar/loader/zipped folders.
    :type dirs: list(str)

    :param hashed: Whether to hash files. True by default.
    :type hashed: bool

    :param compressed: Whether to compress files. True by default.
    :type compressed: bool

    :param deleted: Whether to delete uncompressed files. True by default.
    :type deleted: bool

    :param radios: Whether to create radio autoloaders. True by default.
    :type radios: bool

    :param hashdict: Dictionary of hash rules, in ~\bbarchivist.ini.
    :type hashdict: dict({str: bool})

    :param oldstyle: Whether to make old-style checksum files. Default is false.
    :type oldstyle: bool
    """
    if hashed and oldstyle:
        scriptutils.bulk_hash(dirs, compressed, deleted, radios, hashdict)


def archivist_gpg(gpg, dirs, compressed, deleted, radios):
    """
    GPG-sign everything.

    :param gpg: Whether to use GnuPG verification. False by default.
    :type gpg: bool

    :param dirs: List of OS/radio bar/loader/zipped folders.
    :type dirs: list(str)

    :param compressed: Whether to compress files. True by default.
    :type compressed: bool

    :param deleted: Whether to delete uncompressed files. True by default.
    :type deleted: bool

    :param radios: Whether to create radio autoloaders. True by default.
    :type radios: bool
    """
    if gpg:
        scriptutils.bulk_verify(dirs, compressed, deleted, radios)


def archivist_deleteuncompressed(dirs, deleted, radios):
    """
    Delete uncompressed loaders.

    :param dirs: List of OS/radio bar/loader/zipped folders.
    :type dirs: list(str)

    :param deleted: Whether to delete uncompressed files. True by default.
    :type deleted: bool

    :param radios: Whether to create radio autoloaders. True by default.
    :type radios: bool
    """
    if deleted:
        print("DELETING UNCOMPRESSED LOADERS...")
        barutils.remove_unpacked_loaders(dirs[2], dirs[3], radios)


def archivist_removeemptyfolders(localdir):
    """
    Delete empty folders.

    :param localdir: Working directory. Local by default.
    :type localdir: str
    """
    print("REMOVING EMPTY FOLDERS...")
    barutils.remove_empty_folders(localdir)


def archivist_main(osversion, radioversion=None, softwareversion=None,
                   localdir=None, radios=True, compressed=True, deleted=True,
                   hashed=True, hashdict=None, download=True,
                   extract=True, signed=True, compmethod="7z",
                   gpg=False, integrity=True, altsw=None,
                   core=False, oldstyle=False):
    """
    Wrap around multi-autoloader creation code.
    Some combination of creating, downloading, hashing,
    compressing and moving autoloaders.

    :param osversion: OS version, 10.x.y.zzzz. Required.
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

    :param integrity: Whether to test downloaded files. True by default.
    :type integrity: bool

    :param altsw: Radio software release, if not the same as OS.
    :type altsw: str

    :param core: Whether to create a core/radio loader. Default is false.
    :type core: bool

    :param oldstyle: Whether to make old-style checksum files. Default is false.
    :type oldstyle: bool
    """
    radioversion = scriptutils.return_radio_version(osversion, radioversion)
    softwareversion, swchecked = scriptutils.return_sw_checked(softwareversion, osversion)
    if altsw == "checkme":
        altsw, altchecked = scriptutils.return_radio_sw_checked(altsw, radioversion)
    if localdir is None:
        localdir = os.getcwd()
    if hashed and hashdict is None:
        hashdict = hashutils.verifier_config_loader()
        hashutils.verifier_config_writer(hashdict)
    scriptutils.standard_preamble("archivist", osversion, softwareversion, radioversion, altsw)
    # Generate download URLs
    baseurl, alturl = scriptutils.get_baseurls(softwareversion, altsw)
    osurls, radiourls, cores = utilities.generate_urls(baseurl, osversion, radioversion, True)
    osurls = cores if core else osurls
    for idx, url in enumerate(osurls):
        if "qc8960.factory_sfi" in url:
            vzwurl = url
            vzwindex = idx
            break
    if not networkutils.availability(vzwurl):
        osurls[vzwindex] = osurls[vzwindex].replace("qc8960.factory_sfi", "qc8960.verizon_sfi")
    osurls = list(set(osurls))  # pop duplicates
    if altsw:
        radiourls2 = [x.replace(baseurl, alturl) for x in radiourls]
        radiourls = radiourls2
        del radiourls2
    archivist_checksw(baseurl, softwareversion, swchecked)
    if altsw:
        scriptutils.check_radio_sw(alturl, altsw, altchecked)
    # Check availability of OS, radio
    scriptutils.check_os_bulk(osurls)
    radiourls, radioversion = scriptutils.check_radio_bulk(radiourls, radioversion)
    # Get 7z executable
    compmethod, szexe = scriptutils.get_sz_executable(compmethod)
    # Make dirs: bd_o, bd_r, ld_o, ld_r, zd_o, zd_r
    dirs = barutils.make_dirs(localdir, osversion, radioversion)
    osurls = scriptutils.bulk_avail(osurls)
    radiourls = scriptutils.bulk_avail(radiourls)
    archivist_download(download, osurls, radiourls, localdir)
    archivist_integritybars(integrity, osurls, radiourls, localdir)
    archivist_extractbars(extract, localdir)
    archivist_integritysigned(extract, localdir)
    archivist_movebars(dirs, localdir)
    archivist_generateloaders(osversion, radioversion, radios, localdir, altsw, core)
    archivist_integrityloaders(integrity, localdir)
    archivist_removesigned(signed, localdir)
    archivist_compressor(compressed, integrity, localdir, compmethod, szexe)
    archivist_moveloaders(dirs, localdir)
    archivist_gethashes(dirs, hashed, compressed, deleted, radios, osversion, radioversion, softwareversion, oldstyle)
    archivist_getoldhashes(dirs, hashed, compressed, deleted, radios, hashdict, oldstyle)
    archivist_gpg(gpg, dirs, compressed, deleted, radios)
    archivist_deleteuncompressed(dirs, deleted, radios)
    archivist_removeemptyfolders(localdir)
    print("\nFINISHED!")


if __name__ == "__main__":
    grab_args()
    decorators.enter_to_exit(False)

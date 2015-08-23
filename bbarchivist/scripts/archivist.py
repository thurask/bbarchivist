#!/usr/bin/env python3

"""Download bar files, create autoloaders."""

import os  # filesystem read
import shutil  # directory read/write
import time  # time for downloader
import math  # rounding of floats
import sys  # load arguments
import argparse  # parse arguments
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
            help="Radio software version, if not same as OS",
            nargs="?",
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
        parser.set_defaults(compmethod="7z")
        args = parser.parse_args(sys.argv[1:])
        if args.folder is None:
            args.folder = os.getcwd()
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
                       args.gpg, args.integrity, args.altsw)
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
        hashdict = filehashtools.verifier_config_loader()
        filehashtools.verifier_config_writer(hashdict)
        compmethod = barutils.compress_config_loader()
        download = True
        extract = True
        signed = True
        gpg = False
        integrity = True
        altsw = None
        print(" ")
        archivist_main(osversion, radioversion, softwareversion,
                       localdir, radios, compressed, deleted, hashed,
                       hashdict, download,
                       extract, signed, compmethod, gpg,
                       integrity, altsw)
        smeg = input("Press Enter to exit")
        if smeg or not smeg:
            raise SystemExit


def archivist_main(osversion, radioversion=None, softwareversion=None,
                   localdir=None, radios=True, compressed=True, deleted=True,
                   hashed=True, hashdict=None, download=True,
                   extract=True, signed=True,
                   compmethod="7z", gpg=False,
                   integrity=True, altsw=None):
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

    :param compmethod: Compression method. Default is "7z" with fallback "zip".
    :type compmethod: str

    :param gpg: Whether to use GnuPG verification. False by default.
    :type gpg: bool

    :param integrity: Whether to test downloaded bar files. True by default.
    :type integrity: bool

    :param altsw: Radio software release, if not the same as OS.
    :type altsw: str
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

    baseurl = networkutils.create_base_url(softwareversion)
    if altsw:
        alturl = networkutils.create_base_url(altsw)
    osurls, radiourls, cors = utilities.generate_urls(baseurl, osversion, radioversion)
    del cors
    if not networkutils.availability(osurls[1]):
        osurls[1] = osurls[1].replace("qc8960.factory_sfi", "qc8960.verizon_sfi")  # fallback
    osurls = list(set(osurls))  # pop duplicates
    if altsw:
        radiourls2 = []
        for rad in radiourls:
            radiourls2.append(rad.replace(baseurl, alturl))
        radiourls = radiourls2
        del radiourls2

    # Check availability of software release
    print("CHECKING SOFTWARE RELEASE AVAILABILITY...")
    if not swchecked:
        avlty = networkutils.availability(baseurl)
        if avlty:
            print("SOFTWARE RELEASE", softwareversion, "EXISTS")
        else:
            print("SOFTWARE RELEASE", softwareversion, "NOT FOUND")
            cont = utilities.str2bool(input("CONTINUE? Y/N: "))
            if cont:
                pass
            else:
                print("\nEXITING...")
                raise SystemExit
    else:
        print("SOFTWARE RELEASE", softwareversion, "EXISTS")

    if altsw:
        print("CHECKING RADIO SOFTWARE RELEASE...")
        altavlty = networkutils.availability(alturl)
        if altavlty:
            print("SOFTWARE RELEASE", altsw, "EXISTS")
        else:
            print("SOFTWARE RELEASE", altsw, "NOT FOUND")
            cont = utilities.str2bool(input("CONTINUE? Y/N: "))
            if cont:
                pass
            else:
                print("\nEXITING...")
                raise SystemExit

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
            radioversion = rad2
        else:
            going = utilities.str2bool(input("KEEP GOING? Y/N: "))
            if going:
                pass
            else:
                print("\nEXITING...")
                raise SystemExit

    if compmethod == "7z":
        print("\nCHECKING PRESENCE OF 7ZIP...")
        psz = utilities.prep_seven_zip(True)
        if psz:
            print("7ZIP OK")
            szexe = utilities.get_seven_zip(True)
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

    # Make dirs
    bd_o, bd_r, ld_o, ld_r, zd_o, zd_r = barutils.make_dirs(localdir, osversion, radioversion)

    # Download files
    if download:
        print("\nBEGIN DOWNLOADING...")
        networkutils.download_bootstrap(radiourls+osurls, localdir, workers=3)
        print("ALL FILES DOWNLOADED")

    # Test bar files
    if integrity:
        brokenlist = []
        print("\nTESTING BAR FILES...")
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
        if brokenlist and download:
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
            print("BAR FILES DOWNLOADED OK")

    # Extract bar files
    if extract:
        print("\nEXTRACTING...")
        barutils.extract_bars(localdir)

    # Test signed files
    if integrity:
        print("\nTESTING SIGNED FILES...")
        for file in os.listdir(localdir):
            if file.endswith(".bar"):
                networkutils.line_begin()
                print("TESTING:", file)
                signname, signhash = barutils.retrieve_sha512(file)
                sha512ver = barutils.verify_sha512(signname, signhash)
                if not sha512ver:
                    print("{0} IS BROKEN".format((file)))
                    raise SystemExit
        print("SIGNED FILES EXTRACTED OK")

    # Move bar files
    print("\nMOVING BAR FILES...")
    barutils.move_bars(localdir, bd_o, bd_r)

    # Create loaders
    print("\nGENERATING LOADERS...")
    if altsw:
        altradio = True
    else:
        altradio = False
    loadergen.generate_loaders(osversion,
                                radioversion,
                                radios,
                                localdir,
                                altradio)

    # Remove .signed files
    if signed:
        print("\nREMOVING SIGNED FILES...")
        for file in os.listdir(localdir):
            if os.path.join(localdir, file).endswith(".signed"):
                print("REMOVING: " + file)
                os.remove(os.path.join(localdir, file))

    # If compression = true, compress
    if compressed:
        print("\nCOMPRESSING...")
        barutils.compress(localdir, compmethod, szexe, True)

    if integrity and compressed:
        print("\nTESTING ARCHIVES...")
        barutils.verify(localdir, compmethod, szexe, True)

    # Move zipped/unzipped loaders
    print("\nMOVING LOADERS...")
    barutils.move_loaders(localdir,
                          ld_o, ld_r,
                          zd_o, zd_r)

    # Get hashes (if specified)
    if hashed:
        print("\nHASHING LOADERS...")
        if compressed:
            filehashtools.verifier(
                zd_o,
                **hashdict)
            if radios:
                filehashtools.verifier(
                    zd_r,
                    **hashdict)
        if not deleted:
            filehashtools.verifier(
                ld_o,
                **hashdict)
            if radios:
                filehashtools.verifier(
                    ld_r,
                    **hashdict)
    if gpg:
        gpgkey, gpgpass = filehashtools.gpg_config_loader()
        if gpgkey is None or gpgpass is None:
            print("NO PGP KEY/PASS FOUND")
            cont = utilities.str2bool(input("CONTINUE (Y/N)?: "))
            if cont:
                if gpgkey is None:
                    gpgkey = input("PGP KEY (0x12345678): ")
                    if gpgkey[:2] != "0x":
                        gpgkey = "0x" + gpgkey  # add preceding 0x
                if gpgpass is None:
                    gpgpass = getpass.getpass(prompt="PGP PASSPHRASE: ")
                    writebool = utilities.str2bool(input("WRITE PASSWORD TO FILE (Y/N)?:"))
                if writebool:
                    gpgpass2 = gpgpass
                else:
                    gpgpass2 = None
                filehashtools.gpg_config_writer(gpgkey, gpgpass2)
            else:
                gpgkey = None
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
        print("\nDELETING UNCOMPRESSED LOADERS...")
        shutil.rmtree(ld_o)
        if radios:
            shutil.rmtree(ld_r)

    # Delete empty folders
    print("\nREMOVING EMPTY FOLDERS...")
    barutils.remove_empty_folders(localdir)

    print("\nFINISHED!")
    endtime = time.clock() - starttime
    endtime_proper = math.ceil(endtime * 100) / 100
    print("Completed in " + str(endtime_proper) + " seconds\n")

if __name__ == "__main__":
    grab_args()

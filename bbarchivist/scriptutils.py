#!/usr/bin/env python3
"""This module contains various utilities for the scripts folder."""

import os  # path work
import getpass  # invisible password
import argparse  # generic parser
import sys  # getattr
import shutil  # folder removal
import glob  # file lookup
from bbarchivist import utilities  # little things
from bbarchivist import barutils  # file system work
from bbarchivist import archiveutils  # archive support
from bbarchivist import bbconstants  # constants
from bbarchivist import hashutils  # gpg
from bbarchivist import networkutils  # network tools
from bbarchivist import textgenerator  # writing text to file
from bbarchivist import smtputils  # email
from bbarchivist import sqlutils  # sql

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "Copyright 2015-2016 Thurask"


def shortversion():
    """
    Get short app version (Git tag).
    """
    if not getattr(sys, 'frozen', False):
        ver = bbconstants.VERSION
    else:
        verfile = glob.glob(os.path.join(os.getcwd(), "version.txt"))[0]
        with open(verfile) as afile:
            ver = afile.read()
    return ver


def longversion():
    """
    Get long app version (Git tag + commits + hash).
    """
    if not getattr(sys, 'frozen', False):
        ver = (bbconstants.LONGVERSION, bbconstants.COMMITDATE)
    else:
        verfile = glob.glob(os.path.join(os.getcwd(), "longversion.txt"))[0]
        with open(verfile) as afile:
            ver = afile.read().split("\n")
    return ver


def default_parser(name=None, desc=None, flags=None, vers=None):
    """
    A generic form of argparse's ArgumentParser.

    :param name: App name.
    :type name: str

    :param desc: App description.
    :type desc: str

    :param flags: Tuple of sections to add.
    :type flags: tuple(str)

    :param vers: Versions: [git commit hash, git commit date]
    :param vers: list(str)
    """
    if vers is None:
        vers = longversion()
    parser = argparse.ArgumentParser(
        prog=name,
        description=desc,
        epilog="https://github.com/thurask/bbarchivist")
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version="{0} {1} committed {2}".format(parser.prog, vers[0], vers[1]))
    if flags is not None:
        if "folder" in flags:
            parser.add_argument(
                "-f",
                "--folder",
                dest="folder",
                help="Working folder",
                default=None,
                metavar="DIR",
                type=utilities.file_exists)
        if "osr" in flags:
            parser.add_argument(
                "os",
                help="OS version")
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
    return parser


def external_version(parser, addition):
    """
    Modify the version string of argparse.ArgumentParser, adding something.

    :param parser: Parser to modify.
    :type parser: argparse.ArgumentParser

    :param addition: What to add.
    :type addition: str
    """
    verarg = [arg for arg in parser._actions if type(arg) == argparse._VersionAction][0]
    verarg.version = "{1}{0}".format(addition, verarg.version)
    return parser


def return_radio_version(osversion, radioversion=None):
    """
    Increment radio version, if need be.

    :param osversion: OS version.
    :type osversion: str

    :param radioversion: Radio version, None if incremented.
    :type radioversion: str
    """
    if radioversion is None:
        radioversion = utilities.increment(osversion, 1)
    return radioversion


def return_sw_checked(softwareversion, osversion):
    """
    Check software existence, return boolean.

    :param softwareversion: Software release version.
    :type softwareversion: str

    :param osversion: OS version.
    :type osversion: str
    """
    if softwareversion is None:
        serv = bbconstants.SERVERS["p"]
        softwareversion = networkutils.sr_lookup(osversion, serv)
        if softwareversion == "SR not in system":
            print("SOFTWARE RELEASE NOT FOUND")
            cont = utilities.s2b(input("INPUT MANUALLY? Y/N: "))
            if cont:
                softwareversion = input("SOFTWARE RELEASE: ")
                swchecked = False
            else:
                print("\nEXITING...")
                raise SystemExit  # bye bye
        else:
            swchecked = True
    else:
        swchecked = True
    return softwareversion, swchecked


def return_radio_sw_checked(altsw, radioversion):
    """
    Check radio software existence, return boolean.

    :param altsw: Software release version.
    :type altsw: str

    :param radioversion: Radio version.
    :type radioversion: str
    """
    if altsw == "checkme":
        serv = bbconstants.SERVERS["p"]
        testos = utilities.increment(radioversion, -1)
        altsw = networkutils.sr_lookup(testos, serv)
        if altsw == "SR not in system":
            print("RADIO SOFTWARE RELEASE NOT FOUND")
            cont = utilities.s2b(input("INPUT MANUALLY? Y/N: "))
            if cont:
                altsw = input("SOFTWARE RELEASE: ")
                altchecked = False
            else:
                print("\nEXITING...")
                raise SystemExit  # bye bye
        else:
            altchecked = True
    else:
        altchecked = True
    return altsw, altchecked


def check_sw(baseurl, softwareversion, swchecked):
    """
    Check existence of software release.

    :param baseurl: Base URL (from http to hashed SW release).
    :type basurl: str

    :param softwareversion: Software release.
    :type softwareversion: str

    :param swchecked: If we checked the sw release already.
    :type swchecked: bool
    """
    print("CHECKING SOFTWARE RELEASE AVAILABILITY...")
    if not swchecked:
        avlty = networkutils.availability(baseurl)
        if avlty:
            print("SOFTWARE RELEASE {0} EXISTS".format(softwareversion))
        else:
            print("SOFTWARE RELEASE {0} NOT FOUND".format(softwareversion))
            cont = utilities.s2b(input("CONTINUE? Y/N: "))
            if not cont:
                print("\nEXITING...")
                raise SystemExit
    else:
        print("SOFTWARE RELEASE {0} EXISTS".format(softwareversion))


def check_radio_sw(alturl, altsw, altchecked):
    """
    Check existence of radio software release.

    :param alturl: Radio base URL (from http to hashed SW release).
    :type alturl: str

    :param altsw: Radio software release.
    :type altsw: str

    :param altchecked: If we checked the sw release already.
    :type altchecked: bool
    """
    print("CHECKING RADIO SOFTWARE RELEASE...")
    if not altchecked:
        altavlty = networkutils.availability(alturl)
        if altavlty:
            print("SOFTWARE RELEASE {0} EXISTS".format(altsw))
        else:
            print("SOFTWARE RELEASE {0} NOT FOUND".format(altsw))
            cont = utilities.s2b(input("CONTINUE? Y/N: "))
            if not cont:
                print("\nEXITING...")
                raise SystemExit
    else:
        print("SOFTWARE RELEASE {0} EXISTS".format(altsw))


def check_os_single(osurl, osversion, device):
    """
    Check existence of single OS link.

    :param radiourl: Radio URL to check.
    :type radiourl: str

    :param radioversion: Radio version.
    :type radioversion: str

    :param device: Device family.
    :type device: int
    """
    osav = networkutils.availability(osurl)
    if not osav:
        print("{0} NOT AVAILABLE FOR {1}".format(osversion, bbconstants.DEVICES[device]))
        cont = utilities.s2b(input("CONTINUE? Y/N: "))
        if not cont:
            print("\nEXITING...")
            raise SystemExit


def check_os_bulk(osurls):
    """
    Check existence of list of OS links.

    :param osurls: OS URLs to check.
    :type osurls: list(str)
    """
    for url in osurls:
        osav = networkutils.availability(url)
        if osav:
            break
    else:
        print("OS VERSION NOT FOUND")
        cont = utilities.s2b(input("CONTINUE? Y/N: "))
        if not cont:
            print("\nEXITING...")
            raise SystemExit


def check_radio_single(radiourl, radioversion):
    """
    Check existence of single radio link.

    :param radiourl: Radio URL to check.
    :type radiourl: str

    :param radioversion: Radio version.
    :type radioversion: str
    """
    radav = networkutils.availability(radiourl)
    if not radav:
        print("RADIO VERSION NOT FOUND")
        cont = utilities.s2b(input("INPUT MANUALLY? Y/N: "))
        if cont:
            rad2 = input("RADIO VERSION: ")
            radiourl = radiourl.replace(radioversion, rad2)
            radioversion = rad2
        else:
            going = utilities.s2b(input("KEEP GOING? Y/N: "))
            if not going:
                print("\nEXITING...")
                raise SystemExit
    return radiourl, radioversion


def check_radio_bulk(radiourls, radioversion):
    """
    Check existence of list of radio links.

    :param radiourls: Radio URLs to check.
    :type radiourls: list(str)

    :param radioversion: Radio version.
    :type radioversion: str
    """
    for url in radiourls:
        radav = networkutils.availability(url)
        if radav:
            break
    else:
        print("RADIO VERSION NOT FOUND")
        cont = utilities.s2b(input("INPUT MANUALLY? Y/N: "))
        if cont:
            rad2 = input("RADIO VERSION: ")
            radiourls = [url.replace(radioversion, rad2) for url in radiourls]
            radioversion = rad2
        else:
            going = utilities.s2b(input("KEEP GOING? Y/N: "))
            if not going:
                print("\nEXITING...")
                raise SystemExit
    return radiourls, radioversion


def get_baseurls(softwareversion, altsw=None):
    """
    Generate base URLs for bar links.

    :param softwareversion: Software version.
    :type softwareversion: str

    :param altsw: Radio software version, if necessary.
    :type altsw: str
    """
    baseurl = networkutils.create_base_url(softwareversion)
    alturl = networkutils.create_base_url(altsw) if altsw else None
    return baseurl, alturl


def get_sz_executable(compmethod):
    """
    Get 7z executable.

    :param compmethod: Compression method.
    :type compmethod: str
    """
    if compmethod != "7z":
        szexe = ""
    else:
        print("CHECKING PRESENCE OF 7ZIP...")
        psz = utilities.prep_seven_zip(True)
        if psz:
            print("7ZIP OK")
            szexe = utilities.get_seven_zip(False)
        else:
            szexe = ""
            print("7ZIP NOT FOUND")
            cont = utilities.s2b(input("CONTINUE? Y/N "))
            if cont:
                print("FALLING BACK TO ZIP...")
                compmethod = "zip"
            else:
                print("\nEXITING...")
                raise SystemExit  # bye bye
    return compmethod, szexe


def test_bar_files(localdir, urllist):
    """
    Test bar files after download.

    :param localdir: Directory.
    :type localdir: str

    :param urllist: List of URLs to check.
    :type urllist: list(str)
    """
    brokenlist = []
    print("TESTING BAR FILES...")
    for file in os.listdir(localdir):
        if file.endswith(".bar"):
            print("TESTING: {0}".format(file))
            thepath = os.path.abspath(os.path.join(localdir, file))
            brokens = barutils.bar_tester(thepath)
            if brokens is not None:
                os.remove(brokens)
                for url in urllist:
                    if brokens in url:
                        brokenlist.append(url)
    if brokenlist:
        print("SOME FILES ARE BROKEN!")
        utilities.lprint(brokenlist)
        raise SystemExit
    else:
        print("BAR FILES DOWNLOADED OK")


def test_signed_files(localdir):
    """
    Test signed files after extract.

    :param localdir: Directory.
    :type localdir: str
    """
    print("TESTING SIGNED FILES...")
    for file in os.listdir(localdir):
        if file.endswith(".bar"):
            print("TESTING: {0}".format(file))
            signname, signhash = barutils.retrieve_sha512(file)
            sha512ver = barutils.verify_sha512(signname, signhash)
            if not sha512ver:
                print("{0} IS BROKEN".format((file)))
                break
    else:
        print("ALL FILES EXTRACTED OK")


def test_loader_files(localdir):
    """
    Test loader files after creation.

    :param localdir: Directory.
    :type localdir: str
    """
    if not utilities.is_windows():
        pass
    else:
        print("TESTING LOADER FILES...")
        brokens = utilities.verify_bulk_loaders(localdir)
        if brokens:
            print("BROKEN FILES:")
            utilities.lprint(brokens)
            raise SystemExit
        else:
            print("ALL FILES CREATED OK")


def test_single_loader(loaderfile):
    """
    Test single loader file after creation.

    :param loaderfile: File to check.
    :type loaderfile: str
    """
    if not utilities.is_windows():
        pass
    else:
        print("TESTING LOADER...")
        if not utilities.verify_loader_integrity(loaderfile):
            print("{0} IS BROKEN!".format(os.path.basename(loaderfile)))
            raise SystemExit
        else:
            print("LOADER CREATED OK")


def prod_avail(results, mailer=False, osversion=None, password=None):
    """
    Clean availability for production lookups for autolookup script.

    :param results: Result dict.
    :type results: dict(str: str)

    :param mailer: If we're mailing links. Default is false.
    :type mailer: bool

    :param osversion: OS version.
    :type osversion: str

    :param password: Email password.
    :type password: str
    """
    prel = results['p']
    if prel != "SR not in system" and prel is not None:
        pav = "PD"
        baseurl = networkutils.create_base_url(prel)
        avail = networkutils.availability(baseurl)
        is_avail = "Available" if avail else "Unavailable"
        if avail and mailer:
            sqlutils.prepare_sw_db()
            if not sqlutils.check_exists(osversion, prel):
                rad = utilities.increment(osversion, 1)
                linkgen(osversion, rad, prel, temp=True)
                smtputils.prep_email(osversion, prel, password)
    else:
        pav = "  "
        is_avail = "Unavailable"
    return prel, pav, is_avail


def linkgen(osversion, radioversion=None, softwareversion=None, altsw=None, temp=False):
    """
    Generate debrick/core/radio links for given OS, radio, software release.

    :param osversion: OS version, 10.x.y.zzzz.
    :type osversion: str

    :param radioversion: Radio version, 10.x.y.zzzz. Can be guessed.
    :type radioversion: str

    :param softwareversion: Software version, 10.x.y.zzzz. Can be guessed.
    :type softwareversion: str

    :param altsw: Radio software release, if not the same as OS.
    :type altsw: str

    :param temp: If file we write to is temporary.
    :type temp: bool
    """
    radioversion = return_radio_version(osversion, radioversion)
    softwareversion, swc = return_sw_checked(softwareversion, osversion)
    del swc
    if altsw is not None:
        altsw, aswc = return_radio_sw_checked(altsw, radioversion)
        del aswc
    baseurl = networkutils.create_base_url(softwareversion)

    # List of debrick urls
    oses, cores, radios = textgenerator.url_gen(osversion, radioversion, softwareversion)
    if altsw is not None:
        del radios
        dbks, cors, radios = textgenerator.url_gen(osversion, radioversion, altsw)
        del dbks
        del cors

    avlty = networkutils.availability(baseurl)
    textgenerator.write_links(softwareversion, osversion, radioversion, oses, cores, radios,
                              avlty, False, None, temp, altsw)


def clean_swrel(swrelset):
    """
    Clean a list of software release lookups.

    :param swrelset: List of software releases.
    :type swrelset: set(str)
    """
    for i in swrelset:
        if i != "SR not in system" and i is not None:
            swrelease = i
            break
    else:
        swrelease = ""
    return swrelease


def autolookup_printer(out, avail, log=False, quiet=False, record=None):
    """
    Print autolookup results, logging if specified.

    :param out: Output block.
    :type out: str

    :param avail: Availability. Can be "Available" or "Unavailable".
    :type avail: str

    :param log: If we're logging to file.
    :type log: bool

    :param quiet: If we only note available entries.
    :type quiet: bool

    :param record: If we're logging, the file to log to.
    :type record: str
    """
    if not quiet:
        avail = "Available"  # force things
    if avail == "Available":
        if log:
            with open(record, "a") as rec:
                rec.write("{0}\n".format(out))
        print(out)


def autolookup_output(osversion, swrelease, avail, avpack, sql=False):
    """
    Prepare autolookup block, and add to SQL database.

    :param osversion: OS version.
    :type osversion: str

    :param swrelease: Software release.
    :type swrelease: str

    :param avail: "Unavailable" or "Available".
    :type avail: str

    :param avpack: Availabilities: alpha 1 and 2, beta 1 and 2, production.
    :type avpack: list(str)

    :param sql: If we're adding this to our SQL database.
    :type sql: bool
    """
    if sql:
        sqlutils.prepare_sw_db()
        if not sqlutils.check_exists(osversion, swrelease):
            sqlutils.insert(osversion, swrelease, avail.lower())
    avblok = "[{0}|{1}|{2}|{3}|{4}]".format(*avpack)
    out = "OS {0} - SR {1} - {2} - {3}".format(osversion, swrelease, avblok, avail)
    return out


def export_cchecker(files, npc, hwid, osv, radv, swv, upgrade=False, forced=None):
    """
    Write carrierchecker lookup links to file.

    :param files: List of file URLs.
    :type files: list(str)

    :param npc: MCC + MNC (ex. 302220).
    :type npc: int

    :param hwid: Device hardware ID.
    :type hwid: str

    :param osv: OS version.
    :type osv: str

    :param radv: Radio version.
    :type radv: str

    :param swv: Software release.
    :type swv: str

    :param upgrade: Whether or not to use upgrade files. Default is false.
    :type upgrade: bool

    :param forced: Force a software release. None to go for latest.
    :type forced: str
    """
    if files:
        if not upgrade:
            newfiles = networkutils.carrier_query(npc, hwid, True, False, forced)
            cleanfiles = newfiles[3]
        else:
            cleanfiles = files
        osurls, coreurls, radiourls = textgenerator.url_gen(osv, radv, swv)
        stoppers = ["8960", "8930", "8974", "m5730", "winchester"]
        finals = [link for link in cleanfiles if all(word not in link for word in stoppers)]
        textgenerator.write_links(swv, osv, radv, osurls, coreurls, radiourls, True, True, finals)
        print("\nFINISHED!!!")
    else:
        print("CANNOT EXPORT, NO SOFTWARE RELEASE")


def generate_blitz_links(files, osv, radv, swv):
    """
    Generate blitz URLs (i.e. all OS and radio links).
    :param files: List of file URLs.
    :type files: list(str)

    :param osv: OS version.
    :type osv: str

    :param radv: Radio version.
    :type radv: str

    :param swv: Software release.
    :type swv: str
    """
    baseurl = networkutils.create_base_url(swv)
    suffix = "nto+armle-v7+signed.bar"
    coreurls = [
        "{0}/winchester.factory_sfi-{1}-{2}".format(baseurl, osv, suffix),
        "{0}/qc8960.factory_sfi-{1}-{2}".format(baseurl, osv, suffix),
        "{0}/qc8960.factory_sfi_hybrid_qc8x30-{1}-{2}".format(baseurl, osv, suffix),
        "{0}/qc8974.factory_sfi_hybrid_qc8974-{1}-{2}".format(baseurl, osv, suffix)
    ]
    radiourls = [
        "{0}/m5730-{1}-{2}".format(baseurl, radv, suffix),
        "{0}/qc8960-{1}-{2}".format(baseurl, radv, suffix),
        "{0}/qc8960.wtr-{1}-{2}".format(baseurl, radv, suffix),
        "{0}/qc8960.wtr5-{1}-{2}".format(baseurl, radv, suffix),
        "{0}/qc8930.wtr5-{1}-{2}".format(baseurl, radv, suffix),
        "{0}/qc8974.wtr2-{1}-{2}".format(baseurl, radv, suffix)
    ]
    return files + coreurls + radiourls


def package_blitz(bardir, swv):
    """
    Package and verify a blitz package.

    :param bardir: Path to folder containing bar files.
    :type bardir: str

    :param swv: Software version.
    :type swv: str
    """
    print("\nCREATING BLITZ...")
    barutils.create_blitz(bardir, swv)
    print("\nTESTING BLITZ...")
    zipver = archiveutils.zip_verify("Blitz-{0}.zip".format(swv))
    if not zipver:
        print("BLITZ FILE IS BROKEN")
        raise SystemExit
    else:
        shutil.rmtree(bardir)


def purge_dross(files, craplist):
    """
    Get rid of Nuance/retaildemo apps in a list of apps.

    :param files: List of URLs to clean.
    :type files: list(str)

    :param craplist: List of fragments to check for and remove.
    :type craplist: list(str)
    """
    files2 = [file for file in files if all(word not in file for word in craplist)]
    return files2


def slim_preamble(appname):
    """
    Standard app name header.

    :param appname: Name of app.
    :type appname: str
    """
    print("~~~{0} VERSION {1}~~~".format(appname.upper(), shortversion()))


def standard_preamble(appname, osversion, softwareversion, radioversion, altsw=None):
    """
    Standard app name, OS, radio and software (plus optional radio software) print block.

    :param appname: Name of app.
    :type appname: str

    :param osversion: OS version, 10.x.y.zzzz. Required.
    :type osversion: str

    :param radioversion: Radio version, 10.x.y.zzzz. Can be guessed.
    :type radioversion: str

    :param softwareversion: Software release, 10.x.y.zzzz. Can be guessed.
    :type softwareversion: str

    :param altsw: Radio software release, if not the same as OS.
    :type altsw: str
    """
    slim_preamble(appname)
    print("OS VERSION: {0}".format(osversion))
    print("OS SOFTWARE VERSION: {0}".format(softwareversion))
    print("RADIO VERSION: {0}".format(radioversion))
    if altsw is not None:
        print("RADIO SOFTWARE VERSION: {0}".format(altsw))


def verify_gpg_credentials():
    """
    Read GPG key/pass from file, verify if incomplete.
    """
    gpgkey, gpgpass = hashutils.gpg_config_loader()
    if gpgkey is None or gpgpass is None:
        print("NO PGP KEY/PASS FOUND")
        cont = utilities.s2b(input("CONTINUE (Y/N)?: "))
        if cont:
            if gpgkey is None:
                gpgkey = input("PGP KEY (0x12345678): ")
                if not gpgkey.startswith("0x"):
                    gpgkey = "0x{0}".format(gpgkey)   # add preceding 0x
            if gpgpass is None:
                gpgpass = getpass.getpass(prompt="PGP PASSPHRASE: ")
                writebool = utilities.s2b(input("SAVE PASSPHRASE (Y/N)?:"))
            else:
                writebool = False
            gpgpass2 = gpgpass if writebool else None
            hashutils.gpg_config_writer(gpgkey, gpgpass2)
        else:
            gpgkey = None
    return gpgkey, gpgpass


def bulk_hash(dirs, compressed=True, deleted=True, radios=True, hashdict=None):
    """
    Hash files in several folders based on flags.

    :param dirs: Folders: [OS_bars, radio_bars, OS_exes, radio_exes, OS_zips, radio_zips]
    :type dirs: list(str)

    :param compressed: Whether to hash compressed files. True by default.
    :type compressed: bool

    :param deleted: Whether to delete uncompressed files. True by default.
    :type deleted: bool

    :param radios: Whether to hash radio autoloaders. True by default.
    :type radios: bool

    :param hashdict: Dictionary of hash rules, in ~\bbarchivist.ini.
    :type hashdict: dict({str: bool})
    """
    print("HASHING LOADERS...")
    if compressed:
        hashutils.verifier(dirs[4], hashdict)
        if radios:
            hashutils.verifier(dirs[5], hashdict)
    if not deleted:
        hashutils.verifier(dirs[2], hashdict)
        if radios:
            hashutils.verifier(dirs[3], hashdict)


def bulk_verify(dirs, compressed=True, deleted=True, radios=True):
    """
    Verify files in several folders based on flags.

    :param dirs: Folders: [OS_bars, radio_bars, OS_exes, radio_exes, OS_zips, radio_zips]
    :type dirs: list(str)

    :param compressed: Whether to hash compressed files. True by default.
    :type compressed: bool

    :param deleted: Whether to delete uncompressed files. True by default.
    :type deleted: bool

    :param radios: Whether to hash radio autoloaders. True by default.
    :type radios: bool
    """
    gpgkey, gpgpass = verify_gpg_credentials()
    if gpgpass is not None and gpgkey is not None:
        print("VERIFYING LOADERS...")
        print("KEY: {0}".format(gpgkey))
        if compressed:
            hashutils.gpgrunner(dirs[4], gpgkey, gpgpass, True)
            if radios:
                hashutils.gpgrunner(dirs[5], gpgkey, gpgpass, True)
        if not deleted:
            hashutils.gpgrunner(dirs[2], gpgkey, gpgpass, True)
            if radios:
                hashutils.gpgrunner(dirs[3], gpgkey, gpgpass, True)


def enn_ayy(quant):
    """
    Cheeky way to put a N/A placeholder for a string.

    :param quant: What to check if it's None.
    :type quant: str
    """
    return "N/A" if quant is None else quant


def make_info(filepath, osver, radio=None, software=None, device=None):
    """
    Create a new-style info (names, sizes and hashes) file.

    :param filepath: Path to folder to analyze.
    :type filepath: str

    :param osver: OS version, required for both types.
    :type osver: str

    :param radio: Radio version, required for QNX.
    :type radio: str

    :param software: Software release, required for QNX.
    :type software: str

    :param device: Device type, required for Android.
    :type device: str
    """
    fileext = ".zip" if device else ".7z"
    files = os.listdir(filepath)
    absfiles = [os.path.join(filepath, x) for x in files if x.endswith((fileext, ".exe"))]
    fname = os.path.join(filepath, "!{0}_OSINFO!.txt".format(osver))
    with open(fname, "w") as afile:
        afile.write("OS: {0}\n".format(osver))
        if device:
            afile.write("Device: {0}\n".format(enn_ayy(device)))
        else:
            afile.write("Radio: {0}\n".format(enn_ayy(radio)))
            afile.write("Software: {0}\n".format(enn_ayy(software)))
        afile.write("{0}\n".format("~"*40))
        for indx, file in enumerate(absfiles):
            fsize = os.stat(file).st_size
            afile.write("File: {0}\n".format(os.path.basename(file)))
            afile.write("\tSize: {0} ({1})\n".format(fsize, utilities.fsizer(fsize)))
            afile.write("\tHashes:\n")
            afile.write("\t\tMD5: {0}\n".format(hashutils.hm5(file).upper()))
            afile.write("\t\tSHA1: {0}\n".format(hashutils.hs1(file).upper()))
            afile.write("\t\tSHA256: {0}\n".format(hashutils.hs256(file).upper()))
            afile.write("\t\tSHA512: {0}\n".format(hashutils.hs512(file).upper()))
            if indx != len(absfiles) - 1:
                afile.write("\n")


def bulk_info(dirs, osv, compressed=True, deleted=True, radios=True, rad=None, swv=None, dev=None):
    """
    Generate info files in several folders based on flags.

    :param dirs: Folders: [OS_bars, radio_bars, OS_exes, radio_exes, OS_zips, radio_zips]
    :type dirs: list(str)

    :param osver: OS version, required for both types.
    :type osver: str

    :param compressed: Whether to hash compressed files. True by default.
    :type compressed: bool

    :param deleted: Whether to delete uncompressed files. True by default.
    :type deleted: bool

    :param radios: Whether to hash radio autoloaders. True by default.
    :type radios: bool

    :param rad: Radio version, required for QNX.
    :type rad: str

    :param swv: Software release, required for QNX.
    :type swv: str

    :param dev: Device type, required for Android.
    :type dev: str
    """
    print("GENERATING INFO FILES...")
    if compressed:
        make_info(dirs[4], osv, rad, swv, dev)
        if radios:
            make_info(dirs[5], osv, rad, swv, dev)
    if not deleted:
        make_info(dirs[2], osv, rad, swv, dev)
        if radios:
            make_info(dirs[3], osv, rad, swv, dev)

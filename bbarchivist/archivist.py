#!/usr/bin/env python3

import os  # filesystem read
import shutil  # directory read/write
import hashlib  # SHA-x, MD5
import time  # time for downloader
import math  # rounding of floats
from . import utilities
from . import barutils
from . import bbconstants
from . import networkutils
from . import loadergen
from . import hashwrapper


def do_magic(osversion, radioversion, softwareversion,
             localdir, radios=True, compressed=True, deleted=True,
             hashed=True, crc32=False, adler32=False,
             sha1=True, sha224=False, sha256=False,
             sha384=False, sha512=False, md5=True,
             md4=False, ripemd160=False, cappath="cap.exe",
             download=True, extract=True, loaders=True, signed=True,
             compmethod="7z"):

    """
    Wrap around multi-autoloader creation code.
    Some combination of creating, downloading, hashing,
    compressing and moving autoloaders.
    :param osversion: OS version, 10.x.y.zzzz.
    :type osversion: str
    :param radioversion: Radio version, 10.x.y.zzzz.
    Usually OS version + 1.
    :type radioversion: str
    :param softwareversion: Software release, 10.x.y.zzzz.
    :type softwareversion: str
    :param localdir: Working directory. Required.
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
    :param md4: Whether to use MD4. False by default. Dependent on
    system OpenSSL implementation (not in stdlib).
    :type md4: bool
    :param ripemd160: Whether to use RIPEMD160. False by default. Dependent on
    system OpenSSL implementation (not in stdlib).
    :type ripemd160: bool
    :param cappath: Path to cap.exe. Default is local dir\\cap.exe.
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
    """
    starttime = time.clock()
    version = bbconstants._version  # update as needed

    print("~~~ARCHIVIST VERSION", version + "~~~")
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

    # Hash software version
    swhash = hashlib.sha1(softwareversion.encode('utf-8'))
    hashedsoftwareversion = swhash.hexdigest()

    # Root of all urls
    baseurl = "http://cdn.fs.sl.blackberry.com/fs/qnx/production/"
    baseurl += hashedsoftwareversion

    # List of OS urls
    osurls = [baseurl + "/winchester.factory_sfi.desktop-" +
              osversion + "-nto+armle-v7+signed.bar",
              baseurl + "/qc8960.factory_sfi.desktop-" +
              osversion + "-nto+armle-v7+signed.bar",
              baseurl + "/qc8960.factory_sfi_hybrid_qc8x30.desktop-" +
              osversion + "-nto+armle-v7+signed.bar",
              baseurl + "/qc8960.factory_sfi_hybrid_qc8974.desktop-" +
              osversion + "-nto+armle-v7+signed.bar"]

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

    # Add URLs to dict, programmatically
    osdict = {}
    radiodict = {}
    for i in osurls:
        osdict[str(i)] = i
    for i in radiourls:
        radiodict[str(i)] = i

    # Check availability of software release
    print("\nCHECKING SOFTWARE RELEASE AVAILABILITY...")
    av = networkutils.availability(baseurl)
    if av:
        print("SOFTWARE RELEASE", softwareversion, "EXISTS")
    else:
        print("SOFTWARE RELEASE", softwareversion, "NOT FOUND")
        cont = utilities.str2bool(input("CONTINUE? Y/N "))
        if cont:
            pass
        else:
            print("\nEXITING...")
            raise SystemExit  # bye bye

    # Make dirs
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
        download_manager = networkutils.DownloadManager(radiodict, localdir, 5)
        download_manager.begin_downloads()
        download_manager.download_dict = osdict
        download_manager.begin_downloads()

    # Extract bar files
    if extract:
        print("\nEXTRACTING...")
        barutils.extract_bars(localdir)

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
        print("\nGENERATING LOADERS...\n")
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
            "\n")
        blocksize = 32 * 1024 * 1024
        if compressed:
            hashwrapper.verifier(
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
                ripemd160)
            if radios:
                hashwrapper.verifier(
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
                    ripemd160)
        if not deleted:
            hashwrapper.verifier(
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
                ripemd160)
            if radios:
                hashwrapper.verifier(
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
                    ripemd160)

    # Remove uncompressed loaders (if specified)
    if deleted:
        print("\nDELETING UNCOMPRESSED LOADERS...")
        shutil.rmtree(loaderdir)

    # Delete empty folders
    print("\nREMOVING EMPTY FOLDERS...")
    barutils.remove_empty_folders(localdir)

    print("\nFINISHED!")
    endtime = time.clock() - starttime
    endtime_proper = math.ceil(endtime * 100) / 100
    print("\nCompleted in " + str(endtime_proper) + " seconds\n")

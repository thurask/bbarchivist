#!/usr/bin/env python3
"""This module is used for creation of TCL autoloaders."""

import os  # path work
import shutil  # file copying

from bbarchivist import bbconstants  # versions/constants

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "2018 Thurask"


def point_point_copy(inpath, outpath, filename):
    """
    Copy a file from one absolute path to another.

    :param inpath: Input path.
    :type inpath: str

    :param outpath: Output path.
    :type outpath: str

    :param filename: Filename.
    :type filename: str
    """
    if os.sep in filename:
        filex = os.path.basename(filename)
    else:
        filex = filename
    shutil.copy(os.path.join(inpath, filename), os.path.join(outpath, filex))


def point_point_bulk(inpath, outpath, files):
    """
    Copy a list of files from one absolute path to another.

    :param inpath: Input path.
    :type inpath: str

    :param outpath: Output path.
    :type outpath: str

    :param files: List of filenames.
    :type files: list(str)
    """
    for file in files:
        point_point_copy(inpath, outpath, file)


def generate_tclloader_script(dirname, batchfile, shfile, wipe=True):
    """
    Copy script files from site-packages to loader directory.

    :param dirname: Name for final directory and loader.
    :type dirname: str

    :param batchfile: Path to flashall.bat.
    :type batchfile: str

    :param shfile: Path to flashall.sh.
    :type shfile: str

    :param wipe: If the final loader wipes userdata. Default is True.
    :type wipe: bool
    """
    shutil.copy(batchfile, os.path.join(dirname, "flashall.bat"))
    shutil.copy(shfile, os.path.join(dirname, "flashall.sh"))
    if not wipe:
        tclloader_nowipe(os.path.join(dirname, "flashall.bat"))
        tclloader_nowipe(os.path.join(dirname, "flashall.sh"))


def tclloader_nowipe(infile):
    """
    Modify a script file to strike references to wiping the phone.

    :param infile: Path to script file to modify.
    :type infile: str
    """
    filterout = ("oem securewipe", "flash userdata")
    with open(infile, "r+", newline="") as afile:
        content = afile.read()
        afile.seek(0)
        for line in content.split("\n"):
            if not any(part in line for part in filterout):
                afile.write(line + "\n")
        afile.truncate()


def generate_google_host(hostin, hostout):
    """
    Generate host directory from Google platform tools, i.e. fastboot.

    :param hostin: Directory containing files to copy.
    :type hostin: str

    :param hostout: Directory that files are to be copied to.
    :type hostout: str
    """
    platforms = ["linux", "windows", "darwin"]
    inouts = {os.path.join(hostin, plat, "platform-tools"): os.path.join(hostout, "{0}-x86".format(plat), "bin") for plat in platforms}
    for infile, outfile in inouts.items():
        shutil.copytree(infile, outfile)


def generate_tclloader_host(hostin, hostout):
    """
    Generate host directory from autoloader template, i.e. fastboot.

    :param hostin: Directory containing files to copy.
    :type hostin: str

    :param hostout: Directory that files are to be copied to.
    :type hostout: str
    """
    os.makedirs(os.path.join(hostout, "darwin-x86", "bin"))
    os.makedirs(os.path.join(hostout, "linux-x86", "bin"))
    os.makedirs(os.path.join(hostout, "windows-x86", "bin"))
    macfile = os.path.join("darwin-x86", "bin", "fastboot")
    linfile = os.path.join("linux-x86", "bin", "fastboot")
    winx = ["AdbWinApi.dll", "AdbWinUsbApi.dll", "fastboot.exe"]
    winfiles = [os.path.join("windows-x86", "bin", x) for x in winx]
    winfiles.extend([linfile, macfile])
    point_point_bulk(hostin, hostout, winfiles)


def generate_tclloader_sig(sigin, sigout):
    """
    Generate common signature files.

    :param sigin: Directory containing files to copy.
    :type sigin: str

    :param sigout: Directory that files are to be copied to.
    :type sigout: str
    """
    for entry in ["boot", "recovery"]:
        shutil.copy(os.path.join(sigin, "{0}.img.production.sig".format(entry)), os.path.join(sigout, "{0}.img.sig".format(entry)))


def generate_tclloader_csig(sigin, sigout, carrier):
    """
    Generate carrier variant signature files.

    :param sigin: Directory containing files to copy.
    :type sigin: str

    :param sigout: Directory that files are to be copied to.
    :type sigout: str

    :param carrier: Carrier to check: att, sprint, china, vzw
    :type carrier: str
    """
    for entry in ["boot", "recovery"]:
        shutil.copy(os.path.join(sigin, "{1}.img.production-{0}.sig".format(carrier, entry)), os.path.join(sigout, "{1}.img{0}.sig".format(carrier, entry)))


def generate_tclloader_carriers(sigin, sigout):
    """
    Collect carrier variant signature files.

    :param sigin: Directory containing files to copy.
    :type sigin: str

    :param sigout: Directory that files are to be copied to.
    :type sigout: str
    """
    prods = set(x.split("-")[-1].split(".")[0] for x in os.listdir(sigin) if "production-" in x) - {"boot", "recovery"}
    if prods:
        generate_tclloader_carriter(sigin, sigout, prods)


def generate_tclloader_carriter(sigin, sigout, prods):
    """
    Iterate carrier variant signature files.

    :param sigin: Directory containing files to copy.
    :type sigin: str

    :param sigout: Directory that files are to be copied to.
    :type sigout: str

    :param prods: Set of carriers.
    :type prods: set(str)
    """
    for carr in prods:
        generate_tclloader_csig(sigin, sigout, carr)


def generate_tclloader_mbn(mbnin, mbnout, platform):
    """
    Generate mbn files.

    :param mbnin: Directory containing files to copy.
    :type mbnin: str

    :param mbnout: Directory that files are to be copied to.
    :type mbnout: str

    :param platform: Platform type (i.e. subdirectory of target/product).
    :type platform: str
    """
    files = generate_tclloader_platmbn(platform)
    point_point_bulk(mbnin, mbnout, files)


def generate_tclloader_omniset(omnin, omnilist, prefix, suffix, filt):
    """
    Generic function to generate sets.

    :param omnin: Directory containing files to copy.
    :type omnin: str

    :param omnilist: List of variants.
    :type omnilist: list(str)

    :param prefix: Prefix, before items in list.
    :type prefix: str

    :param suffix: Suffix, after items in list.
    :type suffix: str

    :param filt: Filter, required to pick file out of directory listing.
    :type filt: str
    """
    omfiles = set(os.path.join(omnin, "{1}{0}{2}".format(omni, prefix, suffix)) for omni in omnilist)
    infiles = set(os.path.join(omnin, filex) for filex in os.listdir(omnin) if filt in filex)
    return omfiles, infiles


def generate_tclloader_oemset(oemin, oems):
    """
    Generate sets for OEM variants.

    :param oemin: Directory containing files to copy.
    :type oemin: str

    :param oems: List of OEM variants.
    :type oems: list(str)
    """
    ofiles, infiles = generate_tclloader_omniset(oemin, oems, "", ".img", "oem_")
    return ofiles, infiles


def generate_tclloader_oemfilt(oemin, oems):
    """
    Filter non-existent OEM variants.

    :param oemin: Directory containing files to copy.
    :type oemin: str

    :param oems: List of OEM variants.
    :type oems: list(str)
    """
    ofiles, infiles = generate_tclloader_oemset(oemin, oems)
    coll = [os.path.basename(oemf).replace(".img", "") for oemf in ofiles - infiles]
    oems = [oemp for oemp in oems if oemp not in coll]
    return oems


def generate_tclloader_radset(radin, rads):
    """
    Generate sets for radio variants.

    :param radin: Directory containing files to copy.
    :type radin: str

    :param rads: List of radio variants.
    :type rads: list(str)
    """
    rfiles, infiles = generate_tclloader_omniset(radin, rads, "NON-HLOS-", ".bin", "NON-HLOS-")
    return rfiles, infiles


def generate_tclloader_radfilt(radin, rads):
    """
    Filter non-existent radio variants.

    :param radin: Directory containing files to copy.
    :type radin: str

    :param rads: List of radio variants.
    :type rads: list(str)
    """
    rfiles, infiles = generate_tclloader_radset(radin, rads)
    coll = [os.path.basename(radf).replace(".bin", "").replace("NON-HLOS-", "") for radf in rfiles - infiles]
    rads = [radp for radp in rads if radp not in coll]
    return rads


def generate_tclloader_deps(platform):
    """
    Generate platform-specific file names.

    :param platform: Platform type (i.e. subdirectory of target/product).
    :type platform: str
    """
    if platform == "bbry_qc8953":  # KEYone
        oems = ["oem_att", "oem_china", "oem_common", "oem_sprint", "oem_vzw", "oem_indonesia", "oem_russia"]
        radios = ["china", "dschina", "emea", "global", "india", "japan", "usa"]
    elif platform == "bbry_qc8953krypton":  # Motion
        oems = ["oem_att", "oem_common", "oem_sprint", "oem_russia"]
        radios = ["americas", "cdma", "dscn", "dsglobal", "ssglobal"]
    elif platform == "bbry_sdm660":  # KEY2
        oems = ["oem_att", "oem_china", "oem_common", "oem_india", "oem_indonesia", "oem_sprint", "oem_russia"]
        radios = ["americas", "cn", "dsglobal", "dsjapan", "global", "japan"]
    return oems, radios


def generate_tclloader_looseends(imgout, platform):
    """
    Handle files that need to be handled.

    :param imgout: Directory that files are to be copied to.
    :type imgout: str

    :param platform: Platform type (i.e. subdirectory of target/product).
    :type platform: str
    """
    if platform == "bbry_qc8953":  # KEYone
        pass  # no special exceptions
    elif platform == "bbry_qc8953krypton":  # Motion
        looseends_krypton(imgout)
    elif platform == "bbry_sdm660":  # KEY2
        pass  # no special exceptions


def looseends_krypton(imgout):
    """
    Handle files that need to be handled, for the Motion platform.

    :param imgout: Directory that files are to be copied to.
    :type imgout: str
    """
    oldglobal = os.path.join(imgout, "NON-HLOS-ssglobal.bin")
    newglobal = os.path.join(imgout, "NON-HLOS-global.bin")
    os.rename(oldglobal, newglobal)  # SS intl model has different name than modem
    oldamericas = os.path.join(imgout, "NON-HLOS-americas.bin")
    newamericas = os.path.join(imgout, "NON-HLOS-dsamericas.bin")
    shutil.copy(oldamericas, newamericas)  # DS/SS americas model use same modem


def generate_tclloader_platimg(platform):
    """
    Generate platform-specific .img files.

    :param platform: Platform type (i.e. subdirectory of target/product).
    :type platform: str
    """
    imgs = ["recovery", "system", "userdata", "cache", "boot"]
    if "bbry_sdm660" in platform:
        imgs.append("vendor")
    return imgs


def generate_tclloader_platmbn(platform):
    """
    Generate platform-specific MBN files.

    :param platform: Platform type (i.e. subdirectory of target/product).
    :type platform: str
    """
    if "bbry_sdm660" in platform:
        mbnx = ["devcfg.mbn", "pmic.elf", "xbl.elf", "rpm.mbn", "tz.mbn"]
        mbny = ["hyp.signed.mbn", "cmnlib.signed.mbn", "cmnlib64.signed.mbn", "keymaster64.signed.mbn", "mdtpsecapp.signed.mbn"]
        mbnz = [os.path.join("MBNs", mbn) for mbn in mbny]
        mbns = mbnx + mbnz
    elif "bbry_qc8953" in platform:
        mbns = ["devcfg.mbn", "devcfg_cn.mbn", "rpm.mbn", "tz.mbn"]
    else:
        mbns = [None]
    return mbns


def generate_tclloader_platother(platform):
    """
    Generate platform-specific other files.

    :param platform: Platform type (i.e. subdirectory of target/product).
    :type platform: str
    """
    if "bbry_sdm660" in platform:
        others = ["dspso.bin", "BTFM.bin", "abl.elf"]
    elif "bbry_qc8953" in platform:
        others = ["adspso.bin", "emmc_appsboot.mbn", "sbl1_signed.mbn"]
    else:
        others = [None]
    return others


def generate_tclloader_img(imgin, imgout, platform):
    """
    Generate partition images and radios.

    :param imgin: Directory containing files to copy.
    :type imgin: str

    :param imgout: Directory that files are to be copied to.
    :type imgout: str

    :param platform: Platform type (i.e. subdirectory of target/product).
    :type platform: str
    """
    imgs = generate_tclloader_platimg(platform)
    point_point_bulk(imgin, imgout, ["{0}.img".format(img) for img in imgs])
    oems, radios = generate_tclloader_deps(platform)
    oems = generate_tclloader_oemfilt(imgin, oems)
    point_point_bulk(imgin, imgout, ["{0}.img".format(oem) for oem in oems])
    radios = generate_tclloader_radfilt(imgin, radios)
    point_point_bulk(imgin, imgout, ["NON-HLOS-{0}.bin".format(rad) for rad in radios])
    others = generate_tclloader_platother(platform)
    point_point_bulk(imgin, imgout, others)
    generate_tclloader_looseends(imgout, platform)


def generate_tclloader_scripttype(platform):
    """
    Get the right scripts for the right platform.

    :param platform: Platform type (i.e. subdirectory of target/product).
    :type platform: str
    """
    if "bbry_sdm660" in platform:
        scripts = (bbconstants.FLASHBATBBF.location, bbconstants.FLASHSHBBF.location)
    elif "bbry_qc8953" in platform:
        scripts = (bbconstants.FLASHBAT.location, bbconstants.FLASHSH.location)
    else:
        scripts = (None, None)
    return scripts


def generate_tclloader(localdir, dirname, platform, localtools=False, wipe=True):
    """
    Generate Android loader from extracted template files.

    :param localdir: Directory containing extracted template files.
    :type localdir: str

    :param dirname: Name for final directory and loader.
    :type dirname: str

    :param platform: Platform type (i.e. subdirectory of target/product).
    :type platform: str

    :param localtools: If host files will be copied from a template rather than a download. Default is False.
    :type localtools: bool

    :param wipe: If the final loader wipes userdata. Default is True.
    :type wipe: bool
    """
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    hostdir = os.path.join(dirname, "host")
    os.makedirs(hostdir)
    imgdir = os.path.join(dirname, "img")
    os.makedirs(imgdir)
    platscripts = generate_tclloader_scripttype(platform)
    generate_tclloader_script(dirname, platscripts[0], platscripts[1], wipe)
    if localtools:
        hdir = os.path.join(localdir, "host")
        generate_tclloader_host(hdir, hostdir)
    else:
        platdir = "plattools"
        generate_google_host(platdir, hostdir)
    pdir = os.path.join(localdir, "target", "product", platform)
    generate_tclloader_img(pdir, imgdir, platform)
    sdir = os.path.join(pdir, "sig")
    generate_tclloader_sig(sdir, imgdir)
    generate_tclloader_carriers(sdir, imgdir)
    qdir = os.path.join(pdir, "qcbc")
    generate_tclloader_mbn(qdir, imgdir, platform)

#!/usr/bin/env python3
"""This module is used for creation of autoloaders."""

import glob  # filename matching
import os  # path work
import shutil  # file copying

from bbarchivist import bbconstants  # versions/constants
from bbarchivist import exceptions  # exception handling
from bbarchivist import jsonutils  # json
from bbarchivist import pseudocap  # implement cap
from bbarchivist import utilities  # directory handler

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "2015-2018 Thurask"


def read_files(localdir, core=False):
    """
    Read list of signed files, return name assignments.

    :param localdir: Directory to use.
    :type localdir: str

    :param core: If we're using a core OS image. Default is false.
    :type core: bool
    """
    oslist = read_os_files(localdir, core)
    # [8960, 8x30, 8974, ti]
    radlist = read_radio_files(localdir)
    # [ti, z10, z10_vzw, q10, z30, z3, 8974]
    pairdict = {}
    mapping = {0:3, 1:0, 2:0, 3:0, 4:0, 5:1, 6:2}
    for idx, rad in enumerate(radlist):
        pairdict[rad] = oslist[mapping[idx]]
    filtdict = {k: v for k, v in pairdict.items() if k}  # pop None
    return filtdict


def find_signed_file(match, localdir, title, silent=False):
    """
    Use pattern matching to find a signed file in a directory.

    :param match: Match pattern to use.
    :type match: str

    :param localdir: Directory to use.
    :type localdir: str

    :param title: File type, in case it isn't found.
    :type title: str

    :param silent: Don't print that a file wasn't found. Default is False.
    :type silent: bool
    """
    try:
        signedfile = glob.glob(os.path.join(localdir, match))[0]
    except IndexError:
        signedfile = None
        if not silent:
            print("No {0} found".format(title))
    return signedfile


def generate_os_fixes(core=False):
    """
    Generate name regexes for OS signed files.

    :param core: If we're using a core OS image. Default is false.
    :type core: bool
    """
    if core:
        fix8960 = "*qc8960.*_sfi.BB*.signed"
        fixomap_new = "*winchester.*_sfi.BB*.signed"
        fixomap_old = "*os.factory_sfi.BB*.signed"
        fix8930 = "*qc8x30.BB*.signed"
        fix8974_new = "*qc8974.BB*.signed"
        fix8974_old = "*qc8974.*_sfi.BB*.signed"
    else:
        fix8960 = "*qc8960.*_sfi.desktop.BB*.signed"
        fixomap_new = "*winchester.*_sfi.desktop.BB*.signed"
        fixomap_old = "*os.factory_sfi.desktop.BB*.signed"
        fix8930 = "*qc8x30.desktop.BB*.signed"
        fix8974_new = "*qc8974.desktop.BB*.signed"
        fix8974_old = "*qc8974.*_sfi.desktop.BB*.signed"
    return fix8960, fixomap_new, fixomap_old, fix8930, fix8974_new, fix8974_old


def read_os_files(localdir, core=False):
    """
    Read list of OS signed files, return name assignments.

    :param localdir: Directory to use.
    :type localdir: str

    :param core: If we're using a core OS image. Default is false.
    :type core: bool
    """
    fix8960, fixomap_new, fixomap_old, fix8930, fix8974_new, fix8974_old = generate_os_fixes(core)
    # 8960
    os_8960 = find_signed_file(fix8960, localdir, "8960 OS")
    # 8x30 (10.3.1 MR+)
    os_8x30 = find_signed_file(fix8930, localdir, "8x30 OS", True)
    if os_8x30 is None:
        os_8x30 = find_signed_file(fix8960, localdir, "8x30 OS")
    # 8974
    os_8974 = find_signed_file(fix8974_new, localdir, "8974 OS", True)
    if os_8974 is None:
        os_8974 = find_signed_file(fix8974_old, localdir, "8974 OS")
    # OMAP
    os_ti = find_signed_file(fixomap_new, localdir, "OMAP OS", True)
    if os_ti is None:
        os_ti = find_signed_file(fixomap_old, localdir, "OMAP OS")
    return [os_8960, os_8x30, os_8974, os_ti]


def read_radio_files(localdir):
    """
    Read list of radio signed files, return name assignments.

    :param localdir: Directory to use.
    :type localdir: str
    """
    # STL100-1
    radio_ti = find_signed_file("*radio.m5730*.signed", localdir, "OMAP radio")
    # STL100-X
    radio_z10 = find_signed_file("*radio.qc8960.BB*.signed", localdir, "8960 radio")
    # STL100-4
    radio_z10_vzw = find_signed_file("*radio.qc8960*omadm*.signed", localdir, "VZW 8960 radio")
    # Q10/Q5
    radio_q10 = find_signed_file("*radio.qc8960*wtr.*signed", localdir, "Q10/Q5 radio")
    # Z30/Classic
    radio_z30 = find_signed_file("*radio.qc8960*wtr5*.signed", localdir, "Z30/Classic radio")
    # Z3
    radio_z3 = find_signed_file("*radio.qc8930*wtr5*.signed", localdir, "Z3 radio")
    # Passport
    radio_8974 = find_signed_file("*radio.qc8974*wtr2*.signed", localdir, "Passport radio")
    return [radio_ti, radio_z10, radio_z10_vzw, radio_q10, radio_z30, radio_z3, radio_8974]


def zeropad(splitver, idx, padlen):
    """
    Zero-pad an element of an OS/radio version to a certain length.

    :param splitver: OS/radio version, but split into quarters.
    :type splitver: list(str)

    :param idx: Index of splitver which must be checked.
    :type idx: int

    :param padlen: Length to pad to.
    :type padlen: int
    """
    if len(splitver[idx]) < padlen:
        splitver[idx] = splitver[idx].rjust(padlen, "0")
    return splitver


def versionpad(splitver):
    """
    Properly pad an OS/radio version.

    :param splitver: OS/radio version, but split into quarters.
    :type splitver: list(str)
    """
    splitver = zeropad(splitver, 2, 2)
    splitver = zeropad(splitver, 3, 4)
    return splitver


def pretty_formatter(osversion, radioversion):
    """
    Format OS/radio versions to cope with systems with poor sorting.

    :param osversion: OS version, 10.x.y.zzzz.
    :type osversion: str

    :param radioversion: Radio version, 10.x.y.zzzz.
    :type radioversion: str
    """
    # 10.x.y.zzz becomes 10.x.0y.0zzz
    splitos = osversion.split(".")
    splitos = versionpad(splitos)
    the_os = ".".join(splitos)
    splitrad = radioversion.split(".")
    splitrad = versionpad(splitrad)
    the_radio = ".".join(splitrad)
    return the_os, the_radio


def format_suffix(altradio=None, radioversion=None, core=False):
    """
    Formulate suffix for hybrid autoloaders.

    :param altradio: If a hybrid autoloader is being made.
    :type altradio: bool

    :param radioversion: The hybrid radio version, if applicable.
    :type radioversion: str

    :param core: If we're using a core OS image. Default is false.
    :type core: bool
    """
    suffix = "_R{0}".format(radioversion) if altradio and radioversion else ""
    if core:
        suffix += "_CORE"
    return suffix


def generate_loaders(osversion, radioversion, radios=True, localdir=None, altradio=False, core=False):
    """
    Create and label autoloaders for :mod:`bbarchivist.scripts.archivist`.

    :param osversion: OS version, 10.x.y.zzzz.
    :type osversion: str

    :param radioversion: Radio version, 10.x.y.zzzz.
    :type radioversion: str

    :param radios: Whether to make radios or not. True by default.
    :type radios: bool

    :param localdir: Working path. Default is local dir.
    :type localdir: str

    :param altradio: If we're using an alternate radio. Default is false.
    :type altradio: bool

    :param core: If we're using a core OS image. Default is false.
    :type core: bool
    """
    # default parsing
    localdir = utilities.dirhandler(localdir, os.getcwd())
    print("GETTING FILENAMES...")
    filedict = read_files(localdir, core)
    osversion, radioversion = pretty_formatter(osversion, radioversion)
    suffix = format_suffix(altradio, radioversion, core)
    # Generate loaders
    print("CREATING LOADERS...")
    filtrad = [rad for rad in filedict.keys() if rad]  # pop None
    generate_individual_loaders(filtrad, osversion, radioversion, suffix, filedict, radios, localdir)


def generate_individual_loaders(filtrad, osversion, radioversion, suffix, filedict, radios, localdir):
    """
    Generate individual loaders when generating several at once.

    :param filtrad: List of radio files, if they exist.
    :type filtrad: list(str)

    :param osversion: OS version, 10.x.y.zzzz.
    :type osversion: str

    :param radioversion: Radio version, 10.x.y.zzzz.
    :type radioversion: str

    :param suffix: Alternate radio, or blank.
    :type suffix: str

    :param filedict: Dictionary of radio:OS pairs.
    :type filedict: dict(str: str)

    :param radios: Whether to make radios or not. True by default.
    :type radios: bool

    :param localdir: Working path. Default is local dir.
    :type localdir: str
    """
    for radval in filtrad:
        device = generate_device(radval)
        osname = generate_filename(device, osversion, suffix)
        osfile = filedict[radval]
        if osfile is not None:
            wrap_pseudocap(osname, localdir, osfile, radval)
        if radios:
            radname = generate_filename(device, radioversion, "")
            wrap_pseudocap(radname, localdir, radval)



def wrap_pseudocap(filename, folder, first, second=None):
    """
    A filtered, excepting wrapper for pseudocap.

    :param filename: The title of the new loader.
    :type filename: str

    :param folder: The folder to create the loader in.
    :type folder: str

    :param first: The first signed file, required.
    :type first: str

    :param second: The second signed file, optional.
    :type second: str
    """
    if first is None:
        print("No OS!")
        raise SystemError
    try:
        pseudocap.make_autoloader(filename, [first, second], folder=folder)
    except (OSError, IndexError, SystemError) as exc:
        msg = "Could not create {0}".format(filename)
        exceptions.handle_exception(exc, msg, None)


def generate_skeletons():
    """
    Read JSON to get a dict of all filename components.
    """
    namelist = {0: None, 1: None, 2: None, 3: None, 4: None, 5: None, 6: None}
    data = jsonutils.load_json('integermap')
    for key in data:
        if key['id'] in namelist:
            namelist[key['id']] = (key['parts'])
            namelist[key['id']].append(".exe")
    return namelist


def generate_device(radio):
    """
    Read JSON to get the device integer ID from device radio.

    :param radio: The radio filename to look up.
    :type radio: str
    """
    data = jsonutils.load_json('integermap')
    for key in data:
        if key['radtype'] in radio:
            idx = int(key['id'])
            break
    return idx


def generate_filename(device, version, suffix=None):
    """
    Use skeleton dict to create loader filenames.

    :param device: Device to use.
    :type device: int

    :param version: OS or radio version.
    :type version: str

    :param suffix: Alternate radio, or blank.
    :type suffix: str
    """
    thed = generate_skeletons()
    if device < 0:
        return None
    dev = thed[device]
    if suffix is None:
        suffix = ""
    return "{0}{1}{2}{3}{4}".format(dev[0], version, suffix, dev[1], dev[2])


def generate_lazy_loader(
        osversion, device,
        localdir=None, altradio=None, core=False):
    """
    Create and label autoloaders for :mod:`bbarchivist.scripts.lazyloader`.
    :func:`generate_loaders`, but for making one OS/radio loader.

    :param osversion: OS version, 10.x.y.zzzz.
    :type osversion: str

    :param device: Selected device, from
    :type device: int

    :param localdir: Working path. Default is local dir.
    :type localdir: str

    :param altradio: The alternate radio in use, if there is one.
    :type altradio: str

    :param core: If we're using a core OS image. Default is false.
    :type core: bool
    """
    # default parsing
    localdir = utilities.dirhandler(localdir, os.getcwd())
    print("CREATING LOADER...")
    suffix = format_suffix(bool(altradio), altradio, core)
    osfile = None
    absoglob = "{0}{1}".format(localdir, os.sep)
    try:
        osfile = str(glob.glob("{0}*_sfi*.signed".format(absoglob))[0])
    except IndexError:
        print("No OS found")
    else:
        generate_lazy_set(osversion, device, osfile, suffix, absoglob, localdir)


def generate_lazy_set(osversion, device, osfile, suffix, absoglob, localdir=None):
    """
    Get radio file and then generate autoloader.

    :param osversion: OS version, 10.x.y.zzzz.
    :type osversion: str

    :param device: Selected device, from
    :type device: int

    :param osfile: OS signed filename.
    :type osfile: str

    :param suffix: Loader name suffix.
    :type suffix: str

    :param absoglob: Local path + path separator.
    :type absoglob: str

    :param localdir: Working path. Default is local dir.
    :type localdir: str
    """
    radiofile = None
    try:
        sset = set(glob.glob("{0}*.signed".format(absoglob)))
        rset = sset - set(glob.glob("{0}*_sfi*.signed".format(absoglob)))
        radiofile = str(list(rset)[0])
    except IndexError:
        print("No radio found")
    else:
        loadername = generate_lazy_filename(osversion, suffix, device)
        wrap_pseudocap(loadername, localdir, osfile, radiofile)


def generate_lazy_filename(osversion, suffix, device):
    """
    Read JSON to formulate a single filename.

    :param osversion: OS version.
    :type osversion: str

    :param suffix: Alternate radio, or just blank.
    :type suffix: str

    :param device: Device to use.
    :type device: int
    """
    data = jsonutils.load_json('integermap')
    for key in data:
        if key['id'] == device:
            fname = key['parts']
            break
    return "{0}{1}{2}{3}.exe".format(fname[0], osversion, suffix, fname[1])


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
    shutil.copy(os.path.join(inpath, filename), os.path.join(outpath, filename))


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


def generate_tclloader_mbn(mdnin, mdnout):
    """
    Generate mbn files.

    :param mdnin: Directory containing files to copy.
    :type mdnin: str

    :param mdnout: Directory that files are to be copied to.
    :type mdnout: str
    """
    files = ["devcfg.mbn", "devcfg_cn.mbn", "rpm.mbn", "tz.mbn"]
    point_point_bulk(mdnin, mdnout, files)


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
        oems = ["oem_att", "oem_china", "oem_common", "oem_sprint", "oem_vzw", "oem_indonesia"]
        radios = ["china", "dschina", "emea", "global", "india", "japan", "usa"]
    elif platform == "bbry_qc8953krypton":  # Motion
        oems = ["oem_att", "oem_common", "oem_sprint"]
        radios = ["americas", "cdma", "dscn", "dsglobal", "ssglobal"]
    return oems, radios


def generate_tclloader_looseends(imgout, platform):
    """
    Rename files that need to be renamed.

    :param imgout: Directory that files are to be copied to.
    :type imgout: str

    :param platform: Platform type (i.e. subdirectory of target/product).
    :type platform: str
    """
    if platform == "bbry_qc8953":  # KEYone
        pass  # no special exceptions
    elif platform == "bbry_qc8953krypton":  # Motion
        oldglobal = os.path.join(imgout, "NON-HLOS-ssglobal.bin")
        newglobal = os.path.join(imgout, "NON-HLOS-global.bin")
        os.rename(oldglobal, newglobal)  # SS intl model has different name than modem
        oldamericas = os.path.join(imgout, "NON-HLOS-americas.bin")
        newamericas = os.path.join(imgout, "NON-HLOS-dsamericas.bin")
        shutil.copy(oldamericas, newamericas)  # DS/SS americas model use same modem


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
    imgs = ["recovery", "system", "userdata", "cache", "boot"]
    point_point_bulk(imgin, imgout, ["{0}.img".format(img) for img in imgs])
    oems, radios = generate_tclloader_deps(platform)
    oems = generate_tclloader_oemfilt(imgin, oems)
    point_point_bulk(imgin, imgout, ["{0}.img".format(oem) for oem in oems])
    radios = generate_tclloader_radfilt(imgin, radios)
    point_point_bulk(imgin, imgout, ["NON-HLOS-{0}.bin".format(rad) for rad in radios])
    others = ["adspso.bin", "emmc_appsboot.mbn", "sbl1_signed.mbn"]
    point_point_bulk(imgin, imgout, others)
    generate_tclloader_looseends(imgout, platform)


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
    generate_tclloader_script(dirname, bbconstants.FLASHBAT.location, bbconstants.FLASHSH.location, wipe)
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
    generate_tclloader_mbn(qdir, imgdir)

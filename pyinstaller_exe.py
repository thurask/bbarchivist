#!/usr/bin/env python3

from os import remove, listdir, devnull
from os.path import join, dirname, basename
from shutil import copy, rmtree
from subprocess import call, STDOUT
from requests import certs, get
from bbarchivist.bbconstants import VERSION, LONGVERSION, CAP, JSONFILE, COMMITDATE
from bbarchivist.utilities import prep_seven_zip, get_seven_zip


def write_versions():
    """
    Write temporary version files.
    """
    with open("version.txt", "w") as afile:
        afile.write(VERSION)
    with open("longversion.txt", "w") as afile:
        afile.write("{0}\n{1}".format(LONGVERSION, COMMITDATE))


def clean_versions():
    """
    Remove temporary version files.
    """
    remove("version.txt")
    remove("longversion.txt")


def get_sevenzip():
    """
    Get 7-Zip.
    """
    szurl = "http://www.7-zip.org/a/7z1604-extra.7z"
    psz = prep_seven_zip()
    if psz:
        szexe = get_seven_zip()
        szfile = basename(szurl)
        with open(szfile, "wb") as afile:
            req = get(szurl, stream=True)
            for chunk in req.iter_content(chunk_size=1024):
                afile.write(chunk)
        cmd = "{0} x {1} -o7z".format(szexe, szfile)
        with open(devnull, "wb") as dnull:
            call(cmd, stdout=dnull, stderr=STDOUT, shell=True)
        remove(basename(szurl))
    else:
        print("GO TO {0} AND DO IT MANUALLY".format(szurl))
        raise SystemError


if __name__ == "__main__":
    write_versions()
    specs = [x for x in listdir() if x.endswith(".spec")]
    for spec in specs:  # UPX 3.91 BSODs my computer, disable for now
        cmd = "pyinstaller --onefile --noupx --workpath pyinst-build --distpath pyinst-dist {0}".format(spec)
        call(cmd, shell=True)
    outdir = "pyinst-dist"
    copy("version.txt", outdir)
    copy("longversion.txt", outdir)
    copy(CAP.location, outdir)
    copy(JSONFILE, outdir)
    copy(certs.where(), join(outdir, "cacerts.pem"))
    try:
        get_sevenzip()
    except SystemError:
        pass
    else:
        copy(join("7z", "7za.exe"), outdir)
        copy(join("7z", "x64", "7za.exe"), join(outdir, "7za64.exe"))
        rmtree("7z", ignore_errors=True)
    clean_versions()

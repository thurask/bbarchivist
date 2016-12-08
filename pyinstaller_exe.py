#!/usr/bin/env python3

from os import remove, listdir, devnull, getcwd
from os.path import join, basename
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


def generate_specs():
    """
    Generate pyinstaller spec files.
    """
    scripts = ["archivist", "autolookup", "barlinker", "carrierchecker", "certchecker", "devloader", "downloader", "droidlookup", "droidscraper", "escreens", "kernchecker", "lazyloader", "linkgen", "metachecker", "swlookup"]
    here = getcwd().replace("\\", "\\\\")
    for script in scripts:
        template = "# -*- mode: python -*-\n\nblock_cipher = None\n\n\na = Analysis(['bbarchivist\\\\scripts\\\\{0}.py'],\n             pathex=['{1}'],\n             binaries=None,\n             datas=None,\n             hiddenimports=[],\n             hookspath=[],\n             runtime_hooks=[],\n             excludes=[],\n             win_no_prefer_redirects=False,\n             win_private_assemblies=False,\n             cipher=block_cipher)\npyz = PYZ(a.pure, a.zipped_data,\n             cipher=block_cipher)\nexe = EXE(pyz,\n          a.scripts,\n          a.binaries,\n          a.zipfiles,\n          a.datas,\n          name='{0}',\n          debug=False,\n          strip=False,\n          upx=False,\n          console=True )\n".format(script, here)
        with open("{0}.spec".format(script), "w") as afile:
            afile.write(template)


def clean_specs():
    """
    Remove pyinstaller spec files.
    """
    specs = [x for x in listdir() if x.endswith(".spec")]
    for spec in specs:
        remove(spec)


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
    generate_specs()
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
    clean_specs()

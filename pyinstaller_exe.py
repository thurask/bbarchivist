#!/usr/bin/env python3
"""Generate .exe files with PyInstaller."""

from os import remove, listdir, devnull, getcwd, makedirs
from os.path import join, basename, exists
from platform import architecture
from shutil import copy, rmtree, copytree
from subprocess import call, STDOUT
from requests import certs, get
from bbarchivist.bbconstants import VERSION, LONGVERSION, CAP, JSONDIR, COMMITDATE
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


def bitsdir(indir):
    """
    Create directories based on indir segregated on bit type.

    :param indir: Directory to modify.
    :type indir: str
    """
    if architecture()[0] == "64bit":
        indirx = "{0}-64".format(indir)
    else:
        indirx = indir
    if exists(indirx):
        clean_outdir(indirx)
    makedirs(indirx)
    return indirx


def get_ucrt_dlls():
    """
    Get some magic voodoo Windows DLLs.
    """
    tail = "x64" if architecture()[0] == "64bit" else "x86"
    folder = join("C:\\", "Program Files (x86)", "Windows Kits", "10", "Redist", "ucrt", "DLLs", tail)
    return folder


def generate_specs():
    """
    Generate pyinstaller spec files.
    """
    scripts = ["archivist", "autolookup", "barlinker", "carrierchecker", "certchecker", "devloader", "downloader", "droidlookup", "droidscraper", "escreens", "kernchecker", "lazyloader", "linkgen", "metachecker", "swlookup", "tclscan", "tcldelta"]
    here = getcwd().replace("\\", "\\\\")
    dlldir = get_ucrt_dlls().replace("\\", "\\\\")
    for script in scripts:
        template = "# -*- mode: python -*-\n\nblock_cipher = None\n\n\na = Analysis(['bbarchivist\\\\scripts\\\\{0}.py'],\n             pathex=['{1}', '{2}'],\n             binaries=None,\n             datas=None,\n             hiddenimports=[],\n             hookspath=[],\n             runtime_hooks=[],\n             excludes=[],\n             win_no_prefer_redirects=False,\n             win_private_assemblies=False,\n             cipher=block_cipher)\npyz = PYZ(a.pure, a.zipped_data,\n             cipher=block_cipher)\nexe = EXE(pyz,\n          a.scripts,\n          a.binaries,\n          a.zipfiles,\n          a.datas,\n          name='{0}',\n          debug=False,\n          strip=False,\n          upx=False,\n          console=True )\n".format(script, here, dlldir)
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
    szver = "1701"
    szurl = "http://www.7-zip.org/a/7z{0}-extra.7z".format(szver)
    psz = prep_seven_zip()
    if psz:
        get_sevenzip_write(szurl)
    else:
        print("GO TO {0} AND DO IT MANUALLY".format(szurl))
        raise SystemError


def get_sevenzip_write(szurl):
    """
    Download 7-Zip file.

    :param szurl: Link to 7z download.
    :type szurl: str
    """
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


def call_specs(distdir, builddir):
    """
    Call pyinstaller to make specs.

    :param distdir: Path to distribute files.
    :type distdir: str

    :param builddir: Path to build files.
    :type builddir: str
    """
    specs = [x for x in listdir() if x.endswith(".spec")]
    for spec in specs:  # use UPX 3.93 or up
        cmd = "pyinstaller --onefile --workpath {2} --distpath {1} {0}".format(spec, distdir, builddir)
        call(cmd, shell=True)


def sz_wrapper(outdir):
    """
    Copy 7-Zip to outdir.

    :param outdir: Output directory.
    :type outdir: str
    """
    try:
        get_sevenzip()
    except SystemError:
        pass
    else:
        sz_wrapper_writer(outdir)


def sz_wrapper_writer(outdir):
    """
    Copy 7-Zip to outdir, the actual function.

    :param outdir: Output directory.
    :type outdir: str
    """
    copy(join("7z", "7za.exe"), outdir)
    if architecture()[0] == "64bit":
        copy(join("7z", "x64", "7za.exe"), join(outdir, "7za64.exe"))
    rmtree("7z", ignore_errors=True)


def copy_json(outdir):
    """
    Copy JSON folder to outdir.

    :param outdir: Output directory.
    :type outdir: str
    """
    copytree(JSONDIR, join(outdir, "json"))


def clean_outdir(outdir):
    """
    Nuke outdir, if it exists.

    :param outdir: Output directory.
    :type outdir: str
    """
    if exists(outdir):
        rmtree(outdir, ignore_errors=True)


def main():
    """
    Create .exes with dynamic spec files.
    """
    outdir = bitsdir("pyinst-dist")
    builddir = bitsdir("pyinst-build")
    write_versions()
    generate_specs()
    call_specs(outdir, builddir)
    copy("version.txt", outdir)
    copy("longversion.txt", outdir)
    copy(CAP.location, outdir)
    copy_json(outdir)
    copy(certs.where(), join(outdir, "cacerts.pem"))
    sz_wrapper(outdir)
    clean_versions()
    clean_specs()


if __name__ == "__main__":
    main()

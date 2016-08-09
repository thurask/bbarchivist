#!/usr/bin/env python3

from os import remove
from os.path import join, abspath, dirname
from sys import exec_prefix
from cx_Freeze import setup, Executable
from requests import certs
from bbarchivist.bbconstants import VERSION, LONGVERSION, CAP, JSONFILE, COMMITDATE


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


if __name__ == "__main__":
    # Dependencies are automatically detected, but it might need
    # fine tuning.
    localdir = join(dirname(abspath(__file__)), r"bbarchivist\scripts")
    sq3dll = join(exec_prefix, "DLLs", "sqlite3.dll")
    build_options = dict(packages=["requests", "bbarchivist", "bs4", "gnupg", "simplejson"],
                         includes=[],
                         include_files=[
                             ("version.txt", "version.txt"),
                             ("longversion.txt", "longversion.txt"),
                             (certs.where(), 'cacert.pem'),
                             (CAP.location, CAP.filename),
                             (JSONFILE, "bbconstants.json"),
                             (sq3dll, "sqlite3.dll")  # manual override
                             ],
                         excludes=[
                             "rsa",
                             "pywin32",
                             "pytz",
                             "Pillow",
                             "ecdsa",
                             "amqp",
                             "pydoc",
                             "pyasn1",
                             "distutils",
                             "PyQt5",
                             "numpy",
                             "matplotlib",
                             "PIL",
                             "tk",
                             "tkinter"
                             ],
                         include_msvcr=[True],
                         build_exe="lazyloader",
                         zip_includes=[])

    base = 'Console'
    executables = [
        Executable(join(localdir, 'lazyloader.py'), base=base, targetName="lazyloader.exe"),
        Executable(join(localdir, 'archivist.py'), base=base, targetName="archivist.exe"),
        Executable(join(localdir, 'certchecker.py'), base=base, targetName="certchecker.exe"),
        Executable(join(localdir, 'carrierchecker.py'), base=base, targetName="cchecker.exe"),
        Executable(join(localdir, 'autolookup.py'), base=base, targetName="autolookup.exe"),
        Executable(join(localdir, 'linkgen.py'), base=base, targetName="linkgen.exe"),
        Executable(join(localdir, 'kernchecker.py'), base=base, targetName="kernchecker.exe"),
        Executable(join(localdir, 'escreens.py'), base=base, targetName="escreens.exe"),
        Executable(join(localdir, 'droidlookup.py'), base=base, targetName="droidlookup.exe"),
        Executable(join(localdir, 'metachecker.py'), base=base, targetName="metachecker.exe"),
        Executable(join(localdir, 'devloader.py'), base=base, targetName="devloader.exe")
    ]

    write_versions()
    setup(name='bbarchivist',
          version=VERSION,
          description='bbarchivist {0}'.format(VERSION),
          options=dict(build_exe=build_options),
          executables=executables)
    clean_versions()

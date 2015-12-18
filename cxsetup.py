#!/usr/bin/env python3
#pylint: disable = I0011, C0111, C0103, W0622

from os import chdir
from os.path import join, abspath, dirname
from sys import exec_prefix
from cx_Freeze import setup, Executable
from requests import certs
from bbarchivist.bbconstants import VERSION, CAPLOCATION, CAPVERSION, JSONFILE, CFPLOCATION, CFPVERSION

# Dependencies are automatically detected, but it might need
# fine tuning.
localdir = join(dirname(abspath(__file__)), r"bbarchivist\scripts")
sq3dll = join(exec_prefix, "DLLs", "sqlite3.dll")
build_options = dict(packages=["requests",
                               "bbarchivist",
                               "bs4",
                               "gnupg"],
                     includes=[],
                     include_files=[
                         (certs.where(), 'cacert.pem'),
                         (CAPLOCATION, "cap-" + CAPVERSION + ".dat"),
                         (JSONFILE, "bbconstants.json"),
                         (sq3dll, "sqlite3.dll")  # manual override
                         ],
                     excludes=["rsa",
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
                               "tk"],
                     include_msvcr=[True],
                     build_exe="lazyloader",
                     zip_includes=[])

base = 'Console'

executables = [
    Executable(join(localdir, 'lazyloader.py'),
               base=base,
               targetName="lazyloader.exe"),
    Executable(join(localdir, 'archivist.py'),
               base=base,
               targetName="archivist.exe"),
    Executable(join(localdir, 'certchecker.py'),
               base=base,
               targetName="certchecker.exe"),
    Executable(join(localdir, 'carrierchecker.py'),
               base=base,
               targetName="cchecker.exe"),
    Executable(join(localdir, 'autolookup.py'),
               base=base,
               targetName="autolookup.exe"),
    Executable(join(localdir, 'linkgen.py'),
               base=base,
               targetName="linkgen.exe"),
    Executable(join(localdir, 'kernchecker.py'),
               base=base,
               targetName="kernchecker.exe"),
    Executable(join(localdir, 'escreens.py'),
               base=base,
               targetName="escreens.exe")
]

setup(name='bbarchivist',
      version=VERSION,
      description='bbarchivist ' + VERSION,
      options=dict(
          build_exe=build_options),
      executables=executables)

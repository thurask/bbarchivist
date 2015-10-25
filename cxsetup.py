#!/usr/bin/env python3
#pylint: disable = I0011, C0111, C0103, W0622

from cx_Freeze import setup, Executable
from os import chdir
from os.path import join, abspath, dirname
from requests import certs
from bbarchivist.bbconstants import VERSION, CAPLOCATION, CAPVERSION, JSONFILE

# Dependencies are automatically detected, but it might need
# fine tuning.
localdir = dirname(abspath(__file__))
localdir = join(localdir, r"bbarchivist\scripts")
build_options = dict(packages=["requests",
                               "bbarchivist",
                               "easygui",
                               "bs4"],
                     includes=[],
                     include_files=[
                         (certs.where(), 'cacert.pem'),
                         (CAPLOCATION, "cap-" + CAPVERSION + ".dat"),
                         (JSONFILE, "bbconstants.json")
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
                               "PIL"],
                     include_msvcr=[True],
                     build_exe="lazyloader",
                     zip_includes=[])

base = 'Console'

chdir(localdir)

executables = [
    Executable('lazyloader.py',
               base=base,
               targetName="lazyloader.exe")
]

setup(name='lazyloader',
      version=VERSION,
      description='Lazyloader ' + VERSION,
      options=dict(
          build_exe=build_options),
      executables=executables)

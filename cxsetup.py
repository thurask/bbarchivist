from cx_Freeze import setup, Executable
from os import chdir
from os.path import join, abspath, dirname
from requests import certs
from bbarchivist.bbconstants import VERSION, CAPLOCATION, CAPVERSION

# Dependencies are automatically detected, but it might need
# fine tuning.
localdir = dirname(abspath(__file__))
localdir = join(localdir, "bbarchivist")
buildOptions = dict(packages=["requests",
                              "bbarchivist",
                              "easygui"],
                    includes=[],
                    include_files=[
                   (certs.where(), 'cacert.pem'),
                   (CAPLOCATION, "cap-" + CAPVERSION + ".dat")
                   ],
    excludes=["rsa",
              "pywin32",
              "pytz",
              "Pillow",
              "ecdsa",
              "amqp",
              "pydoc",
              "pyasn1",
              "distutils"],
    include_msvcr=[True],
    build_exe="lazyloader",
    zip_includes=[])

base = 'Console'

chdir(localdir)

executables = [
    Executable('lazyloader_gui.py',
               base=base,
               appendScriptToExe=True,
               appendScriptToLibrary=True,
               targetName="lazyloader.exe")
]

setup(name='lazyloader',
      version=VERSION,
      description='Lazyloader ' + VERSION,
      options=dict(
          build_exe=buildOptions),
      executables=executables)

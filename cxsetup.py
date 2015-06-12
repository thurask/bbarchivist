from cx_Freeze import setup, Executable
from os import chdir
from os.path import join, abspath, dirname
from requests import certs
from bbarchivist.bbconstants import VERSION, CAPLOCATION

# Dependencies are automatically detected, but it might need
# fine tuning.
localdir = dirname(abspath(__file__))
localdir = join(localdir, "bbarchivist")
buildOptions = dict(packages=["requests",
                              "bbarchivist"],
                    includes=[
    join(localdir, "lazyloader_wrap.py"),
    join(localdir, "lazyloader.py"),
    join(localdir, "bbconstants.py"),
    join(localdir, "utilities.py"),
    join(localdir, "barutils.py"),
    join(localdir, "networkutils.py"),
    join(localdir, "loadergen.py"),
    join(localdir, "pseudocap.py")
],
    include_files=[CAPLOCATION,
                   (certs.where(), 'cacert.pem')],
    excludes=[],
    include_msvcr=[True],
    build_exe="lazyloader",
    zip_includes=[
    join(localdir, "lazyloader_wrap.py"),
    join(localdir, "lazyloader.py"),
    join(localdir, "bbconstants.py"),
    join(localdir, "utilities.py"),
    join(localdir, "barutils.py"),
    join(localdir, "networkutils.py"),
    join(localdir, "loadergen.py"),
    join(localdir, "pseudocap.py"),
    (certs.where(), 'cacert.pem')
])

base = 'Console'

chdir(localdir)

executables = [
    Executable('lazyloader_wrap.py',
               base=base,
               appendScriptToExe=True,
               appendScriptToLibrary=True)
]

setup(name='lazyloader',
      version=VERSION,
      description='A REALLY lazy autoloader maker',
      options=dict(
          build_exe=buildOptions),
      executables=executables)

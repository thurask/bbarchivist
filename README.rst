README
======

.. image:: https://pypip.in/download/bbarchivist/badge.svg?period=day
    :target: https://pypi.python.org/pypi/bbarchivist
    :alt: Downloads

.. image:: https://pypip.in/download/bbarchivist/badge.svg?period=week
    :target: https://pypi.python.org/pypi/bbarchivist
    :alt: Downloads
    
.. image:: https://pypip.in/download/bbarchivist/badge.svg?period=month
    :target: https://pypi.python.org/pypi/bbarchivist
    :alt: Downloads
    
.. image:: https://pypip.in/py_versions/bbarchivist/badge.svg
    :target: https://pypi.python.org/pypi/bbarchivist
    :alt: Supported Python versions

.. image:: https://pypip.in/version/bbarchivist/badge.svg?text=version
    :target: https://pypi.python.org/pypi/bbarchivist
    :alt: Latest Version
    
.. image:: https://pypip.in/wheel/bbarchivist/badge.svg
    :target: https://pypi.python.org/pypi/bbarchivist
    :alt: Wheel Status


A Python 3 package to download bars and turn them into autoloaders.
Subsumes `archivist <https://github.com/thurask/archivist>`__ and
`lazyloader <https://github.com/thurask/lazyloader>`__.

With command line arguments, it proceeds as directed. Without command
line arguments, it queries the user as to OS version, radio version,
software version, etc. Most arguments are assumed with the
questionnaire, so if you want fine control, use arguments.

This can be used either as importing bbarchivist., or the bb-archivist
and bb-lazyloader scripts from a command line.

Requirements
------------

Universal
~~~~~~~~~

Requires Python >=3.4. Install the latest.

To get this package, install with pip:

::

    $ pip install bbarchivist

On POSIX, type that in your command line. For Windows, I recommend
`pip-win <https://sites.google.com/site/pydatalog/python/pip-for-windows>`__.

A copy of cap.exe is included with this script.

Since it does the entire autoloader process for all devices from start
to finish, make sure to have A LOT of hard drive space. 40GB at least,
even more if you aren't using 7-Zip compression.

It also requires the
`requests <http://docs.python-requests.org/en/latest/user/install/>`__
library installed somehow. Installation with pip does this
automatically, or use your package manager's version.

7-Zip compression (default) uses
`p7zip <http://sourceforge.net/projects/p7zip/>`__
(Linux/Mac)/`7-Zip <http://www.7-zip.org/download.html>`__ (Windows).
Zip and tar.xxx compression don't require external programs.

Windows
~~~~~~~

To use 7-Zip compression, have 7-Zip installed. If not, make sure to
specify a non-7-Zip compression method when invoking the script.

Linux
~~~~~

If you're using 7z compression, this requires p7zip (look through your
package manager, or install from source) in your path. I.e.:

::

    $ which 7za

resolves to something.

Your package manager should also have a python-requests package
available. If not, or if you want the latest, compile from source. Or
use pip.

Other than that, install this with pip.

Mac
~~~

Same as Linux, but you'll have to either install p7zip from source, or
install it with something like `Homebrew <http://brew.sh>`__ or
`MacPorts <https://www.macports.org>`__.

What It Does
------------

Archivist
~~~~~~~~~

1. Ask for OS/radio/software versions (if not specified)
2. Ask for compression of loaders/deletion of uncompressed
   loaders/verification of loaders (if not specified)
3. Download all bars
4. Extract all bars
5. Make OS + radio (and radio-only loaders if specified) for each
   recognized signed file
6. Compress them (optional)
7. Sort bars and loaders into subfolders
8. Delete uncompressed loaders (optional)
9. Verify loaders (optional)

Lazyloader
~~~~~~~~~~

1. Ask for OS/radio/software versions, device type (if not specified)
2. Download the right OS/radio bar based on above input/specification
3. Extract bars
4. Create autoloader
5. Ask to load autoloader (Windows only)

Command Line Arguments
----------------------

Help
~~~~

::

    > bb-archivist -h

    usage: bb-archivist [-h] [-v] [-f DIR] [-c PATH] [-no] [-nx] [-nl] [-nr] [-ns]
                 [-nc] [-nd] [-nv] [--crc32] [--adler32] [--md4] [--sha224]
                 [--sha384] [--sha512] [--ripemd160] [--no-sha1] [--no-sha256]
                 [--no-md5] [--7z | --tgz | --tbz | --txz | --zip]
                 os radio swrelease

    Download bar files, create autoloaders.

    positional arguments:
      os                    OS version, 10.x.y.zzzz
      radio                 Radio version, 10.x.y.zzzz
      swrelease             Software version, 10.x.y.zzzz

    optional arguments:
      -h, --help            show this help message and exit
      -v, --version         show program's version number and exit
      -f DIR, --folder DIR  Working folder
      -c PATH, --cap PATH   Path to cap.exe

    negators:
      Disable program functionality

      -no, --no-download    Don't download files
      -nx, --no-extract     Don't extract bar files
      -nl, --no-loaders     Don't create autoloaders
      -nr, --no-radios      Don't make radio autoloaders
      -ns, --no-rmsigned    Don't remove signed files
      -nc, --no-compress    Don't compress loaders
      -nd, --no-delete      Don't delete uncompressed loaders
      -nv, --no-verify      Don't verify created loaders

    verifiers:
      Verification methods

      --crc32               Enable CRC32 verification
      --adler32             Enable Adler-32 verification
      --md4                 Enable MD4 verification
      --sha224              Enable SHA-224 verification
      --sha384              Enable SHA-384 verification
      --sha512              Enable SHA-512 verification
      --ripemd160           Enable RIPEMD-160 verification
      --no-sha1             Disable SHA-1 verification
      --no-sha256           Disable SHA-256 verification
      --no-md5              Disable MD5 verification

    compressors:
      Compression methods

      --7z                  Compress with 7z, LZMA2
      --tgz                 Compress with tar, GZIP
      --tbz                 Compress with tar, BZIP2
      --txz                 Compress with tar, LZMA
      --zip                 Compress with zip, DEFLATE

    http://github.com/thurask/bbarchivist

----------------------------------------

::

    > bb-lazyloader -h

    usage: bb-lazyloader-script.py [-h] [-v]
                               (--stl100-1 | --stl100-x | --stl100-4 | --q10 | --z30 | --z3 | --passport)
                               [--run-loader]
                               os radio swrelease

    Create one autoloader for personal use.

    positional arguments:
      os             OS version, 10.x.y.zzzz
      radio          Radio version, 10.x.y.zzzz
      swrelease      Software version, 10.x.y.zzzz

    optional arguments:
      -h, --help     show this help message and exit
      -v, --version  show program's version number and exit
      --run-loader   Run autoloader after creation

    devices:
      Device to load (one required)

      --stl100-1     STL100-1
      --stl100-x     STL100-2/3, P'9982
      --stl100-4     STL100-4
      --q10          Q10, Q5, P'9983
      --z30          Z30, Classic, Leap
      --z3           Z3
      --passport     Passport

    http://github.com/thurask/bbarchivist

Example
~~~~~~~

::

    > bb-archivist 10.3.1.2726 10.3.1.2727 10.3.1.1877 -nr --sha512 --no-md5

would make OS-only autoloaders for OS 10.3.1.2726/radio 10.3.1.2727
(software release 10.3.1.1877), compress them, delete uncompressed
loaders and verify with SHA-1, SHA-256, SHA-512.

::

    > bb-lazyloader 10.3.1.1955 10.3.1.1956 10.3.1.1372 --passport --run-autoloader

would create a Passport autoloader for OS 10.3.1.1955/radio 10.3.1.1956
(software release 10.3.1.1372), and run it (Windows only).

License
-------

No fancy licensing here, just fork this and do whatever. Although, if
you figure out something interesting, please do try to put it upstream
via pull request.

Authors
-------

-  `Thurask <https://twitter.com/thuraski>`__
-  Viewers Like You

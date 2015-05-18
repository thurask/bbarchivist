README
======
    
.. image:: https://img.shields.io/pypi/dd/bbarchivist.svg
    :target: https://pypi.python.org/pypi/bbarchivist
    :alt: Downloads/day

.. image:: https://img.shields.io/pypi/v/bbarchivist.svg?label=release
    :target: https://pypi.python.org/pypi/bbarchivist
    :alt: Pypi version
    
.. image:: https://img.shields.io/github/tag/thurask/bbarchivist.svg?label=source
    :target: https://github.com/thurask/bbarchivist
    :alt: GitHub version

.. image:: https://img.shields.io/github/issues/thurask/bbarchivist.svg
    :target: https://github.com/thurask/bbarchivist
    :alt: GitHub issues
    
.. image:: https://img.shields.io/github/forks/thurask/bbarchivist.svg
    :target: https://github.com/thurask/bbarchivist
    :alt: GitHub forks
    
.. image:: https://img.shields.io/github/stars/thurask/bbarchivist.svg
    :target: https://github.com/thurask/bbarchivist
    :alt: GitHub stars

A Python 3 package to download bars and turn them into autoloaders.
Includes support scripts.
Subsumes `archivist <https://github.com/thurask/archivist>`__ and
`lazyloader <https://github.com/thurask/lazyloader>`__. Don't use those anymore.

With command line arguments, it proceeds as directed. Without command
line arguments, it queries the user as to OS version, radio version,
software version, etc. Most arguments are assumed with the
questionnaire, so if you want fine control, use arguments.

This can be used either as importing the bbarchivist module, or the scripts from a command line.

Requirements
------------

Universal
~~~~~~~~~

Requires Python >=3.2. Install the latest, though.

To get this package, install with pip:

::

    $ pip install bbarchivist

On POSIX, type that in your command line. For Windows, I recommend
`pip-win <https://sites.google.com/site/pydatalog/python/pip-for-windows>`__.

A copy of cap.exe is included with this script.

Since archivist does the entire autoloader process for all devices from start
to finish, make sure to have A LOT of hard drive space. 40GB at least,
even more if you aren't using 7-Zip compression. Other processes require several GB,
but not 40.

It also requires the
`requests <http://docs.python-requests.org/en/latest/user/install/>`__
library installed somehow. Installation with pip does this
automatically, or use your package manager's version.

PGP support requires the
`python-gnupg <https://pythonhosted.org/python-gnupg/index.html>`__
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

CarrierChecker
~~~~~~~~~~~~~~

1. Ask for MCC, MNC, devicename (if not specified)
2. Check which OS release is available with given conditions
3. Download (if specified)

FileHasher
~~~~~~~~~~

1. Ask for hash types (if not specified)
2. Apply given hash functions for all files in local/a given directory
3. Output results to an "all.cksum" file

EScreens
~~~~~~~~

1. Ask for PIN, OS version, uptime, duration (if not specified)
2. Return EScreens key for given values

LinkGen
~~~~~~~

1. Ask for OS version, radio version, software version (if not specified)
2. Write debrick/core/radio links to file

GPGRunner
~~~~~~~~~

1. Ask for PGP key ID, passphrase (if not specified)
2. Verify all files in local/given folder

Autolookup
~~~~~~~~~~

1. Ask for OS version, whether to loop (if not specified)
2. Return lookup/availability for given OS (if lookup is valid)

Command Line Arguments
----------------------

Help
~~~~

::

    > bb-archivist -h

    usage: bb-archivist [-h] [-v] [-f DIR] [-c PATH] [-no] [-nx] [-nl] [-nr] [-ns]
                    [-nc] [-nd] [-nv] [--crc32] [--adler32] [--md4] [--sha224]
                    [--sha384] [--sha512] [--ripemd160] [--whirlpool]
                    [--no-sha1] [--no-sha256] [--no-md5] [-a] [-g]
                    [--7z | --tgz | --tbz | --txz | --zip]
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
	  -g, --gpg             Enable GPG signing. Set up GnuPG.

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
	  --whirlpool           Enable Whirlpool verification
	  --no-sha1             Disable SHA-1 verification
	  --no-sha256           Disable SHA-256 verification
	  --no-md5              Disable MD5 verification
	  -a, --all             Use all methods

	compressors:
	  Compression methods

	  --7z                  Compress with 7z, LZMA2
	  --tgz                 Compress with tar, GZIP
	  --tbz                 Compress with tar, BZIP2
	  --txz                 Compress with tar, LZMA (py3.3+)
	  --zip                 Compress with zip, DEFLATE

	http://github.com/thurask/bbarchivist


----------------------------------------

::

    > bb-lazyloader -h

    usage: bb-lazyloader [-h] [-v]
                     (--stl100-1 | --stl100-x | --stl100-4 | --q10 | --z30 | --z3 | --passport)
                     [--run-loader] [-f DIR]
                     os radio swrelease

    Create one autoloader for personal use.
    
    positional arguments:
      os                    OS version, 10.x.y.zzzz
      radio                 Radio version, 10.x.y.zzzz
      swrelease             Software version, 10.x.y.zzzz
    
    optional arguments:
      -h, --help            show this help message and exit
      -v, --version         show program's version number and exit
      --run-loader          Run autoloader after creation
      -f DIR, --folder DIR  Working folder
    
    devices:
      Device to load (one required)
    
      --stl100-1            STL100-1
      --stl100-x            STL100-2/3, P'9982
      --stl100-4            STL100-4
      --q10                 Q10, Q5, P'9983
      --z30                 Z30, Classic, Leap
      --z3                  Z3
      --passport            Passport
    
    http://github.com/thurask/bbarchivist

----------------------------------------

::

    > bb-cchecker -h

    usage: bb-cchecker [-h] [-v] [-a] [-d] [-e] [-u | -r] [-f DIR] [-b]
                       mcc mnc device
    
    Checks a carrier for an OS version, can download.
    
    positional arguments:
      mcc                   1-3 digit country code
      mnc                   1-3 digit carrier code
      device                'STL100-1', 'SQW100-3', etc.
    
    optional arguments:
      -h, --help            show this help message and exit
      -v, --version         show program's version number and exit
      -a, --available-bundles
                            Check available bundles
      -d, --download        Download files after checking
      -e, --export          Export links to files
      -f DIR, --folder DIR  Working folder
      -b, --blitz           Create blitz package
    
    bartypes:
      File types
    
      -u, --upgrade         Upgrade instead of debrick bars
      -r, --repair          Debrick instead of upgrade bars
    
    http://github.com/thurask/bbarchivist
    
----------------------------------------

::

    > bb-filehasher -h
    
    usage: bb-filehasher [-h] [-v] [-b INT] [--crc32] [--adler32] [--md4]
                     [--sha224] [--sha384] [--sha512] [--ripemd160]
                     [--whirlpool] [--no-sha1] [--no-sha256] [--no-md5] [-a]
                     [folder]

    Applies hash functions to files. Default: SHA-1, SHA-256, MD5
    
    positional arguments:
      folder               Working directory, default is local
    
    optional arguments:
      -h, --help           show this help message and exit
      -v, --version        show program's version number and exit
      -b INT, --block INT  Blocksize (bytes), default = 16777216 (16MB)
    
    verifiers:
      Verification methods
    
      --crc32              Enable CRC32 verification
      --adler32            Enable Adler-32 verification
      --md4                Enable MD4 verification
      --sha224             Enable SHA-224 verification
      --sha384             Enable SHA-384 verification
      --sha512             Enable SHA-512 verification
      --ripemd160          Enable RIPEMD-160 verification
      --whirlpool          Enable Whirlpool verification
      --no-sha1            Disable SHA-1 verification
      --no-sha256          Disable SHA-256 verification
      --no-md5             Disable MD5 verification
      -a, --all            Use all methods
    
    http://github.com/thurask/bbarchivist

----------------------------------------

::

    > bb-escreens -h
    
    usage: bb-escreens [-h] [-v] pin app uptime duration

    Calculates escreens codes.
    
    positional arguments:
      pin            PIN, 8 characters
      app            OS version, 10.x.y.zzzz
      uptime         Uptime, in ms
      duration       1/3/6/15/30 days
    
    optional arguments:
      -h, --help     show this help message and exit
      -v, --version  show program's version number and exit
    
    http://github.com/thurask/bbarchivist
    
----------------------------------------

::

    > bb-linkgen -h
    
    usage: bb-linkgen [-h] [-v] os radio swrelease

    Generate links from OS/radio/software.
    
    positional arguments:
      os             OS version, 10.x.y.zzzz
      radio          Radio version, 10.x.y.zzzz
      swrelease      Software version, 10.x.y.zzzz
    
    optional arguments:
      -h, --help     show this help message and exit
      -v, --version  show program's version number and exit
    
    http://github.com/thurask/bbarchivist
    
----------------------------------------

::

    > bb-gpgrunner -h
    
    usage: bb-gpgrunner [-h] [-v] [folder]

	GPG-sign all files in a directory.

	positional arguments:
	  folder         Working directory, default is local

	optional arguments:
	  -h, --help     show this help message and exit
	  -v, --version  show program's version number and exit

	http://github.com/thurask/bbarchivist

    
----------------------------------------

::

    > bb-autolookup -h
    
    usage: bb-autolookup [-h] [-v] [-l] [-o] os

    Get software release for one/many OS versions.
    
    positional arguments:
      os             OS version, 10.x.y.zzzz
    
    optional arguments:
      -h, --help     show this help message and exit
      -v, --version  show program's version number and exit
      -l, --loop     Loop lookup, CTRL-C to quit
      -o, --output   Output to file
    
    http://github.com/thurask/bbarchivist
        
Example
~~~~~~~

::

    > bb-archivist 10.3.1.2726 10.3.1.2727 10.3.1.1877 -nr --sha512 --no-md5

would make only OS+radio autoloaders for OS 10.3.1.2726/radio 10.3.1.2727
(software release 10.3.1.1877), compress them, delete uncompressed
loaders and verify with SHA-1, SHA-256, SHA-512.

::

    > bb-lazyloader 10.3.1.1955 10.3.1.1956 10.3.1.1372 --passport --run-autoloader

would create a Passport autoloader for OS 10.3.1.1955/radio 10.3.1.1956
(software release 10.3.1.1372), and run it (Windows only).

::

    > bb-cchecker 311 480 STA100-3

would check the latest OS for the Z30 STA100-3 on Verizon Wireless.

::

    > bb-filehasher -a
    
would use all available methods to hash all files in the local directory.

::

    > bb-escreens acdcacdc 10.3.2.6969 69696969 30
    
would generate the code for that PIN, OS version and uptime and for 30 days.

::

    > bb-linkgen 10.3.1.2726 10.3.1.2727 10.3.1.1877
    
would generate the URLs for that given OS/radio/software release combination.

::

    > bb-gpgrunner "~/some_stuff"
    
would create ASCII signature files for all files in the given folder.
Make sure to have bbarchivist.ini in ~ or \Users\<your username> like so:

::    
    [gpgrunner]
    key = 0xACDCACDC
    pass = correct horse battery staple
    
If not, it'll ask you while running the script and make the file.
More importantly, MAKE SURE TO HAVE GnuPG SET UP BEFOREHAND!

::

    > bb-autolookup 10.3.1.2726 -l -o
    
would start a lookup loop from OS 10.3.1.2726, outputting results to screen and to a log file.
Location is in your home directory.

License
-------

No fancy licensing here, just fork this and do whatever. Although, if
you figure out something interesting, please do try to put it upstream
via pull request.

Credits/Software Used
---------------------

-  bbarchivist: `Thurask <https://twitter.com/thuraski>`__
-  Python: `The Python Software Foundation <https://www.python.org>`__
-  Requests: `Kenneth Reitz et al. <http://docs.python-requests.org/en/latest/dev/authors/>`__
-  Python-GnuPG: `Vinay Sajip et al. <https://pythonhosted.org/python-gnupg/index.html#acknowledgements>`__
-  PyDev: `Brainwy Software Ltda. <http://pydev.org>`__
-  Momentics: `BlackBerry Ltd. <https://developer.blackberry.com/native/downloads/>`__
-  Feedback, testing: Users Like You

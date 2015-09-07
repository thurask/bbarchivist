README
======
.. image:: https://img.shields.io/pypi/dd/bbarchivist.svg
    :target: https://pypi.python.org/pypi/bbarchivist
    :alt: Downloads/day

.. image:: https://img.shields.io/pypi/v/bbarchivist.svg?label=release
    :target: https://pypi.python.org/pypi/bbarchivist
    :alt: Pypi version
    
.. image:: https://travis-ci.org/thurask/bbarchivist.svg?branch=master
    :target: https://travis-ci.org/thurask/bbarchivist
    :alt: Travis CI

.. image:: https://img.shields.io/github/issues/thurask/bbarchivist.svg
    :target: https://github.com/thurask/bbarchivist
    :alt: GitHub issues
    
.. image:: https://img.shields.io/github/forks/thurask/bbarchivist.svg
    :target: https://github.com/thurask/bbarchivist
    :alt: GitHub forks
    
.. image:: https://img.shields.io/github/stars/thurask/bbarchivist.svg
    :target: https://github.com/thurask/bbarchivist
    :alt: GitHub stars
    
.. image:: http://www.quantifiedcode.com/api/v1/project/b4f0ae406aea484587534740c91800cb/badge.svg
    :target: http://www.quantifiedcode.com/app/project/b4f0ae406aea484587534740c91800cb
    :alt: QuantifiedCode

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

Just Lazyloader
~~~~~~~~~~~~~~~

As of version 1.7.1 (12 June 2015), lazyloader is also provided by itself on `GitHub <https://github.com/thurask/bbarchivist/releases>`__.

To use, just download the archive attached to the latest release, unpack somewhere and double click the executable.

Lazyloader is still included within the pip package.

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
and `Beautiful Soup 4 <http://www.crummy.com/software/BeautifulSoup/#Download>`__
libraries installed somehow. Installation with pip does this
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

Testing
~~~~~~~

If you want to run the unit tests yourself, you'll also need mock, pytest
and httmock installed via pip.

Testing of GnuPG-related functions requires setting up GnuPG in the first place.

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

Certchecker
~~~~~~~~~~~

1. Ask for hardware/FCC ID or model number (if not specified)
2. Return certified OS versions for that device

Pseudocap
~~~~~~~~~

1. Take in filename, signed file locations
2. Produce an autoloader from those

SQLExport
~~~~~~~~~

1. Convert ~\bbarchivist.db into ~\swrelease.csv, that's it

Kompressor
~~~~~~~~~~

1. Compress all files in a directory

Downloader
~~~~~~~~~~

1. The same download function as in Archivist, but in isolation.

Command Line Arguments
----------------------

Help
~~~~

::

    > bb-archivist -h

    usage: bb-archivist [-h] [-v] [-f DIR] [-no] [-ni] [-nx] [-nr] [-ns] [-nc]
                    [-nd] [-nv] [-g] [-r [SW]] [-m [METHOD]]
                    os [radio] [swrelease]

	Download bar files, create autoloaders.

	positional arguments:
	  os                    OS version, 10.x.y.zzzz
	  radio                 Radio version, 10.x.y.zzzz
	  swrelease             Software version, 10.x.y.zzzz

	optional arguments:
	  -h, --help            show this help message and exit
	  -v, --version         show program's version number and exit
	  -f DIR, --folder DIR  Working folder
	  -g, --gpg             Enable GPG signing. Set up GnuPG.
	  -r [SW], --radiosw [SW]
							Radio software version, if not same as OS
	  -m [METHOD], --method [METHOD]
							Compression method

	negators:
	  Disable program functionality

	  -no, --no-download    Don't download files
	  -ni, --no-integrity   Don't test bar files after download
	  -nx, --no-extract     Don't extract bar files
	  -nr, --no-radios      Don't make radio autoloaders
	  -ns, --no-rmsigned    Don't remove signed files
	  -nc, --no-compress    Don't compress loaders
	  -nd, --no-delete      Don't delete uncompressed loaders
	  -nv, --no-verify      Don't verify created loaders

	http://github.com/thurask/bbarchivist

----------------------------------------

::

    > bb-lazyloader -h

    usage: bb-lazyloader [-h] [-v]
                     [--stl100-1 | --stl100-x | --stl100-4 | --q10 | --z30 | --z3 | --passport]
                     [--run-loader] [-g | -ng] [-f DIR] [-n] [-r [SW]]
                     [os] [radio] [swrelease]

	Create one autoloader for personal use.

	positional arguments:
	  os                    OS version, 10.x.y.zzzz
	  radio                 Radio version, 10.x.y.zzzz
	  swrelease             Software version, 10.x.y.zzzz

	optional arguments:
	  -h, --help            show this help message and exit
	  -v, --version         show program's version number and exit
	  --run-loader          Run autoloader after creation
	  -g, --gui             Use GUI
	  -ng, --no-gui         Don't use GUI
	  -f DIR, --folder DIR  Working folder
	  -n, --no-download     Don't download files
	  -r [SW], --radiosw [SW]
							Radio software version, if not same as OS
    
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

    usage: bb-cchecker [-h] [-v] [-a] [-d] [-e] [-r] [-f DIR] [-b]
                   [-s SWRELEASE | -o OS]
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
	  -r, --repair          Debrick instead of upgrade bars
	  -f DIR, --folder DIR  Working folder
	  -b, --blitz           Create blitz package
	  -s SWRELEASE, --software-release SWRELEASE
							Force SW release (check bundles first!)
	  -o OS, --os OS        Force OS (check bundles first!)

	http://github.com/thurask/bbarchivist
    
----------------------------------------

::

    > bb-filehasher -h
    
    usage: bb-filehasher [-h] [-v] [folder]

	Applies hash functions to files.

	positional arguments:
	  folder         Working directory, default is local

	optional arguments:
	  -h, --help     show this help message and exit
	  -v, --version  show program's version number and exit

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
    
    usage: bb-linkgen [-h] [-v] [-r [SW]] os [radio] [swrelease]

	Generate links from OS/radio/software.

	positional arguments:
	  os                    OS version, 10.x.y.zzzz
	  radio                 Radio version, 10.x.y.zzzz
	  swrelease             Software version, 10.x.y.zzzz

	optional arguments:
	  -h, --help            show this help message and exit
	  -v, --version         show program's version number and exit
	  -r [SW], --radiosw [SW]
							Radio software version, if not same as OS
   
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
    
    usage: bb-autolookup [-h] [-v] [-l] [-o] [-a] [-i INT] [-s] os

    Get software release for one/many OS versions.
    
    positional arguments:
      os                    OS version, 10.x.y.zzzz
    
    optional arguments:
      -h, --help            show this help message and exit
      -v, --version         show program's version number and exit
      -l, --loop            Loop lookup, CTRL-C to quit
      -o, --output          Output to file
      -a, --autogen         Generate links for availables
      -i INT, --increment INT
                            Loop increment, default = 3
      -s, --sql             Add valid links to database
    
    http://github.com/thurask/bbarchivist
   
----------------------------------------

::

    > bb-certchecker -h
    
    usage: bb-certchecker [-h] [-v] device

    Checks a carrier for an OS version, can download.
    
    positional arguments:
      device         FCCID/HWID/model number
    
    optional arguments:
      -h, --help     show this help message and exit
      -v, --version  show program's version number and exit
    
    http://github.com/thurask/bbarchivist

----------------------------------------

::

    > bb-pseudocap -h
    
	usage: bb-pseudocap [-h] [-v] [-f DIR]
						filename first [second] [third] [fourth] [fifth] [sixth]

	cap.exe, implemented in Python

	positional arguments:
	  filename              Filename

	optional arguments:
	  -h, --help            show this help message and exit
	  -v, --version         show program's version number and exit
	  -f DIR, --folder DIR  Working folder

	  first                 First file
	  second                Second file, optional
	  third                 Third file, optional
	  fourth                Fourth file, optional
	  fifth                 Fifth file, optional
	  sixth                 Sixth file, optional

	http://github.com/thurask/bbarchivist

----------------------------------------

::

    > bb-sqlexport -h
    
    usage: bb-sqlexport [-h] [-v]

    Export SQL database to CSV
    
    optional arguments:
      -h, --help     show this help message and exit
      -v, --version  show program's version number and exit
    
    http://github.com/thurask/bbarchivist

----------------------------------------

::

	> bb-kompressor -h

	usage: bb-kompressor [-h] [-v] [-m--method [METHOD]] [folder]

	Compress all files in a directory.

	positional arguments:
	  folder               Working directory, default is local

	optional arguments:
	  -h, --help           show this help message and exit
	  -v, --version        show program's version number and exit
	  -m--method [METHOD]  Compression method

	http://github.com/thurask/bbarchivist

----------------------------------------

::

	> bb-downloader -h

	usage: bb-downloader [-h] [-v] [-f DIR] [-a [SW]] [-d] [-c] [-r] [-ni]
                     os [radio] [swrelease]

	Download bar files.

	positional arguments:
	  os                    OS version, 10.x.y.zzzz
	  radio                 Radio version, 10.x.y.zzzz
	  swrelease             Software version, 10.x.y.zzzz

	optional arguments:
	  -h, --help            show this help message and exit
	  -v, --version         show program's version number and exit
	  -f DIR, --folder DIR  Working folder
	  -a [SW], --altsw [SW]
							Radio software version, if not same as OS
	  -d, --debricks        Download debricks
	  -c, --cores           Download debricks
	  -r, --radios          Download radios
	  -ni, --no-integrity   Don't test bar files after download

	http://github.com/thurask/bbarchivist

Example
~~~~~~~

::

    > bb-archivist 10.3.1.2726 10.3.1.2727 10.3.1.1877 -nr

would make only OS+radio autoloaders for OS 10.3.1.2726/radio 10.3.1.2727
(software release 10.3.1.1877), compress them, delete uncompressed
loaders and verify with default options (SHA1, SHA512, MD5)

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
Make sure to have bbarchivist.ini in ~ or \Users\<your username> configured like so:

::

    [gpgrunner]
    key = 0xACDCACDC
    pass = yourpass (or leave this line blank to ask every time)
    
If not, it'll ask you while running the script and make the file.
More importantly, MAKE SURE TO HAVE GnuPG SET UP BEFOREHAND!

::

    > bb-autolookup 10.3.1.2726 -l -o
    
would start a lookup loop from OS 10.3.1.2726, outputting results to screen and to a log file.
Location is in your home directory.

::

    > bb-certchecker STA100-5
    
would print a list of all of the OSs that were ever certified for the Z30 STA100-5.

::

    > bb-pseudocap Autoload-10.3.2.2339-SQN100-X.exe QC8960_10.3.2.2339.signed QC8960.WTR_10.3.2340.signed
    
would create an autoloader with the name Autoloader-10.3.2.2339-SQN100-X.exe, from those two signed files,
in the current folder.

::

    > bb-sqlexport

does one thing and one thing only. You're free to guess.

 ::

	> bb-kompressor -m zip

would compress all files in the local directory to zip archives, since you specified zip.

::

	> bb-downloader 10.3.2.798 -r

would download the guessed radios (10.3.2.799) for OS 10.3.2.798.

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
-  Beautiful Soup: `Leonard Richardson et al. <http://www.crummy.com/software/BeautifulSoup/>`__
-  Python-GnuPG: `Vinay Sajip et al. <https://pythonhosted.org/python-gnupg/index.html#acknowledgements>`__
-  easygui: `easygui dev team <https://pythonhosted.org/easygui/support.html>`__
-  Visual Studio Community 2015: `Microsoft <https://www.visualstudio.com>`__
-  Python Tools for Visual Studio: `Microsoft <http://microsoft.github.io/PTVS/>`__
-  Integration: `Travis CI <https://travis-ci.org>`__
-  Feedback, bug reports, feature requests: Users Like You

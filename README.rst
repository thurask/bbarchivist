README
======
    
.. image:: https://travis-ci.org/thurask/bbarchivist.svg?branch=master
    :target: https://travis-ci.org/thurask/bbarchivist
    :alt: Travis CI

.. image:: https://coveralls.io/repos/thurask/bbarchivist/badge.svg?branch=master&service=github
    :target: https://coveralls.io/github/thurask/bbarchivist?branch=master
    :alt: Coveralls.io

A Python 3.2+ package for various BlackBerry 10-related functions.
Includes support scripts.
Replaces `archivist <https://github.com/thurask/archivist>`__ and
`lazyloader <https://github.com/thurask/lazyloader>`__. Don't use those anymore.

This can be used either as importing the bbarchivist library, or a variety of command-line scripts.

Requirements
------------

Just Lazyloader
~~~~~~~~~~~~~~~

As of version 1.7.1 (12 June 2015), lazyloader is also provided by itself for Windows on `GitHub <https://github.com/thurask/bbarchivist/releases>`__.

To use, just download the archive attached to the latest release, unpack somewhere and double click the executable.

Lazyloader is still included within the pip package.

Universal
~~~~~~~~~

Requires Python >=3.2. Install the latest possible, though.

To get this package, install with pip:

::

    $ pip install bbarchivist

On non-Windows systems, type that in your command line. It may be a different
command depending on how your system maintainer has organized pip, such as

::

	$ pip3 install bbarchivist
	
For Windows, I recommend `pip-win <https://sites.google.com/site/pydatalog/python/pip-for-windows>`__.

A copy of cap.exe is included with this script.

Compression with 7-Zip requires a fairly hefty CPU/RAM setup.
Using archivist's bulk autoloader creator requires a few dozen GB of hard drive space.

It also requires the
`requests <http://docs.python-requests.org/en/latest/user/install/>`__
and `Beautiful Soup 4 <http://www.crummy.com/software/BeautifulSoup/#Download>`__
libraries installed somehow. Installation with pip does this automatically, or use your package manager's version.

PGP support requires the
`python-gnupg <https://pythonhosted.org/python-gnupg/index.html>`__
library installed somehow. Installation with pip does this
automatically, or use your package manager's version.

Note, python-gnupg also requires some form of GPG client installed.
For Windows, get `Gpg4Win <http://www.gpg4win.org>`__.
For Mac, get `GPGTools <https://gpgtools.org>`__.
For Linux/BSD, you probably already have `GnuPG <https://www.gnupg.org>`__ installed.
If not, install it from the link above, or your package manager.

Python 3.2 further requires `shutilwhich <https://pypi.python.org/pypi/shutilwhich/>`__.
Installation of shutilwhich on Python 3.3+ has no effect, so it's harmless.

7-Zip compression (default) uses
`p7zip <http://sourceforge.net/projects/p7zip/>`__
(Linux/Mac/BSD)/`7-Zip <http://www.7-zip.org/download.html>`__ (Windows).
Zip and tar.xxx compression don't require external programs.

Windows
~~~~~~~

To use 7-Zip compression, have 7-Zip installed. If not, make sure to
specify a non-7-Zip compression method when compressing.

Linux/BSD
~~~~~~~~~

If you're using 7z compression, this requires p7zip (look through your
package manager, or install from source) in your path. I.e.:

::

    $ which 7za

resolves to something.

Your package manager should also have requests and beautifulsoup4 packages
available. If not, or if you want the latest, compile from source. Or use pip.

Other than that, install this with pip.

Mac
~~~

Same as Linux, but you'll have to either install p7zip from source, or
install it with something like `Homebrew <http://brew.sh>`__ or
`MacPorts <https://www.macports.org>`__.

Testing
~~~~~~~

If you want to run the unit tests yourself, you'll also need mock, pytest
and httmock installed via pip. Install from the requirements-devel file with pip.

Coverage requires installation of pytest-cov.

Testing of GnuPG/7-Zip functions requires setting up GnuPG/7-Zip in the first place.

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
							Radio software version; use without software to guess
	  -m [METHOD], --method [METHOD]
							Compression method
	  -c, --core            Make core/radio loaders

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
	  -f DIR, --folder DIR  Working folder
	  -n, --no-download     Don't download files
	  -r [SW], --radiosw [SW]
	                        Radio software version; use without software to guess
	  -c, --core            Make core/radio loader

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
    
    usage: bb-autolookup [-h] [-v] [-l] [-o] [-a] [-q] [-i INT] [-s] [-e] [-c INT]
                     os

	Get software release for one/many OS versions.

	positional arguments:
	  os                    OS version, 10.x.y.zzzz

	optional arguments:
	  -h, --help            show this help message and exit
	  -v, --version         show program's version number and exit
	  -l, --loop            Loop lookup, CTRL-C to quit
	  -o, --output          Output to file
	  -a, --autogen         Generate links for availables
	  -q, --quiet           Only print if available
	  -i INT, --increment INT
							Loop increment, default = 3
	  -s, --sql             Add valid links to database
	  -e, --email           Email valid links to self
	  -c INT, --ceiling INT
							When to stop script, default = 9996

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

	BlackBerry CAP, in Python.

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
    
    usage: bb-sqlexport [-h] [-v] [-p OS SW] [-l]

	Export SQL database to CSV.

	optional arguments:
	  -h, --help            show this help message and exit
	  -v, --version         show program's version number and exit
	  -p OS SW, --pop OS SW
							Pop this OS and SW from the database
	  -l, --list            List entries in database

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

----------------------------------------

::

	> bb-kernchecker -h

	usage: bb-kernchecker [-h] [-v]

	Kernel version scraper.

	optional arguments:
	  -h, --help     show this help message and exit
	  -v, --version  show program's version number and exit

	http://github.com/thurask/bbarchivist

Credits/Software Used
---------------------

-  bbarchivist: `Thurask <https://twitter.com/thuraski>`__
-  Python: `The Python Software Foundation <https://www.python.org>`__
-  Requests: `Kenneth Reitz et al. <http://docs.python-requests.org/en/latest/dev/authors/>`__
-  Beautiful Soup: `Leonard Richardson et al. <http://www.crummy.com/software/BeautifulSoup/>`__
-  Python-GnuPG: `Vinay Sajip et al. <https://pythonhosted.org/python-gnupg/index.html#acknowledgements>`__
-  Visual Studio Community 2015: `Microsoft <https://www.visualstudio.com>`__
-  Python Tools for Visual Studio: `Microsoft <http://microsoft.github.io/PTVS/>`__
-  Integration: `Travis CI <https://travis-ci.org>`__, `Coveralls.io <https://coveralls.io>`__
-  Feedback, bug reports, feature requests: Users Like You

License
-------
Copyright 2015 Thurask <thuraski@hotmail.com>
This work is free. You can redistribute it and/or modify it under the
terms of the Do What The Fuck You Want To Public License, Version 2,
as published by Sam Hocevar. See the LICENSE file for more details.

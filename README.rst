README
======
    
.. image:: https://travis-ci.org/thurask/bbarchivist.svg?branch=master
    :target: https://travis-ci.org/thurask/bbarchivist
    :alt: Travis CI

.. image:: https://coveralls.io/repos/thurask/bbarchivist/badge.svg?branch=master&service=github
    :target: https://coveralls.io/github/thurask/bbarchivist?branch=master
    :alt: Coveralls.io

.. image:: https://readthedocs.org/projects/bbarchivist/badge/?version=latest
    :target: http://bbarchivist.readthedocs.org/en/latest/?badge=latest
    :alt: Documentation Status

A Python 3.2+ package for various BlackBerry 10/Priv-related functions and scripts.

Packaged Executables
--------------------

As of version 2.3.0 (18 December 2015), a few scripts are packaged as Windows executables on `GitHub <https://github.com/thurask/bbarchivist/releases>`__.

To use, just download the archive attached to the latest release, unpack somewhere and double click the executable.

Alternatively, if you wish full functionality or Linux/Mac/BSD support, keep reading.

Installation
------------

Requires Python >=3.2, with 3.5 or later preferred.

To get the latest stable version, install with pip:

::

    $ pip install bbarchivist

For some systems, it may be a different command depending on how your system maintainer has organized pip, perhaps like:

::

    $ pip3 install bbarchivist

If you want the latest development version, clone from Git and install with setuptools:

::

    $ git clone https://github.com/thurask/bbarchivist.git
    $ cd bbarchivist
    $ python setup.py install

If you have `Git LFS <https://git-lfs.github.com>`__, the data files will download automatically.
If you don't have Git LFS, then run the :code:`download_dats.py` script in this folder.
The data files will be considered different with regards to git, so be warned.

Python Libraries
~~~~~~~~~~~~~~~~

This library requires the
`Requests <http://docs.python-requests.org/en/latest/user/install/>`__
and `Beautiful Soup 4 <http://www.crummy.com/software/BeautifulSoup/#Download>`__
libraries. PGP support requires the `python-gnupg <https://pythonhosted.org/python-gnupg/index.html>`__ library.

Python 3.2 further requires `shutilwhich <https://pypi.python.org/pypi/shutilwhich/>`__.
Installation of shutilwhich on Python 3.3+ has no effect, so it's unnecessary.

External Programs
~~~~~~~~~~~~~~~~~

Copies of cap.exe and cfp.exe are included.
Windows can directly access both .exe files through the :code:`bb-cap` and :code:`bb-cfp` frontends.

7-Zip compression (default) uses
`p7zip <http://sourceforge.net/projects/p7zip/>`__
(Linux/Mac/BSD) or `7-Zip <http://www.7-zip.org/download.html>`__ (Windows).
Zip and tar.xxx compression don't require external programs.

PGP support also requires some form of GPG client installed:

- Windows: `Gpg4Win <http://www.gpg4win.org>`__.
- Mac: `GPGTools <https://gpgtools.org>`__.
- Linux/BSD: `GnuPG <https://www.gnupg.org>`__, if not already installed.

Testing
-------

If you want to run the unit tests yourself, you'll also need mock, pytest
and httmock. Install from the requirements-devel file with pip.

Coverage requires installation of pytest-cov.

Testing of GnuPG/7-Zip functions requires setting up GnuPG/7-Zip in the first place.

Contributing
------------

If you wish to contribute to this project, please do the following:

1. Fork and clone source from GitHub (again, requires `Git LFS <https://git-lfs.github.com>`__)
2. Make sure all tests run on your system (requires GPG, 7-Zip)
3. Make your changes on a new branch without breaking any tests
4. Open a pull request on GitHub

Documentation
-------------

Online documentation is hosted at `ReadTheDocs <http://bbarchivist.rtfd.org>`__.

Docs use Sphinx for automatic generation.


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
-  Documentation: `ReadTheDocs <http://bbarchivist.rtfd.org>`__
-  Feedback, bug reports, feature requests: Users Like You

License
-------
Copyright 2015-2016 Thurask <thuraski@hotmail.com>
This work is free. You can redistribute it and/or modify it under the
terms of the Do What The Fuck You Want To Public License, Version 2,
as published by Sam Hocevar. See the LICENSE file for more details.

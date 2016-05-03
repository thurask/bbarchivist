README
======

.. image:: https://travis-ci.org/thurask/bbarchivist.svg?branch=master
    :target: https://travis-ci.org/thurask/bbarchivist
    :alt: Travis CI

.. image:: https://ci.appveyor.com/api/projects/status/92lobvk91tbcrgc1?svg=true
    :target: https://ci.appveyor.com/project/thurask/bbarchivist
    :alt: Appveyor

.. image:: https://coveralls.io/repos/thurask/bbarchivist/badge.svg?branch=master&service=github
    :target: https://coveralls.io/github/thurask/bbarchivist?branch=master
    :alt: Coveralls.io

.. image:: https://readthedocs.org/projects/bbarchivist/badge/?version=latest
    :target: http://bbarchivist.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

A Python 3.2+ package for various BlackBerry 10/Priv-related functions and scripts.

Packaged Executables
--------------------

As of version 2.3.0 (18 December 2015), a few scripts are packaged as Windows executables on `GitHub <https://github.com/thurask/bbarchivist/releases>`__.

To use, just download the bbarchivist-<version> archive attached to the latest release, unpack somewhere and double click an executable.

Alternatively, if you require full functionality or Linux/Mac/BSD support, keep reading.

Installation
------------

Requires Python >=3.2, with 3.5 or later preferred.

To get the latest stable version, install with pip:

::

    $ pip install bbarchivist

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
libraries. GPG support requires the `python-gnupg <https://pythonhosted.org/python-gnupg/index.html>`__ library.

Python 3.2 further requires `shutilwhich <https://pypi.python.org/pypi/shutilwhich/>`__.
Installation of shutilwhich on Python 3.3+ has no effect, so it's unnecessary.

The `simplejson <http://simplejson.readthedocs.io/en/latest/>`__ module is installed on Python 3.3+, for improved
performance with dealing with JSON.

External Programs
~~~~~~~~~~~~~~~~~

Copies of cap.exe and cfp.exe are included.
Windows can directly access both .exe files through the :code:`bb-cap` and :code:`bb-cfp` frontends.

7-Zip compression (default) uses
`p7zip <http://sourceforge.net/projects/p7zip/>`__
(Linux/Mac/BSD) or `7-Zip <http://www.7-zip.org/download.html>`__ (Windows).
Zip and tar.xxx compression don't require external programs.

GPG support also requires some form of GPG client installed:

- Windows: `Gpg4Win <http://www.gpg4win.org>`__.
- Mac: `GPGTools <https://gpgtools.org>`__.
- Linux/BSD: `GnuPG <https://www.gnupg.org>`__, if not already installed.

Testing
-------

If you want to run the tests yourself, you'll also need `pytest <http://pytest.org/latest/>`__
and `httmock <https://github.com/patrys/httmock>`__. Install from the :code:`requirements-devel.txt` file with pip.

If you're testing on Python 3.2, install the `mock backport <https://pypi.python.org/pypi/mock>`__ as well.

Coverage requires installation of pytest-cov.

Testing of GnuPG/7-Zip functions requires setting up GnuPG/7-Zip in the first place.

Contributing
------------

If you wish to contribute to this project, please do the following:

1. Fork and clone source from GitHub (requires `Git LFS <https://git-lfs.github.com>`__)
2. Make sure all tests run on your system (requires GPG, 7-Zip)
3. Make your changes on a new branch without breaking any tests, and add tests for your new code if applicable
4. Open a pull request on GitHub

Documentation
-------------

Online documentation is hosted at `ReadTheDocs <http://bbarchivist.readthedocs.io>`__.

Docs use Sphinx for automatic generation.

License
-------
Copyright 2015-2016 Thurask <thuraski@hotmail.com>
This work is free. You can redistribute it and/or modify it under the
terms of the Do What The Fuck You Want To Public License, Version 2,
as published by Sam Hocevar. See the LICENSE file for more details.

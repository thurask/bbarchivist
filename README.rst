README
======

.. image:: https://travis-ci.org/thurask/bbarchivist.svg?branch=master
    :target: https://travis-ci.org/thurask/bbarchivist
    :alt: Travis CI

.. image:: https://ci.appveyor.com/api/projects/status/92lobvk91tbcrgc1?svg=true
    :target: https://ci.appveyor.com/project/thurask/bbarchivist
    :alt: Appveyor

.. image:: https://codecov.io/gh/thurask/bbarchivist/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/thurask/bbarchivist
    :alt: Codecov

.. image:: https://scrutinizer-ci.com/g/thurask/bbarchivist/badges/quality-score.png?b=master
    :target: https://scrutinizer-ci.com/g/thurask/bbarchivist/?branch=master
    :alt: Scrutinizer Code Quality

.. image:: https://codeclimate.com/github/thurask/bbarchivist/badges/gpa.svg
   :target: https://codeclimate.com/github/thurask/bbarchivist
   :alt: Code Climate

.. image:: https://api.codacy.com/project/badge/Grade/71913fc9723340d5bf4a3396fead1026
    :target: https://www.codacy.com/app/thuraski/bbarchivist?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=thurask/bbarchivist&amp;utm_campaign=Badge_Grade
    :alt: Codacy Badge

.. image:: https://readthedocs.org/projects/bbarchivist/badge/?version=latest
    :target: https://bbarchivist.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. image:: https://requires.io/github/thurask/bbarchivist/requirements.svg?branch=master
     :target: https://requires.io/github/thurask/bbarchivist/requirements/?branch=master
     :alt: Requirements Status

A Python 3.2+ package for various BlackBerry 10/BlackBerry Android-related functions and scripts.

Packaged Executables
--------------------

As of version 2.3.0 (18 December 2015), most scripts are packaged as Windows executables on `GitHub <https://github.com/thurask/bbarchivist/releases>`__.

To use, just download the bbarchivist-<version>-<system bit> archive attached to the latest release, unpack somewhere and double click an executable.

Executables are prepared with `PyInstaller <http://www.pyinstaller.org>`__. Distributing them as of Windows 10 and Python 3.5+ requires the Windows 10 SDK, thanks to `Universal CRT <https://blogs.msdn.microsoft.com/vcblog/2015/03/03/introducing-the-universal-crt>`__.

Alternatively, if you require full functionality or Linux/Mac/BSD support, keep reading.

Installation
------------

Requires Python >=3.2, with 3.7 or later preferred.

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
`Requests <http://docs.python-requests.org/en/latest/user/install/>`__,
`appdirs <https://github.com/ActiveState/appdirs/>`__,
`user_agent <https://github.com/lorien/user_agent>`__,
and `Beautiful Soup 4 <https://www.crummy.com/software/BeautifulSoup/#Download>`__
libraries. GPG support requires the `python-gnupg <https://pythonhosted.org/python-gnupg/index.html>`__ library.

Python 3.2 further requires `shutilwhich <https://pypi.org/project/shutilwhich/>`__.
Installation of shutilwhich on Python 3.3+ has no effect, so it's unnecessary.

The optional `simplejson <https://simplejson.readthedocs.io/en/latest/>`__ module is installed on Python 3.3+, for improved
performance with dealing with JSON.

The optional `defusedxml <https://bitbucket.org/tiran/defusedxml>`__ module is installed for safer XML handling.
Use defusedxml 0.4.1 if you're using Python 3.2 or 3.3.

External Programs
~~~~~~~~~~~~~~~~~

Copies of cap.exe and cfp.exe are included.
Windows can directly access both .exe files through the :code:`bb-cap` and :code:`bb-cfp` frontends.

7-Zip compression (default) uses
`p7zip <https://sourceforge.net/projects/p7zip/>`__
(Linux/Mac/BSD) or `7-Zip <http://www.7-zip.org/download.html>`__ (Windows).
Zip and tar.xxx compression don't require external programs.

GPG support also requires some form of GPG client installed:

- Windows: `Gpg4Win <https://www.gpg4win.org>`__.
- Mac: `GPGTools <https://gpgtools.org>`__.
- Linux/BSD: `GnuPG <https://www.gnupg.org>`__, if not already installed.

Testing
-------

If you want to run the tests yourself, you'll also need `pytest <https://pytest.org/latest/>`__
and `httmock <https://github.com/patrys/httmock>`__. Install from the :code:`requirements-devel.txt` file with pip.

If you're testing on Python 3.2, install the `mock backport <https://pypi.org/project/mock/>`__ as well.

Coverage requires installation of `pytest-cov <https://github.com/pytest-dev/pytest-cov>`__.

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

An overview of change history can be found in the `CHANGES <CHANGES.rst>`__ file.

Online documentation is hosted at `ReadTheDocs <https://bbarchivist.readthedocs.io>`__.

Docs use `Sphinx <http://www.sphinx-doc.org/en/master/>`__ for automatic generation.

License
-------
Copyright 2015-2019 Thurask <thuraski@hotmail.com>
This work is free. You can redistribute it and/or modify it under the
terms of the Do What The Fuck You Want To Public License, Version 2,
as published by Sam Hocevar. See the `LICENSE <LICENSE>`__ file for more details.

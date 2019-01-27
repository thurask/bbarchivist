#!/usr/bin/env python3
"""Setuptools setup file."""

from sys import version_info

from setuptools import find_packages, setup

import versioneer

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "2015-2019 Thurask"


def readme():
    """
    Read ReST readme file, use as long description.
    """
    with open('README.rst') as file:
        data = file.read()
        data = data.replace("`LICENSE <LICENSE>`__", "LICENSE")
        return data

def main():
    """
    Perform setuptools setup.
    """
    cond_requires = [
        'python-gnupg>=0.3.9',
        'beautifulsoup4>=4.5.3',
        'appdirs>=1.4.3',
        'user_agent>=0.1.9'
    ]
    if version_info[1] == 2:  # 3.2; shutilwhich, no simplejson, old requests/defusedxml
        deplist = ['shutilwhich>=1.1.0', 'requests==2.10', 'defusedxml==0.4.1']
    elif version_info[1] == 3:  # 3.3; simplejson, old requests/defusedxml
        deplist = ['simplejson>=3.10.0', 'requests>=2.10.0,<2.18.4', 'defusedxml==0.4.1']
    else:  # 3.4+; simplejson, new requests/defusedxml
        deplist = ['simplejson>=3.10.0', 'requests>=2.10.0', 'defusedxml>=0.4.1']
    cond_requires.extend(deplist)
    scriptlist = [
        'bb-archivist=bbarchivist.scripts.archivist:grab_args',
        'bb-lazyloader=bbarchivist.scripts.lazyloader:grab_args',
        'bb-cchecker=bbarchivist.scripts.carrierchecker:grab_args',
        'bb-certchecker=bbarchivist.scripts.certchecker:grab_args',
        'bb-filehasher=bbarchivist.scripts.filehasher:filehasher_main',
        'bb-escreens=bbarchivist.scripts.escreens:escreens_main',
        'bb-linkgen=bbarchivist.scripts.linkgen:grab_args',
        'bb-gpgrunner=bbarchivist.scripts.gpgrunner:gpgrunner_main',
        'bb-autolookup=bbarchivist.scripts.autolookup:grab_args',
        'bb-pseudocap=bbarchivist.scripts.pycaptool:pycaptool_main',
        'bb-sqlexport=bbarchivist.scripts.sqlexport:grab_args',
        'bb-kompressor=bbarchivist.scripts.kompressor:kompressor_main',
        'bb-downloader=bbarchivist.scripts.downloader:grab_args',
        'bb-kernchecker=bbarchivist.scripts.kernchecker:grab_args',
        'bb-cfp=bbarchivist.scripts.exeshim:cfp_main',
        'bb-cap=bbarchivist.scripts.exeshim:cap_main',
        'bb-droidlookup=bbarchivist.scripts.droidlookup:grab_args',
        'bb-metachecker=bbarchivist.scripts.metachecker:metachecker_main',
        'bb-devloader=bbarchivist.scripts.devloader:grab_args',
        'bb-swlookup=bbarchivist.scripts.swlookup:grab_args',
        'bb-infogen=bbarchivist.scripts.infogenerator:grab_args',
        'bb-droidscraper=bbarchivist.scripts.droidscraper:droidscraper_main',
        'bb-barlinker=bbarchivist.scripts.barlinker:barlinker_main',
        'bb-tclscan=bbarchivist.scripts.tclscan:grab_args',
        'bb-tclloader=bbarchivist.scripts.tclloader:grab_args',
        'bb-tcldelta=bbarchivist.scripts.tcldelta:grab_args',
        'bb-tclnewprd=bbarchivist.scripts.tclnewprd:grab_args'
    ]
    setup(name='bbarchivist',
          version=versioneer.get_version().split("-")[0],
          cmdclass=versioneer.get_cmdclass(),
          description='BlackBerry OS tools, in Pythons',
          long_description=readme(),
          url='https://github.com/thurask/bbarchivist',
          keywords='blackberry autoloader android',
          author='Thurask',
          author_email='thuraski@hotmail.com',
          license='WTFPL v2',
          classifiers=[
              "Development Status :: 5 - Production/Stable",
              "Environment :: Console",
              "Environment :: MacOS X",
              "Environment :: Win32 (MS Windows)",
              "Environment :: X11 Applications",
              "Intended Audience :: End Users/Desktop",
              "License :: Freely Distributable",
              "Operating System :: MacOS",
              "Operating System :: MacOS :: MacOS X",
              "Operating System :: Microsoft",
              "Operating System :: Microsoft :: Windows",
              "Operating System :: OS Independent",
              "Operating System :: POSIX",
              "Operating System :: POSIX :: BSD :: FreeBSD",
              "Operating System :: POSIX :: BSD :: NetBSD",
              "Operating System :: POSIX :: BSD :: OpenBSD",
              "Operating System :: POSIX :: Linux",
              "Operating System :: Unix",
              "Programming Language :: Python :: 3.2",
              "Programming Language :: Python :: 3.3",
              "Programming Language :: Python :: 3.4",
              "Programming Language :: Python :: 3.5",
              "Programming Language :: Python :: 3.6",
              "Programming Language :: Python :: 3.7",
              "Programming Language :: Python :: 3",
              "Programming Language :: Python :: 3 :: Only",
              "Topic :: Utilities"
          ],
          python_requires=">=3.2",
          packages=find_packages(),
          zip_safe=False,
          include_package_data=True,
          install_requires=cond_requires,
          entry_points={'console_scripts': scriptlist})

if __name__ == "__main__":
    main()

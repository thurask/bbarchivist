#!/usr/bin/env python3
#pylint: disable = I0011, C0111, C0103, W0622, R0801
from sys import version_info
from setuptools import setup, find_packages
from bbarchivist import bbconstants


def readme():
    """
    Read ReST readme file, use as long description.
    """
    with open('README.rst') as file:
        return file.read()


cond_requires = ['requests',
                 'python-gnupg',
                 'beautifulsoup4']
if version_info[1] < 3:  # 3.2 and under
    cond_requires.append('shutilwhich')
scriptlist = ['bb-archivist=bbarchivist.scripts.archivist:grab_args',
              'bb-lazyloader=bbarchivist.scripts.lazyloader:grab_args',
              'bb-cchecker=bbarchivist.scripts.carrierchecker:grab_args',
              'bb-certchecker=bbarchivist.scripts.certchecker:grab_args',
              'bb-filehasher=bbarchivist.scripts.filehasher:filehasher_main',
              'bb-escreens=bbarchivist.scripts.escreens:escreens_main',
              'bb-linkgen=bbarchivist.scripts.linkgen:grab_args',
              'bb-gpgrunner=bbarchivist.scripts.gpgrunner:gpgrunner_main',
              'bb-autolookup=bbarchivist.scripts.autolookup:grab_args',
              'bb-pseudocap=bbarchivist.scripts.cap:cap_main',
              'bb-sqlexport=bbarchivist.scripts.sqlexport:sqlexport_main',
              'bb-kompressor=bbarchivist.scripts.kompressor:kompressor_main',
              'bb-downloader=bbarchivist.scripts.downloader:grab_args',
              'bb-kernchecker=bbarchivist.scripts.kernchecker:kernchecker_main',
              'bb-cfp=bbarchivist.scripts.cfp:cfp_main']
setup(name='bbarchivist',
      version=bbconstants.VERSION,
      description='BlackBerry 10 autoloader tools',
      long_description=readme(),
      url='http://github.com/thurask/bbarchivist',
      keywords='blackberry autoloader',
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
          "Programming Language :: Python :: 3 :: Only",
          "Topic :: Utilities"
      ],
      packages=find_packages(),
      zip_safe=False,
      include_package_data=True,
      install_requires=cond_requires,
      entry_points={
          'console_scripts': scriptlist}
      )

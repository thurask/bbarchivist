from setuptools import setup
from bbarchivist import bbconstants
from sys import version_info


def readme():
    """
    Read ReST readme file, use as long description.
    """
    with open('README.rst') as file:
        return file.read()


cond_requires = ['requests',
                 'python-gnupg']
if version_info[1] < 3:  # 3.2 and under
    cond_requires.append('shutilwhich')
setup(name='bbarchivist',
      version=bbconstants.VERSION,
      description='BlackBerry 10 autoloader tools',
      long_description=readme(),
      url='http://github.com/thurask/bbarchivist',
      keywords='blackberry autoloader',
      author='Thurask',
      author_email='thuraski@hotmail.com',
      license='Do whatever',
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
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Utilities"
      ],
      packages=['bbarchivist'],
      zip_safe=False,
      include_package_data=True,
      install_requires=cond_requires,
      entry_points={
        'console_scripts': ['bb-archivist=bbarchivist.archivist_wrap:main',
                            'bb-lazyloader=bbarchivist.lazyloader_wrap:main',
                            'bb-cchecker=bbarchivist.carrierchecker_wrap:main',
                            'bb-filehasher=bbarchivist.filehasher_wrap:main',
                            'bb-escreens=bbarchivist.escreens_wrap:main',
                            'bb-linkgen=bbarchivist.linkgen_wrap:main',
                            'bb-gpgrunner=bbarchivist.gpgrunner_wrap:main',
                            'bb-autolookup=bbarchivist.autolookup_wrap:main'],
        })

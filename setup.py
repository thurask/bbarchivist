from setuptools import setup
from bbarchivist import bbconstants


def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='bbarchivist',
      version=bbconstants._version,
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
        "Operating System :: POSIX :: Linux",
        "Operating System :: Unix",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Utilities"
      ],
      packages=['bbarchivist'],
      zip_safe=False,
      include_package_data=True,
      install_requires=[
          'requests',
      ],
      entry_points={
        'console_scripts': ['bb-archivist=bbarchivist.archivist_wrap:main',
                            'bb-lazyloader=bbarchivist.lazyloader_wrap:main',
                            'bb-cchecker=bbarchivist.carrierchecker_wrap:main',
                            'bb-filehasher=bbarchivist.filehasher_wrap:main',
                            'bb-escreens=bbarchivist.escreens_wrap:main',
                            'bb-linkgen=bbarchivist.linkgen_wrap:main'],
        })

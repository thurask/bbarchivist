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
        "Classifier: Development Status :: 5 - Production/Stable",
        "Classifier: Environment :: Console",
        "Classifier: Environment :: MacOS X",
        "Classifier: Environment :: Win32 (MS Windows)",
        "Classifier: Environment :: X11 Applications",
        "Classifier: Intended Audience :: End Users/Desktop",
        "Classifier: License :: Freely Distributable",
        "Classifier: Operating System :: MacOS",
        "Classifier: Operating System :: MacOS :: MacOS X",
        "Classifier: Operating System :: Microsoft",
        "Classifier: Operating System :: Microsoft :: Windows",
        "Classifier: Operating System :: OS Independent",
        "Classifier: Operating System :: POSIX",
        "Classifier: Operating System :: POSIX :: Linux",
        "Classifier: Operating System :: Unix",
        "Classifier: Programming Language :: Python :: 3.4",
        "Classifier: Programming Language :: Python :: 3 :: Only",
        "Classifier: Topic :: Utilities"
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

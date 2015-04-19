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
        "Intended Audience :: End Users/Desktop",
        "License :: Freely Distributable",
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
        'console_scripts': ['bb-archivist=bbarchivist.bbarchivist:main',
                            'bb-lazyloader=bbarchivist.bblazyloader:main',
                            'bb-cchecker=bbarchivist.bbcarrierchecker:main'],
        })

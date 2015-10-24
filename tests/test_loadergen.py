#!/usr/bin/env python3
#pylint: disable = I0011, R0201, W0613, C0301
"""Test the loadergen module."""

import bbarchivist.loadergen as bl
import os
import pytest
try:
    import unittest.mock as mock
except ImportError:
    import mock
from shutil import rmtree, copyfile
from hashlib import sha512


def setup_module(module):
    """
    Create necessary files.
    """
    if not os.path.exists("temp_loadergen"):
        os.mkdir("temp_loadergen")
    os.chdir("temp_loadergen")
    with open("cap-3.11.0.22.dat", "w") as targetfile:
        targetfile.write("0"*9500000)


def teardown_module(module):
    """
    Delete necessary files.
    """
    os.chdir("..")
    rmtree("temp_loadergen", ignore_errors=True)


class TestClassLoadergen:
    """
    Test autoloader generation.
    """
    def test_read_os_none(self):
        """
        Test finding OS filenames when there are no OS files.
        """
        assert set(bl.read_os_files(os.getcwd())) == {None}

    def test_read_radio_none(self):
        """
        Test finding radio filenames when there are no radio files.
        """
        assert set(bl.read_radio_files(os.getcwd())) == {None}

    def test_generate_lazy_loader(self):
        """
        Test creating one autoloader (lazyloader).
        """
        with open("desktop_sfi.signed", "w") as targetfile:
            targetfile.write("Jackdaws love my big sphinx of quartz"*5000)
        with open("radio.signed", "w") as targetfile:
            targetfile.write("Why must I chase the cat?"*5000)
        bl.generate_lazy_loader("TESTING", 0)
        shahash = sha512()
        with open("Z10_TESTING_STL100-1.exe", "rb") as targetfile:
            data = targetfile.read()
            shahash.update(data)
        thehash = shahash.hexdigest()
        os.remove("desktop_sfi.signed")
        os.remove("radio.signed")
        assert thehash == 'd4872a853e19fb8512067f50555827c74ec33da6fd5d71ae3ddd1b0ce98a18e01727eb1f345f476d6d59bcb438be8780e3f1dc7b212dc63b4b7c09914093a730'

    def test_generate_lazy_no_os(self, capsys):
        """
        Test creating one autoloader but no OS is given.
        """
        with pytest.raises(SystemExit):
            bl.generate_lazy_loader("TESTING", 0)
            assert "No OS found" in capsys.readouterr()[0]

    def test_generate_lazy_no_rad(self, capsys):
        """
        Test creating one autoloader but no radio is given.
        """
        with open("desktop.signed", "w") as targetfile:
            targetfile.write("Jackdaws love my big sphinx of quartz"*5000)
        with pytest.raises(SystemExit):
            bl.generate_lazy_loader("TESTING", 0)
            assert "No radio found" in capsys.readouterr()[0]
        os.remove("desktop.signed")

    def test_generate_loaders(self):
        """
        Test creating multiple autoloaders (archivist).
        """
        with open("qc8960.factory_sfi.desktop.signed", "w") as targetfile:
            targetfile.write("Jackdaws love my big sphinx of quartz"*5000)
        copyfile("qc8960.factory_sfi.desktop.signed", "qc8x30.factory_sfi.desktop.signed")
        copyfile("qc8960.factory_sfi.desktop.signed", "qc8974.factory_sfi.desktop.signed")
        copyfile("qc8960.factory_sfi.desktop.signed", "winchester.factory_sfi.desktop.signed")
        with open("radio.m5730.signed", "w") as targetfile:
            targetfile.write("Why must I chase the cat?"*5000)
        copyfile("radio.m5730.signed", "radio.qc8960.BB.signed")
        copyfile("radio.m5730.signed", "radio.qc8960.omadm.signed")
        copyfile("radio.m5730.signed", "radio.qc8960.wtr.signed")
        copyfile("radio.m5730.signed", "radio.qc8960.wtr5.signed")
        copyfile("radio.m5730.signed", "radio.qc8930.wtr5.signed")
        copyfile("radio.m5730.signed", "radio.qc8974.wtr2.signed")
        bl.generate_loaders("10.1.2.3000", "10.3.2.1000", True)
        for file in os.listdir():
            if file.endswith(".exe"):
                with open(file, 'rb') as filehandle:
                    shahash = sha512()
                    while True:
                        data = filehandle.read(16777216)
                        if not data:
                            break
                        shahash.update(data)
                    assert shahash.hexdigest() in ("3143a5bdfffbab199fe071d720b374d8678e5a2baafaeaf375f747c578a314cdf10059ccfac51fbe992d6d473106c2ba18bb8a80026269b046c3e299c33adaf3",
                                                   "d4872a853e19fb8512067f50555827c74ec33da6fd5d71ae3ddd1b0ce98a18e01727eb1f345f476d6d59bcb438be8780e3f1dc7b212dc63b4b7c09914093a730")

    def test_filename_malformed(self):
        """
        Test filename creation if the device is imaginary.
        """
        assert bl.generate_filename(-1, "10.3.2.2789") is None

    def test_filename_nosuffix(self):
        """
        Test filename creation without suffix.
        """
        assert bl.generate_filename(0, "10.3.2.2789", None) == "Z10_10.3.2.2789_STL100-1.exe"

    def test_suffix_hybrid(self):
        """
        Test suffix formation, if hybrid radio is specified.
        """
        assert bl.format_suffix(True, "SUFFIX", True) == "_RSUFFIX_CORE"

    def test_pretty_formatter(self):
        """
        Test OS/radio version formatting.
        """
        assert bl.pretty_formatter("10.3.2.680",
                                   "10.3.2.681") == ("10.3.02.0680",
                                                     "10.3.02.0681")

    def test_wrap_pseudocap_none(self):
        """
        Test wrapping pseudocap when no files are given.
        """
        with pytest.raises(SystemError):
            bl.wrap_pseudocap("filename.exe", os.getcwd(), None, None)

    def test_wrap_pseudocap_error(self, capsys):
        """
        Test wrapping pseudocap when an error is raised.
        """
        with mock.patch('bbarchivist.pseudocap.make_autoloader', mock.MagicMock(side_effect=IndexError)):
            bl.wrap_pseudocap("filename.exe", os.getcwd(), "radio.m5730.signed", None)
            assert "Could not create" in capsys.readouterr()[0]

#!/usr/bin/env python3
#pylint: disable = I0011, R0201, W0613, C0301
"""Test the barutils module."""

import bbarchivist.barutils as bb
import os
from bbarchivist.utilities import prep_seven_zip, get_seven_zip
from shutil import rmtree, copyfile
from sys import version_info
from hashlib import sha512
from zipfile import ZipFile, ZIP_DEFLATED
try:
    import unittest.mock as mock
except ImportError:
    import mock

def setup_module(module):
    """
    Create necessary files.
    """
    if not os.path.exists("temp"):
        os.mkdir("temp")
    os.chdir("temp")
    with open("testfile.signed", "w") as targetfile:
        targetfile.write("Jackdaws love my big sphinx of quartz")
    with open("Z10_BIGLOADER.exe", "w") as targetfile:
        targetfile.write("0"*95000000)
    if os.path.exists("a_temp_folder"):
        rmtree("a_temp_folder")
    os.mkdir("a_temp_folder")


def teardown_module(module):
    """
    Delete necessary files.
    """
    if os.path.exists("testfile.bar"):
        os.remove("testfile.bar")
    rmtree("bigloaders", ignore_errors=True)
    rmtree("smallloaders", ignore_errors=True)
    rmtree("bigzipped", ignore_errors=True)
    rmtree("smallzipped", ignore_errors=True)
    os.chdir("..")
    rmtree("temp", ignore_errors=True)


class TestClassBarutils:
    """
    Test compression, extraction and related operations.
    """
    def test_extract_bars(self):
        """
        Test extraction.
        """
        shahash = sha512()
        with open("testfile.signed", 'rb') as file:
            while True:
                data = file.read(1024)
                if not data:
                    break
                shahash.update(data)
        orighash = shahash.hexdigest()
        with ZipFile('testfile.bar',
                     'w',
                     ZIP_DEFLATED) as zfile:
            zfile.write("testfile.signed")
        os.remove("testfile.signed")
        bb.extract_bars(os.getcwd())
        shahash2 = sha512()
        with open("testfile.signed", 'rb') as file:
            while True:
                data = file.read(1024)
                if not data:
                    break
                shahash2.update(data)
        newhash = shahash2.hexdigest()
        assert orighash == newhash

    def test_compress_sz(self):
        """
        Test 7z compression.
        """
        exists = prep_seven_zip()
        if exists:
            szexe = get_seven_zip(False)
            bb.compress(os.getcwd(), "7z", szexe=szexe)
            result = bb.sz_verify("Z10_BIGLOADER.7z", szexe)
            if os.path.exists("Z10_BIGLOADER.7z"):
                os.remove("Z10_BIGLOADER.7z")
            assert result
        else:
            pass

    def test_compress_zip(self):
        """
        Test zip compression.
        """
        bb.compress(os.getcwd(), "zip")
        assert bb.zip_verify("Z10_BIGLOADER.zip") == True

    def test_check_zip(self):
        """
        Test zip verification.
        """
        copyfile("Z10_BIGLOADER.zip", "Z10_BIGLOADER.bar")
        assert bb.zip_verify("Z10_BIGLOADER.bar") == True
        if os.path.exists("Z10_BIGLOADER.bar"):
            os.remove("Z10_BIGLOADER.bar")
        if os.path.exists("Z10_BIGLOADER.zip"):
            os.remove("Z10_BIGLOADER.zip")

    def test_compress_gzip(self):
        """
        Test gzip compression.
        """
        bb.compress(os.getcwd(), "tgz")
        assert bb.tgz_verify("Z10_BIGLOADER.tar.gz") == True
        if os.path.exists("Z10_BIGLOADER.tar.gz"):
            os.remove("Z10_BIGLOADER.tar.gz")

    def test_compress_bz2(self):
        """
        Test bz2 compression.
        """
        bb.compress(os.getcwd(), "tbz")
        assert bb.tbz_verify("Z10_BIGLOADER.tar.bz2") == True
        if os.path.exists("Z10_BIGLOADER.tar.bz2"):
            os.remove("Z10_BIGLOADER.tar.bz2")

    def test_compress_lzma(self):
        """
        Test xz compression.
        """
        if version_info[1] < 3:
            pass
        else:
            bb.compress(os.getcwd(), "txz")
            assert bb.txz_verify("Z10_BIGLOADER.tar.xz") == True
            if os.path.exists("Z10_BIGLOADER.tar.xz"):
                os.remove("Z10_BIGLOADER.tar.xz")

    def test_remove_empty_folders(self):
        """
        Test removal of empty folders.
        """
        bb.remove_empty_folders(os.getcwd())
        assert "a_temp_folder" not in os.listdir()

    def test_create_blitz(self):
        """
        Test blitz package creation.
        """
        bb.create_blitz(os.getcwd(), "testing")
        assert bb.zip_verify("Blitz-testing.zip") == True
        if os.path.exists("Blitz-testing.zip"):
            os.remove("Blitz-testing.zip")

    def test_filter_method_good(self):
        """
        Test method checking, best case.
        """
        assert bb.filter_method("tbz", None) == "tbz"

    def test_filter_method_bad(self):
        """
        Test method checking, worst case.
        """
        with mock.patch('bbarchivist.utilities.prep_seven_zip', mock.MagicMock(return_value=False)):
            assert bb.filter_method("7z", None) == "zip"

    def test_calculate_strength_32(self):
        """
        Test compression strength for 32-bit systems.
        """
        with mock.patch('bbarchivist.utilities.is_amd64', mock.MagicMock(return_value=False)):
            assert bb.calculate_strength() == 5

    def test_calculate_strength_64(self):
        """
        Test compression strength for 64-bit systems.
        """
        with mock.patch('bbarchivist.utilities.is_amd64', mock.MagicMock(return_value=True)):
            assert bb.calculate_strength() == 9

class TestClassBarutilsLoaderMover():
    """
    Test moving of files.
    """
    @classmethod
    def setup_class(cls):
        """
        Create files to move.
        """
        with open("Z30_SMALLLOADER.exe", "w") as targetfile:
            targetfile.write("0"*95000)
        if not os.path.exists("Z10_BIGLOADER.exe"):
            with open("Z10_BIGLOADER.exe", "w") as targetfile:
                targetfile.write("0"*95000000)
        copyfile("Z10_BIGLOADER.exe", "Q10_BIGZIPPED.zip")
        copyfile("Z30_SMALLLOADER.exe", "Z3_SMALLZIPPED.zip")
        os.mkdir("bigloaders")
        os.mkdir("smallloaders")
        os.mkdir("bigzipped")
        os.mkdir("smallzipped")
        bb.move_loaders(os.getcwd(), "bigloaders", "smallloaders", "bigzipped", "smallzipped")

    def test_move_loaders_smallzip(self):
        """
        Test moving small, compressed loaders.
        """
        assert "Z3_SMALLZIPPED.zip" in os.listdir("smallzipped")

    def test_move_loaders_bigzip(self):
        """
        Test moving large, compressed loaders.
        """
        assert "Q10_BIGZIPPED.zip" in os.listdir("bigzipped")

    def test_move_loaders_smallexe(self):
        """
        Test moving small, uncompressed loaders.
        """
        assert "Z30_SMALLLOADER.exe" in os.listdir("smallloaders")

    def test_move_loaders_bigexe(self):
        """
        Test moving large, uncompressed loaders.
        """
        assert "Z10_BIGLOADER.exe" in os.listdir("bigloaders")

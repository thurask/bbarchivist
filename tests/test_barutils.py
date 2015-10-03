#!/usr/bin/env python3
#pylint: disable = I0011, R0201, W0613, C0301
"""Test the barutils module."""

import bbarchivist.barutils as bb
import os
from bbarchivist.utilities import prep_seven_zip, get_seven_zip
from shutil import rmtree, copyfile
from sys import version_info
from hashlib import sha512
import zipfile
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
    rmtree("bigbars", ignore_errors=True)
    rmtree("smallbars", ignore_errors=True)
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
        with zipfile.ZipFile('testfile.bar',
                             'w',
                             zipfile.ZIP_DEFLATED) as zfile:
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

    def test_remove_signed_files(self):
        """
        Test removal of signed files.
        """
        os.mkdir("signeds")
        signeddir = os.path.abspath(os.path.join(os.getcwd(), "signeds"))
        with open(os.path.join(signeddir, "something.signed"), "w") as afile:
            afile.write("Haters gonna hate")
        with open(os.path.join(signeddir, "something.else"), "w") as afile:
            afile.write("I'm just gonna shake")
        bb.remove_signed_files(signeddir)
        assert len(os.listdir("signeds")) == 1
        rmtree(signeddir, ignore_errors=True)

    def test_remove_uncomps(self):
        """
        Test removing uncompressed loader directories.
        """
        os.mkdir("uncompL")
        os.mkdir("uncompR")
        bb.remove_unpacked_loaders("uncompL", "uncompR", True)
        assert not any(["uncompL", "uncompR"]) in os.listdir()

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

    def test_compress_suite(self):
        """
        Test the bulk compression/verification suite.
        """
        os.mkdir("suite")
        suitedir = os.path.abspath(os.path.join(os.getcwd(), "suite"))
        with open(os.path.join(suitedir, "Z10.exe"), "w") as afile:
            afile.write("Haters gonna hate")
        with open(os.path.join(suitedir, "Z30.exe"), "w") as afile:
            afile.write("I'm just gonna shake")
        bb.compress_suite(suitedir, "zip", None, True)
        rmtree(suitedir, ignore_errors=True)


class TestClassBarutilsVerifier:
    """
    Test verification of archives.
    """
    @classmethod
    def setup_class(cls):
        """
        Create compressed loaders to verify.
        """
        os.mkdir("verifiers")
        verdir = os.path.abspath(os.path.join(os.getcwd(), "verifiers"))
        aloader = os.path.join(verdir, "Q10.exe")
        with open(aloader, "w") as afile:
            afile.write("Haters gonna hate")
        exists = prep_seven_zip()
        if exists:
            szexe = get_seven_zip(False)
            bb.compress(verdir, "7z", szexe, True)
        else:
            pass

    def test_verify_sz(self):
        """
        Test 7z verification.
        """
        verdir = os.path.abspath(os.path.join(os.getcwd(), "verifiers"))
        exists = prep_seven_zip()
        if not exists:
            pass
        else:
            szexe = get_seven_zip(False)
            assert bb.verify(verdir, '7z', szexe, True)

    def test_verify_zip(self):
        """
        Test zip verification.
        """
        verdir = os.path.abspath(os.path.join(os.getcwd(), "verifiers"))
        assert bb.verify(verdir, 'zip', None, True)

    def test_verify_tgz(self):
        """
        Test tar.gz verification.
        """
        verdir = os.path.abspath(os.path.join(os.getcwd(), "verifiers"))
        assert bb.verify(verdir, 'tgz', None, True)

    def test_verify_tbz(self):
        """
        Test tar.bz2 verification.
        """
        verdir = os.path.abspath(os.path.join(os.getcwd(), "verifiers"))
        assert bb.verify(verdir, 'tbz', None, True)

    def test_verify_txz(self):
        """
        Test tar.xz verification.
        """
        if version_info[1] < 3:
            pass
        else:
            verdir = os.path.abspath(os.path.join(os.getcwd(), "verifiers"))
            assert bb.verify(verdir, 'txz', None, True)


class TestClassBarutilsSha512:
    """
    Test manifest parsing/verification.
    """
    @classmethod
    def setup_class(cls):
        """
        Create file to verify.
        """
        mstring = b"Somestuff\nName: target.signed\nDigest: tmpeiqm5cFdIwu5YWw4aOkEojS2vw74tsS-onS8qPhT53sEd5LqGW7Ueqmws_rKUE5RV402n2CehlQSwkGwBwQ\nmorestuff"
        fstring = b"Jackdaws love my big sphinx of quartz"
        with zipfile.ZipFile("mfest.bar.dummy", mode="w",
                             compression=zipfile.ZIP_DEFLATED) as zfile:
            zfile.writestr("MANIFEST.MF", mstring)
            zfile.writestr("target.signed", fstring)
        with open("target.signed", "wb") as targetfile:
            targetfile.write(fstring)

    def test_sha512_retrieve(self):
        """
        Test retrieval of SHA512 hash (in Base64) from a bar file's manifest.
        """
        assert bb.retrieve_sha512("mfest.bar.dummy") == (b"target.signed", b"tmpeiqm5cFdIwu5YWw4aOkEojS2vw74tsS-onS8qPhT53sEd5LqGW7Ueqmws_rKUE5RV402n2CehlQSwkGwBwQ")

    def test_sha512_verify(self):
        """
        Test comparison of signed file hash with that from the manifest.
        """
        assert  bb.verify_sha512("target.signed", b"tmpeiqm5cFdIwu5YWw4aOkEojS2vw74tsS-onS8qPhT53sEd5LqGW7Ueqmws_rKUE5RV402n2CehlQSwkGwBwQ")


class TestClassBarutilsLoaderMover:
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
        bdo, bdr, ldo, ldr, zdo, zdr = bb.make_dirs(os.getcwd(), "osversion", "radioversion")
        del bdo
        del bdr
        bb.move_loaders(os.getcwd(), ldo, ldr, zdo, zdr)

    def test_move_loaders_smallzip(self):
        """
        Test moving small, compressed loaders.
        """
        zipped = os.path.join(os.getcwd(), "zipped")
        assert "Z3_SMALLZIPPED.zip" in os.listdir(os.path.join(zipped, "radioversion"))

    def test_move_loaders_bigzip(self):
        """
        Test moving large, compressed loaders.
        """
        zipped = os.path.join(os.getcwd(), "zipped")
        assert "Q10_BIGZIPPED.zip" in os.listdir(os.path.join(zipped, "osversion"))

    def test_move_loaders_smallexe(self):
        """
        Test moving small, uncompressed loaders.
        """
        loaders = os.path.join(os.getcwd(), "loaders")
        assert "Z30_SMALLLOADER.exe" in os.listdir(os.path.join(loaders, "radioversion"))

    def test_move_loaders_bigexe(self):
        """
        Test moving large, uncompressed loaders.
        """
        loaders = os.path.join(os.getcwd(), "loaders")
        assert "Z10_BIGLOADER.exe" in os.listdir(os.path.join(loaders, "osversion"))


class TestClassBarUtilsBarMover:
    """
    Test moving of files.
    """
    @classmethod
    def setup_class(cls):
        """
        Create files to move.
        """
        with open("BIGBAR.bar", "w") as targetfile:
            targetfile.write("0"*95000000)
        with open("SMALLBAR.bar", "w") as targetfile:
            targetfile.write("0"*95000)
        bardir = os.path.join(os.getcwd(), "bars")
        bardir_os = os.path.join(bardir, "osversion")
        bardir_radio = os.path.join(bardir, "radioversion")
        bb.move_bars(os.getcwd(), bardir_os, bardir_radio)

    def test_move_bars_small(self):
        """
        Test moving small bar files.
        """
        bars = os.path.join(os.getcwd(), "bars")
        assert "SMALLBAR.bar" in os.listdir(os.path.join(bars, "radioversion"))

    def test_move_bars_big(self):
        """
        Test moving large bar files.
        """
        bars = os.path.join(os.getcwd(), "bars")
        assert "BIGBAR.bar" in os.listdir(os.path.join(bars, "osversion"))

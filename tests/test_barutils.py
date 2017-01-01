#!/usr/bin/env python3
"""Test the barutils module."""

import os
import tempfile
from shutil import rmtree, copyfile
from hashlib import sha512
import zipfile
try:
    import unittest.mock as mock
except ImportError:
    import mock
import pytest
import bbarchivist.barutils as bb

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "2015-2017 Thurask"


def setup_module(module):
    """
    Create necessary files.
    """
    if not os.path.exists("temp_barutils"):
        os.mkdir("temp_barutils")
    os.chdir("temp_barutils")
    with open("testfile.signed", "w") as targetfile:
        targetfile.write("Jackdaws love my big sphinx of quartz")
    with open("Z10_BIGLOADER.exe", "w") as targetfile:
        targetfile.write("0" * 95000000)
    if os.path.exists("a_temp_folder"):
        rmtree("a_temp_folder")
    os.mkdir("a_temp_folder")


def teardown_module(module):
    """
    Delete necessary files.
    """
    os.chdir("..")
    rmtree("temp_barutils", ignore_errors=True)


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
        with zipfile.ZipFile('testfile.bar', 'w', zipfile.ZIP_DEFLATED) as zfile:
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

    def test_extract_bars_fail(self, capsys):
        """
        Test extraction failure, raise exception.
        """
        with mock.patch('os.listdir', mock.MagicMock(side_effect=OSError)):
            bb.extract_bars(os.getcwd())
            assert "EXTRACTION FAILURE" in capsys.readouterr()[0]

    def test_check_bar(self):
        """
        Test zip verification.
        """
        if not os.path.exists("testfile.bar"):
            if not os.path.exists("testfile.signed"):
                with open("testfile.signed", "w") as targetfile:
                    targetfile.write("Jackdaws love my big sphinx of quartz")
            with zipfile.ZipFile('testfile.bar', 'w', zipfile.ZIP_DEFLATED) as zfile:
                zfile.write("testfile.signed")
        assert zipfile.is_zipfile("testfile.bar")

    def test_create_blitz(self):
        """
        Test blitz package creation.
        """
        bb.create_blitz(os.getcwd(), "testing")
        assert zipfile.is_zipfile("Blitz-testing.zip")
        if os.path.exists("Blitz-testing.zip"):
            os.remove("Blitz-testing.zip")


class TestClassBarutilsRemovers:
    """
    Test file/folder removal.
    """

    def test_remove_empty_folders(self):
        """
        Test removal of empty folders.
        """
        if not os.path.exists("a_temp_folder"):
            os.mkdir("a_temp_folder")
        bb.remove_empty_folders(os.getcwd())
        assert "a_temp_folder" not in os.listdir()

    def test_remove_empty_folders_fail(self):
        """
        Test failure to remove empty folders.
        """
        if not os.path.exists("a_temp_folder"):
            os.mkdir("a_temp_folder")
        with mock.patch('os.rmdir', mock.MagicMock(side_effect=NotImplementedError)):
            bb.remove_empty_folders(os.getcwd())
        assert "a_temp_folder" in os.listdir()

    def test_remove_signed_files(self):
        """
        Test removal of signed files.
        """
        with tempfile.TemporaryDirectory() as tempdir:
            signeddir = os.path.abspath(tempdir)
            with open(os.path.join(signeddir, "something.signed"), "w") as afile:
                afile.write("Haters gonna hate")
            with open(os.path.join(signeddir, "something.else"), "w") as afile:
                afile.write("I'm just gonna shake")
            bb.remove_signed_files(signeddir)
            assert len(os.listdir(signeddir)) == 1

    def test_remove_uncomps(self):
        """
        Test removing uncompressed loader directories.
        """
        os.mkdir("uncompL")
        os.mkdir("uncompR")
        bb.remove_unpacked_loaders("uncompL", "uncompR", True)
        assert any(["uncompL", "uncompR"]) not in os.listdir()


class TestClassBarutilsBarTester:
    """
    Test verification of bar files.
    """
    @classmethod
    def setup_class(cls):
        """
        Create compressed loaders to verify.
        """
        if not os.path.exists("verifiers"):
            os.makedirs("verifiers", exist_ok=True)
        verdir = os.path.abspath(os.path.join(os.getcwd(), "verifiers"))
        aloader = os.path.join(verdir, "Q10.exe")
        azip = os.path.join(verdir, "Q10.zip")
        with open(aloader, "w") as afile:
            afile.write("Haters gonna hate")
        with zipfile.ZipFile(azip, 'w', zipfile.ZIP_DEFLATED, allowZip64=True) as zfile:
            zfile.write(aloader)

    def test_bar_tester(self):
        """
        Test bar verification.
        """
        verdir = os.path.abspath(os.path.join(os.getcwd(), "verifiers"))
        infile = os.path.join(verdir, "Q10.zip")
        outfile = os.path.join(verdir, "Q10.bar")
        copyfile(infile, outfile)
        assert bb.bar_tester(outfile) is None

    def test_bar_tester_fail(self):
        """
        Test bar verification failure.
        """
        verdir = os.path.abspath(os.path.join(os.getcwd(), "verifiers"))
        infile = os.path.join(verdir, "Q11.bar")
        with open(infile, "w") as afile:
            afile.write("Heartbreakers gonna break")
        assert "Q11.bar" in bb.bar_tester(infile)


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
        with zipfile.ZipFile("nomfest.bar.dummy", mode="w",
                             compression=zipfile.ZIP_DEFLATED) as zfile:
            zfile.writestr("target.signed", fstring)
        with open("target.signed", "wb") as targetfile:
            targetfile.write(fstring)

    def test_sha512_retrieve(self):
        """
        Test retrieval of SHA512 hash (in Base64) from a bar file's manifest.
        """
        assert bb.retrieve_sha512("mfest.bar.dummy") == (
            b"target.signed",
            b"tmpeiqm5cFdIwu5YWw4aOkEojS2vw74tsS-onS8qPhT53sEd5LqGW7Ueqmws_rKUE5RV402n2CehlQSwkGwBwQ")

    def test_sha512_retrieve_fail(self, capsys):
        """
        Test SHA512 hash retrieval failure.
        """
        with mock.patch('zipfile.ZipFile', mock.MagicMock(side_effect=OSError)):
            bb.retrieve_sha512("mfest.bar.dummy")
            assert "EXTRACTION FAILURE" in capsys.readouterr()[0]

    def test_sha512_retrieve_noman(self):
        """
        Test SHA512 manifest read failure.
        """
        with pytest.raises(SystemExit):
            bb.retrieve_sha512("nomfest.bar.dummy")

    def test_sha512_verify(self):
        """
        Test comparison of signed file hash with that from the manifest.
        """
        assert bb.verify_sha512(
            "target.signed",
            b"tmpeiqm5cFdIwu5YWw4aOkEojS2vw74tsS-onS8qPhT53sEd5LqGW7Ueqmws_rKUE5RV402n2CehlQSwkGwBwQ")


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
            targetfile.write("0" * 95000)
        if not os.path.exists("Z10_BIGLOADER.exe"):
            with open("Z10_BIGLOADER.exe", "w") as targetfile:
                targetfile.write("0" * 95000000)
        copyfile("Z10_BIGLOADER.exe", "Q10_BIGZIPPED.zip")
        copyfile("Z30_SMALLLOADER.exe", "Z3_SMALLZIPPED.zip")
        bdo, bdr, ldo, ldr, zdo, zdr = bb.make_dirs(os.getcwd(), "osversion", "radioversion")
        del bdo
        del bdr
        while True:
            try:
                bb.move_loaders(os.getcwd(), ldo, ldr, zdo, zdr)
            except PermissionError:
                continue
            else:
                break

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


class TestClassBarutilsBarMover:
    """
    Test moving of files.
    """
    @classmethod
    def setup_class(cls):
        """
        Create files to move.
        """
        with open("BIGBAR.bar", "w") as targetfile:
            targetfile.write("0" * 95000000)
        with open("SMALLBAR.bar", "w") as targetfile:
            targetfile.write("0" * 95000)
        copyfile("BIGBAR.bar", "BIGBAR2.bar")
        copyfile("BIGBAR.bar", "BIGBAR3.bar")
        copyfile("SMALLBAR.bar", "SMALLBAR2.bar")
        copyfile("SMALLBAR.bar", "SMALLBAR3.bar")
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

    def test_replace_bar_pair(self):
        """
        Test replacing single bar pair.
        """
        osfile = os.path.join(os.getcwd(), "bars", "osversion", "BIGBAR3.bar")
        radfile = os.path.join(os.getcwd(), "bars", "radioversion", "SMALLBAR3.bar")
        bb.replace_bar_pair(os.getcwd(), osfile, radfile)
        assert all(x in os.listdir() for x in ["BIGBAR3.bar", "SMALLBAR3.bar"])

    def test_replace_bars_bulk(self):
        """
        Test replacing multiple bar pairs.
        """
        os1 = os.path.join(os.getcwd(), "bars", "osversion", "BIGBAR.bar")
        os2 = os.path.join(os.getcwd(), "bars", "osversion", "BIGBAR2.bar")
        rad1 = os.path.join(os.getcwd(), "bars", "radioversion", "SMALLBAR.bar")
        rad2 = os.path.join(os.getcwd(), "bars", "radioversion", "SMALLBAR2.bar")
        bb.replace_bars_bulk(os.getcwd(), [os1, os2, rad1, rad2])
        assert all(x in os.listdir() for x in ["BIGBAR2.bar", "SMALLBAR2.bar", "BIGBAR.bar", "SMALLBAR.bar"])

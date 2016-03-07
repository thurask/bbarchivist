#!/usr/bin/env python3
#pylint: disable=no-self-use,unused-argument,line-too-long
"""Test the barutils module."""

import os
from shutil import rmtree, copyfile
from sys import version_info
from hashlib import sha512
import zipfile
try:
    import unittest.mock as mock
except ImportError:
    import mock
import pytest
import bbarchivist.barutils as bb
from bbarchivist.utilities import prep_seven_zip, get_seven_zip

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "Copyright 2015-2016 Thurask"


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
        targetfile.write("0"*95000000)
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
        smeg = bb.zip_verify("testfile.bar")
        assert smeg

    def test_create_blitz(self):
        """
        Test blitz package creation.
        """
        bb.create_blitz(os.getcwd(), "testing")
        smeg = bb.zip_verify("Blitz-testing.zip")
        assert smeg
        if os.path.exists("Blitz-testing.zip"):
            os.remove("Blitz-testing.zip")

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


class TestClassBarutilsCompression:
    """
    Test file compression.
    """
    def test_compress_sz(self):
        """
        Test 7z compression.
        """
        exists = prep_seven_zip()
        if exists:
            szexe = get_seven_zip(False)
            bb.compress(os.getcwd(), method="7z", szexe=szexe)
            result = bb.sz_verify("Z10_BIGLOADER.7z", szexe)
            if os.path.exists("Z10_BIGLOADER.7z"):
                os.remove("Z10_BIGLOADER.7z")
            assert result
        else:
            pass

    def test_compress_sz_fail(self, capsys):
        """
        Test 7z compresssion failure.
        """
        exists = prep_seven_zip()
        if exists:
            szexe = get_seven_zip(False)
            with mock.patch("subprocess.call", mock.MagicMock(return_value=2)):
                bb.sz_compress(os.getcwd(), "7z", szexe=szexe, errors=True)
                assert "FATAL ERROR" in capsys.readouterr()[0]
        else:
            pass

    def test_compress_zip(self):
        """
        Test zip compression.
        """
        bb.compress(os.getcwd(), "zip")
        smeg = bb.zip_verify("Z10_BIGLOADER.zip")
        assert smeg

    def test_compress_zip_fail(self):
        """
        Test zip compression failure.
        """
        with mock.patch("bbarchivist.barutils.bar_tester", mock.MagicMock(return_value="Z10_BIGLOADER.zip")):
            smeg = bb.zip_verify("Z10_BIGLOADER.zip")
            assert not smeg

    def test_compress_tar(self):
        """
        Test tar packing.
        """
        bb.compress(os.getcwd(), "tar")
        assert bb.tar_verify("Z10_BIGLOADER.tar")
        if os.path.exists("Z10_BIGLOADER.tar"):
            os.remove("Z10_BIGLOADER.tar")

    def test_compress_tar_fail(self):
        """
        Test tar packing failure.
        """
        with mock.patch("tarfile.TarFile.getmembers", mock.MagicMock(return_value=False)):
            assert not bb.zip_verify("Z10_BIGLOADER.tar")

    def test_compress_gzip(self):
        """
        Test gzip compression.
        """
        bb.compress(os.getcwd(), "tgz")
        assert bb.tgz_verify("Z10_BIGLOADER.tar.gz")
        if os.path.exists("Z10_BIGLOADER.tar.gz"):
            os.remove("Z10_BIGLOADER.tar.gz")

    def test_compress_gzip_fail(self):
        """
        Test gzip compression failure.
        """
        with mock.patch("tarfile.TarFile.getmembers", mock.MagicMock(return_value=False)):
            assert not bb.zip_verify("Z10_BIGLOADER.tar.gz")

    def test_compress_bz2(self):
        """
        Test bz2 compression.
        """
        bb.compress(os.getcwd(), "tbz")
        assert bb.tbz_verify("Z10_BIGLOADER.tar.bz2")
        if os.path.exists("Z10_BIGLOADER.tar.bz2"):
            os.remove("Z10_BIGLOADER.tar.bz2")

    def test_compress_bz2_fail(self):
        """
        Test bz2 compression failure.
        """
        with mock.patch("tarfile.TarFile.getmembers", mock.MagicMock(return_value=False)):
            assert not bb.zip_verify("Z10_BIGLOADER.tar.bz2")

    def test_compress_lzma(self):
        """
        Test xz compression.
        """
        if version_info[1] < 3:
            pass
        else:
            bb.compress(os.getcwd(), "txz")
            assert bb.txz_verify("Z10_BIGLOADER.tar.xz")
            if os.path.exists("Z10_BIGLOADER.tar.xz"):
                os.remove("Z10_BIGLOADER.tar.xz")

    def test_compress_lzma_fail(self):
        """
        Test xz compression failure.
        """
        if version_info[1] < 3:
            pass
        else:
            with mock.patch("tarfile.TarFile.getmembers", mock.MagicMock(return_value=False)):
                assert not bb.zip_verify("Z10_BIGLOADER.tar.xz")

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
        os.mkdir("signeds")
        signeddir = os.path.abspath("signeds")
        with open(os.path.join(signeddir, "something.signed"), "w") as afile:
            afile.write("Haters gonna hate")
        with open(os.path.join(signeddir, "something.else"), "w") as afile:
            afile.write("I'm just gonna shake")
        bb.remove_signed_files(signeddir)
        assert len(os.listdir(signeddir)) == 1
        rmtree(signeddir, ignore_errors=True)

    def test_remove_uncomps(self):
        """
        Test removing uncompressed loader directories.
        """
        os.mkdir("uncompL")
        os.mkdir("uncompR")
        bb.remove_unpacked_loaders("uncompL", "uncompR", True)
        assert any(["uncompL", "uncompR"]) not in os.listdir()


class TestClassBarutilsMethods:
    """
    Test method filtering.
    """
    def test_filter_method_null(self):
        """
        Test method checking, null case.
        """
        assert bb.filter_method("tbz", None) == "tbz"

    def test_filter_method_good(self):
        """
        Test method checking, best case.
        """
        with mock.patch('bbarchivist.utilities.prep_seven_zip', mock.MagicMock(return_value=False)):
            assert bb.filter_method("7z", "7za") == "7z"

    def test_filter_method_bad(self):
        """
        Test method checking, worst case.
        """
        with mock.patch('bbarchivist.utilities.prep_seven_zip', mock.MagicMock(return_value=False)):
            assert bb.filter_method("7z", None) == "zip"

    def test_filter_method_ok(self):
        """
        Test method checking, middle case.
        """
        with mock.patch('bbarchivist.utilities.prep_seven_zip', mock.MagicMock(return_value=True)):
            with mock.patch('bbarchivist.utilities.get_seven_zip', mock.MagicMock(return_value='7za')):
                assert bb.filter_method("7z", None) == "7z"

    def test_filter_method_legacy(self):
        """
        Test method checking, Python 3.2.
        """
        if version_info[1] > 2:
            pass
        else:
            assert bb.filter_method("txz", None) == "zip"


class TestClassBarutilsVerifier:
    """
    Test verification of archives.
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
        with open(aloader, "w") as afile:
            afile.write("Haters gonna hate")

    def test_verify_sz(self):
        """
        Test 7z verification.
        """
        with mock.patch('subprocess.call', mock.MagicMock(return_value=0)):
            verdir = os.path.abspath(os.path.join(os.getcwd(), "verifiers"))
            filepath = os.path.join(verdir, "Q10.7z")
            exists = prep_seven_zip()
            if not exists:
                pass
            else:
                szexe = get_seven_zip(False)
                if not os.path.exists("Q10.7z"):
                    bb.compress(verdir, "7z", szexe, True)
                assert bb.sz_verify(filepath, szexe)

    def test_verify_sz_fail(self):
        """
        Test 7z verification failure.
        """
        with mock.patch('subprocess.call', mock.MagicMock(return_value=255)):
            verdir = os.path.abspath(os.path.join(os.getcwd(), "verifiers"))
            filepath = os.path.join(verdir, "Q10.7z")
            exists = prep_seven_zip()
            if not exists:
                pass
            else:
                szexe = get_seven_zip(False)
                assert not bb.sz_verify(filepath, szexe)

    def test_verify_zip(self):
        """
        Test zip verification.
        """
        verdir = os.path.abspath(os.path.join(os.getcwd(), "verifiers"))
        if not os.path.exists("Q10.zip"):
            bb.compress(verdir, "zip", None, True)
        filepath = os.path.join(verdir, "Q10.zip")
        smeg = bb.zip_verify(filepath)
        assert smeg

    def test_verify_zip_fail(self):
        """
        Test zip verification failure.
        """
        with mock.patch('zipfile.is_zipfile', mock.MagicMock(return_value=False)):
            verdir = os.path.abspath(os.path.join(os.getcwd(), "verifiers"))
            filepath = os.path.join(verdir, "Q10.zip")
            assert not bb.zip_verify(filepath)

    def test_verify_tgz(self):
        """
        Test tar.gz verification.
        """
        verdir = os.path.abspath(os.path.join(os.getcwd(), "verifiers"))
        if not os.path.exists("Q10.tar.gz"):
            bb.compress(verdir, "tgz", None, True)
        filepath = os.path.join(verdir, "Q10.tar.gz")
        assert bb.tgz_verify(filepath)

    def test_verify_tgz_fail(self):
        """
        Test tar.gz verification failure.
        """
        with mock.patch('tarfile.is_tarfile', mock.MagicMock(return_value=False)):
            verdir = os.path.abspath(os.path.join(os.getcwd(), "verifiers"))
            filepath = os.path.join(verdir, "Q10.tar.gz")
            assert not bb.tgz_verify(filepath)

    def test_verify_tbz(self):
        """
        Test tar.bz2 verification.
        """
        verdir = os.path.abspath(os.path.join(os.getcwd(), "verifiers"))
        if not os.path.exists("Q10.tar.bz2"):
            bb.compress(verdir, "tbz", None, True)
        filepath = os.path.join(verdir, "Q10.tar.bz2")
        assert bb.tbz_verify(filepath)

    def test_verify_tbz_fail(self):
        """
        Test tar.bz2 verification failure.
        """
        with mock.patch('tarfile.is_tarfile', mock.MagicMock(return_value=False)):
            verdir = os.path.abspath(os.path.join(os.getcwd(), "verifiers"))
            filepath = os.path.join(verdir, "Q10.tar.bz2")
            assert not bb.tbz_verify(filepath)

    def test_verify_txz(self):
        """
        Test tar.xz verification.
        """
        if version_info[1] < 3:
            pass
        else:
            verdir = os.path.abspath(os.path.join(os.getcwd(), "verifiers"))
            if not os.path.exists("Q10.tar.xz"):
                bb.compress(verdir, "txz", None, True)
            filepath = os.path.join(verdir, "Q10.tar.xz")
            assert bb.txz_verify(filepath)

    def test_verify_txz_fail(self):
        """
        Test tar.xz verification failure.
        """
        if version_info[1] < 3:
            pass
        else:
            with mock.patch('tarfile.is_tarfile', mock.MagicMock(return_value=False)):
                verdir = os.path.abspath(os.path.join(os.getcwd(), "verifiers"))
                filepath = os.path.join(verdir, "Q10.tar.xz")
                assert not bb.txz_verify(filepath)

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
        assert bb.retrieve_sha512("mfest.bar.dummy") == (b"target.signed", b"tmpeiqm5cFdIwu5YWw4aOkEojS2vw74tsS-onS8qPhT53sEd5LqGW7Ueqmws_rKUE5RV402n2CehlQSwkGwBwQ")

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


class TestClassBarutilsConfig:
    """
    Test reading/writing configs with ConfigParser.
    """
    def test_compress_loader(self):
        """
        Test reading compression settings.
        """
        try:
            os.remove("bbarchivist.ini")
        except (OSError, IOError):
            pass
        with mock.patch('os.path.expanduser', mock.MagicMock(return_value=os.getcwd())):
            assert bb.compress_config_loader(os.getcwd()) == "7z"

    def test_compress_loader_legacy(self):
        """
        Test reading compression settings, Python 3.2.
        """
        if version_info[1] > 2:
            pass
        else:
            try:
                os.remove("bbarchivist.ini")
            except (OSError, IOError):
                pass
            with mock.patch('os.path.expanduser', mock.MagicMock(return_value=os.getcwd())):
                bb.compress_config_writer("txz")
                print(bb.compress_config_loader())
                assert bb.compress_config_loader(os.getcwd()) == "zip"

    def test_compress_writer(self):
        """
        Test writing compression settings.
        """
        try:
            os.remove("bbarchivist.ini")
        except (OSError, IOError):
            pass
        with mock.patch('os.path.expanduser', mock.MagicMock(return_value=os.getcwd())):
            with mock.patch('bbarchivist.barutils.compress_config_loader', mock.MagicMock(return_value="tbz")):
                bb.compress_config_writer()
            assert bb.compress_config_loader() == "tbz"

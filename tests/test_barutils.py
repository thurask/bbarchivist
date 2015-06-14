import bbarchivist.barutils as bb
import os
from shutil import rmtree, copyfile
from sys import version_info
from tarfile import is_tarfile
from hashlib import sha512
from zipfile import ZipFile, ZIP_DEFLATED


def setup_module(module):
    if not os.path.exists("temp"):
        os.mkdir("temp")
    os.chdir("temp")
    with open("testfile.signed", "w") as targetfile:
        targetfile.write("Jackdaws love my big sphinx of quartz")
    with open("Z10_BIGLOADER.exe", "w") as targetfile:
        targetfile.write("0"*95000000)
    os.mkdir("a_temp_folder")


def teardown_module(module):
    os.remove("testfile.bar")
    rmtree("bigloaders", ignore_errors=True)
    rmtree("smallloaders", ignore_errors=True)
    rmtree("bigzipped", ignore_errors=True)
    rmtree("bigzipped", ignore_errors=True)
    os.chdir("..")
    rmtree("temp")


class TestClassBarutils:

    def test_extract_bars(self):
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

    def test_compress_zip(self):
        bb.compress(os.getcwd(), "zip")
        with ZipFile("Z10_BIGLOADER.zip",
                     mode="r",
                     compression=ZIP_DEFLATED) as zfile:
            assert zfile.testzip() == None

    def test_compress_gzip(self):
        bb.compress(os.getcwd(), "tgz")
        assert is_tarfile("Z10_BIGLOADER.tar.gz")

    def test_compress_bz2(self):
        bb.compress(os.getcwd(), "tbz")
        assert is_tarfile("Z10_BIGLOADER.tar.bz2")

    def test_compress_lzma(self):
        if version_info[1] < 3:
            pass
        else:
            bb.compress(os.getcwd(), "txz")
            assert is_tarfile("Z10_BIGLOADER.tar.xz")

    def test_remove_empty_folders(self):
        bb.remove_empty_folders(os.getcwd())
        assert "a_temp_folder" not in os.listdir()

    def test_create_blitz(self):
        bb.create_blitz(os.getcwd(), "testing")
        with ZipFile("Blitz-testing.zip",
                     mode="r",
                     compression=ZIP_DEFLATED) as zfile:
            assert zfile.testzip() == None

    def test_move_loaders(self):
        if os.path.exists("Z10_BIGLOADER.zip"):
            os.remove("Z10_BIGLOADER.zip")
        if os.path.exists("Z10_BIGLOADER.tar.gz"):
            os.remove("Z10_BIGLOADER.tar.gz")
        if os.path.exists("Z10_BIGLOADER.tar.bz2"):
            os.remove("Z10_BIGLOADER.tar.bz2")
        if os.path.exists("Z10_BIGLOADER.tar.xz"):
            os.remove("Z10_BIGLOADER.tar.xz")
        if os.path.exists("Blitz-testing.zip"):
            os.remove("Blitz-testing.zip")
        with open("Z30_SMALLLOADER.exe", "w") as targetfile:
            targetfile.write("0"*95000)
        copyfile("Z10_BIGLOADER.exe", "Q10_BIGZIPPED.zip")
        copyfile("Z30_SMALLLOADER.exe", "Z3_SMALLZIPPED.zip")
        os.mkdir("bigloaders")
        os.mkdir("smallloaders")
        os.mkdir("bigzipped")
        os.mkdir("smallzipped")
        bb.move_loaders(os.getcwd(), "bigloaders", "smallloaders", "bigzipped", "smallzipped") #@IgnorePep8
        assert os.listdir("bigloaders")[0] == "Z10_BIGLOADER.exe"
        assert os.listdir("smallloaders")[0] == "Z30_SMALLLOADER.exe"
        assert os.listdir("bigzipped")[0] == "Q10_BIGZIPPED.zip"
        assert os.listdir("smallzipped")[0] == "Z3_SMALLZIPPED.zip"
import bbarchivist.pseudocap as bp
import os
from shutil import rmtree, copyfile
from hashlib import sha512


def setup_module(module):
    if not os.path.exists("temp"):
        os.mkdir("temp")
    os.chdir("temp")
    with open("firstfile", "w") as targetfile:
        targetfile.write("Jackdaws love my big sphinx of quartz")
    with open("cap-3.11.0.22.dat", "w") as targetfile:
        targetfile.write("0"*9500000)
    bp.make_offset("firstfile")
    copyfile("offset.hex", "offset.tmp")
    bp.make_autoloader("loader.exe", "firstfile")
    copyfile("offset.tmp", "offset.hex")
    if os.path.exists("offset.tmp"):
        os.remove("offset.tmp")


def teardown_module(module):
    if os.path.exists("cap-3.11.0.22.dat"):
        os.remove("cap-3.11.0.22.dat")
    if os.path.exists("firstfile"):
        os.remove("firstfile")
    os.chdir("..")
    rmtree("temp")


class TestClassPseudocap:

    def test_ghetto_convert(self):
        assert bp.ghetto_convert(987654321) == b'\x00\x00\x00\x00\xb1h\xde:'

    def test_make_offset_len(self):
        with open("offset.hex", "rb") as targetfile:
            data = targetfile.read()
        assert len(data) == 208

    def test_make_offset_hash(self):
        shahash = sha512()
        with open("offset.hex", "rb") as targetfile:
            data = targetfile.read()
            shahash.update(data)
        thehash = shahash.hexdigest()
        assert thehash == '8001a4814bff60f755d8e86a250fee517e983e54cdfc64964b2120f8ce0444ea786c441f0707f1a8a3ccda612281f6ee226264059833abcf8c910883564e8d32'

    def test_make_autoloader_hash(self):
        shahash = sha512()
        with open("loader.exe", 'rb') as file:
            while True:
                data = file.read(1048576)
                if not data:
                    break
                shahash.update(data)
        thehash = shahash.hexdigest()
        assert thehash == 'f4f6ac62387a665471898b14b4934c594b5877ac4170a1d204264ca8ed9be8709b6c5fd66c75c975ab76e26fbf512a02918d723e34c579d523c3b2bfbd11d6e4'

import bbarchivist.pseudocap as bp
import os
from shutil import rmtree
from hashlib import sha512


def setup_module(module):
    if not os.path.exists("temp"):
        os.mkdir("temp")
    os.chdir("temp")
    with open("firstfile", "w") as targetfile:
        targetfile.write("Jackdaws love my big sphinx of quartz")
    with open("capfile", "w") as targetfile:
        targetfile.write("0"*9500000)


def teardown_module(module):
    os.remove("capfile")
    os.remove("firstfile")
    os.chdir("..")
    rmtree("temp")


class TestClassPseudocap:

    def test_ghetto_convert(self):
        assert bp.ghetto_convert(987654321) == b'\x00\x00\x00\x00\xb1h\xde:'

    def test_make_offset(self):
        bp.make_offset("capfile", "firstfile")
        shahash = sha512()
        with open("offset.hex", "rb") as targetfile:
            data = targetfile.read()
            shahash.update(data)
        thehash = shahash.hexdigest()
        assert len(data) == 213
        assert thehash == '0a10007b5645456af5d230bc1cd896328920954285e9fc480531f14fdc098d9514699ab5b8000bcfd158c0953c230835936a8461e2059f29ab1e01de6eff3653' #@IgnorePep8

    def test_make_autoloader(self):
        bp.make_autoloader("loader.exe", "capfile", "firstfile")
        shahash = sha512()
        with open("loader.exe", 'rb') as file:
            while True:
                data = file.read(1048576)
                if not data:
                    break
                shahash.update(data)
        thehash = shahash.hexdigest()
        print(thehash)
        assert thehash == '0998665125e62d6d9e2a1d9ba0a6a4eb58355c6e908605b759fc47cdee7594feb7600a4cb2f61e9604cff53cc984d54f9b7b2e2a9e3056f6f6a1812c3aafebff' #@IgnorePep8
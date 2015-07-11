import bbarchivist.loadergen as bl
import os
from shutil import rmtree, copyfile
from hashlib import sha512


def setup_module(module):
    if not os.path.exists("temp"):
        os.mkdir("temp")
    os.chdir("temp")
    with open("capfile", "w") as targetfile:
        targetfile.write("0"*9500000)


def teardown_module(module):
    for file in os.listdir():
            if file.endswith(".signed"):
                os.remove(file)
    if os.path.exists("capfile"):
        os.remove("capfile")
    os.chdir("..")
    rmtree("temp")


class TestClassLoadergen:

    def test_generate_lazy_loader(self):
        with open("desktop.signed", "w") as targetfile:
            targetfile.write("Jackdaws love my big sphinx of quartz"*5000)
        with open("radio.signed", "w") as targetfile:
            targetfile.write("Why must I chase the cat?"*5000)
        bl.generate_lazy_loader("TESTING", 0, "capfile")
        shahash = sha512()
        with open("Z10_TESTING_STL100-1.exe", "rb") as targetfile:
            data = targetfile.read()
            shahash.update(data)
        thehash = shahash.hexdigest()
        os.remove("desktop.signed")
        os.remove("radio.signed")
        assert thehash == '616124e8991b5c0559f0246c4ff31bf6a96194f4d0fc10b796bf642549907beb34b5198a3792d17ecb30dc9a1a02b4015091ffa399efe260563c3a3884f7a73a' #@IgnorePep8

    def test_generate_loaders(self):
        with open("qc8960.factory_sfi.desktop.signed", "w") as targetfile:
            targetfile.write("Jackdaws love my big sphinx of quartz"*5000)
        copyfile("qc8960.factory_sfi.desktop.signed", "qc8x30.factory_sfi.desktop.signed") #@IgnorePep8
        copyfile("qc8960.factory_sfi.desktop.signed", "qc8974.factory_sfi.desktop.signed") #@IgnorePep8
        copyfile("qc8960.factory_sfi.desktop.signed", "winchester.factory_sfi.desktop.signed") #@IgnorePep8
        with open("radio.m5730.signed", "w") as targetfile:
            targetfile.write("Why must I chase the cat?"*5000)
        copyfile("radio.m5730.signed", "radio.qc8960.BB.signed")
        copyfile("radio.m5730.signed", "radio.qc8960.omadm.signed")
        copyfile("radio.m5730.signed", "radio.qc8960.wtr.signed")
        copyfile("radio.m5730.signed", "radio.qc8960.wtr5.signed")
        copyfile("radio.m5730.signed", "radio.qc8930.wtr5.signed")
        copyfile("radio.m5730.signed", "radio.qc8974.wtr2.signed")
        bl.generate_loaders("10.1.2.3000", "10.3.2.1000", True, "capfile")
        for file in os.listdir():
            if file.endswith(".exe"):
                with open(file, 'rb') as filehandle:
                    shahash = sha512()
                    while True:
                        data = filehandle.read(16777216)
                        if not data:
                            break
                        shahash.update(data)
                    assert shahash.hexdigest() in ("17645875c314827c4d60c722819accab7e05f1e70108707459631ab8bf64d5c0b1dfa199d05d8ff41f78e69178e2133af6daac9ab11c1c6a5097cca6395ab947",#@IgnorePep8
                                                   "616124e8991b5c0559f0246c4ff31bf6a96194f4d0fc10b796bf642549907beb34b5198a3792d17ecb30dc9a1a02b4015091ffa399efe260563c3a3884f7a73a") #@IgnorePep8

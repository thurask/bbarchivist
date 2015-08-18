import bbarchivist.loadergen as bl
import os
from shutil import rmtree, copyfile
from hashlib import sha512


def setup_module(module):
    if not os.path.exists("temp"):
        os.mkdir("temp")
    os.chdir("temp")
    with open("cap-3.11.0.22.dat", "w") as targetfile:
        targetfile.write("0"*9500000)


def teardown_module(module):
    for file in os.listdir():
            if file.endswith(".signed"):
                os.remove(file)
    if os.path.exists("cap-3.11.0.22.dat"):
        os.remove("cap-3.11.0.22.dat")
    os.chdir("..")
    rmtree("temp")


class TestClassLoadergen:

    def test_generate_lazy_loader(self):
        with open("desktop.signed", "w") as targetfile:
            targetfile.write("Jackdaws love my big sphinx of quartz"*5000)
        with open("radio.signed", "w") as targetfile:
            targetfile.write("Why must I chase the cat?"*5000)
        bl.generate_lazy_loader("TESTING", 0)
        shahash = sha512()
        with open("Z10_TESTING_STL100-1.exe", "rb") as targetfile:
            data = targetfile.read()
            shahash.update(data)
        thehash = shahash.hexdigest()
        os.remove("desktop.signed")
        os.remove("radio.signed")
        assert thehash == '71edeced963cd8cf1a7b99c8be9dc93df670471a02eef5da5e40ad4822be1e321c8e1495369dc685b943ac07287bb4b8245636c7b28c861cfd9238e0d42288a2' #@IgnorePep8

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
                    assert shahash.hexdigest() in ("3143a5bdfffbab199fe071d720b374d8678e5a2baafaeaf375f747c578a314cdf10059ccfac51fbe992d6d473106c2ba18bb8a80026269b046c3e299c33adaf3",#@IgnorePep8
                                                   "71edeced963cd8cf1a7b99c8be9dc93df670471a02eef5da5e40ad4822be1e321c8e1495369dc685b943ac07287bb4b8245636c7b28c861cfd9238e0d42288a2") #@IgnorePep8

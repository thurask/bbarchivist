import os
from shutil import rmtree
try:
    import gnupg
    nognupg = False
except ImportError:
    nognupg = True
else:
    import configparser
from bbarchivist import hashwrapper as bh


def setup_module(module):
    if not os.path.exists("temp"):
        os.mkdir("temp")
    os.chdir("temp")
    with open("tempfile.txt", "w") as targetfile:
        targetfile.write("Jackdaws love my big sphinx of quartz")


def teardown_module(module):
    os.remove(os.path.join(os.getcwd(), "tempfile.txt"))
    os.remove(os.path.join(os.getcwd(), "tempfile.txt.cksum"))
    if not nognupg:
        os.remove(os.path.join(os.getcwd(), "tempfile.txt.asc"))
    os.chdir("..")
    rmtree("temp")


class TestClassHashwrapper:

    def test_verifier(self):
        bh.verifier(os.getcwd())
        stocklines = ["MD5",
                      "822E1187FDE7C8D55AFF8CC688701650 tempfile.txt ",
                      "",
                      "SHA1",
                      "71DC7CE8F27C11B792BE3F169ECF985865E276D0 tempfile.txt ", #@IgnorePep8
                      ""]
        with open("tempfile.txt.cksum", "r") as checksumfile:
            assert checksumfile.read() == "\n".join(stocklines)

    def test_gpgrunner(self):
        if nognupg:
            pass
        else:
            config = configparser.ConfigParser()
            homepath = os.path.expanduser("~")
            conffile = os.path.join(homepath, "bbarchivist.ini")
            config.read(conffile)
            gpgkey = config.get('gpgrunner', 'key', fallback=None)
            gpgpass = config.get('gpgrunner', 'pass', fallback=None)
            gpginst = gnupg.GPG()
            bh.gpgrunner(os.getcwd(), gpgkey, gpgpass)
            with open("tempfile.txt.asc", "rb") as sig:
                verified = gpginst.verify_file(sig, 'tempfile.txt')
                assert verified

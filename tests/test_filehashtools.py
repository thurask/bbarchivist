import os
from shutil import rmtree
try:
    import gnupg
    nognupg = False
except ImportError:
    nognupg = True
else:
    import configparser
from hashlib import algorithms_available as algos
from bbarchivist import filehashtools as bf


def setup_module(module):
    os.mkdir("temp")
    os.chdir("temp")
    with open("tempfile.txt", "w") as targetfile:
        targetfile.write("Jackdaws love my big sphinx of quartz")


def teardown_module(module):
    os.remove(os.path.join(os.getcwd(), "tempfile.txt"))
    if not nognupg:
        os.remove(os.path.join(os.getcwd(), "tempfile.txt.asc"))
    os.chdir("..")
    rmtree("temp")


class TestClassFilehashtools:

    def test_crc32hash(self):
        assert bf.crc32hash("tempfile.txt") == "ed5d3f26"

    def test_adler32hash(self):
        assert bf.adler32hash("tempfile.txt") == "02470dcd"

    def test_sha1hash(self):
        assert bf.sha1hash("tempfile.txt") == "71dc7ce8f27c11b792be3f169ecf985865e276d0" #@IgnorePep8

    def test_sha224hash(self):
        assert bf.sha224hash("tempfile.txt") == "7bcd7b77f63633bf0f7db181106f08eb630a58c521b109be1cc4a404" #@IgnorePep8

    def test_sha256hash(self):
        assert bf.sha256hash("tempfile.txt") == "f118871c45171d5fe4e9049980959e033eeeabcfa12046c243fda310580e8a0b" #@IgnorePep8

    def test_sha384hash(self):
        assert bf.sha384hash("tempfile.txt") == "76620873c0d27873c137b082425c6e87e3d601c4b19241a1f2222f7f700a2fe8d3c648b26f62325a411cb020bff527be" #@IgnorePep8

    def test_sha512hash(self):
        assert bf.sha512hash("tempfile.txt") == "b66a5e8aa9b9705748c2ee585b0e1a3a41288d2dafc3be2db12fa89d2f2a3e14f9dec11de4ba865bb51eaa6c2cfeb294139455e34da7d827a19504b0906c01c1" #@IgnorePep8

    def test_md4hash(self):
        if "md4" not in algos:
            pass
        else:
            assert bf.md4hash("tempfile.txt") == "df26ada1a895f94e1f1257fad984e809" #@IgnorePep8

    def test_md5hash(self):
        assert bf.md5hash("tempfile.txt") == "822e1187fde7c8d55aff8cc688701650"

    def test_ripemd160hash(self):
        if "ripemd160" not in algos:
            pass
        else:
            assert bf.ripemd160hash("tempfile.txt") == "f3e191024c33768e2589e2efca53d55f4e4945ee" #@IgnorePep8

    def test_whirlpoolhash(self):
        if "whirlpool" not in algos:
            pass
        else:
            assert bf.whirlpoolhash("tempfile.txt") == "9835d12f3cb3ea3934635e4a7cc918e489379ed69d894ebc2c09bbf99fe72567bfd26c919ad666e170752abfc4b8c37b376f5102f9e5de59af2b65efc2e01293" #@IgnorePep8

    def test_gpgfile(self):
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
            bf.gpgfile("tempfile.txt", gpginst, gpgkey, gpgpass)
            with open("tempfile.txt.asc", "rb") as sig:
                verified = gpginst.verify_file(sig, 'tempfile.txt')
                assert verified

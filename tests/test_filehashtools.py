import os
from shutil import rmtree
try:
    import gnupg
except ImportError:
    NOGNUPG = True
else:
    NOGNUPG = False
from hashlib import algorithms_available as algos
from bbarchivist import filehashtools as bf


def setup_module(module):
    if not os.path.exists("temp"):
        os.mkdir("temp")
    os.chdir("temp")
    with open("tempfile.txt", "w") as targetfile:
        targetfile.write("Jackdaws love my big sphinx of quartz")


def teardown_module(module):
    if os.path.exists("tempfile.txt"):
        os.remove("tempfile.txt")
    if os.path.exists("tempfile.txt.cksum"):
        os.remove("tempfile.txt.cksum")
    if not NOGNUPG:
        if os.path.exists("tempfile.txt.asc"):
            os.remove("tempfile.txt.asc")
    os.chdir("..")
    rmtree("temp")


class TestClassFilehashtools:

    def test_crc32hash(self):
        assert bf.crc32hash("tempfile.txt") == "ed5d3f26"

    def test_adler32hash(self):
        assert bf.adler32hash("tempfile.txt") == "02470dcd"

    def test_sha1hash(self):
        assert bf.sha1hash("tempfile.txt") == "71dc7ce8f27c11b792be3f169ecf985865e276d0"

    def test_sha224hash(self):
        assert bf.sha224hash("tempfile.txt") == "7bcd7b77f63633bf0f7db181106f08eb630a58c521b109be1cc4a404"

    def test_sha256hash(self):
        assert bf.sha256hash("tempfile.txt") == "f118871c45171d5fe4e9049980959e033eeeabcfa12046c243fda310580e8a0b"

    def test_sha384hash(self):
        assert bf.sha384hash("tempfile.txt") == "76620873c0d27873c137b082425c6e87e3d601c4b19241a1f2222f7f700a2fe8d3c648b26f62325a411cb020bff527be"

    def test_sha512hash(self):
        assert bf.sha512hash("tempfile.txt") == "b66a5e8aa9b9705748c2ee585b0e1a3a41288d2dafc3be2db12fa89d2f2a3e14f9dec11de4ba865bb51eaa6c2cfeb294139455e34da7d827a19504b0906c01c1"

    def test_md4hash(self):
        if "md4" not in algos:
            pass
        else:
            assert bf.md4hash("tempfile.txt") == "df26ada1a895f94e1f1257fad984e809"

    def test_md5hash(self):
        assert bf.md5hash("tempfile.txt") == "822e1187fde7c8d55aff8cc688701650"

    def test_ripemd160hash(self):
        if "ripemd160" not in algos:
            pass
        else:
            assert bf.ripemd160hash("tempfile.txt") == "f3e191024c33768e2589e2efca53d55f4e4945ee"

    def test_whirlpoolhash(self):
        if "whirlpool" not in algos:
            pass
        else:
            assert bf.whirlpoolhash("tempfile.txt") == "9835d12f3cb3ea3934635e4a7cc918e489379ed69d894ebc2c09bbf99fe72567bfd26c919ad666e170752abfc4b8c37b376f5102f9e5de59af2b65efc2e01293"

    def test_gpgfile(self):
        if os.getenv("TRAVIS", "false") == "true":
            pass
        elif NOGNUPG:
            pass
        else:
            gpgkey, gpgpass = bf.gpg_config_loader()
            if gpgkey is None or gpgpass is None:
                pass
            else:
                gpginst = gnupg.GPG()
                # Note: if you get a "Unknown status message 'NEWSIG'" error, then look here:
                # https://bitbucket.org/vinay.sajip/python-gnupg/issues/35/status-newsig-missing-in-verify
                bf.gpgfile("tempfile.txt", gpginst, gpgkey, gpgpass)
                with open("tempfile.txt.asc", "rb") as sig:
                    verified = gpginst.verify_file(sig, 'tempfile.txt')
                    assert verified

    def test_escreens(self):
        pin = "acdcacdc"
        app = "10.3.2.500"
        uptime = "69696969"
        assert bf.calculate_escreens(pin, app, uptime) == "E23F8E7F"

    def test_verifier(self):
        confload = bf.verifier_config_loader()
        confload = confload.fromkeys(confload, False)
        confload['md5'] = True
        confload['sha1'] = True
        confload['blocksize'] = 16777216
        bf.verifier(os.getcwd(), **confload)
        stocklines = [b"MD5",
                      b"822E1187FDE7C8D55AFF8CC688701650 tempfile.txt",
                      b"",
                      b"SHA1",
                      b"71DC7CE8F27C11B792BE3F169ECF985865E276D0 tempfile.txt",
                      b""]
        stocklines2 = []
        for item in stocklines:
            item2 = item.strip()
            item2 = item2.replace(b'\r\n', b'')
            item2 = item2.replace(b'\n', b'')
            item2 = item2.replace(b'\r', b'')
            stocklines2.append(item2)
        print(os.path.isfile("tempfile.txt"))
        with open("tempfile.txt.cksum", "rb") as checksumfile:
            content = checksumfile.read().splitlines()
        content2 = []
        for item in content:
            item2 = item.strip()
            item2 = item2.replace(b'\r\n', b'')
            item2 = item2.replace(b'\n', b'')
            item2 = item2.replace(b'\r', b'')
            content2.append(item2)
        for idx, value in enumerate(content2):
            assert stocklines2[idx] == value

    def test_gpgrunner(self):
        if os.getenv("TRAVIS", "false") == "true":
            pass
        elif NOGNUPG:
            pass
        else:
            gpgkey, gpgpass = bf.gpg_config_loader()
            if gpgkey is None or gpgpass is None:
                pass
            else:
                gpginst = gnupg.GPG()
                # Note: if you get a "Unknown status message 'NEWSIG'" error, then look here:
                # https://bitbucket.org/vinay.sajip/python-gnupg/issues/35/status-newsig-missing-in-verify
                bf.gpgrunner(os.getcwd(), gpgkey, gpgpass)
                with open("tempfile.txt.asc", "rb") as sig:
                    verified = gpginst.verify_file(sig, 'tempfile.txt')
                    assert verified

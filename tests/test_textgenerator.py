import bbarchivist.textgenerator as bt
from shutil import rmtree
import os


def setup_module(module):
    if not os.path.exists("temp"):
        os.mkdir("temp")
    os.chdir("temp")


def teardown_module(module):
    if os.path.exists("10.3.3000.txt"):
        os.remove("10.3.3000.txt")
    os.chdir("..")
    rmtree("temp")


class TestClassTextGenerator:

    def test_url_generator(self):
        deb, cor, rad = bt.url_generator("10.1.1000", "10.2.2000", "10.3.3000")
        assert len(deb) == 5
        assert deb[0].find("winchester") != -1
        assert len(cor) == 5
        assert cor[4].find("factory_sfi_hybrid_qc8974") != -1
        assert len(rad) == 7
        assert rad[-1].find("wtr2") != -1

    def test_write_links(self):
        deb, cor, rad = bt.url_generator("10.1.1000", "10.2.2000", "10.3.3000")
        bt.write_links("10.3.3000", "10.1.1000", "10.2.2000",
                       deb, cor, rad, True, False, None)
        with open("10.3.3000.txt", 'r') as file:
            data = file.read()
            assert len(data) == 2917

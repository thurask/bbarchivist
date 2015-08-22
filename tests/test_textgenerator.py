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
    @classmethod
    def setup_class(cls):
        deb, cor, rad = bt.url_generator("10.1.1000", "10.2.2000", "10.3.3000")
        cls.deb = deb
        cls.cor = cor
        cls.rad = rad

    def test_url_generator_debrick_len(self):
        assert len(self.deb) == 5

    def test_url_generator_debrick_find(self):
        assert self.deb[0].find("winchester") != -1

    def test_url_generator_core_length(self):
        assert len(self.cor) == 5

    def test_url_generator_core_find(self):
        assert self.cor[4].find("factory_sfi_hybrid_qc8974") != -1

    def test_url_generator_radio_length(self):
        assert len(self.rad) == 7

    def test_url_generator_radio_find(self):
        assert self.rad[-1].find("wtr2") != -1

    def test_write_links(self):
        bt.write_links("10.3.3000", "10.1.1000", "10.2.2000",
                       self.deb, self.cor, self.rad, True, False, None)
        with open("10.3.3000.txt", 'r') as file:
            data = file.read()
            assert len(data) == 2934

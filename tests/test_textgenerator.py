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

    def test_generator_debrick_length(self):
        assert len(self.deb.values()) == 5

    def test_generator_core_length(self):
        assert len(self.cor.values()) == 5

    def test_generator_radio_length(self):
        assert len(self.rad.values()) == 7

    def test_write_links(self):
        bt.write_links("10.3.3000", "10.1.1000", "10.2.2000",
                       self.deb, self.cor, self.rad, True, False, None)
        with open("10.3.3000.txt", 'rb') as file:
            data = file.read()
            data = data.replace(b"\r", b"")
            assert len(data) == 2848

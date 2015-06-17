import bbarchivist.textgenerator as bt
from hashlib import sha512


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
        shahash = sha512()
        with open("10.3.3000.txt", 'rb') as file:
            while True:
                data = file.read(1024)
                if not data:
                    break
                shahash.update(data)
        assert shahash.hexdigest() == "35e208b97f77d87a6e73f0bd76f997bcaadfe7d68582e31a7ef4065044d88980ea00376557bd213269cb3541384eaacb2d8641fec520d9455dc81046ab8066b1" #@IgnorePep8
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
                data = file.read()
                if not data:
                    break
                shahash.update(data)
        assert shahash.hexdigest() in ("6d321d8b9bfb01088c4d8f306880f3e291e2d881a874a1ec9e00ff2e6584a01e058df035f3f41f1aeb3167b20c4513e227af8ad0a3599e04ab56f093050d98fc", #@IgnorePep8
                                       "5ce59665b3a8faf4f1124fa6d728464cd6d942c3905b7f2bc0fd64ee014244bb393dfc1eb1ce551ab5fbd8d0ea52d135a66fcbf2b4d404b749e22341fd6190f1", #@IgnorePep8
                                       "35e208b97f77d87a6e73f0bd76f997bcaadfe7d68582e31a7ef4065044d88980ea00376557bd213269cb3541384eaacb2d8641fec520d9455dc81046ab8066b1") #@IgnorePep8
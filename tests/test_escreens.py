import bbarchivist.escreens as be


class TestClassEscreens:

    def test_escreens(self):
        pin = "acdcacdc"
        app = "10.3.2.500"
        uptime = "69696969"
        assert be.calculate_escreens(pin, app, uptime) == "E23F8E7F"

#!/usr/bin/env python3
"""Test the jsonutils module."""

import os
try:
    import simplejson as json
except ImportError:
    import json
from shutil import rmtree
import pytest
import bbarchivist.jsonutils as bj

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "2015-2017 Thurask"


def setup_module(module):
    """
    Create necessary files.
    """
    if not os.path.exists("temp_jsonutils"):
        os.mkdir("temp_jsonutils")
    os.chdir("temp_jsonutils")
    ptcrbdev = {}
    ptcrbdev['name'] = "PTCDEVICE"
    ptcrbdev['device'] = "GALAXY_S5"
    ptcrbdev['family'] = "SAMSUNG"
    ptcrbdev['hwid'] = ""
    ptcrbdev['ptcrbid'] = "12345"
    ptcrbdev['fccid'] = "FUK999LW"
    unkdev = {}
    unkdev['name'] = "UNKNOWN"
    unkdev['device'] = "ROTARY"
    unkdev['family'] = "BLACKBERRY"
    unkdev['hwid'] = ""
    unkdev['ptcrbid'] = ""
    unkdev['fccid'] = ""
    iddev = {}
    iddev['name'] = "TEST"
    iddev['device'] = "GRUNTMASTER_6000"
    iddev['family'] = "PATHETECH"
    iddev['hwid'] = "69696969"
    iddev['ptcrbid'] = "98765"
    iddev['fccid'] = ""
    devlist = [ptcrbdev, iddev, unkdev]
    devices = {}
    devices['devices'] = devlist
    dmp = json.dumps(devices)
    if not os.path.exists("json"):
        os.mkdir("json")
    with open(os.path.join("json", "devices.json"), "w") as targetfile:
        targetfile.write(dmp)


def teardown_module(module):
    """
    Delete necessary files.
    """
    os.chdir("..")
    rmtree("temp_jsonutils", ignore_errors=True)


class TestClassJsonutils:
    """
    Test JSON utilities.
    """
    @classmethod
    def setup_class(cls):
        """
        Create local variables.
        """
        cls.devlist = [
            {
                'device': 'GALAXY_S5',
                'fccid': 'FUK999LW',
                'hwid': '',
                'name': 'PTCDEVICE',
                'ptcrbid': '12345',
                'family': 'SAMSUNG'
            },
            {
                'device': 'GRUNTMASTER_6000',
                'fccid': '',
                'hwid': '69696969',
                'name': 'TEST',
                'ptcrbid': '98765',
                'family': 'PATHETECH'
            },
            {
                'device': 'ROTARY',
                'fccid': '',
                'hwid': '',
                'name': 'UNKNOWN',
                'ptcrbid': '',
                'family': 'BLACKBERRY'
            }
        ]

    def test_grab_json(self):
        """
        Test finding JSON file location.
        """
        assert bj.grab_json("devices") == os.path.join(os.getcwd(), "json", "devices.json")

    def test_load_json(self):
        """
        Test loading table from JSON.
        """
        devs = bj.load_json("devices")
        assert devs == self.devlist

    def test_extract_cert_good(self):
        """
        Test cert extraction, best case.
        """
        assert bj.extract_cert(self.devlist, "PTCDEVICE") == ("PTCDEVICE", "12345", "", "FUK999LW")

    def test_extract_cert_bad(self):
        """
        Test cert extraction, worst case.
        """
        with pytest.raises(SystemExit):
            bj.extract_cert(self.devlist, "UNKNOWN")

    def test_certchecker_good(self):
        """
        Test certchecker's JSON function, best case.
        """
        assert bj.certchecker_prep(self.devlist, "PTCDEVICE") == ("GALAXY_S5", "SAMSUNG", "")

    def test_certchecker_bad(self):
        """
        Test certchecker's JSON function, worst case.
        """
        with pytest.raises(SystemExit):
            bj.certchecker_prep(self.devlist, "SNEK")

    def test_print_certs(self, capsys):
        """
        Test printing just certified devices.
        """
        bj.list_available_certs(self.devlist)
        assert "UNKNOWN" not in capsys.readouterr()[0]

    def test_print_all(self, capsys):
        """
        Test printing all devices.
        """
        bj.list_devices(self.devlist)
        assert "UNKNOWN" in capsys.readouterr()[0]

    def test_read_family(self):
        """
        Test reading families from table.
        """
        assert bj.read_family(self.devlist, "GALAXY_S5")[0] == ("FUK999LW")

    def test_list_family(self, capsys):
        """
        Test listing families from table.
        """
        bj.list_family(self.devlist)
        assert "GRUNTMASTER" in capsys.readouterr()[0]

    def test_list_prds(self, capsys):
        """
        Test listing PRDs from table.
        """
        prdlist = {"KEYone": ["PRD-12345-678"]}
        bj.list_prds(prdlist)
        assert "~KEYone~" in capsys.readouterr()[0]

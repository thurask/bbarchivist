#!/usr/bin/env python3
"""Test the jsonutils module."""

import os
import json
from shutil import rmtree
import pytest
import bbarchivist.jsonutils as bj


def setup_module(module):
    """
    Create necessary files.
    """
    if not os.path.exists("temp_jsonutils"):
        os.mkdir("temp_jsonutils")
    os.chdir("temp_jsonutils")
    ptcrbdev = {}
    ptcrbdev['name'] = "PTCDEVICE"
    ptcrbdev['device'] = "GALAXY S5"
    ptcrbdev['hwid'] = ""
    ptcrbdev['ptcrbid'] = "12345"
    ptcrbdev['fccid'] = "FUK999LW"
    unkdev = {}
    unkdev['name'] = "UNKNOWN"
    unkdev['device'] = "ROTARY"
    unkdev['hwid'] = ""
    unkdev['ptcrbid'] = ""
    unkdev['fccid'] = ""
    iddev = {}
    iddev['name'] = "TEST"
    iddev['device'] = "GRUNTMASTER 6000"
    iddev['hwid'] = "69696969"
    iddev['ptcrbid'] = "98765"
    iddev['fccid'] = ""
    devlist = [ptcrbdev, iddev, unkdev]
    devices = {}
    devices['devices'] = devlist
    dmp = json.dumps(devices)
    with open("bbconstants.json", "w") as targetfile:
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
        cls.devlist = [{'device': 'GALAXY S5', 'fccid': 'FUK999LW', 'hwid': '', 'name': 'PTCDEVICE', 'ptcrbid': '12345'},
                       {'device': 'GRUNTMASTER 6000', 'fccid': '', 'hwid': '69696969', 'name': 'TEST', 'ptcrbid': '98765'},
                       {'device': 'ROTARY', 'fccid': '', 'hwid': '', 'name': 'UNKNOWN', 'ptcrbid': ''}]

    def test_grab_json(self):
        """
        Test finding JSON file location.
        """
        assert os.path.dirname(bj.grab_json()) == os.getcwd()

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

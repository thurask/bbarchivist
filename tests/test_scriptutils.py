#!/usr/bin/env python3
#pylint: disable = I0011, R0201, W0613, C0301
"""Test the scriptutils module."""

import bbarchivist.scriptutils as bs
try:
    import unittest.mock as mock
except ImportError:
    import mock
import pytest

class TestClassScriptutils:
    """
    Test script-related tools.
    """
    def test_radio_version(self):
        """
        Test radio version non-incrementing.
        """
        assert bs.return_radio_version("10.3.2.2639", "10.3.2.2640") == "10.3.2.2640"

    def test_radio_version_inc(self):
        """
        Test radio version incrementing.
        """
        assert bs.return_radio_version("10.3.2.2639") == "10.3.2.2640"

    def test_return_swc_auto(self):
        """
        Test software release non-checking,
        """
        assert bs.return_sw_checked("10.3.2.2474", "10.3.2.2639") == ("10.3.2.2474", True)

    def test_return_swc_manual(self):
        """
        Test software release checking.
        """
        with mock.patch('bbarchivist.networkutils.software_release_lookup',
                        mock.MagicMock(return_value="10.3.2.2474")):
            assert bs.return_sw_checked(None, "10.3.2.2639") == ("10.3.2.2474", True)

    def test_return_rswc_auto(self):
        """
        Test radio software release non-checking.
        """
        assert bs.return_radio_sw_checked("10.3.2.2474", "10.3.2.2640") == ("10.3.2.2474", True)

    def test_return_rswc_manual(self):
        """
        Test radio software release checking.
        """
        with mock.patch('bbarchivist.networkutils.software_release_lookup',
                        mock.MagicMock(return_value="10.3.2.2474")):
            assert bs.return_radio_sw_checked("checkme", "10.3.2.2640") == ("10.3.2.2474", True)

    def test_check_sw_auto(self, capsys):
        """
        Test automatic software availability checking.
        """
        bs.check_sw("http://qrrbrbirlbel.yu/", "10.3.2.2474", True)
        assert "EXISTS" in capsys.readouterr()[0]

    def test_check_sw_manual(self, capsys):
        """
        Test manual software availability checking.
        """
        with mock.patch('bbarchivist.networkutils.availability',
                        mock.MagicMock(return_value=True)):
            bs.check_sw("http://qrrbrbirlbel.yu/", "10.3.2.2474", False)
            assert "EXISTS" in capsys.readouterr()[0]

    def test_check_rsw_auto(self, capsys):
        """
        Test automatic radio software availability checking.
        """
        bs.check_radio_sw("http://qrrbrbirlbel.yu/", "10.3.2.2474", True)
        assert "EXISTS" in capsys.readouterr()[0]

    def test_check_rsw_manual(self, capsys):
        """
        Test manual radio software availability checking.
        """
        with mock.patch('bbarchivist.networkutils.availability',
                        mock.MagicMock(return_value=True)):
            bs.check_radio_sw("http://qrrbrbirlbel.yu/", "10.3.2.2474", False)
            assert "EXISTS" in capsys.readouterr()[0]

    def test_os_single(self, capsys):
        """
        Test single OS availability.
        """
        with mock.patch('bbarchivist.networkutils.availability',
                        mock.MagicMock(return_value=True)):
            bs.check_os_single("http://qrrbrbirlbel.yu/", "10.3.2.2639", 0)
            assert "NOT AVAILABLE" not in capsys.readouterr()[0]

    def test_os_bulk(self, capsys):
        """
        Test bulk OS availability.
        """
        osurls = ["http://qrrbrbirlbel.yu/", "http://zeekyboogydoog.su/"]
        with mock.patch('bbarchivist.networkutils.availability',
                        mock.MagicMock(return_value=True)):
            bs.check_os_bulk(osurls, "10.3.2.2639")
            assert "NOT FOUND" not in capsys.readouterr()[0]

    def test_radio_single(self, capsys):
        """
        Test single radio availability.
        """
        with mock.patch('bbarchivist.networkutils.availability',
                        mock.MagicMock(return_value=True)):
            assert bs.check_radio_single("http://qrrbrbirlbel.yu/",
                                         "10.3.2.2640") == ("http://qrrbrbirlbel.yu/",
                                                            "10.3.2.2640")
            assert "NOT AVAILABLE" not in capsys.readouterr()[0]

    def test_radio_bulk(self, capsys):
        """
        Test bulk radio availability.
        """
        radiourls = ["http://qrrbrbirlbel.yu/", "http://zeekyboogydoog.su/"]
        with mock.patch('bbarchivist.networkutils.availability',
                        mock.MagicMock(return_value=True)):
            assert bs.check_radio_bulk(radiourls,
                                       "10.3.2.2640") == (radiourls,
                                                          "10.3.2.2640")
            assert "NOT FOUND" not in capsys.readouterr()[0]

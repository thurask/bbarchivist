#!/usr/bin/env python3
"""Scrape Android autoloader webpage."""

import sys  # load arguments

from bbarchivist import argutils  # arguments
from bbarchivist import decorators  # enter to exit
from bbarchivist import networkutils  # lookup

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "2016-2019 Thurask"


def droidscraper_main():
    """
    Wrap around :mod:`bbarchivist.networkutils` web scraping.
    """
    parser = argutils.default_parser("bb-droidscraper", "Autoloader scraper.")
    parser.set_defaults()
    parser.parse_args(sys.argv[1:])
    argutils.slim_preamble("DROIDSCRAPER")
    print(" ")
    session = networkutils.generic_session()
    networkutils.loader_page_scraper_og(session)
    decorators.enter_to_exit(True)


if __name__ == "__main__":
    droidscraper_main()

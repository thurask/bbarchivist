#!/usr/bin/env python3
"""Scrape Android autoloader webpage."""

import sys  # load arguments
from bbarchivist import decorators  # enter to exit
from bbarchivist import networkutils  # lookup
from bbarchivist import scriptutils  # default parser

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "2016-2017 Thurask"


def droidscraper_main():
    """
    Wrap around :mod:`bbarchivist.networkutils` web scraping.
    """
    parser = scriptutils.default_parser("bb-droidscraper", "Autoloader scraper.")
    parser.set_defaults()
    args = parser.parse_args(sys.argv[1:])
    scriptutils.slim_preamble("DROIDSCRAPER")
    print(" ")
    networkutils.loader_page_scraper()
    decorators.enter_to_exit(True)


if __name__ == "__main__":
    droidscraper_main()

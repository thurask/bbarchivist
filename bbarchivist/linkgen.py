#!/usr/bin/env python3

from bbarchivist import networkutils  # lookup, if sw not specified
from bbarchivist import utilities  # increment version, if radio not specified
from bbarchivist import bbconstants  # versions/constants


def do_magic(osversion, radioversion=None, softwareversion=None):
    """
    Generate debrick/core/radio links for given OS, radio, software release.

    :param osversion: OS version, 10.x.y.zzzz.
    :type osversion: str

    :param radioversion: Radio version, 10.x.y.zzzz. Can be guessed.
    :type radioversion: str

    :param softwareversion: Software version, 10.x.y.zzzz. Can be guessed.
    :type softwareversion: str
    """
    if radioversion is None:
        radioversion = utilities.version_incrementer(osversion, 1)
    if softwareversion is None:
        serv = bbconstants.SERVERS["p"]
        softwareversion = networkutils.software_release_lookup(osversion, serv)
        if softwareversion == "SR not in system":
            print("SOFTWARE RELEASE NOT FOUND")
            cont = utilities.str2bool(input("INPUT MANUALLY? Y/N "))
            if cont:
                softwareversion = input("SOFTWARE RELEASE: ")
            else:
                print("\nEXITING...")
                raise SystemExit  # bye bye
    baseurl = networkutils.create_base_url(softwareversion)

    # List of debrick urls
    osurls = ["STL100-1: " + baseurl +
              "/winchester.factory_sfi.desktop-" +
              osversion + "-nto+armle-v7+signed.bar",
              "QC8960: " + baseurl +
              "/qc8960.factory_sfi.desktop-" +
              osversion + "-nto+armle-v7+signed.bar",
              "VERIZON 8960: " + baseurl +
              "/qc8960.verizon_sfi.desktop-" +
              osversion + "-nto+armle-v7+signed.bar",
              "Z3: " + baseurl +
              "/qc8960.factory_sfi_hybrid_qc8x30.desktop-" +
              osversion + "-nto+armle-v7+signed.bar",
              "PASSPORT: " + baseurl +
              "/qc8960.factory_sfi_hybrid_qc8974.desktop-" +
              osversion + "-nto+armle-v7+signed.bar"]

    # List of core urls
    coreurls = ["STL100-1: " + baseurl +
                "/winchester.factory_sfi-" +
                osversion + "-nto+armle-v7+signed.bar",
                "QC8960: " + baseurl +
                "/qc8960.factory_sfi-" +
                osversion + "-nto+armle-v7+signed.bar",
                "VERIZON 8960: " + baseurl +
                "/qc8960.verizon_sfi-" +
                osversion + "-nto+armle-v7+signed.bar",
                "Z3: " + baseurl +
                "/qc8960.factory_sfi_hybrid_qc8x30-" +
                osversion + "-nto+armle-v7+signed.bar",
                "PASSPORT: " + baseurl +
                "/qc8960.factory_sfi_hybrid_qc8974-" +
                osversion + "-nto+armle-v7+signed.bar"]

    # List of radio urls
    radiourls = ["STL100-1: " + baseurl + "/m5730-" + radioversion +
                 "-nto+armle-v7+signed.bar",
                 "STL100-X/P9982: " + baseurl + "/qc8960-" + radioversion +
                 "-nto+armle-v7+signed.bar",
                 "STL100-4: " + baseurl + "/qc8960.omadm-" + radioversion +
                 "-nto+armle-v7+signed.bar",
                 "Q10/Q5/P9983: " + baseurl + "/qc8960.wtr-" + radioversion +
                 "-nto+armle-v7+signed.bar",
                 "Z30/LEAP/CLASSIC: " + baseurl + "/qc8960.wtr5-" +
                 radioversion +
                 "-nto+armle-v7+signed.bar",
                 "Z3: " + baseurl + "/qc8930.wtr5-" + radioversion +
                 "-nto+armle-v7+signed.bar",
                 "PASSPORT: " + baseurl + "/qc8974.wtr2-" + radioversion +
                 "-nto+armle-v7+signed.bar"]

    avlty = networkutils.availability(baseurl)

    with open(softwareversion + ".txt", "w") as target:
        target.write("OS VERSION: " + osversion + "\n")
        target.write("RADIO VERSION: " + radioversion + "\n")
        target.write("SOFTWARE RELEASE: " + softwareversion + "\n")
        if not avlty:
            target.write("\n!!EXISTENCE NOT GUARANTEED!!\n")
        target.write("\nDEBRICK URLS:\n")
        for i in osurls:
            target.write(i + "\n")
        target.write("\nCORE URLS:\n")
        for i in coreurls:
            target.write(i + "\n")
        target.write("\nRADIO URLS:\n")
        for i in radiourls:
            target.write(i + "\n")

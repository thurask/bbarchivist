#!/usr/bin/env python3

import hashlib


def doMagic(osversion, radioversion, softwareversion):
    """
    Generate debrick/core/radio links for given OS, radio, software release.

    :param osversion: OS version, 10.x.y.zzzz.
    :type osversion: str

    :param radioversion: Radio version, 10.x.y.zzzz.
    :type radioversion: str

    :param softwareversion: Software version, 10.x.y.zzzz.
    :type softwareversion: str
    """
    # Hash software version
    swhash = hashlib.sha1(softwareversion.encode('utf-8'))
    hashedsoftwareversion = swhash.hexdigest()

    # Root of all urls
    baseurl = "http://cdn.fs.sl.blackberry.com/fs/qnx/production/"
    baseurl += hashedsoftwareversion

    # List of debrick urls
    osurls = ["STL100-1: " + baseurl +
              "/winchester.factory_sfi.desktop-" +
              osversion + "-nto+armle-v7+signed.bar",
              "QC8960: " + baseurl +
              "/qc8960.factory_sfi.desktop-" +
              osversion + "-nto+armle-v7+signed.bar",
              "Z3: " + baseurl +
              "/qc8960.factory_sfi_hybrid_qc8x30.desktop-" +
              osversion + "-nto+armle-v7+signed.bar",
              "PASSPORT: " + baseurl +
              "/qc8960.factory_sfi_hybrid_qc8974.desktop-" +
              osversion + "-nto+armle-v7+signed.bar"]

    # List of debrick urls
    coreurls = ["STL100-1: " + baseurl +
                "/winchester.factory_sfi-" +
                osversion + "-nto+armle-v7+signed.bar",
                "QC8960: " + baseurl +
                "/qc8960.factory_sfi-" +
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

    with open(softwareversion + ".txt", "w") as target:
        target.write("OS VERSION: " + osversion)
        target.write("RADIO VERSION: " + radioversion)
        target.write("SOFTWARE RELEASE: " + softwareversion)
        target.write("\n!!EXISTENCE NOT GUARANTEED!!\n")
        target.write("DEBRICK URLS:")
        for i in osurls:
            target.write(i + "\n")
        target.write("\nCORE URLS:")
        for i in coreurls:
            target.write(i + "\n")
        target.write("\nRADIO URLS:")
        for i in radiourls:
            target.write(i + "\n")

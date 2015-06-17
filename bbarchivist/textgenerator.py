from bbarchivist.networkutils import create_base_url


def write_links(softwareversion, osversion, radioversion,
                osurls, coreurls, radiourls, avlty=False,
                appendbars=False, appurls=None):
    """
    Write lookup links to file. Checks for availability, can include app bars.

    :param softwareversion: Software release version.
    :type softwareversion: str

    :param osversion: OS version.
    :type osversion: str

    :param radioversion: Radio version.
    :type radioversion: str

    :param osurls: Pre-formed debrick OS URLs.
    :type osurls: list

    :param coreurls: Pre-formed core OS URLs.
    :type coreurls: str

    :param radiourls: Pre-formed radio URLs.
    :type radiourls: str

    :param avlty: Availability of links to download. Default is false.
    :type avlty: bool

    :param appendbars: Whether to add app bars to this file. Default is false.
    :type appendbars: bool

    :param appurls: App bar URLs to add.
    :type softwareversion: list
    """
    thename = softwareversion
    if appendbars:
        thename += "plusapps"
    with open(thename + ".txt", "w") as target:
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
        if appendbars:
            target.write("\nAPP URLS:\n")
            for i in appurls:
                stoppers = ["8960", "8930", "8974", "m5730", "winchester"]
                if all(word not in i for word in stoppers):
                    target.write(i + "\n")


def url_generator(osversion, radioversion, softwareversion):
    """
    Return all debrick, core radio URLs from given OS, radio software.

    :param softwareversion: Software release version.
    :type softwareversion: str

    :param osversion: OS version.
    :type osversion: str

    :param radioversion: Radio version.
    :type radioversion: str
    """
    baseurl = create_base_url(softwareversion)
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

    return osurls, coreurls, radiourls

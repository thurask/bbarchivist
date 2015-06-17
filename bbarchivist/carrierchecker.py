#!/usr/bin/env python3

from bbarchivist import bbconstants  # versions/constants
from bbarchivist import networkutils  # check function
from bbarchivist import utilities  # index lookup
from bbarchivist import barutils  # file/folder operations
from bbarchivist import textgenerator  # text work
import os  # file/path operations
import shutil  # folder removal


def do_magic(mcc, mnc, device,
             download=False, upgrade=False,
             directory=None,
             export=False,
             blitz=False,
             bundles=False):
    """
    Wrap around :mod:`bbarchivist.networkutils` carrier checking.

    :param mcc: Country code.
    :type mcc: int

    :param mnc: Network code.
    :type mnc: int

    :param device: Device ID (SXX100-#)
    :type device: str

    :param download: Whether or not to download. Default is false.
    :type download: bool

    :param upgrade: Whether or not to use upgrade files. Default is false.
    :type upgrade: bool

    :param directory: Where to store files. Default is local directory.
    :type directory: str

    :param export: Whether or not to write URLs to a file. Default is false.
    :type export: bool

    :param blitz: Whether or not to create a blitz package. Default is false.
    :type blitz: bool

    :param bundles: Whether or not to check software bundles. Default is false.
    :type bundles: bool
    """
    if directory is None:
        directory = os.getcwd()
    try:
        devindex = bbconstants.DEVICELIST.index(device.upper())
    except ValueError as exc:
        print(str(exc).upper())
        print("INVALID DEVICE!")
        raise SystemExit
    model = bbconstants.MODELLIST[utilities.return_model(devindex)]
    family = bbconstants.FAMILYLIST[utilities.return_family(devindex)]
    hwid = bbconstants.HWIDLIST[devindex]
    version = bbconstants.VERSION
    print("~~~CARRIERCHECKER VERSION", version + "~~~")
    country, carrier = networkutils.carrier_checker(mcc, mnc)
    print("COUNTRY:", country.upper())
    print("CARRIER:", carrier.upper())
    print("DEVICE:", model.upper())
    print("VARIANT:", device.upper())
    print("HARDWARE ID:", hwid)
    print("\nCHECKING CARRIER...")
    if bundles:
        releases = networkutils.available_bundle_lookup(mcc, mnc, hwid)
        print("\nAVAILABLE BUNDLES:")
        for bundle in releases:
            print(bundle)
    else:
        swv, osv, radv, files = networkutils.carrier_update_request(mcc, mnc,
                                                                    hwid,
                                                                    upgrade,
                                                                    blitz)
        print("SOFTWARE RELEASE:", swv)
        print("OS VERSION:", osv)
        print("RADIO VERSION:", radv)
        if export:
            print("\nEXPORTING...")
            if len(files) > 0:
                if not upgrade:
                    newfiles = networkutils.carrier_update_request(mcc, mnc, hwid, True, False) #@IgnorePep8
                    newfiles = newfiles[3]
                else:
                    newfiles = files
                osurls, coreurls, radiourls = textgenerator.url_generator(osv, radv, swv) #@IgnorePep8
                finalfiles = []
                stoppers = ["8960", "8930", "8974", "m5730", "winchester"]
                for link in newfiles:
                    if all(word not in link for word in stoppers):
                        finalfiles.append(link)
                textgenerator.write_links(swv, osv, radv,
                                          osurls, coreurls, radiourls,
                                          True, True, newfiles)
                print("\nFINISHED!!!")
            else:
                print("CANNOT EXPORT, NO SOFTWARE RELEASE")
        if download:
            if blitz:
                bardir = os.path.join(directory, swv + "-BLITZ")
            else:
                bardir = os.path.join(directory, swv + "-" + family)
            if not os.path.exists(bardir):
                os.makedirs(bardir)
            if blitz:
                baseurl = networkutils.create_base_url(swv)
                coreurls = [baseurl + "/winchester.factory_sfi-" +
                            osv + "-nto+armle-v7+signed.bar",
                            baseurl + "/qc8960.factory_sfi-" +
                            osv + "-nto+armle-v7+signed.bar",
                            baseurl + "/qc8960.factory_sfi_hybrid_qc8x30-" +
                            osv + "-nto+armle-v7+signed.bar",
                            baseurl + "/qc8960.factory_sfi_hybrid_qc8974-" +
                            osv + "-nto+armle-v7+signed.bar"]
                for i in coreurls:
                    files.append(i)
                # List of radio urls
                radiourls = [baseurl + "/m5730-" + radv +
                             "-nto+armle-v7+signed.bar",
                             baseurl + "/qc8960-" + radv +
                             "-nto+armle-v7+signed.bar",
                             baseurl + "/qc8960.wtr-" + radv +
                             "-nto+armle-v7+signed.bar",
                             baseurl + "/qc8960.wtr5-" +
                             radv + "-nto+armle-v7+signed.bar",
                             baseurl + "/qc8930.wtr5-" + radv +
                             "-nto+armle-v7+signed.bar",
                             baseurl + "/qc8974.wtr2-" + radv +
                             "-nto+armle-v7+signed.bar"]
                for i in radiourls:
                    files.append(i)
            print("\nDOWNLOADING...")
            networkutils.download_bootstrap(files, outdir=bardir)
            # integrity check
            brokenlist = []
            print("\nTESTING...")
            for file in os.listdir(bardir):
                if file.endswith(".bar"):
                    print("TESTING:", file)
                    thepath = os.path.abspath(os.path.join(bardir, file))
                    brokens = barutils.bar_tester(thepath)
                    if brokens is not None:
                        os.remove(brokens)
                        for url in files:
                            if brokens in url:
                                brokenlist.append(url)
            if len(brokenlist) > 0:
                if len(brokenlist) > 5:
                    workers = 5
                else:
                    workers = len(brokenlist)
                print("\nREDOWNLOADING BROKEN FILES...")
                networkutils.download_bootstrap(brokenlist,
                                                outdir=bardir,
                                                lazy=False,
                                                workers=workers)
                for file in os.listdir(bardir):
                    if file.endswith(".bar"):
                        thepath = os.path.abspath(os.path.join(bardir, file))
                        brokens = barutils.bar_tester(thepath)
                        if brokens is not None:
                            print(file, "STILL BROKEN")
                            raise SystemExit
            else:
                print("\nALL FILES DOWNLOADED OK")
            if blitz:
                print("\nCREATING BLITZ...")
                barutils.create_blitz(bardir, swv)
                shutil.rmtree(bardir)
            print("\nFINISHED!!!")

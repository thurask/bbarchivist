import os
import glob
from . import pseudocap


def generate_loaders(
        osversion, radioversion, radios=True,
        cap="cap.exe", localdir=os.getcwd()):
    """
    Create and properly label autoloaders.
    Leverages Python implementation of cap.exe.
    :param osversion: OS version, 10.x.y.zzzz.
    Autoconverted to 10.x.0y.zzzz if need be.
    :type osversion: str
    :param radioversion: Radio version, 10.x.y.zzzz.
    Autoconverted to 10.x.0y.zzzz if need be.
    :type radioversion: str
    :param radios: Whether to make radios or not. True by default.
    :type radios: bool
    :param cap: Path to cap.exe. Default is local dir\\cap.exe.
    :type cap: str
    :param localdir: Working path. Default is local dir.
    :type localdir: str
    """
    # #OS Images
    print("GETTING FILENAMES...")
    # 8960
    try:
        os_8960 = glob.glob(
            os.path.join(
                localdir,
                "*qc8960*_sfi.desktop*.signed"))[0]
    except IndexError:
        print("No 8960 image found")

    # 8x30 (10.3.1 MR+)
    try:
        os_8x30 = glob.glob(
            os.path.join(
                localdir,
                "*qc8x30*desktop*.signed"))[0]
    except IndexError:
        print("No 8x30 image found")

    # 8974
    try:
        os_8974 = glob.glob(
            os.path.join(
                localdir,
                "*qc8974*desktop*.signed"))[0]
    except IndexError:
        print("No 8974 image found")

    # OMAP (incl. 10.3.1)
    try:
        os_ti = glob.glob(os.path.join(localdir, "*winchester*.signed"))[0]
    except IndexError:
        print("No OMAP image found")

    # Radio files
    # STL100-1
    try:
        radio_z10_ti = glob.glob(
            os.path.join(
                localdir,
                "*radio.m5730*.signed"))[0]
    except IndexError:
        print("No OMAP radio found")

    # STL100-X
    try:
        radio_z10_qcm = glob.glob(
            os.path.join(
                localdir,
                "*radio.qc8960.BB*.signed"))[0]
    except IndexError:
        print("No 8960 radio found")

    # STL100-4
    try:
        radio_z10_vzw = glob.glob(
            os.path.join(
                localdir,
                "*radio.qc8960*omadm*.signed"))[0]
    except IndexError:
        print("No Verizon 8960 radio found")

    # Q10/Q5
    try:
        radio_q10 = glob.glob(os.path.join(localdir, "*8960*wtr.*.signed"))[0]
    except IndexError:
        print("No Q10/Q5 radio found")

    # Z30/Classic
    try:
        radio_z30 = glob.glob(os.path.join(localdir, "*8960*wtr5*.signed"))[0]
    except IndexError:
        print("No Z30/Classic radio found")

    # Z3
    try:
        radio_z3 = glob.glob(os.path.join(localdir, "*8930*wtr5*.signed"))[0]
    except IndexError:
        print("No Z3 radio found")

    # Passport
    try:
        radio_8974 = glob.glob(os.path.join(localdir, "*8974*wtr2*.signed"))[0]
    except IndexError:
        print("No Passport radio found")

    # Pretty format names
    # 10.x.y.zzz becomes 10.x.0y.0zzz
    splitos = osversion.split(".")
    if len(splitos[2]) == 1:
        splitos[2] = "0" + splitos[2]
    if len(splitos[3]) < 4:
        splitos[3] = splitos[3].rjust(4, '0')
    osversion = ".".join(splitos)
    splitrad = radioversion.split(".")
    if len(splitrad[2]) == 1:
        splitrad[2] = "0" + splitrad[2]
    if len(splitrad[3]) < 4:
        splitrad[3] = splitrad[3].rjust(4, '0')
    radioversion = ".".join(splitrad)

    # Generate loaders
    print("\nCREATING LOADERS...")
    # STL100-1
    try:
        print("\nCreating OMAP Z10 OS...")
        pseudocap.make_autoloader(  # @UndefinedVariable, since PyDev is dumb
            filename="Z10_" +
            osversion +
            "_STL100-1.exe",
            cap=cap,
            firstfile=os_ti,
            secondfile=radio_z10_ti,
            folder=localdir)
    except Exception:
        print("Could not create STL100-1 OS/radio loader")
    if radios:
        print("Creating OMAP Z10 radio...")
        try:
            pseudocap.make_autoloader(
                "Z10_" +
                radioversion +
                "_STL100-1.exe",
                cap=cap,
                firstfile=radio_z10_ti,
                folder=localdir)
        except Exception:
            print("Could not create STL100-1 radio loader")

    # STL100-X
    try:
        print("\nCreating Qualcomm Z10 OS...")
        pseudocap.make_autoloader(
            "Z10_" +
            osversion +
            "_STL100-2-3.exe",
            cap=cap,
            firstfile=os_8960,
            secondfile=radio_z10_qcm,
            folder=localdir)
    except Exception:
        print("Could not create Qualcomm Z10 OS/radio loader")
    if radios:
        print("Creating Qualcomm Z10 radio...")
        try:
            pseudocap.make_autoloader(
                "Z10_" +
                radioversion +
                "_STL100-2-3.exe",
                cap=cap,
                firstfile=radio_z10_qcm,
                folder=localdir)
        except Exception:
            print("Could not create Qualcomm Z10 radio loader")

    # STL100-4
    try:
        print("\nCreating Verizon Z10 OS...")
        pseudocap.make_autoloader(
            "Z10_" +
            osversion +
            "_STL100-4.exe",
            cap=cap,
            firstfile=os_8960,
            secondfile=radio_z10_vzw,
            folder=localdir)
    except Exception:
        print("Could not create Verizon Z10 OS/radio loader")
    if radios:
        print("Creating Verizon Z10 radio...")
        try:
            pseudocap.make_autoloader(
                "Z10_" +
                radioversion +
                "_STL100-4.exe",
                cap=cap,
                firstfile=radio_z10_vzw,
                folder=localdir)
        except Exception:
            print("Could not create Verizon Z10 radio loader")

    # Q10/Q5
    try:
        print("\nCreating Q10/Q5 OS...")
        pseudocap.make_autoloader(
            "Q10_" +
            osversion +
            "_SQN100-1-2-3-4-5.exe",
            cap=cap,
            firstfile=os_8960,
            secondfile=radio_q10,
            folder=localdir)
    except Exception:
        print("Could not create Q10/Q5 OS/radio loader")
    if radios:
        print("Creating Q10/Q5 radio...")
        try:
            pseudocap.make_autoloader(
                "Q10_" +
                radioversion +
                "_SQN100-1-2-3-4-5.exe",
                cap=cap,
                firstfile=radio_q10,
                folder=localdir)
        except Exception:
            print("Could not create Q10/Q5 radio loader")

    # Z30/Classic
    try:
        print("\nCreating Z30/Classic OS...")
        pseudocap.make_autoloader(
            "Z30_" +
            osversion +
            "_STA100-1-2-3-4-5-6.exe",
            cap=cap,
            firstfile=os_8960,
            secondfile=radio_z30,
            folder=localdir)
    except Exception:
        print("Could not create Z30/Classic OS/radio loader")
    if radios:
        print("Creating Z30/Classic radio...")
        try:
            pseudocap.make_autoloader(
                "Z30_" +
                radioversion +
                "_STA100-1-2-3-4-5-6.exe",
                cap=cap,
                firstfile=radio_z30,
                folder=localdir)
        except Exception:
            print("Could not create Z30/Classic radio loader")

    # Z3
    try:
        print("\nCreating Z3 OS...")
        pseudocap.make_autoloader(
            "Z3_" +
            osversion +
            "_STJ100-1-2.exe",
            cap=cap,
            firstfile=os_8x30,
            secondfile=radio_z3,
            folder=localdir)
    except Exception:
        print("Could not create Z3 OS/radio loader")
    if radios:
        print("Creating Z3 radio...")
        try:
            pseudocap.make_autoloader(
                "Z3_" +
                radioversion +
                "_STJ100-1-2.exe",
                cap=cap,
                firstfile=radio_z3,
                folder=localdir)
        except Exception:
            print("Could not create Z3 radio loader")

    # Passport
    try:
        print("\nCreating Passport OS...")
        pseudocap.make_autoloader(
            "Passport_" +
            osversion +
            "_SQW100-1-2-3.exe",
            cap=cap,
            firstfile=os_8974,
            secondfile=radio_8974,
            folder=localdir)
    except Exception:
        print("Could not create Passport OS/radio loader")
    if radios:
        print("Creating Passport radio...")
        try:
            pseudocap.make_autoloader(
                "Passport_" +
                radioversion +
                "_SQW100-1-2-3.exe",
                cap=cap,
                firstfile=radio_8974,
                folder=localdir)
        except Exception:
            print("Could not create Passport radio loader")


def generate_lazy_loader(
        osversion, radioversion, device,
        cap="cap.exe", localdir=os.getcwd()):
    print("\nCREATING LOADER...")
    if device == 0:
        try:
            os_ti = str(glob.glob("*winchester*.signed")[0])
        except IndexError:
            print("No OMAP image found")
            return
        try:
            radio_z10_ti = str(glob.glob("*radio.m5730*.signed")[0])
        except IndexError:
            print("No OMAP radio found")
            return
        else:
            print("Creating OMAP Z10 OS...")
            try:
                pseudocap.make_autoloader(
                    filename="Z10_" +
                    osversion +
                    "_STL100-1.exe",
                    cap=cap,
                    firstfile=os_ti,
                    secondfile=radio_z10_ti,
                    thirdfile="",
                    fourthfile="",
                    fifthfile="",
                    sixthfile="",
                    folder=localdir)
            except Exception:
                print("Could not create STL100-1 OS/radio loader")
                return
    elif device == 1:
        try:
            os_8960 = str(glob.glob("*qc8960*_sfi.desktop*.signed")[0])
        except IndexError:
            print("No 8960 image found")
            return
        try:
            radio_z10_qcm = str(glob.glob("*radio.qc8960.BB*.signed")[0])
        except IndexError:
            print("No 8960 radio found")
            return
        else:
            print("Creating Qualcomm Z10 OS...")
            try:
                pseudocap.make_autoloader(
                    "Z10_" +
                    osversion +
                    "_STL100-2-3.exe",
                    cap,
                    os_8960,
                    radio_z10_qcm,
                    folder=localdir)
            except Exception:
                print("Could not create Qualcomm Z10 OS/radio loader")
                return
    elif device == 2:
        try:
            os_8960 = str(glob.glob("*qc8960*_sfi.desktop*.signed")[0])
        except IndexError:
            print("No 8960 image found")
            return
        try:
            radio_z10_vzw = str(glob.glob("*radio.qc8960*omadm*.signed")[0])
        except IndexError:
            print("No Verizon 8960 radio found")
            return
        else:
            print("Creating Verizon Z10 OS...")
            try:
                pseudocap.make_autoloader(
                    "Z10_" +
                    osversion +
                    "_STL100-4.exe",
                    cap,
                    os_8960,
                    radio_z10_vzw,
                    folder=localdir)
            except Exception:
                print("Could not create Verizon Z10 OS/radio loader")
                return
    elif device == 3:
        try:
            os_8960 = str(glob.glob("*qc8960*_sfi.desktop*.signed")[0])
        except IndexError:
            print("No 8960 image found")
            return
        try:
            radio_q10 = str(glob.glob("*8960*wtr.*.signed")[0])
        except IndexError:
            print("No Q10/Q5 radio found")
            return
        else:
            print("Creating Q10/Q5 OS...")
            try:
                pseudocap.make_autoloader(
                    "Q10_" +
                    osversion +
                    "_SQN100-1-2-3-4-5.exe",
                    cap,
                    os_8960,
                    radio_q10,
                    folder=localdir)
            except Exception:
                print("Could not create Q10/Q5 OS/radio loader")
                return
    elif device == 4:
        try:
            os_8960 = str(glob.glob("*qc8960*_sfi.desktop*.signed")[0])
        except IndexError:
            print("No 8960 image found")
            return
        try:
            radio_z30 = str(glob.glob("*8960*wtr5*.signed")[0])
        except IndexError:
            print("No Z30/Classic radio found")
            return
        else:
            print("Creating Z30/Classic OS...")
            try:
                pseudocap.make_autoloader(
                    "Z30_" +
                    osversion +
                    "_STA100-1-2-3-4-5-6.exe",
                    cap,
                    os_8960,
                    radio_z30,
                    folder=localdir)
            except Exception:
                print("Could not create Z30/Classic OS/radio loader")
                return
    elif device == 5:
        try:
            os_8x30 = str(glob.glob("*qc8x30*desktop*.signed")[0])
        except IndexError:
            print("No 8x30 image found")
            return
        try:
            radio_z3 = str(glob.glob("*8930*wtr5*.signed")[0])
        except IndexError:
            print("No Z3 radio found")
            return
        else:
            print("Creating Z3 OS...")
            try:
                pseudocap.make_autoloader(
                    "Z3_" +
                    osversion +
                    "_STJ100-1-2.exe",
                    cap,
                    os_8x30,
                    radio_z3,
                    folder=localdir)
            except Exception:
                print("Could not create Z3 OS/radio loader")
                return
    elif device == 6:
        try:
            os_8974 = str(glob.glob("*qc8974*desktop*.signed")[0])
        except IndexError:
            print("No 8974 image found")
            return
        try:
            radio_8974 = str(glob.glob("*8974*wtr2*.signed")[0])
        except IndexError:
            print("No Passport radio found")
            return
        else:
            print("Creating Passport OS...")
            try:
                pseudocap.make_autoloader(
                    "Passport_" +
                    osversion +
                    "_SQW100-1-2-3.exe",
                    cap,
                    os_8974,
                    radio_8974,
                    folder=localdir)
            except Exception:
                print("Could not create Passport OS/radio loader")
                return
    else:
        return

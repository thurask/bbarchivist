from os.path import abspath, dirname, join

_version = "1.2.0"
_capversion = "3.11.0.22"
_caplocation = join(dirname(abspath(__file__)), "cap-" + _capversion + ".dat")
_devicelist = ["STL100-1",
               "STL100-2",
               "STL100-3",
               "STL100-4",
               "STK100-1",
               "STK100-2",
               "SQN100-1",
               "SQN100-2",
               "SQN100-3",
               "SQN100-4",
               "SQN100-5",
               "SQR100-1",
               "SQR100-2",
               "SQR100-3",
               "SQK100-1",
               "SQK100-2",
               "STA100-1",
               "STA100-2",
               "STA100-3",
               "STA100-4",
               "STA100-5",
               "STA100-6",
               "SQC100-1",
               "SQC100-2",
               "SQC100-3",
               "SQC100-4",
               "SQC100-5",
               "STR100-1",
               "STR100-2",
               "STJ100-1",
               "STJ100-2",
               "SQW100-1",
               "SQW100-2",
               "SQW100-3"]
_hwidlist = ["4002607",
             "8700240A",
             "8500240A",
             "8400240A",
             "A500240A",
             "A600240A",
             "8400270A",
             "8500270A",
             "8600270A",
             "8C00270A",
             "8700270A",
             "84002A0A",
             "85002A0A",
             "86002A0A",
             "8F00270A",
             "8E00270A",
             "8C00240A",
             "8D00240A",
             "8E00240A",
             "8F00240A",
             "9500240A",
             "B500240A",
             "9600270A",
             "9400270A",
             "9500270A",
             "9700270A",
             "9C00270A",
             "7002E0A",
             "6002E0A",
             "4002E07",
             "5002E07",
             "87002C0A",
             "85002C0A",
             "84002C0A"]
_modellist = ["Z10",
              "P9982",
              "Q10",
              "Q5",
              "P9983",
              "Z30",
              "CLASSIC",
              "LEAP",
              "Z3",
              "PASSPORT"]


def return_constant(constant):
    """
    Returns constant referred to by given name/name + index.
    :param constant: A constant declared in this file.
    :type constant: str
    """
    return constant

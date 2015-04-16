from os.path import abspath, dirname, join

_version = "1.0.1"
_capversion = "3.11.0.18"
_caplocation = join(dirname(abspath(__file__)), "cap-" + _capversion + ".dat")


def return_constant(constant):
    """
    Returns constant provided in function,
    :param constant: A constant declared in this file.
    :type constant: str
    """
    return constant

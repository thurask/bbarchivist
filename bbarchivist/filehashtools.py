#!/usr/bin/env python3

"""This module is used to generate file hashes/checksums and PGP signatures."""

__author__ = "Thurask"
__license__ = "Do whatever"
__copyright__ = "2015 Thurask"

import zlib  # crc32/adler32
import hashlib  # all other hashes
import hmac  # escreens is a hmac, news at 11
import os  # path work
import gnupg  # interface b/w Python, GPG
import configparser  # config parsing, duh
from bbarchivist import bbconstants  # premade stuff


def crc32hash(filepath, blocksize=16 * 1024 * 1024):
    """
    Return CRC32 checksum of a file.

    :param filepath: File you wish to verify.
    :type filepath: str

    :param blocksize: How much of file to read at once.
    :type blocksize: int
    """
    seed = 0
    with open(filepath, 'rb') as file:
        for chunk in iter(lambda: file.read(blocksize), b''):
            seed = zlib.crc32(chunk, seed)
    final = format(seed & 0xFFFFFFFF, "08x")
    return final


def adler32hash(filepath, blocksize=16 * 1024 * 1024):
    """
    Return Adler32 checksum of a file.

    :param filepath: File you wish to verify.
    :type filepath: str

    :param blocksize: How much of file to read at once.
    :type blocksize: int
    """
    asum = 1
    with open(filepath, 'rb') as file:
        while True:
            data = file.read(blocksize)
            if not data:
                break
            asum = zlib.adler32(data, asum)
            if asum < 0:
                asum += 2 ** 32
    final = format(asum & 0xFFFFFFFF, "08x")
    return final


def sha1hash(filepath, blocksize=16 * 1024 * 1024):
    """
    Return SHA-1 hash of a file.

    :param filepath: File you wish to verify.
    :type filepath: str

    :param blocksize: How much of file to read at once.
    :type blocksize: int
    """
    sha1 = hashlib.sha1()
    with open(filepath, 'rb') as file:
        while True:
            data = file.read(blocksize)
            if not data:
                break
            sha1.update(data)
    return sha1.hexdigest()


def sha224hash(filepath, blocksize=16 * 1024 * 1024):
    """
    Return SHA-224 hash of a file.

    :param filepath: File you wish to verify.
    :type filepath: str

    :param blocksize: How much of file to read at once.
    :type blocksize: int
    """
    sha224 = hashlib.sha224()
    with open(filepath, 'rb') as file:
        while True:
            data = file.read(blocksize)
            if not data:
                break
            sha224.update(data)
    return sha224.hexdigest()


def sha256hash(filepath, blocksize=16 * 1024 * 1024):
    """
    Return SHA-256 hash of a file.

    :param filepath: File you wish to verify.
    :type filepath: str

    :param blocksize: How much of file to read at once.
    :type blocksize: int
    """
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as file:
        while True:
            data = file.read(blocksize)
            if not data:
                break
            sha256.update(data)
    return sha256.hexdigest()


def sha384hash(filepath, blocksize=16 * 1024 * 1024):
    """
    Return SHA-384 hash of a file.

    :param filepath: File you wish to verify.
    :type filepath: str

    :param blocksize: How much of file to read at once.
    :type blocksize: int
    """
    sha384 = hashlib.sha384()
    with open(filepath, 'rb') as file:
        while True:
            data = file.read(blocksize)
            if not data:
                break
            sha384.update(data)
    return sha384.hexdigest()


def sha512hash(filepath, blocksize=16 * 1024 * 1024):
    """
    Return SHA-512 hash of a file.

    :param filepath: File you wish to verify.
    :type filepath: str

    :param blocksize: How much of file to read at once.
    :type blocksize: int
    """
    sha512 = hashlib.sha512()
    with open(filepath, 'rb') as file:
        while True:
            data = file.read(blocksize)
            if not data:
                break
            sha512.update(data)
    return sha512.hexdigest()


def md4hash(filepath, blocksize=16 * 1024 * 1024):
    """
    Return MD4 hash of a file; depends on system SSL library.

    :param filepath: File you wish to verify.
    :type filepath: str

    :param blocksize: How much of file to read at once.
    :type blocksize: int
    """
    try:
        md4 = hashlib.new('md4')
        with open(filepath, 'rb') as file:
            while True:
                data = file.read(blocksize)
                if not data:
                    break
                md4.update(data)
        return md4.hexdigest()
    except ValueError as exc:
        print(str(exc))
        print("MD4 HASH FAILED:\nIS IT AVAILABLE?")


def md5hash(filepath, blocksize=16 * 1024 * 1024):
    """
    Return MD5 hash of a file.

    :param filepath: File you wish to verify.
    :type filepath: str

    :param blocksize: How much of file to read at once.
    :type blocksize: int
    """
    md5 = hashlib.md5()
    with open(filepath, 'rb') as file:
        while True:
            data = file.read(blocksize)
            if not data:
                break
            md5.update(data)
    return md5.hexdigest()


def ripemd160hash(filepath, blocksize=16 * 1024 * 1024):
    """
    Return RIPEMD160 hash of a file; depends on system SSL library.

    :param filepath: File you wish to verify.
    :type filepath: str

    :param blocksize: How much of file to read at once.
    :type blocksize: int
    """
    try:
        r160 = hashlib.new('ripemd160')
        with open(filepath, 'rb') as file:
            while True:
                data = file.read(blocksize)
                if not data:
                    break
                r160.update(data)
        return r160.hexdigest()
    except ValueError as exc:
        print(str(exc))
        print("RIPEMD160 HASH FAILED:\nIS IT AVAILABLE?")


def whirlpoolhash(filepath, blocksize=16 * 1024 * 1024):
    """
    Return Whirlpool hash of a file; depends on system SSL library.

    :param filepath: File you wish to verify.
    :type filepath: str

    :param blocksize: How much of file to read at once.
    :type blocksize: int
    """
    try:
        wpool = hashlib.new('whirlpool')
        with open(filepath, 'rb') as file:
            while True:
                data = file.read(blocksize)
                if not data:
                    break
                wpool.update(data)
        return wpool.hexdigest()
    except ValueError as exc:
        print(str(exc))
        print("WHIRLPOOL HASH FAILED:\nIS IT AVAILABLE?")


def gpgfile(filepath, gpginst, keyid=None, passphrase=None):
    """
    Make ASCII-armored signature files with a given private key.
    Takes an instance of gnupg.GPG().

    :param filepath: File you wish to verify.
    :type filepath: str

    :param gpginst: Instance of Python GnuPG executable.
    :type gpginst: gnupg.GPG()

    :param keyid: Key ID. 0xABCDEF01
    :type keyid: str

    :param passphrase: Passphrase for key.
    :type passphrase: str
    """
    with open(filepath, "rb") as file:
        gpginst.sign_file(file,
                          detach=True,
                          keyid=keyid,
                          passphrase=passphrase,
                          output=file.name + ".asc")


def calculate_escreens(pin, app, uptime, duration=30):
    """
    Calculate key for the Engineering Screens based on input.

    :param pin: PIN to check. 8 character hexadecimal, lowercase.
    :type pin: str

    :param app: App version. 10.x.y.zzzz.
    :type app: str

    :param uptime: Uptime in ms.
    :type uptime: str

    :param duration: 1, 3, 6, 15, 30 (days).
    :type duration: str
    """
    #: Somehow, values for lifetimes for escreens.
    lifetimes = {
        1: "",
        3: "Hello my baby, hello my honey, hello my rag time gal",
        7: "He was a boy, and she was a girl, can I make it any more obvious?",
        15: "So am I, still waiting, for this world to stop hating?",
        30: "I love myself today, not like yesterday. I'm cool, I'm calm, I'm gonna be okay"
    }
    #: Escreens magic HMAC secret.
    secret = 'Up the time stream without a TARDIS'
    duration = int(duration)
    if duration not in [1, 3, 6, 15, 30]:
        duration = 1
    data = pin.lower() + app + uptime + lifetimes[duration]
    newhmac = hmac.new(secret.encode(),
                       data.encode(),
                       digestmod=hashlib.sha1)
    key = newhmac.hexdigest()[:8]
    return key.upper()


def verifier(workingdir, **kwargs):
    """
    For all files in a directory, perform various hash/checksum functions.
    Take dict to define hashes, write the output to a/individual .cksum file(s).

    :param workingdir: Path containing files you wish to verify.
    :type workingdir: str
    """
    if kwargs is None:
        kwargs = verifier_config_loader()
    hashoutput_crc32 = "CRC32\n"
    hashoutput_adler32 = "ADLER32\n"
    hashoutput_sha1 = "SHA1\n"
    hashoutput_sha224 = "SHA224\n"
    hashoutput_sha256 = "SHA256\n"
    hashoutput_sha384 = "SHA384\n"
    hashoutput_sha512 = "SHA512\n"
    hashoutput_md5 = "MD5\n"
    hashoutput_md4 = "MD4\n"
    hashoutput_ripemd160 = "RIPEMD160\n"
    hashoutput_whirlpool = "WHIRLPOOL\n"
    if os.listdir(workingdir) == []:
        return
    else:
        for file in os.listdir(workingdir):
            if os.path.isdir(os.path.join(workingdir, file)):
                pass  # exclude folders
            elif file.endswith(bbconstants.SUPPS):
                pass  # exclude already generated files
            else:
                print("HASHING:", str(file))
                if kwargs['adler32']:
                    print("ADLER32 ", end="")
                    result_adler32 = adler32hash(
                        os.path.join(
                            workingdir,
                            file),
                        kwargs['blocksize'])
                    hashoutput_adler32 += str(result_adler32.upper())
                    hashoutput_adler32 += " "
                    hashoutput_adler32 += str(file)
                    hashoutput_adler32 += " \n"
                if kwargs['crc32']:
                    print("CRC32 ", end="")
                    result_crc32 = crc32hash(
                        os.path.join(
                            workingdir,
                            file),
                        kwargs['blocksize'])
                    hashoutput_crc32 += str(result_crc32.upper())
                    hashoutput_crc32 += " "
                    hashoutput_crc32 += str(file)
                    hashoutput_crc32 += " \n"
                if kwargs['md4']:
                    print("MD4 ", end="")
                    result_md4 = md4hash(
                        os.path.join(
                            workingdir,
                            file),
                        kwargs['blocksize'])
                    hashoutput_md4 += str(result_md4.upper())
                    hashoutput_md4 += " "
                    hashoutput_md4 += str(file)
                    hashoutput_md4 += " \n"
                if kwargs['md5']:
                    print("MD5 ", end="")
                    result_md5 = md5hash(
                        os.path.join(
                            workingdir,
                            file),
                        kwargs['blocksize'])
                    hashoutput_md5 += str(result_md5.upper())
                    hashoutput_md5 += " "
                    hashoutput_md5 += str(file)
                    hashoutput_md5 += " \n"
                if kwargs['sha1']:
                    print("SHA1 ", end="")
                    result_sha1 = sha1hash(
                        os.path.join(
                            workingdir,
                            file),
                        kwargs['blocksize'])
                    hashoutput_sha1 += str(result_sha1.upper())
                    hashoutput_sha1 += " "
                    hashoutput_sha1 += str(file)
                    hashoutput_sha1 += " \n"
                if kwargs['sha224']:
                    print("SHA224 ", end="")
                    result_sha224 = sha224hash(
                        os.path.join(
                            workingdir,
                            file),
                        kwargs['blocksize'])
                    hashoutput_sha224 += str(result_sha224.upper())
                    hashoutput_sha224 += " "
                    hashoutput_sha224 += str(file)
                    hashoutput_sha224 += " \n"
                if kwargs['sha256']:
                    print("SHA256 ", end="")
                    result_sha256 = sha256hash(
                        os.path.join(
                            workingdir,
                            file),
                        kwargs['blocksize'])
                    hashoutput_sha256 += str(result_sha256.upper())
                    hashoutput_sha256 += " "
                    hashoutput_sha256 += str(file)
                    hashoutput_sha256 += " \n"
                if kwargs['sha384']:
                    print("SHA384 ", end="")
                    result_sha384 = sha384hash(
                        os.path.join(
                            workingdir,
                            file),
                        kwargs['blocksize'])
                    hashoutput_sha384 += str(result_sha384.upper())
                    hashoutput_sha384 += " "
                    hashoutput_sha384 += str(file)
                    hashoutput_sha384 += " \n"
                if kwargs['sha512']:
                    print("SHA512 ", end="")
                    result_sha512 = sha512hash(
                        os.path.join(
                            workingdir,
                            file),
                        kwargs['blocksize'])
                    hashoutput_sha512 += str(result_sha512.upper())
                    hashoutput_sha512 += " "
                    hashoutput_sha512 += str(file)
                    hashoutput_sha512 += " \n"
                if kwargs['ripemd160']:
                    print("RIPEMD160 ", end="")
                    result_ripemd160 = ripemd160hash(
                        os.path.join(
                            workingdir,
                            file),
                        kwargs['blocksize'])
                    hashoutput_ripemd160 += str(result_ripemd160.upper())
                    hashoutput_ripemd160 += " "
                    hashoutput_ripemd160 += str(file)
                    hashoutput_ripemd160 += " \n"
                if kwargs['whirlpool']:
                    print("WHIRLPOOL ", end="")
                    result_whirlpool = whirlpoolhash(
                        os.path.join(
                            workingdir,
                            file),
                        kwargs['blocksize'])
                    hashoutput_whirlpool += str(result_whirlpool.upper())
                    hashoutput_whirlpool += " "
                    hashoutput_whirlpool += str(file)
                    hashoutput_whirlpool += " \n"
                print("\n")
                if not kwargs['onefile']:
                    basename = file + ".cksum"
                    targetname = os.path.join(workingdir, basename)
                    with open(targetname, 'w') as target:
                        if kwargs['adler32']:
                            target.write(hashoutput_adler32 + "\n")
                        if kwargs['crc32']:
                            target.write(hashoutput_crc32 + "\n")
                        if kwargs['md4']:
                            target.write(hashoutput_md4 + "\n")
                        if kwargs['md5']:
                            target.write(hashoutput_md5 + "\n")
                        if kwargs['sha1']:
                            target.write(hashoutput_sha1 + "\n")
                        if kwargs['sha224']:
                            target.write(hashoutput_sha224 + "\n")
                        if kwargs['sha256']:
                            target.write(hashoutput_sha256 + "\n")
                        if kwargs['sha384']:
                            target.write(hashoutput_sha384 + "\n")
                        if kwargs['sha512']:
                            target.write(hashoutput_sha512 + "\n")
                        if kwargs['ripemd160']:
                            target.write(hashoutput_ripemd160 + "\n")
                        if kwargs['whirlpool']:
                            target.write(hashoutput_whirlpool + "\n")
                    if any((kwargs['crc32'], kwargs['adler32'],
                            kwargs['md4'], kwargs['md5'], kwargs['sha1'],
                            kwargs['sha224'], kwargs['sha256'], kwargs['sha384'],
                            kwargs['sha512'], kwargs['ripemd160'],
                            kwargs['whirlpool'])):
                        with open(targetname, 'rb+') as target:
                            target.seek(-2, os.SEEK_END)
                            target.truncate()
                    else:
                        os.remove(targetname)
                    # reset hashes
                    hashoutput_crc32 = "CRC32\n"
                    hashoutput_adler32 = "ADLER32\n"
                    hashoutput_sha1 = "SHA1\n"
                    hashoutput_sha224 = "SHA224\n"
                    hashoutput_sha256 = "SHA256\n"
                    hashoutput_sha384 = "SHA384\n"
                    hashoutput_sha512 = "SHA512\n"
                    hashoutput_md5 = "MD5\n"
                    hashoutput_md4 = "MD4\n"
                    hashoutput_ripemd160 = "RIPEMD160\n"
                    hashoutput_whirlpool = "WHIRLPOOL\n"
        if kwargs['onefile']:
            with open(os.path.join(workingdir, 'all.cksum'), 'w') as target:
                if kwargs['adler32']:
                    target.write(hashoutput_adler32 + "\n")
                if kwargs['crc32']:
                    target.write(hashoutput_crc32 + "\n")
                if kwargs['md4']:
                    target.write(hashoutput_md4 + "\n")
                if kwargs['md5']:
                    target.write(hashoutput_md5 + "\n")
                if kwargs['sha1']:
                    target.write(hashoutput_sha1 + "\n")
                if kwargs['sha224']:
                    target.write(hashoutput_sha224 + "\n")
                if kwargs['sha256']:
                    target.write(hashoutput_sha256 + "\n")
                if kwargs['sha384']:
                    target.write(hashoutput_sha384 + "\n")
                if kwargs['sha512']:
                    target.write(hashoutput_sha512 + "\n")
                if kwargs['ripemd160']:
                    target.write(hashoutput_ripemd160 + "\n")
                if kwargs['whirlpool']:
                    target.write(hashoutput_whirlpool + "\n")
            if any((kwargs['crc32'], kwargs['adler32'],
                    kwargs['md4'], kwargs['md5'], kwargs['sha1'],
                    kwargs['sha224'], kwargs['sha256'], kwargs['sha384'],
                    kwargs['sha512'], kwargs['ripemd160'],
                    kwargs['whirlpool'])):
                with open(os.path.join(workingdir,
                                       'all.cksum'), 'rb+') as target:
                    target.seek(-2, os.SEEK_END)  # navigate to last character
                    target.truncate()  # get rid of trailing \n
            else:
                os.remove(os.path.join(workingdir, 'all.cksum'))


def gpgrunner(workingdir, keyid=None, passphrase=None, selective=False):
    """
    Create ASCII-armored PGP signatures for all files in a given directory.

    :param workingdir: Path containing files you wish to verify.
    :type workingdir: str

    :param keyid: Key to use. 8-character hexadecimal, with or without 0x.
    :type keyid: str

    :param passphrase: Passphrase for given key.
    :type passphrase: str

    :param selective: Filtering filenames/extensions. Default is false.
    :type selective: bool
    """
    try:
        gpg = gnupg.GPG()
    except ValueError:
        print("COULD NOT FIND GnuPG!")
        raise SystemExit
    else:
        if not keyid.startswith("0x"):
            keyid = "0x" + keyid.upper()
        files = (file for file in os.listdir(workingdir) if not os.path.isdir(file))
        for file in files:
            sup = bbconstants.SUPPS
            if not file.endswith(sup):
                aps = bbconstants.ARCSPLUS
                pfx = bbconstants.PREFIXES
                if (file.endswith(aps) and file.startswith(pfx)) if selective else True:
                    print("VERIFYING:", str(file))
                    thepath = os.path.join(workingdir, file)
                    try:
                        gpgfile(thepath, gpg, keyid=keyid, passphrase=passphrase)
                    except Exception as exc:
                        print("SOMETHING WENT WRONG")
                        print(str(exc))
                        raise SystemExit


def gpg_config_loader():
    """
    Read a ConfigParser file to get PGP key, password (optional)
    """
    config = configparser.ConfigParser()
    homepath = os.path.expanduser("~")
    conffile = os.path.join(homepath, "bbarchivist.ini")
    config.read(conffile)
    gpgkey = config.get('gpgrunner', 'key', fallback=None)
    gpgpass = config.get('gpgrunner', 'pass', fallback=None)
    return gpgkey, gpgpass


def gpg_config_writer(key=None, password=None):
    """
    Write a ConfigParser file to store PGP key, password (optional)

    :param key: Key ID, leave as None to not write.
    :type key: str

    :param password: Key password, leave as None to not write.
    :type password: str
    """
    config = configparser.ConfigParser()
    homepath = os.path.expanduser("~")
    conffile = os.path.join(homepath, "bbarchivist.ini")
    config['gpgrunner'] = {}
    if key is not None:
        config['gpgrunner']['key'] = key
    if password is not None:
        config['gpgrunner']['pass'] = password
    with open(conffile, "w") as configfile:
        config.write(configfile)


def verifier_config_loader():
    """
    Read a ConfigParser file to get hash preferences.
    """
    resultdict = {}
    config = configparser.ConfigParser()
    homepath = os.path.expanduser("~")
    conffile = os.path.join(homepath, "bbarchivist.ini")
    config.read(conffile)
    if not config.has_section('hashmodes'):
        config['hashmodes'] = {}
        with open(conffile, "w") as configfile:
            config.write(configfile)
    hashini = config['hashmodes']
    resultdict['crc32'] = bool(hashini.getboolean('crc32', fallback=False))
    resultdict['adler32'] = bool(hashini.getboolean('adler32', fallback=False))
    resultdict['sha1'] = bool(hashini.getboolean('sha1', fallback=True))
    resultdict['sha224'] = bool(hashini.getboolean('sha224', fallback=False))
    resultdict['sha256'] = bool(hashini.getboolean('sha256', fallback=True))
    resultdict['sha384'] = bool(hashini.getboolean('sha384', fallback=False))
    resultdict['sha512'] = bool(hashini.getboolean('sha512', fallback=False))
    resultdict['md5'] = bool(hashini.getboolean('md5', fallback=True))
    resultdict['md4'] = bool(hashini.getboolean('md4', fallback=False))
    resultdict['ripemd160'] = bool(hashini.getboolean('ripemd160', fallback=False))
    resultdict['whirlpool'] = bool(hashini.getboolean('whirlpool', fallback=False))
    resultdict['onefile'] = bool(hashini.getboolean('onefile', fallback=False))
    resultdict['blocksize'] = int(hashini.getint('blocksize', fallback=16777216))
    return resultdict


def verifier_config_writer(resultdict=None):
    """
    Write a ConfigParser file to store hash preferences.

    :param resultdict: Dictionary of results: {method, bool}
    :type resultdict: dict({str, bool})
    """
    if resultdict is None:
        resultdict = verifier_config_loader()
    config = configparser.ConfigParser()
    homepath = os.path.expanduser("~")
    conffile = os.path.join(homepath, "bbarchivist.ini")
    config.read(conffile)
    for method, flag in resultdict.items():
        config.set('hashmodes', method, str(flag).lower())
    with open(conffile, "w") as configfile:
        config.write(configfile)

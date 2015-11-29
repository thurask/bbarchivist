#!/usr/bin/env python3
"""This module is used to generate file hashes/checksums and PGP signatures."""

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "Copyright 2015 Thurask"

import zlib  # crc32/adler32
import hashlib  # all other hashes
import hmac  # escreens is a hmac, news at 11
import os  # path work
import gnupg  # interface b/w Python, GPG
import configparser  # config parsing, duh
from bbarchivist import bbconstants  # premade stuff
from bbarchivist.barutils import prepends  # file parsing


def hc32(filepath, blocksize=16 * 1024 * 1024):
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


def ha32(filepath, blocksize=16 * 1024 * 1024):
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


def hs1(filepath, blocksize=16 * 1024 * 1024):
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


def hs224(filepath, blocksize=16 * 1024 * 1024):
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


def hs256(filepath, blocksize=16 * 1024 * 1024):
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


def hs384(filepath, blocksize=16 * 1024 * 1024):
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


def hs512(filepath, blocksize=16 * 1024 * 1024):
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


def hm4(filepath, blocksize=16 * 1024 * 1024):
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


def hm5(filepath, blocksize=16 * 1024 * 1024):
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


def hr160(filepath, blocksize=16 * 1024 * 1024):
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


def hwp(filepath, blocksize=16 * 1024 * 1024):
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
        30: "I love myself today, not like yesterday. "
    }
    lifetimes[30] += "I'm cool, I'm calm, I'm gonna be okay"
    #: Escreens magic HMAC secret.
    secret = 'Up the time stream without a TARDIS'
    duration = int(duration)
    if duration not in [1, 3, 6, 15, 30]:
        duration = 1
    data = pin.lower() + app + str(uptime) + lifetimes[duration]
    newhmac = hmac.new(secret.encode(),
                       data.encode(),
                       digestmod=hashlib.sha1)
    key = newhmac.hexdigest()[:8]
    return key.upper()


def hash_get(filename, hashfunc, workingdir, blocksize=16777216):
    """
    Generate and pretty format the hash result for a file.

    :param filename: File to hash.
    :type filename: str

    :param hashfunc: Hash function to use.
    :type hashfunc: function

    :param workingdir: Working directory.
    :type workingdir: str

    :param blocksize: Block size. Default is 16MB.
    :type blocksize: int
    """
    result = hashfunc(os.path.join(workingdir, filename), blocksize)
    return "{0} {1}\n".format(result.upper(), filename)


def hash_reset(hashlist):
    """
    Reset list by returning only the first item.

    :param hashlist: List to reset. First item is the type of hash.
    :type hashlist: list
    """
    return [hashlist[0]]


def verifier(workingdir, kwargs=None):
    """
    For all files in a directory, perform various hash/checksum functions.
    Take dict to define hashes, write output to a/individual .cksum file(s).

    :param workingdir: Path containing files you wish to verify.
    :type workingdir: str

    :param kwargs: Values. Refer to `:func:verifier_config_loader`.
    :type kwargs: dict
    """
    if kwargs is None:
        kwargs = verifier_config_loader()
    h_c32 = ["CRC32"]
    h_a32 = ["ADLER32"]
    h_s1 = ["SHA1"]
    h_s224 = ["SHA224"]
    h_s256 = ["SHA256"]
    h_s384 = ["SHA384"]
    h_s512 = ["SHA512"]
    h_m5 = ["MD5"]
    h_m4 = ["MD4"]
    h_r160 = ["RIPEMD160"]
    h_wp = ["WHIRLPOOL"]
    block = int(kwargs['blocksize'])
    if os.listdir(workingdir):
        for file in os.listdir(workingdir):
            if os.path.isdir(os.path.join(workingdir, file)):
                pass  # exclude folders
            elif file.endswith(bbconstants.SUPPS):
                pass  # exclude already generated files
            else:
                print("HASHING:", str(file))
                if kwargs['adler32']:
                    h_a32.append(hash_get(file, ha32, workingdir, block))
                if kwargs['crc32']:
                    h_c32.append(hash_get(file, hc32, workingdir, block))
                if kwargs['md4']:
                    h_m4.append(hash_get(file, hm4, workingdir, block))
                if kwargs['md5']:
                    h_m5.append(hash_get(file, hm5, workingdir, block))
                if kwargs['sha1']:
                    h_s1.append(hash_get(file, hs1, workingdir, block))
                if kwargs['sha224']:
                    h_s224.append(hash_get(file, hs224, workingdir, block))
                if kwargs['sha256']:
                    h_s256.append(hash_get(file, hs256, workingdir, block))
                if kwargs['sha384']:
                    h_s384.append(hash_get(file, hs384, workingdir, block))
                if kwargs['sha512']:
                    h_s512.append(hash_get(file, hs512, workingdir, block))
                if kwargs['ripemd160']:
                    h_r160.append(hash_get(file, hr160, workingdir, block))
                if kwargs['whirlpool']:
                    h_wp.append(hash_get(file, hwp, workingdir, block))
                if not kwargs['onefile']:
                    basename = file + ".cksum"
                    targetname = os.path.join(workingdir, basename)
                    with open(targetname, 'w') as target:
                        if kwargs['adler32']:
                            target.write("\n".join(h_a32))
                        if kwargs['crc32']:
                            target.write("\n".join(h_c32))
                        if kwargs['md4']:
                            target.write("\n".join(h_m4))
                        if kwargs['md5']:
                            target.write("\n".join(h_m5))
                        if kwargs['sha1']:
                            target.write("\n".join(h_s1))
                        if kwargs['sha224']:
                            target.write("\n".join(h_s224))
                        if kwargs['sha256']:
                            target.write("\n".join(h_s256))
                        if kwargs['sha384']:
                            target.write("\n".join(h_s384))
                        if kwargs['sha512']:
                            target.write("\n".join(h_s512))
                        if kwargs['ripemd160']:
                            target.write("\n".join(h_r160))
                        if kwargs['whirlpool']:
                            target.write("\n".join(h_wp))
                    # reset hashes
                    h_c32 = hash_reset(h_c32)
                    h_a32 = hash_reset(h_a32)
                    h_s1 = hash_reset(h_s1)
                    h_s224 = hash_reset(h_s224)
                    h_s256 = hash_reset(h_s256)
                    h_s384 = hash_reset(h_s384)
                    h_s512 = hash_reset(h_s512)
                    h_m5 = hash_reset(h_m5)
                    h_m4 = hash_reset(h_m4)
                    h_r160 = hash_reset(h_r160)
                    h_wp = hash_reset(h_wp)
        if kwargs['onefile']:
            with open(os.path.join(workingdir, 'all.cksum'), 'w') as target:
                if kwargs['adler32']:
                    target.write("\n".join(h_a32))
                if kwargs['crc32']:
                    target.write("\n".join(h_c32))
                if kwargs['md4']:
                    target.write("\n".join(h_m4))
                if kwargs['md5']:
                    target.write("\n".join(h_m5))
                if kwargs['sha1']:
                    target.write("\n".join(h_s1))
                if kwargs['sha224']:
                    target.write("\n".join(h_s224))
                if kwargs['sha256']:
                    target.write("\n".join(h_s256))
                if kwargs['sha384']:
                    target.write("\n".join(h_s384))
                if kwargs['sha512']:
                    target.write("\n".join(h_s512))
                if kwargs['ripemd160']:
                    target.write("\n".join(h_r160))
                if kwargs['whirlpool']:
                    target.write("\n".join(h_wp))


def gpgrunner(workingdir, keyid=None, pword=None, selective=False):
    """
    Create ASCII-armored PGP signatures for all files in a given directory.

    :param workingdir: Path containing files you wish to verify.
    :type workingdir: str

    :param keyid: Key to use. 8-character hexadecimal, with or without 0x.
    :type keyid: str

    :param pword: Passphrase for given key.
    :type pword: str

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
        dirlist = os.listdir(workingdir)
        files = (file for file in dirlist if not os.path.isdir(file))
        for file in files:
            sup = bbconstants.SUPPS
            if not file.endswith(sup):
                aps = bbconstants.ARCSPLUS
                pfx = bbconstants.PREFIXES
                if (prepends(file, pfx, aps)) if selective else True:
                    print("VERIFYING:", str(file))
                    thepath = os.path.join(workingdir, file)
                    try:
                        gpgfile(thepath, gpg, keyid=keyid, passphrase=pword)
                    except Exception as exc:
                        print("SOMETHING WENT WRONG")
                        print(str(exc))
                        raise SystemExit


def gpg_config_loader(homepath=None):
    """
    Read a ConfigParser file to get PGP key, password (optional)

    :param homepath: Folder containing ini file. Default is user directory.
    :type homepath: str
    """
    config = configparser.ConfigParser()
    if homepath is None:
        homepath = os.path.expanduser("~")
    conffile = os.path.join(homepath, "bbarchivist.ini")
    if not os.path.exists(conffile):
        open(conffile, 'w').close()
    config.read(conffile)
    if not config.has_section('gpgrunner'):
        config['gpgrunner'] = {}
    gpgkey = config.get('gpgrunner', 'key', fallback=None)
    gpgpass = config.get('gpgrunner', 'pass', fallback=None)
    return gpgkey, gpgpass


def gpg_config_writer(key=None, password=None, homepath=None):
    """
    Write a ConfigParser file to store PGP key, password (optional)

    :param key: Key ID, leave as None to not write.
    :type key: str

    :param password: Key password, leave as None to not write.
    :type password: str

    :param homepath: Folder containing ini file. Default is user directory.
    :type homepath: str
    """
    config = configparser.ConfigParser()
    if homepath is None:
        homepath = os.path.expanduser("~")
    conffile = os.path.join(homepath, "bbarchivist.ini")
    if not os.path.exists(conffile):
        open(conffile, 'w').close()
    config.read(conffile)
    if not config.has_section('gpgrunner'):
        config['gpgrunner'] = {}
    if key is not None:
        config['gpgrunner']['key'] = key
    if password is not None:
        config['gpgrunner']['pass'] = password
    with open(conffile, "w") as configfile:
        config.write(configfile)


def verifier_config_loader(homepath=None):
    """
    Read a ConfigParser file to get hash preferences.

    :param homepath: Folder containing ini file. Default is user directory.
    :type homepath: str
    """
    results = {}
    config = configparser.ConfigParser()
    if homepath is None:
        homepath = os.path.expanduser("~")
    conffile = os.path.join(homepath, "bbarchivist.ini")
    if not os.path.exists(conffile):
        open(conffile, 'w').close()
    config.read(conffile)
    if not config.has_section('hashmodes'):
        config['hashmodes'] = {}
    ini = config['hashmodes']
    results['crc32'] = bool(ini.getboolean('crc32', fallback=False))
    results['adler32'] = bool(ini.getboolean('adler32', fallback=False))
    results['sha1'] = bool(ini.getboolean('sha1', fallback=True))
    results['sha224'] = bool(ini.getboolean('sha224', fallback=False))
    results['sha256'] = bool(ini.getboolean('sha256', fallback=True))
    results['sha384'] = bool(ini.getboolean('sha384', fallback=False))
    results['sha512'] = bool(ini.getboolean('sha512', fallback=False))
    results['md5'] = bool(ini.getboolean('md5', fallback=True))
    results['md4'] = bool(ini.getboolean('md4', fallback=False))
    results['ripemd160'] = bool(ini.getboolean('ripemd160', fallback=False))
    results['whirlpool'] = bool(ini.getboolean('whirlpool', fallback=False))
    results['onefile'] = bool(ini.getboolean('onefile', fallback=False))
    results['blocksize'] = int(ini.getint('blocksize', fallback=16777216))
    return results


def verifier_config_writer(resultdict=None, homepath=None):
    """
    Write a ConfigParser file to store hash preferences.

    :param resultdict: Dictionary of results: {method, bool}
    :type resultdict: dict({str, bool})

    :param homepath: Folder containing ini file. Default is user directory.
    :type homepath: str
    """
    if resultdict is None:
        resultdict = verifier_config_loader()
    config = configparser.ConfigParser()
    if homepath is None:
        homepath = os.path.expanduser("~")
    conffile = os.path.join(homepath, "bbarchivist.ini")
    if not os.path.exists(conffile):
        open(conffile, 'w').close()
    config.read(conffile)
    if not config.has_section('hashmodes'):
        config['hashmodes'] = {}
    for method, flag in resultdict.items():
        config.set('hashmodes', method, str(flag).lower())
    with open(conffile, "w") as configfile:
        config.write(configfile)

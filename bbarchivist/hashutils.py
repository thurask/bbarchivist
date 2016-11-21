#!/usr/bin/env python3
"""This module is used to generate file hashes/checksums and PGP signatures."""

import zlib  # crc32/adler32
import hashlib  # all other hashes
import hmac  # escreens is a hmac, news at 11
import os  # path work
import concurrent.futures  # parallelization
import gnupg  # interface b/w Python, GPG
from bbarchivist import bbconstants  # premade stuff
from bbarchivist import exceptions  # exceptions
from bbarchivist import utilities  # cores
from bbarchivist import iniconfig  # config parsing

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "Copyright 2015-2016 Thurask"


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
    hashfunc_reader(filepath, sha1, blocksize)
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
    hashfunc_reader(filepath, sha224, blocksize)
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
    hashfunc_reader(filepath, sha256, blocksize)
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
    hashfunc_reader(filepath, sha384, blocksize)
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
    hashfunc_reader(filepath, sha512, blocksize)
    return sha512.hexdigest()


def hs3224(filepath, blocksize=16 * 1024 * 1024):
    """
    Return SHA3-224 hash of a file.

    :param filepath: File you wish to verify.
    :type filepath: str

    :param blocksize: How much of file to read at once.
    :type blocksize: int
    """
    try:
        sha3224 = hashlib.sha3_224()
    except AttributeError:
        print("REQUIRES PYTHON 3.6+")
    else:
        hashfunc_reader(filepath, sha3224, blocksize)
        return sha3224.hexdigest()


def hs3256(filepath, blocksize=16 * 1024 * 1024):
    """
    Return SHA3-256 hash of a file.

    :param filepath: File you wish to verify.
    :type filepath: str

    :param blocksize: How much of file to read at once.
    :type blocksize: int
    """
    try:
        sha3256 = hashlib.sha3_256()
    except AttributeError:
        print("REQUIRES PYTHON 3.6+")
    else:
        hashfunc_reader(filepath, sha3256, blocksize)
        return sha3256.hexdigest()


def hs3384(filepath, blocksize=16 * 1024 * 1024):
    """
    Return SHA3-384 hash of a file.

    :param filepath: File you wish to verify.
    :type filepath: str

    :param blocksize: How much of file to read at once.
    :type blocksize: int
    """
    try:
        sha3384 = hashlib.sha3_384()
    except AttributeError:
        print("REQUIRES PYTHON 3.6+")
    else:
        hashfunc_reader(filepath, sha3384, blocksize)
        return sha3384.hexdigest()


def hs3512(filepath, blocksize=16 * 1024 * 1024):
    """
    Return SHA3-512 hash of a file.

    :param filepath: File you wish to verify.
    :type filepath: str

    :param blocksize: How much of file to read at once.
    :type blocksize: int
    """
    try:
        sha3512 = hashlib.sha3_512()
    except AttributeError:
        print("REQUIRES PYTHON 3.6+")
    else:
        hashfunc_reader(filepath, sha3512, blocksize)
        return sha3512.hexdigest()


def hm5(filepath, blocksize=16 * 1024 * 1024):
    """
    Return MD5 hash of a file.

    :param filepath: File you wish to verify.
    :type filepath: str

    :param blocksize: How much of file to read at once.
    :type blocksize: int
    """
    md5 = hashlib.md5()
    hashfunc_reader(filepath, md5, blocksize)
    return md5.hexdigest()


def hashfunc_reader(filepath, engine, blocksize=16 * 1024 * 1024):
    """
    Generate hash from file contents.

    :param filepath: File you wish to verify.
    :type filepath: str

    :param engine: Hash object to update with file contents.
    :type engine: _hashlib.HASH

    :param blocksize: How much of file to read at once.
    :type blocksize: int
    """
    with open(filepath, 'rb') as file:
        while True:
            data = file.read(blocksize)
            if not data:
                break
            engine.update(data)


def ssl_hash(filepath, method, blocksize=16 * 1024 * 1024):
    """
    Return SSL-library dependent hash of a file.

    :param filepath: File you wish to verify.
    :type filepath: str

    :param method: Method to use: algorithms in hashlib that are not guaranteed.
    :type method: str

    :param blocksize: How much of file to read at once.
    :type blocksize: int
    """
    try:
        engine = hashlib.new(method)
        hashfunc_reader(filepath, engine, blocksize)
        return engine.hexdigest()
    except ValueError as exc:
        msg = "{0} HASH FAILED".format(method.upper())
        exceptions.handle_exception(exc, msg, exceptions.DummyException)
        


def hm4(filepath, blocksize=16 * 1024 * 1024):
    """
    Return MD4 hash of a file; depends on system SSL library.

    :param filepath: File you wish to verify.
    :type filepath: str

    :param blocksize: How much of file to read at once.
    :type blocksize: int
    """
    return ssl_hash(filepath, "md4", blocksize)


def hr160(filepath, blocksize=16 * 1024 * 1024):
    """
    Return RIPEMD160 hash of a file; depends on system SSL library.

    :param filepath: File you wish to verify.
    :type filepath: str

    :param blocksize: How much of file to read at once.
    :type blocksize: int
    """
    return ssl_hash(filepath, "ripemd160", blocksize)


def hwp(filepath, blocksize=16 * 1024 * 1024):
    """
    Return Whirlpool hash of a file; depends on system SSL library.

    :param filepath: File you wish to verify.
    :type filepath: str

    :param blocksize: How much of file to read at once.
    :type blocksize: int
    """
    return ssl_hash(filepath, "whirlpool", blocksize)


def hs0(filepath, blocksize=16 * 1024 * 1024):
    """
    Return SHA-0 hash of a file; depends on system SSL library.

    :param filepath: File you wish to verify.
    :type filepath: str

    :param blocksize: How much of file to read at once.
    :type blocksize: int
    """
    return ssl_hash(filepath, "sha", blocksize)


def gpgfile(filepath, gpginst, key=None, pword=None):
    """
    Make ASCII-armored signature files with a given private key.
    Takes an instance of gnupg.GPG().

    :param filepath: File you wish to verify.
    :type filepath: str

    :param gpginst: Instance of Python GnuPG executable.
    :type gpginst: gnupg.GPG()

    :param key: Key ID. 0xABCDEF01
    :type key: str

    :param pword: Passphrase for key.
    :type pword: str
    """
    with open(filepath, "rb") as file:
        fname = file.name + ".asc"
        gpginst.sign_file(file, detach=True, keyid=key, passphrase=pword, output=fname)


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
    newhmac = hmac.new(secret.encode(), data.encode(), digestmod=hashlib.sha1)
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
    return "{0} {1}\n".format(result.upper(), os.path.basename(filename))


def base_hash(hashtype, source, workingdir, block, hashfunc, target, kwargs=None):
    """
    Generic hash function; get hash, write to file.

    :param hashtype: Hash type.
    :type hashtype: str

    :param source: File to be hashed; foobar.ext
    :type source: str

    :param workingdir: Path containing files you wish to verify.
    :type workingdir: str

    :param block: Blocksize, in bytes.
    :type block: int

    :param target: File to write to.
    :type target: file

    :param kwargs: Values. Refer to `:func:verifier_config_loader`.
    :type kwargs: dict
    """
    if kwargs[hashtype]:
        hash_generic = [hashtype.upper()]
        hash_generic.append(hash_get(source, hashfunc, workingdir, block))
        target.write("\n".join(hash_generic))


def hash_writer(source, dest, workingdir, kwargs=None):
    """
    Write per-file hashes.

    :param source: File to be hashed; foobar.ext
    :type source: str

    :param dest: Destination file; foobar.ext.cksum
    :type dest: str

    :param workingdir: Path containing files you wish to verify.
    :type workingdir: str

    :param kwargs: Values. Refer to `:func:verifier_config_loader`.
    :type kwargs: dict
    """
    block = int(kwargs['blocksize'])
    with open(dest, 'w') as target:
        base_hash("adler32", source, workingdir, block, ha32, target, kwargs)
        base_hash("crc32", source, workingdir, block, hc32, target, kwargs)
        base_hash("md4", source, workingdir, block, hm4, target, kwargs)
        base_hash("md5", source, workingdir, block, hm5, target, kwargs)
        base_hash("sha0", source, workingdir, block, hs0, target, kwargs)
        base_hash("sha1", source, workingdir, block, hs1, target, kwargs)
        base_hash("sha224", source, workingdir, block, hs224, target, kwargs)
        base_hash("sha256", source, workingdir, block, hs256, target, kwargs)
        base_hash("sha384", source, workingdir, block, hs384, target, kwargs)
        base_hash("sha512", source, workingdir, block, hs512, target, kwargs)
        base_hash("ripemd160", source, workingdir, block, hr160, target, kwargs)
        base_hash("whirlpool", source, workingdir, block, hwp, target, kwargs)
        base_hash("sha3224", source, workingdir, block, hs3224, target, kwargs)
        base_hash("sha3256", source, workingdir, block, hs3256, target, kwargs)
        base_hash("sha3384", source, workingdir, block, hs3384, target, kwargs)
        base_hash("sha3512", source, workingdir, block, hs3512, target, kwargs)


def filefilter(file, workingdir, extras=()):
    """
    Check if file in folder is a folder, or if it's got a forbidden extension.

    :param file: File to be hashed.
    :type file: str

    :param workingdir: Path containing files you wish to verify.
    :type workingdir: str

    :param extras: Tuple of extra extensions.
    :type extras: tuple
    """
    return not (os.path.isdir(os.path.join(workingdir, file)) or file.endswith(bbconstants.SUPPS + extras))


def verifier(ldir, kwargs=None, selective=False):
    """
    For all files in a directory, perform various hash/checksum functions.
    Take dict to define hashes, write output to a/individual .cksum file(s).

    :param ldir: Path containing files you wish to verify.
    :type ldir: str

    :param kwargs: Values. Refer to `:func:verifier_config_loader`.
    :type kwargs: dict
    """
    kwargs = verifier_config_loader() if kwargs is None else kwargs
    exts = (".txt",) if selective else ()
    files = [os.path.join(ldir, file) for file in os.listdir(ldir) if filefilter(file, ldir, exts)]
    with concurrent.futures.ThreadPoolExecutor(max_workers=utilities.workers(files)) as xec:
        for file in files:
            verifier_individual(xec, ldir, file, kwargs)


def verifier_individual(xec, ldir, file, kwargs):
    """
    Individually verify files through a ThreadPoolExecutor.

    :param xec: ThreadPoolExecutor instance.
    :type xec: concurrent.futures.ThreadPoolExecutor

    :param ldir: Path containing files you wish to verify.
    :type ldir: str

    :param file: Filename.
    :type file: str

    :param kwargs: Values. Refer to `:func:verifier_config_loader`.
    :type kwargs: dict
    """
    print("HASHING:", os.path.basename(file))
    basename = file + ".cksum"
    targetname = os.path.join(ldir, basename)
    try:
        xec.submit(hash_writer, file, targetname, ldir, kwargs)
    except Exception as exc:
        exceptions.handle_exception(exc)


def gpgrunner(workingdir, keyid=None, pword=None, selective=False):
    """
    Create ASCII-armored PGP signatures for all files in a given directory, in parallel.

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
        gpgrunner_clean(gpg, workingdir, keyid, pword, selective)


def gpgrunner_clean(gpg, workingdir, keyid=None, pword=None, selective=False):
    """
    Run GPG signature generation after filtering out errors.

    :param gpg: Instance of Python GnuPG executable.
    :type gpg: gnupg.GPG()

    :param workingdir: Path containing files you wish to verify.
    :type workingdir: str

    :param keyid: Key to use. 8-character hexadecimal, with or without 0x.
    :type keyid: str

    :param pword: Passphrase for given key.
    :type pword: str

    :param selective: Filtering filenames/extensions. Default is false.
    :type selective: bool
    """
    keyid = "0x" + keyid.upper() if not keyid.startswith("0x") else keyid.upper().replace("X", "x")
    dirlist = os.listdir(workingdir)
    files = [file for file in dirlist if filefilter(file, workingdir)]
    with concurrent.futures.ThreadPoolExecutor(max_workers=utilities.workers(files)) as xec:
        for file in files:
            gpgwriter(gpg, xec, file, workingdir, selective, keyid, pword)


def gpgwriter(gpg, xec, file, workingdir, selective=False, keyid=None, pword=None):
    """
    Write individual GPG signatures.

    :param gpg: Instance of Python GnuPG executable.
    :type gpg: gnupg.GPG()

    :param xec: ThreadPoolExecutor instance.
    :type xec: concurrent.futures.ThreadPoolExecutor

    :param file: File inside workingdir that is being verified.
    :type file: str

    :param workingdir: Path containing files you wish to verify.
    :type workingdir: str

    :param selective: Filtering filenames/extensions. Default is false.
    :type selective: bool

    :param keyid: Key to use. 8-character hexadecimal, with or without 0x.
    :type keyid: str

    :param pword: Passphrase for given key.
    :type pword: str
    """
    sup = bbconstants.SUPPS + (".txt",) if selective else bbconstants.SUPPS
    if not file.endswith(sup):
        aps = bbconstants.ARCSPLUS
        pfx = bbconstants.PREFIXES
        if (utilities.prepends(file, pfx, aps)) if selective else True:
            gpgwriter_clean(gpg, xec, file, workingdir, keyid, pword)


def gpgwriter_clean(gpg, xec, file, workingdir, keyid=None, pword=None):
    """
    Write individual GPG signatures after filtering file list.

    :param gpg: Instance of Python GnuPG executable.
    :type gpg: gnupg.GPG()

    :param xec: ThreadPoolExecutor instance.
    :type xec: concurrent.futures.ThreadPoolExecutor

    :param file: File inside workingdir that is being verified.
    :type file: str

    :param workingdir: Path containing files you wish to verify.
    :type workingdir: str

    :param keyid: Key to use. 8-character hexadecimal, with or without 0x.
    :type keyid: str

    :param pword: Passphrase for given key.
    :type pword: str
    """
    print("VERIFYING:", os.path.basename(file))
    thepath = os.path.join(workingdir, file)
    try:
        xec.submit(gpgfile, thepath, gpg, keyid, pword)
    except Exception as exc:
        exceptions.handle_exception(exc)


def gpg_config_loader(homepath=None):
    """
    Read a ConfigParser file to get PGP key, password (optional)

    :param homepath: Folder containing ini file. Default is user directory.
    :type homepath: str
    """
    config = iniconfig.generic_loader('gpgrunner', homepath)
    gpgkey = config.get('key', fallback=None)
    gpgpass = config.get('pass', fallback=None)
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
    results = {}
    if key is not None:
        results["key"] = key
    if password is not None:
        results["pass"] = password
    iniconfig.generic_writer("gpgrunner", results, homepath)


def verifier_config_loader(homepath=None):
    """
    Read a ConfigParser file to get hash preferences.

    :param homepath: Folder containing ini file. Default is user directory.
    :type homepath: str
    """
    ini = iniconfig.generic_loader("hashmodes", homepath)
    results = {}
    results['crc32'] = bool(ini.getboolean('crc32', fallback=False))
    results['adler32'] = bool(ini.getboolean('adler32', fallback=False))
    results['sha0'] = bool(ini.getboolean('sha0', fallback=False))
    results['sha1'] = bool(ini.getboolean('sha1', fallback=True))
    results['sha224'] = bool(ini.getboolean('sha224', fallback=False))
    results['sha256'] = bool(ini.getboolean('sha256', fallback=True))
    results['sha384'] = bool(ini.getboolean('sha384', fallback=False))
    results['sha512'] = bool(ini.getboolean('sha512', fallback=False))
    results['md5'] = bool(ini.getboolean('md5', fallback=True))
    results['md4'] = bool(ini.getboolean('md4', fallback=False))
    results['ripemd160'] = bool(ini.getboolean('ripemd160', fallback=False))
    results['whirlpool'] = bool(ini.getboolean('whirlpool', fallback=False))
    results['blocksize'] = int(ini.getint('blocksize', fallback=16777216))
    results['sha3224'] = bool(ini.getboolean('sha3224', fallback=False))
    results['sha3256'] = bool(ini.getboolean('sha3256', fallback=False))
    results['sha3384'] = bool(ini.getboolean('sha3384', fallback=False))
    results['sha3512'] = bool(ini.getboolean('sha3512', fallback=False))
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
    results = {method: str(flag).lower() for method, flag in resultdict.items()}
    iniconfig.generic_writer("hashmodes", results, homepath)

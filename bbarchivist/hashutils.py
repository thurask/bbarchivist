#!/usr/bin/env python3
"""This module is used to generate file hashes/checksums."""

import zlib  # crc32/adler32
import hashlib  # all other hashes
import hmac  # escreens is a hmac, news at 11
import os  # path work
import concurrent.futures  # parallelization
from bbarchivist import bbconstants  # premade stuff
from bbarchivist import exceptions  # exceptions
from bbarchivist import utilities  # cores
from bbarchivist import iniconfig  # config parsing

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "2015-2017 Thurask"


def zlib_hash(filepath, method, blocksize=16 * 1024 * 1024):
    """
    Return zlib-based (i.e. CRC32/Adler32) checksum of a file.

    :param filepath: File you wish to verify.
    :type filepath: str

    :param method: "crc32" or "adler32".
    :type method: str

    :param blocksize: How much of file to read at once. Default is 16MB.
    :type blocksize: int
    """
    hashfunc, seed = zlib_handler(method)
    with open(filepath, 'rb') as file:
        for chunk in iter(lambda: file.read(blocksize), b''):
            seed = hashfunc(chunk, seed)
    final = format(seed & 0xFFFFFFFF, "08x")
    return final


def zlib_handler(method):
    """
    Prepare hash method and seed depending on CRC32/Adler32.

    :param method: "crc32" or "adler32".
    :type method: str
    """
    hashfunc = zlib.crc32 if method == "crc32" else zlib.adler32
    seed = 0 if method == "crc32" else 1
    return hashfunc, seed


def hashlib_hash(filepath, engine, blocksize=16 * 1024 * 1024):
    """
    Return MD5/SHA-1/SHA-2/SHA-3 hash of a file.

    :param filepath: File you wish to verify.
    :type filepath: str

    :param engine: Hash object to update with file contents.
    :type engine: _hashlib.HASH

    :param blocksize: How much of file to read at once. Default is 16MB.
    :type blocksize: int
    """
    hashfunc_reader(filepath, engine, blocksize)
    return engine.hexdigest()


def hashfunc_reader(filepath, engine, blocksize=16 * 1024 * 1024):
    """
    Generate hash from file contents.

    :param filepath: File you wish to verify.
    :type filepath: str

    :param engine: Hash object to update with file contents.
    :type engine: _hashlib.HASH

    :param blocksize: How much of file to read at once. Default is 16MB.
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

    :param blocksize: How much of file to read at once. Default is 16MB.
    :type blocksize: int
    """
    try:
        engine = hashlib.new(method)
        hashfunc_reader(filepath, engine, blocksize)
        return engine.hexdigest()
    except ValueError as exc:
        msg = "{0} HASH FAILED".format(method.upper())
        exceptions.handle_exception(exc, msg, None)


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
    ehmac = 'Up the time stream without a TARDIS'
    duration = int(duration)
    if duration not in [1, 3, 6, 15, 30]:
        duration = 1
    data = pin.lower() + app + str(uptime) + lifetimes[duration]
    newhmac = hmac.new(ehmac.encode(), data.encode(), digestmod=hashlib.sha1)
    key = newhmac.hexdigest()[:8]
    return key.upper()


def get_hashfunc(hashtype):
    """
    Get genericized hash function from hash type.

    :param hashtype: Hash type.
    :type hashtype: str
    """
    hashfuncs = {"adler32": zlib_hash,
                 "crc32": zlib_hash,
                 "md4": ssl_hash,
                 "sha0": ssl_hash,
                 "ripemd160": ssl_hash,
                 "whirlpool": ssl_hash,
                 "md5": hashlib_hash,
                 "sha1": hashlib_hash,
                 "sha224": hashlib_hash,
                 "sha256": hashlib_hash,
                 "sha384": hashlib_hash,
                 "sha512": hashlib_hash,
                 "sha3224": hashlib_hash,
                 "sha3256": hashlib_hash,
                 "sha3384": hashlib_hash,
                 "sha3512": hashlib_hash}
    return hashfuncs[hashtype]


def get_engine(hashtype):
    """
    Get hashlib engine from hash type.

    :param hashtype: Hash type.
    :type hashtype: str
    """
    hashengines = {"md5": hashlib.md5(),
                   "sha1": hashlib.sha1(),
                   "sha224": hashlib.sha224(),
                   "sha256": hashlib.sha256(),
                   "sha384": hashlib.sha384(),
                   "sha512": hashlib.sha512()}
    if utilities.new_enough(6):
        hashengines.update({"sha3224": hashlib.sha3_224(),
                            "sha3256": hashlib.sha3_256(),
                            "sha3384": hashlib.sha3_384(),
                            "sha3512": hashlib.sha3_512()})
    return hashengines[hashtype]


def hash_get(filename, hashfunc, hashtype, workingdir, blocksize=16777216):
    """
    Generate and pretty format the hash result for a file.

    :param filename: File to hash.
    :type filename: str

    :param hashfunc: Hash function to use.
    :type hashfunc: function

    :param hashtype: Hash type.
    :type hashtype: str

    :param workingdir: Working directory.
    :type workingdir: str

    :param blocksize: Block size. Default is 16MB.
    :type blocksize: int
    """
    if hashfunc == hashlib_hash:
        method = get_engine(hashtype)
    else:
        method = hashtype
    result = hashfunc(os.path.join(workingdir, filename), method, blocksize)
    return "{0} {1}\n".format(result.upper(), os.path.basename(filename))


def base_hash(hashtype, source, workingdir, block, target, kwargs=None):
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
        hashfunc = get_hashfunc(hashtype)
        hashtype2 = "sha" if hashtype == "sha0" else hashtype
        hash_generic.append(hash_get(source, hashfunc, hashtype2, workingdir, block))
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
        base_hash("adler32", source, workingdir, block, target, kwargs)
        base_hash("crc32", source, workingdir, block, target, kwargs)
        base_hash("md4", source, workingdir, block, target, kwargs)
        base_hash("md5", source, workingdir, block, target, kwargs)
        base_hash("sha0", source, workingdir, block, target, kwargs)
        base_hash("sha1", source, workingdir, block, target, kwargs)
        base_hash("sha224", source, workingdir, block, target, kwargs)
        base_hash("sha256", source, workingdir, block, target, kwargs)
        base_hash("sha384", source, workingdir, block, target, kwargs)
        base_hash("sha512", source, workingdir, block, target, kwargs)
        base_hash("ripemd160", source, workingdir, block, target, kwargs)
        base_hash("whirlpool", source, workingdir, block, target, kwargs)
        if utilities.new_enough(6):
            base_hash("sha3224", source, workingdir, block, target, kwargs)
            base_hash("sha3256", source, workingdir, block, target, kwargs)
            base_hash("sha3384", source, workingdir, block, target, kwargs)
            base_hash("sha3512", source, workingdir, block, target, kwargs)


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


def prep_verifier(ldir, selective=False):
    """
    Prepare files for verifier function.

    :param ldir: Path containing files you wish to verify.
    :type ldir: str

    :param selective: Filtering filenames/extensions. Default is false.
    :type selective: bool
    """
    exts = (".txt",) if selective else ()
    fxs = [os.path.join(ldir, afx) for afx in os.listdir(ldir) if filefilter(afx, ldir, exts)]
    return fxs


def verifier(ldir, kwargs=None, selective=False):
    """
    For all files in a directory, perform various hash/checksum functions.
    Take dict to define hashes, write output to a/individual .cksum file(s).

    :param ldir: Path containing files you wish to verify.
    :type ldir: str

    :param kwargs: Values. Refer to `:func:verifier_config_loader`.
    :type kwargs: dict

    :param selective: Filtering filenames/extensions. Default is false.
    :type selective: bool
    """
    kwargs = verifier_config_loader() if kwargs is None else kwargs
    fxs = prep_verifier(ldir, selective)
    with concurrent.futures.ThreadPoolExecutor(max_workers=utilities.cpu_workers(fxs)) as xec:
        for file in fxs:
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

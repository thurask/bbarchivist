#!/usr/bin/env python3

import zlib
import hashlib


def crc32hash(filepath, blocksize=16 * 1024 * 1024):
    """
    Return CRC32 checksum of a file.
    :param filepath: File you wish to verify.
    :type filepath: str
    :param blocksize: File read chunk size;
    how much of it to load into memory at a time.
    :type blocksize: int
    """
    seed = 0
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(1024), b''):
            seed = zlib.crc32(chunk, seed)
    final = format(seed & 0xFFFFFFFF, "x")
    return final


def adler32hash(filepath, blocksize=16 * 1024 * 1024):
    """
    Return Adler32 checksum of a file.
    :param filepath: File you wish to verify.
    :type filepath: str
    :param blocksize: File read chunk size;
    how much of it to load into memory at a time.
    :type blocksize: int
    """
    asum = 1
    with open(filepath, 'rb') as f:
        while True:
            data = f.read(blocksize)
            if not data:
                break
            asum = zlib.adler32(data, asum)
            if asum < 0:
                asum += 2 ** 32
    final = format(asum & 0xFFFFFFFF, "x")
    return final


def sha1hash(filepath, blocksize=16 * 1024 * 1024):
    """
    Return SHA-1 hash of a file.
    :param filepath: File you wish to verify.
    :type filepath: str
    :param blocksize: File read chunk size;
    how much of it to load into memory at a time.
    :type blocksize: int
    """
    sha1 = hashlib.sha1()
    with open(filepath, 'rb') as f:
        while True:
            data = f.read(blocksize)
            if not data:
                break
            sha1.update(data)
    return sha1.hexdigest()


def sha224hash(filepath, blocksize=16 * 1024 * 1024):
    """
    Return SHA-224 hash of a file.
    :param filepath: File you wish to verify.
    :type filepath: str
    :param blocksize: File read chunk size;
    how much of it to load into memory at a time.
    :type blocksize: int
    """
    sha224 = hashlib.sha224()
    with open(filepath, 'rb') as f:
        while True:
            data = f.read(blocksize)
            if not data:
                break
            sha224.update(data)
    return sha224.hexdigest()


def sha256hash(filepath, blocksize=16 * 1024 * 1024):
    """
    Return SHA-256 hash of a file.
    :param filepath: File you wish to verify.
    :type filepath: str
    :param blocksize: File read chunk size;
    how much of it to load into memory at a time.
    :type blocksize: int
    """
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while True:
            data = f.read(blocksize)
            if not data:
                break
            sha256.update(data)
    return sha256.hexdigest()


def sha384hash(filepath, blocksize=16 * 1024 * 1024):
    """
    Return SHA-384 hash of a file.
    :param filepath: File you wish to verify.
    :type filepath: str
    :param blocksize: File read chunk size;
    how much of it to load into memory at a time.
    :type blocksize: int
    """
    sha384 = hashlib.sha384()
    with open(filepath, 'rb') as f:
        while True:
            data = f.read(blocksize)
            if not data:
                break
            sha384.update(data)
    return sha384.hexdigest()


def sha512hash(filepath, blocksize=16 * 1024 * 1024):
    """
    Return SHA-512 hash of a file.
    :param filepath: File you wish to verify.
    :type filepath: str
    :param blocksize: File read chunk size;
    how much of it to load into memory at a time.
    :type blocksize: int
    """
    sha512 = hashlib.sha512()
    with open(filepath, 'rb') as f:
        while True:
            data = f.read(blocksize)
            if not data:
                break
            sha512.update(data)
    return sha512.hexdigest()


def md4hash(filepath, blocksize=16 * 1024 * 1024):
    """
    Return MD4 hash of a file; depends on system SSL library.
    :param filepath: File you wish to verify.
    :type filepath: str
    :param blocksize: File read chunk size;
    how much of it to load into memory at a time.
    :type blocksize: int
    """
    try:
        md4 = hashlib.new('md4')
        with open(filepath, 'rb') as f:
            while True:
                data = f.read(blocksize)
                if not data:
                    break
                md4.update(data)
        return md4.hexdigest()
    except Exception:
        print("MD4 HASH FAILED:\nIS IT AVAILABLE?")


def md5hash(filepath, blocksize=16 * 1024 * 1024):
    """
    Return MD5 hash of a file.
    :param filepath: File you wish to verify.
    :type filepath: str
    :param blocksize: File read chunk size;
    how much of it to load into memory at a time.
    :type blocksize: int
    """
    md5 = hashlib.md5()
    with open(filepath, 'rb') as f:
        while True:
            data = f.read(blocksize)
            if not data:
                break
            md5.update(data)
    return md5.hexdigest()


def ripemd160hash(filepath, blocksize=16 * 1024 * 1024):
    """
    Return RIPEMD160 hash of a file; depends on system SSL library.
    :param filepath: File you wish to verify.
    :type filepath: str
    :param blocksize: File read chunk size;
    how much of it to load into memory at a time.
    :type blocksize: int
    """
    try:
        r160 = hashlib.new('ripemd160')
        with open(filepath, 'rb') as f:
            while True:
                data = f.read(blocksize)
                if not data:
                    break
                r160.update(data)
        return r160.hexdigest()
    except Exception:
        print("RIPEMD160 HASH FAILED:\nIS IT AVAILABLE?")


def whirlpoolhash(filepath, blocksize=16 * 1024 * 1024):
    """
    Return Whirlpool hash of a file; depends on system SSL library.
    :param filepath: File you wish to verify.
    :type filepath: str
    :param blocksize: File read chunk size;
    how much of it to load into memory at a time.
    :type blocksize: int
    """
    try:
        wp = hashlib.new('whirlpool')
        with open(filepath, 'rb') as f:
            while True:
                data = f.read(blocksize)
                if not data:
                    break
                wp.update(data)
        return wp.hexdigest()
    except Exception:
        print("WHIRLPOOL HASH FAILED:\nIS IT AVAILABLE?")

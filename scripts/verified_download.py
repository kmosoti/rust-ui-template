"""Checksum-verified optional download cache; partial/corrupt entries are replaced."""
import hashlib
import os
import tempfile
import urllib.request
from pathlib import Path


def fetch(url, sha256, cache):
    cache = Path(cache)
    data = cache.read_bytes() if cache.is_file() else b''
    if hashlib.sha256(data).hexdigest() == sha256:
        return data
    with urllib.request.urlopen(url, timeout=120) as response:
        data = response.read()
    if hashlib.sha256(data).hexdigest() != sha256:
        raise RuntimeError(f'checksum mismatch: {url}')
    cache.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(dir=cache.parent, prefix=cache.name+'.')
    try:
        with os.fdopen(fd, 'wb') as output:
            output.write(data)
        os.replace(temporary, cache)
    finally:
        Path(temporary).unlink(missing_ok=True)
    return data

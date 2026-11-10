"""Verified, cached official Trunk binary for the Ubuntu x86_64 CI jobs."""
import hashlib
import io
import tarfile
import urllib.request
from pathlib import Path

URL = 'https://github.com/trunk-rs/trunk/releases/download/v0.21.14/trunk-x86_64-unknown-linux-gnu.tar.gz'
SHA256 = 'f2b4680cd239693a646a2795e4633c625328d7b2a044fbe749fa3a2fe9e7036b'
ROOT = Path(__file__).resolve().parents[1]


def main():
    archive_path = ROOT / '.tools/downloads/trunk-0.21.14.tar.gz'
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    data = archive_path.read_bytes() if archive_path.exists() else b''
    if hashlib.sha256(data).hexdigest() != SHA256:
        data = urllib.request.urlopen(URL).read()
        if hashlib.sha256(data).hexdigest() != SHA256:
            raise RuntimeError('Trunk checksum mismatch')
        archive_path.write_bytes(data)
    with tarfile.open(fileobj=io.BytesIO(data), mode='r:gz') as archive:
        member = next(m for m in archive if Path(m.name).name == 'trunk' and m.isfile())
        target = ROOT / '.tools/trunk'
        target.write_bytes(archive.extractfile(member).read())
        target.chmod(0o755)
    print('Verified official Trunk 0.21.14')


if __name__ == '__main__':
    main()

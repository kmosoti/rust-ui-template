"""Install the checksum-pinned official Tauri CLI for Linux x86_64."""
import hashlib
import io
import tarfile
import urllib.request
from pathlib import Path
from verified_download import fetch

URL = 'https://github.com/tauri-apps/tauri/releases/download/tauri-cli-v2.12.4/cargo-tauri-x86_64-unknown-linux-gnu.tgz'
SHA256 = '820ae3c7580ca637cad15f65638960ee2a96e5a491e224691c86d6f25e6c9e8a'
ROOT = Path(__file__).resolve().parents[1]
data = fetch(URL, SHA256, ROOT / '.tools/downloads/tauri-cli-2.12.4.tgz')
with tarfile.open(fileobj=io.BytesIO(data), mode='r:gz') as archive:
    member = next(m for m in archive if Path(m.name).name == 'cargo-tauri' and m.isfile())
    target = ROOT / '.tools/cargo-tauri'
    target.parent.mkdir(exist_ok=True)
    target.write_bytes(archive.extractfile(member).read())
    target.chmod(0o755)
print('Verified official Tauri CLI 2.12.4')

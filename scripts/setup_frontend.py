"""Download pinned official Tailwind and axe test assets; no Node required."""
import base64
import hashlib
import io
import json
import os
import platform
import tarfile
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / '.tools'


def main():
    manifest = json.loads((ROOT / 'scripts/tool-assets.json').read_text())
    system = {'Linux': 'linux', 'Darwin': 'macos', 'Windows': 'windows'}[platform.system()]
    arch = {'x86_64': 'x64', 'AMD64': 'x64', 'aarch64': 'arm64', 'arm64': 'arm64'}[platform.machine()]
    name = f'tailwindcss-{system}-{arch}' + ('.exe' if system == 'windows' else '')
    if system == 'linux' and (platform.libc_ver()[0] == 'musl' or any(Path('/lib').glob('ld-musl-*.so.1'))):
        name += '-musl'
    name = os.environ.get('TAILWIND_TARGET', name)
    asset = manifest['tailwind'][name]
    DEST.mkdir(exist_ok=True)
    target = DEST / ('tailwindcss.exe' if system == 'windows' else 'tailwindcss')
    if not target.exists() or hashlib.sha256(target.read_bytes()).hexdigest() != asset['sha256']:
        data = urllib.request.urlopen(asset['url']).read()
        if hashlib.sha256(data).hexdigest() != asset['sha256']:
            raise RuntimeError('Tailwind checksum mismatch')
        target.write_bytes(data)
    target.chmod(0o755)
    axe = manifest['axe']
    data = urllib.request.urlopen(axe['url']).read()
    if 'sha512-' + base64.b64encode(hashlib.sha512(data).digest()).decode() != axe['integrity']:
        raise RuntimeError('axe checksum mismatch')
    with tarfile.open(fileobj=io.BytesIO(data), mode='r:gz') as archive:
        for source, output in [('package/axe.min.js', 'axe.min.js'), ('package/LICENSE', 'axe-LICENSE')]:
            (DEST / output).write_bytes(archive.extractfile(source).read())
    print(f'Verified Tailwind 4.3.4 ({name}) and axe-core {axe["version"]}')


if __name__ == '__main__':
    main()

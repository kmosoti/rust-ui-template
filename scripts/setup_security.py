"""Pinned official Linux x86_64 security tools, sharing verified download setup."""
import io
import json
import platform
import tarfile
from pathlib import Path
from verified_download import fetch

ROOT = Path(__file__).resolve().parents[1]


def main():
    if platform.system() != 'Linux' or platform.machine() != 'x86_64':
        raise SystemExit('Security binary setup is validated only on Linux x86_64')
    for name, asset in json.loads((ROOT/'scripts/security-assets.json').read_text()).items():
        data = fetch(asset['url'], asset['sha256'], ROOT/'.tools/downloads'/asset['archive'])
        if asset.get('member'):
            with tarfile.open(fileobj=io.BytesIO(data), mode='r:gz') as archive:
                member = next(m for m in archive if m.isfile() and Path(m.name).name == asset['member'])
                data = archive.extractfile(member).read()
        target = ROOT/'.tools'/name
        target.write_bytes(data)
        target.chmod(0o755)
        print(f'Verified {name} {asset["version"]}')


if __name__ == '__main__':
    main()

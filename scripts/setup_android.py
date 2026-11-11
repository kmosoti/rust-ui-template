"""Install checksum-pinned Android SDK archives; reruns verify installed bytes.

Linux x86_64 only. ZIP extraction uses unzip to preserve the NDK's Unix symlinks.
No signing keys or writable emulator state belong in these directories/caches.
"""
import argparse
import hashlib
import json
import os
import platform
from pathlib import Path
import shutil
import subprocess
import tempfile
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    with path.open('rb') as source:
        return hashlib.file_digest(source, 'sha256').hexdigest()


def installed_digest(directory):
    """Hash names, executable modes, symlink destinations and file contents."""
    result = hashlib.sha256()
    for path in sorted(directory.rglob('*')):
        if path.name in ('.verified.json', 'package.xml') or (path.is_dir() and not path.is_symlink()):
            continue
        result.update(str(path.relative_to(directory)).encode() + b'\0')
        result.update(str(path.lstat().st_mode & 0o777).encode() + b'\0')
        result.update(os.readlink(path).encode() if path.is_symlink() else bytes.fromhex(digest(path)))
    return result.hexdigest()


def install(identifier, asset, sdk, downloads):
    destination = sdk / asset['destination']
    marker = destination / '.verified.json'
    metadata = asset['metadata_xml'].replace('<localPackage ', (ROOT / 'scripts/android-sdk-license.xml').read_text() + '<localPackage ', 1)
    if marker.exists():
        try:
            saved = json.loads(marker.read_text())
        except (OSError, ValueError):
            saved = {}
        if saved.get('archive') == asset['sha256'] and saved.get('tree') == installed_digest(destination):
            (destination / 'package.xml').write_text(metadata)
            print('Verified installed', identifier, flush=True)
            return
    archive = downloads / asset['url'].rsplit('/', 1)[1]
    if not archive.exists() or digest(archive) != asset['sha256']:
        partial = archive.with_suffix('.partial')
        with urllib.request.urlopen(asset['url']) as source, partial.open('wb') as target:
            shutil.copyfileobj(source, target)
        if digest(partial) != asset['sha256']:
            raise RuntimeError('Android archive checksum mismatch: ' + identifier)
        partial.replace(archive)
    with tempfile.TemporaryDirectory(dir=downloads) as temporary:
        temporary = Path(temporary)
        with zipfile.ZipFile(archive) as zipped:
            if any(Path(name).is_absolute() or '..' in Path(name).parts for name in zipped.namelist()):
                raise RuntimeError('Unsafe Android archive path')
        subprocess.run(['unzip', '-q', str(archive), '-d', str(temporary)], check=True)
        candidates = [p for p in temporary.iterdir() if p.is_dir()]
        if len(candidates) != 1:
            raise RuntimeError('Unexpected Android archive layout: ' + identifier)
        fresh = candidates[0]
        (fresh / 'package.xml').write_text(metadata)
        (fresh / '.verified.json').write_text(json.dumps({'archive': asset['sha256'], 'tree': installed_digest(fresh)}))
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists():
            # Keep old contents until verified replacement is ready; do not merge trees.
            backup = temporary / 'previous-install'
            destination.rename(backup)
        fresh.rename(destination)
    print('Installed verified', identifier, flush=True)


def main():
    if platform.system() != "Linux" or platform.machine() not in ("x86_64", "AMD64"):
        raise SystemExit("Pinned Android build tools require Linux x86_64")
    parser = argparse.ArgumentParser()
    parser.add_argument('--emulator', action='store_true')
    args = parser.parse_args()
    manifest = json.loads((ROOT / 'scripts/android-assets.json').read_text())
    sdk = ROOT / '.tools/android-sdk'
    downloads = ROOT / '.tools/android-downloads'
    downloads.mkdir(parents=True, exist_ok=True)
    for identifier, asset in manifest.items():
        if not asset['emulator_only'] or args.emulator:
            install(identifier, asset, sdk, downloads)
    variables = {'ANDROID_HOME': str(sdk), 'ANDROID_SDK_ROOT': str(sdk), 'NDK_HOME': str(sdk / 'ndk/29.0.14206865')}
    for name, value in variables.items():
        print(f'{name}={value}')
    if os.environ.get('GITHUB_ENV'):
        with open(os.environ['GITHUB_ENV'], 'a') as target:
            target.write(''.join(f'{name}={value}\n' for name, value in variables.items()))
        with open(os.environ['GITHUB_PATH'], 'a') as target:
            target.write(f'{sdk}/cmdline-tools/19.0/bin\n{sdk}/platform-tools\n{sdk}/emulator\n')


if __name__ == '__main__':
    main()

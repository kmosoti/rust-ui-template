"""Validate installed package-owned desktop metadata, without launching as root."""
import argparse
import configparser
from pathlib import Path
import shlex
import shutil
import subprocess


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--format', choices=['deb', 'rpm'], required=True)
    args = parser.parse_args()
    command = ['dpkg-query', '-L', 'rust-ui-template'] if args.format == 'deb' else ['rpm', '-ql', 'rust-ui-template']
    files = subprocess.check_output(command, text=True).splitlines()
    entries = [Path(p) for p in files if p.endswith('.desktop')]
    assert len(entries) == 1, entries
    subprocess.run(['desktop-file-validate', str(entries[0])], check=True)
    config = configparser.ConfigParser(interpolation=None)
    config.read(entries[0])
    entry = config['Desktop Entry']
    assert entry['Type'] == 'Application'
    executable = shlex.split(entry['Exec'])[0]
    assert Path(shutil.which(executable) or executable).resolve() == Path('/usr/bin/rust-ui-native')
    assert Path('/usr/bin/rust-ui-native').is_file()
    icon = entry['Icon']
    assert any(Path(p).stem == icon and Path(p).suffix == '.png' and Path(p).is_file() for p in files), icon
    print('PASS: installed executable, valid desktop entry and package-owned icon')


if __name__ == '__main__':
    main()

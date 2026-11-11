"""Validate bounded maintenance exceptions and exercise actual license rejection."""
import datetime
import json
import subprocess
import tempfile
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def check_expiry(exceptions, today):
    seen = set()
    for exception in exceptions:
        if exception['id'] in seen:
            raise ValueError('Duplicate advisory exception')
        seen.add(exception['id'])
        if exception['kind'] != 'unmaintained' or not exception['reason'].strip():
            raise ValueError('Only justified maintenance exceptions are approved')
        if datetime.date.fromisoformat(exception['expires']) <= today:
            raise ValueError(f'Expired exception: {exception["id"]}')
    return seen


def main():
    exceptions = json.loads((ROOT/'security-exceptions.json').read_text())
    ids = check_expiry(exceptions, datetime.date.today())
    config = tomllib.loads((ROOT/'deny.toml').read_text())
    if set(row['id'] for row in config['advisories']['ignore']) != ids:
        raise ValueError('cargo-deny exceptions differ from expiry-checked inventory')
    with tempfile.TemporaryDirectory(prefix='rust-ui-license-negative-') as directory:
        fixture = Path(directory)
        (fixture/'src').mkdir()
        (fixture/'src/lib.rs').write_text('pub fn fixture() {}\n')
        (fixture/'Cargo.toml').write_text('[package]\nname="forbidden-license-fixture"\nversion="0.1.0"\nedition="2024"\nlicense="MPL-2.0"\n[workspace]\n')
        subprocess.run(['cargo', 'generate-lockfile', '--manifest-path', str(fixture/'Cargo.toml'), '--offline'], check=True)
        result = subprocess.run([str(ROOT/'.tools/cargo-deny'), '--manifest-path', str(fixture/'Cargo.toml'), '--config', str(ROOT/'deny.toml'), '--locked', 'check', 'licenses'], capture_output=True, text=True)
        if result.returncode == 0 or ('error[rejected]' not in result.stderr or 'MPL-2.0' not in result.stderr):
            raise RuntimeError('Actual MPL rejection check failed: '+result.stderr)
    print('Maintenance exceptions unexpired; actual MPL-only fixture rejected.')


if __name__ == '__main__':
    main()

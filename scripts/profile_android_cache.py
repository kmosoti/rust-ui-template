"""Observe non-overlapping Android cache roots without reading file contents."""
import argparse
import json
import os
import stat
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def measure(directory):
    totals = {'apparent_bytes': 0, 'allocated_bytes': 0, 'files': 0, 'symlinks': 0, 'errors': []}
    seen = set()
    pending = [Path(directory)]
    while pending:
        path = pending.pop()
        try:
            info = path.lstat()
            if stat.S_ISLNK(info.st_mode):
                totals['symlinks'] += 1
                continue  # Never count a linked SDK/tool tree a second time.
            if stat.S_ISDIR(info.st_mode):
                pending.extend(path.iterdir())
            elif stat.S_ISREG(info.st_mode):
                identity = (info.st_dev, info.st_ino)
                if identity in seen:
                    continue
                seen.add(identity)
                totals['files'] += 1
                totals['apparent_bytes'] += info.st_size
                totals['allocated_bytes'] += info.st_blocks * 512
        except FileNotFoundError:
            if path != Path(directory):
                totals['errors'].append(str(path))
        except OSError as error:
            totals['errors'].append(f'{path}: {type(error).__name__}')
    return totals


def profile_bucket(directory):
    directory = Path(directory)
    summary = measure(directory)
    # A symlink root must not be followed for the child breakdown either.
    children = sorted(directory.iterdir()) if not directory.is_symlink() and directory.is_dir() else []
    summary['children'] = {child.name: measure(child) for child in children}
    return summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--phase', choices=['restored', 'ready-to-save'], required=True)
    args = parser.parse_args()
    home = Path.home()
    roots = {
        'sdk': ROOT/'.tools/android-sdk',
        'cargo-registry': home/'.cargo/registry',
        'cargo-git': home/'.cargo/git/db',
        'trunk-tools': home/'.cache/trunk',
        'tool-archives': ROOT/'.tools/downloads',
        'gradle-cache': home/'.gradle/caches',
        'gradle-wrapper': home/'.gradle/wrapper/dists',
        'frontend-target': ROOT/'target',
        'native-target': ROOT/'apps/native/target',
    }
    started = time.monotonic()
    buckets = {}
    for name, directory in roots.items():
        buckets[name] = profile_bucket(directory)
    output = ROOT/'artifacts/android-cache'
    output.mkdir(parents=True, exist_ok=True)
    result = {
        'phase': args.phase, 'source': os.environ.get('GITHUB_SHA'),
        'runner_image': {'os': os.environ.get('ImageOS'), 'version': os.environ.get('ImageVersion')},
        'cache_hit': os.environ.get('ANDROID_CACHE_HIT', ''),
        'cache_matched_key': os.environ.get('ANDROID_CACHE_MATCHED_KEY', ''),
        'cache_key': os.environ.get('ANDROID_CACHE_KEY', ''),
        'components': json.loads(os.environ.get('ANDROID_CACHE_COMPONENTS', '{}')),
        'forced_cold': os.environ.get('ANDROID_CACHE_COLD') == 'true',
        'measurement_seconds': time.monotonic()-started, 'buckets': buckets,
        'apparent_bytes': sum(b['apparent_bytes'] for b in buckets.values()),
        'allocated_bytes': sum(b['allocated_bytes'] for b in buckets.values()),
    }
    (output/(args.phase+'.json')).write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({k: result[k] for k in ('phase', 'source', 'cache_hit', 'forced_cold', 'apparent_bytes', 'allocated_bytes', 'measurement_seconds')}))
    if any(bucket['errors'] or any(child['errors'] for child in bucket['children'].values()) for bucket in buckets.values()):
        raise SystemExit('Cache measurement incomplete; inspect recorded errors')


if __name__ == '__main__':
    main()

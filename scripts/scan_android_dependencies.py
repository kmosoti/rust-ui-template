"""Scan every committed Gradle lock without relying on custom filename discovery."""
import hashlib
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    files = subprocess.check_output(['git', 'ls-files', '-z', 'apps/native/gen/android'], cwd=ROOT).decode().split('\0')
    locks = sorted(ROOT/name for name in files if name.endswith('.lockfile'))
    if len(locks) < 4:
        raise RuntimeError('Expected app, Tauri, buildscript and buildSrc Gradle locks')
    output = ROOT/'artifacts/security'
    output.mkdir(parents=True, exist_ok=True)
    manifest = [{'path': str(p.relative_to(ROOT)), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for p in locks]
    (output/'gradle-lock-manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    with tempfile.TemporaryDirectory(prefix='rust-ui-osv-') as directory:
        args = [str(ROOT/'.tools/osv-scanner'), 'scan', 'source', '--no-resolve', '--all-packages', '--licenses=', '--format', 'json', '--output-file', str(output/'gradle-osv.json')]
        sources = {}
        for index, lock in enumerate(locks):
            target = Path(directory)/str(index)/'gradle.lockfile'
            target.parent.mkdir()
            shutil.copyfile(lock, target)  # identical bytes, scanner's supported filename
            sources[str(target)] = str(lock.relative_to(ROOT))
            args.extend(['--lockfile', str(target)])
        result = subprocess.run(args, cwd=ROOT)
        report_path = output/'gradle-osv.json'
        inventory = {}
        if report_path.exists():
            report = json.loads(report_path.read_text())
            for entry in report.get('results', []):
                original = sources.get(entry['source']['path'], entry['source']['path'])
                entry['source']['path'] = original
                for package in entry.get('packages', []):
                    info = package['package']
                    key = (info['ecosystem'], info['name'], info['version'])
                    row = inventory.setdefault(key, {**info, 'licenses': package.get('licenses') or ['UNKNOWN'], 'locks': []})
                    row['locks'].append(original)
            report_path.write_text(json.dumps(report, indent=2)+'\n')
        if not inventory:
            raise RuntimeError('Scanner produced no dependency inventory')
        (output/'gradle-licenses.json').write_text(json.dumps(list(inventory.values()), indent=2)+'\n')
        print(f'Scanned {len(locks)} Gradle locks; inventoried {len(inventory)} versions (UNKNOWN is not license approval).')
        if result.returncode:
            raise SystemExit(result.returncode)


if __name__ == '__main__':
    main()

"""Build/test independent clean checkouts; compare exact production asset bytes."""
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT/'artifacts/frontend-repro'


def run(args, directory, env, label, report):
    started = time.monotonic()
    with (OUTPUT/(label+'.log')).open('w') as log:
        result = subprocess.run(args, cwd=directory, env=env, stdout=log, stderr=subprocess.STDOUT)
    report['commands'].append({'command': args, 'checkout': directory.name, 'seconds': time.monotonic()-started, 'exit_code': result.returncode})
    (OUTPUT/'report.json').write_text(json.dumps(report, indent=2)+'\n')
    if result.returncode:
        raise RuntimeError(f'{label} failed; inspect {OUTPUT/(label+".log")}')


def assets(directory):
    return {str(p.relative_to(directory)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(directory.rglob('*')) if p.is_file()}


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    epoch = subprocess.check_output(['git', 'show', '-s', '--format=%ct', revision], cwd=ROOT, text=True).strip()
    report = {'source': revision, 'source_date_epoch': epoch, 'commands': [], 'build_cache': 'none; independent empty targets', 'registry_cache': 'source downloads may be reused', 'signing': 'not tested'}
    manifests = []
    with tempfile.TemporaryDirectory(prefix='rust-ui-clean-') as temporary:
        for iteration in ('first', 'second'):
            checkout = Path(temporary)/iteration
            subprocess.run(['git', 'clone', '--quiet', '--no-hardlinks', str(ROOT), str(checkout)], check=True)
            subprocess.run(['git', 'checkout', '--quiet', '--detach', revision], cwd=checkout, check=True)
            env = os.environ.copy()
            env.update(NO_COLOR='false', CARGO_INCREMENTAL='0', CARGO_BUILD_JOBS='2', CARGO_PROFILE_DEV_DEBUG='0', CARGO_PROFILE_TEST_DEBUG='0', SOURCE_DATE_EPOCH=epoch, CARGO_TARGET_DIR=str(checkout/'target'))
            env['RUSTFLAGS'] = f'--remap-path-prefix={checkout}=/source'
            env['PATH'] = str(checkout/'.tools')+os.pathsep+env['PATH']
            steps = [
                ('toolchain', ['rustc', '--version', '--verbose']),
                ('trunk-setup', ['python3', 'scripts/setup_ci_tools.py']),
                ('frontend-setup', ['python3', 'scripts/setup_frontend.py']),
                ('fetch', ['cargo', 'fetch', '--locked']),
                ('css', ['.tools/tailwindcss', '-i', 'styles/input.css', '-o', 'styles/generated.css', '--minify']),
                ('css-check', ['python3', 'scripts/check_css.py']),
                ('production', ['.tools/trunk', 'build', '--release', '--locked']),
            ]
            for label, command in steps:
                run(command, checkout, env, iteration+'-'+label, report)
            manifests.append(assets(checkout/'dist'))
            if iteration == 'first':
                run(['cargo', 'test', '--workspace', '--locked', '--offline'], checkout, env, 'fresh-tests', report)
                run(['.tools/trunk', 'build', '--release', '--locked', '--public-url', '/sub/', '--dist', 'dist/sub'], checkout, env, 'fresh-subpath', report)
                run(['cargo', 'run', '-p', 'browser-tests', '--locked', '--offline'], checkout, env, 'fresh-browser', report)
                shutil.copytree(checkout/'artifacts', OUTPUT/'browser', dirs_exist_ok=True)
            run(['git', 'diff', '--exit-code'], checkout, env, iteration+'-source-drift', report)
            # Avoid keeping two full clean target trees on the runner.
            shutil.rmtree(checkout)
    report['manifests'] = manifests
    report['identical'] = manifests[0] == manifests[1] and bool(manifests[0])
    (OUTPUT/'report.json').write_text(json.dumps(report, indent=2)+'\n')
    if not report['identical']:
        raise RuntimeError('Independent production assets differ; inspect report.json')
    print(f'Independent production assets identical: {len(manifests[0])} files; fresh workspace/browser tests passed.')


if __name__ == '__main__':
    main()

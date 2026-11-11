"""Check compatibility boundaries in actual workflow keys (stdlib fixtures only).

This interprets hashFiles path selections, not the GitHub expression engine.
Hosted profiles separately establish restore/matched-key behavior.
"""
import glob
import hashlib
from pathlib import Path
import re
import tempfile
import unittest

WORKFLOW = Path(__file__).resolve().parents[1]/'.github/workflows/android.yml'


def configurations(text):
    result = {}
    for block in re.split(r'(?m)^      - uses: actions/cache/restore@', text)[1:]:
        name = re.search(r'(?m)^        id: (\S+)$', block).group(1)
        result[name] = {field: match.group(1) for field in ('key', 'restore-keys') if (match := re.search(r'(?m)^          '+field+r': (.+)$', block))}
    return result


def selected_hash(expression, root):
    paths = set()
    for pattern in re.findall(r"'([^']+)'", expression):
        paths.update(Path(p) for p in glob.glob(str(root/pattern), recursive=True, include_hidden=True) if Path(p).is_file())
    if not paths:
        return ''
    digest = hashlib.sha256()
    for path in sorted(paths):
        digest.update(hashlib.sha256(path.read_bytes()).digest())
    return digest.hexdigest()


def expand_hashes(template, root):
    return re.sub(r'\$\{\{ hashFiles\((.*?)\) \}\}', lambda m: selected_hash(m.group(1), root), template)


class AndroidCacheCompatibilityTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(); self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.workflow = WORKFLOW.read_text()
        self.config = configurations(self.workflow)
        self.write('.github/workflows/android.yml', self.workflow.encode())
        for name in ('Cargo.lock', 'apps/native/Cargo.lock', 'apps/native/gen/android/app/gradle.lockfile', 'apps/native/gen/android/gradle/verification-metadata.xml', 'scripts/setup_android.py', 'scripts/android-assets.json', 'scripts/tool-assets.json', 'scripts/setup_frontend.py', 'vendor/wry/src/lib.rs', 'crates/app-ui/Cargo.toml', 'Cargo.toml', 'apps/native/Cargo.toml'):
            self.write(name, b'fixture baseline')

    def write(self, name, value):
        path = self.root/name; path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(value)

    def key(self, name, field='key'):
        return expand_hashes(self.config[name][field], self.root)

    def test_lock_only_changes_preserve_compatible_prefixes_and_sdk_identity(self):
        for name in ('Cargo.lock', 'apps/native/Cargo.lock', 'apps/native/gen/android/app/gradle.lockfile', 'apps/native/gen/android/gradle/verification-metadata.xml'):
            with self.subTest(name=name):
                before = {n: (self.key(n), self.key(n, 'restore-keys')) for n in ('dependency-cache', 'target-cache')}
                sdk = self.key('sdk-cache')
                self.write(name, b'fixture changed lock bytes')
                self.assertEqual(sdk, self.key('sdk-cache'))
                for n, (primary, prefix) in before.items():
                    self.assertEqual(prefix, self.key(n, 'restore-keys'))
                    self.assertNotEqual(primary, self.key(n))
                    self.assertTrue(self.key(n).startswith(prefix))
                self.write(name, b'fixture baseline')

    def test_sdk_and_external_linker_inputs_invalidate_compatibility(self):
        for name in ('scripts/android-assets.json', 'scripts/setup_android.py'):
            with self.subTest(name=name):
                before = {n: self.key(n, 'restore-keys') for n in ('dependency-cache', 'target-cache')}
                sdk = self.key('sdk-cache')
                self.write(name, b'changed installation identity')
                self.assertNotEqual(sdk, self.key('sdk-cache'))
                for n, prefix in before.items():
                    self.assertNotEqual(prefix, self.key(n, 'restore-keys'))
                self.write(name, b'fixture baseline')

    def test_tool_setup_changes_preserve_sdk_but_invalidate_build_reuse(self):
        for name in ('scripts/tool-assets.json', 'scripts/setup_frontend.py'):
            with self.subTest(name=name):
                sdk = self.key('sdk-cache')
                before = {n: self.key(n, 'restore-keys') for n in ('dependency-cache', 'target-cache')}
                self.write(name, b'changed pinned tool/setup identity')
                self.assertEqual(sdk, self.key('sdk-cache'))
                for n, prefix in before.items():
                    self.assertNotEqual(prefix, self.key(n, 'restore-keys'))
                self.write(name, b'fixture baseline')

    def test_vendor_manifest_and_workflow_flags_invalidate_compiled_fallback(self):
        for name in ('vendor/wry/src/lib.rs', 'apps/native/Cargo.toml', 'crates/app-ui/Cargo.toml', '.github/workflows/android.yml'):
            with self.subTest(name=name):
                before = self.key('target-cache', 'restore-keys')
                original = (self.root/name).read_bytes()
                self.write(name, original+b' changed build input')
                self.assertNotEqual(before, self.key('target-cache', 'restore-keys'))
                self.write(name, original)

    def test_sdk_is_exact_and_component_namespaces_cannot_overlap(self):
        self.assertNotIn('restore-keys', self.config['sdk-cache'])
        sdk = self.key('sdk-cache')
        for name in ('dependency-cache', 'target-cache'):
            prefix = self.key(name, 'restore-keys')
            self.assertFalse(sdk.startswith(prefix))
            self.assertIn("ci-cache-stale", self.config[name]['key'])
            self.assertIn("!contains(github.event.pull_request.labels.*.name, 'ci-cache-cold')", self.config[name]['key'])

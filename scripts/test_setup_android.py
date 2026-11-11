import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

import setup_android


class AndroidSetupTests(unittest.TestCase):
    def test_repeat_and_corrupt_install_converge_from_verified_archive(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'scripts').mkdir()
            (root / 'scripts/android-sdk-license.xml').write_text('<license id="test">test</license>')
            archive = root / 'sdk.zip'
            with zipfile.ZipFile(archive, 'w') as zipped:
                zipped.writestr('sdk/source.properties', 'Pkg.Revision=1')
                zipped.writestr('sdk/bin/tool', 'expected')
            downloads = root / 'downloads'
            downloads.mkdir()
            asset = {'url': archive.as_uri(), 'sha256': hashlib.sha256(archive.read_bytes()).hexdigest(), 'destination': 'example', 'metadata_xml': '<repository><localPackage path="example"/></repository>'}
            with patch.object(setup_android, 'ROOT', root):
                setup_android.install('example', asset, root / 'sdk', downloads)
                with patch('urllib.request.urlopen', side_effect=AssertionError('warm setup must not download')):
                    setup_android.install('example', asset, root / 'sdk', downloads)
                    (root / 'sdk/example/bin/tool').write_text('tampered')
                    setup_android.install('example', asset, root / 'sdk', downloads)
                self.assertEqual('expected', (root / 'sdk/example/bin/tool').read_text())
                (root / 'sdk/example/.verified.json').write_text('broken JSON')
                setup_android.install('example', asset, root / 'sdk', downloads)
                (root / 'sdk/example/.verified.json').write_text('[]')
                setup_android.install('example', asset, root / 'sdk', downloads)
                (downloads / 'sdk.zip').write_bytes(b'corrupt archive')
                (root / 'sdk/example/bin/tool').write_text('tampered')
                setup_android.install('example', asset, root / 'sdk', downloads)
                self.assertEqual('expected', (root / 'sdk/example/bin/tool').read_text())

    def test_wrong_hash_never_replaces_existing_install(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'scripts').mkdir()
            (root / 'scripts/android-sdk-license.xml').write_text('<license/>')
            archive = root / 'sdk.zip'
            archive.write_bytes(b'wrong bytes')
            downloads = root / 'downloads'
            downloads.mkdir()
            destination = root / 'sdk/example'
            destination.mkdir(parents=True)
            (destination / 'keep').write_text('original')
            asset = {'url': archive.as_uri(), 'sha256': '0'*64, 'destination': 'example', 'metadata_xml': '<localPackage path="example"/>'}
            with patch.object(setup_android, 'ROOT', root), self.assertRaisesRegex(RuntimeError, 'checksum mismatch'):
                setup_android.install('example', asset, root / 'sdk', downloads)
            self.assertEqual('original', (destination / 'keep').read_text())


if __name__ == '__main__':
    unittest.main()

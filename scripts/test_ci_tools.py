"""Executable cache integrity regressions; all downloads are local mock archives."""
import hashlib
import io
from pathlib import Path
import tarfile
import tempfile
import unittest
from unittest.mock import patch

import setup_ci_tools


def archive_bytes():
    data = io.BytesIO()
    with tarfile.open(fileobj=data, mode='w:gz') as archive:
        member = tarfile.TarInfo('trunk')
        member.size = len(b'verified tool')
        archive.addfile(member, io.BytesIO(b'verified tool'))
    return data.getvalue()


class ToolCacheTests(unittest.TestCase):
    def test_verified_archive_is_reused_and_binary_is_reextracted(self):
        data = archive_bytes()
        with tempfile.TemporaryDirectory() as temporary, patch.object(setup_ci_tools, 'ROOT', Path(temporary)), patch.object(setup_ci_tools, 'SHA256', hashlib.sha256(data).hexdigest()), patch('setup_ci_tools.urllib.request.urlopen', return_value=io.BytesIO(data)) as download:
            setup_ci_tools.main()
            (Path(temporary) / '.tools/trunk').write_bytes(b'tampered binary')
            setup_ci_tools.main()
            self.assertEqual(download.call_count, 1)
            self.assertEqual((Path(temporary) / '.tools/trunk').read_bytes(), b'verified tool')

    def test_corrupt_cached_archive_is_replaced_from_verified_download(self):
        data = archive_bytes()
        with tempfile.TemporaryDirectory() as temporary, patch.object(setup_ci_tools, 'ROOT', Path(temporary)), patch.object(setup_ci_tools, 'SHA256', hashlib.sha256(data).hexdigest()), patch('setup_ci_tools.urllib.request.urlopen', return_value=io.BytesIO(data)) as download:
            archive = Path(temporary) / '.tools/downloads/trunk-0.21.14.tar.gz'
            archive.parent.mkdir(parents=True)
            archive.write_bytes(b'corrupt')
            setup_ci_tools.main()
            download.assert_called_once()
            self.assertEqual(archive.read_bytes(), data)

    def test_unverified_download_is_never_installed(self):
        with tempfile.TemporaryDirectory() as temporary, patch.object(setup_ci_tools, 'ROOT', Path(temporary)), patch('setup_ci_tools.urllib.request.urlopen', return_value=io.BytesIO(b'unverified')):
            with self.assertRaisesRegex(RuntimeError, 'checksum mismatch'):
                setup_ci_tools.main()
            self.assertFalse((Path(temporary) / '.tools/trunk').exists())


if __name__ == '__main__':
    unittest.main()

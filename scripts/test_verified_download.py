import hashlib
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from verified_download import fetch


class VerifiedDownloadTests(unittest.TestCase):
    def test_cold_warm_and_corrupt_cache(self):
        good = b'verified artifact'
        digest = hashlib.sha256(good).hexdigest()
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)/'nested/archive'
            with patch('urllib.request.urlopen', return_value=io.BytesIO(good)) as network:
                self.assertEqual(fetch('https://example.invalid/tool', digest, target), good)
                self.assertEqual(fetch('https://example.invalid/tool', digest, target), good)
                self.assertEqual(network.call_count, 1)
            target.write_bytes(b'partial')
            with patch('urllib.request.urlopen', return_value=io.BytesIO(good)):
                self.assertEqual(fetch('https://example.invalid/tool', digest, target), good)
            self.assertEqual(target.read_bytes(), good)

    def test_rejected_download_never_replaces_cached_file(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)/'archive'
            target.write_bytes(b'old invalid data')
            with patch('urllib.request.urlopen', return_value=io.BytesIO(b'untrusted')):
                with self.assertRaisesRegex(RuntimeError, 'checksum mismatch'):
                    fetch('https://example.invalid/tool', hashlib.sha256(b'expected').hexdigest(), target)
            self.assertEqual(target.read_bytes(), b'old invalid data')
            self.assertEqual(list(Path(directory).iterdir()), [target])

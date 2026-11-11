import os
import json
from unittest.mock import patch
import profile_android_cache
from pathlib import Path
import tempfile
import unittest
from profile_android_cache import measure, profile_bucket


class CacheSizeTests(unittest.TestCase):
    def test_no_symlink_traversal_and_no_hardlink_double_count(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            tree = root/'cache'; tree.mkdir()
            (tree/'one').write_bytes(b'abc')
            os.link(tree/'one', tree/'two')
            (root/'outside').write_bytes(b'x'*100)
            (tree/'external').symlink_to(root/'outside')
            result = measure(tree)
            self.assertEqual((result['files'], result['symlinks'], result['apparent_bytes']), (1, 1, 3))
            self.assertEqual(result['errors'], [])

    def test_symlink_root_has_no_child_breakdown(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root/'real').mkdir()
            (root/'real/data').write_bytes(b'outside')
            (root/'linked').symlink_to(root/'real', target_is_directory=True)
            result = profile_bucket(root/'linked')
            self.assertEqual(result['symlinks'], 1)
            self.assertEqual(result['files'], 0)
            self.assertEqual(result['children'], {})

    def test_sparse_apparent_and_allocated_sizes_are_distinct(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/'sparse'
            with path.open('wb') as output:
                output.truncate(4*1024*1024)
            result = measure(folder)
            self.assertEqual(result['apparent_bytes'], 4*1024*1024)
            self.assertLess(result['allocated_bytes'], result['apparent_bytes'])
        self.assertEqual(measure(path)['files'], 0)


class CacheMetadataTests(unittest.TestCase):
    def test_fallback_is_distinct_from_cold_miss_in_saved_profile(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            environment = {'ANDROID_CACHE_HIT':'false', 'ANDROID_CACHE_KEY':'compatible-new-lock', 'ANDROID_CACHE_MATCHED_KEY':'compatible-old-lock'}
            with patch.object(profile_android_cache, 'ROOT', root), patch('pathlib.Path.home', return_value=root/'home'), patch.dict(os.environ, environment, clear=True), patch('sys.argv', ['profile', '--phase', 'restored']):
                profile_android_cache.main()
            result = json.loads((root/'artifacts/android-cache/restored.json').read_text())
            self.assertEqual(result['cache_hit'], 'false')
            self.assertNotEqual(result['cache_matched_key'], result['cache_key'])
            self.assertEqual(result['cache_matched_key'], 'compatible-old-lock')

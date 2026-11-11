"""Do not confuse an instrumentation process exit with a passing UI test."""
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import android_smoke


class AndroidResultTests(unittest.TestCase):
    def run_report(self, report):
        def device(*args, **kwargs):
            if args[:3] == ('shell', 'am', 'instrument'):
                return report
            if args[:3] == ('shell', 'am', 'force-stop'):
                raise RuntimeError('cleanup failed')
            return 'Success'
        with tempfile.TemporaryDirectory() as folder:
            with patch('sys.argv', ['android_smoke.py', '--apk', 'app.apk', '--test-apk', 'test.apk']), \
                 patch('android_smoke.Path', side_effect=lambda name: Path(folder) / name), \
                 patch('android_smoke.adb', side_effect=device), \
                 patch('android_smoke.subprocess.run', side_effect=subprocess.CalledProcessError(1, 'diagnostic')):
                android_smoke.main()

    def test_process_crash_is_not_success_and_survives_cleanup_failure(self):
        with self.assertRaisesRegex(RuntimeError, 'one passing test'):
            self.run_report('INSTRUMENTATION_RESULT: shortMsg=Process crashed.\nINSTRUMENTATION_CODE: 0')

    def test_cleanup_failure_after_success_is_reported(self):
        with self.assertRaisesRegex(RuntimeError, 'cleanup failed'):
            self.run_report('OK (1 test)\nINSTRUMENTATION_CODE: -1')


if __name__ == '__main__':
    unittest.main()

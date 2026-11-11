"""Desktop requests reach the shared native verifier without changing settings."""
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

import desktop_evidence


class DesktopScaleTests(unittest.TestCase):
    def test_expected_dpr_is_forwarded_and_recorded_without_renderer_override(self):
        child = Mock(); child.wait.return_value = 0
        with tempfile.TemporaryDirectory() as directory:
            previous = Path.cwd()
            try:
                os.chdir(directory)
                with patch.dict(os.environ, {'GDK_BACKEND':'wayland'}, clear=True), patch('sys.argv', ['desktop_evidence.py','--expected-dpr','2']), patch('desktop_evidence.platform.platform', return_value='test Linux'), patch('desktop_evidence.free_ports', return_value=(1234,1235)), patch('desktop_evidence.subprocess.Popen', return_value=child) as spawn, patch('desktop_evidence.stop'):
                    desktop_evidence.main()
                command = spawn.call_args.args[0]
                self.assertEqual(command[-2:], ['--expected-dpr','2'])
                report = json.loads(Path('artifacts/desktop-desktop.json').read_text())
                self.assertEqual(report['expected_dpr'], 2)
                self.assertFalse(report['hardware_gpu_verified'])
                self.assertFalse(report['orca_verified'])
                self.assertNotIn('env', spawn.call_args.kwargs)
            finally:
                os.chdir(previous)


if __name__ == '__main__':
    unittest.main()

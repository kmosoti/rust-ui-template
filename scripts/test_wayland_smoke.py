import socket
import signal
import subprocess
import unittest
from unittest.mock import Mock, patch
from owned_process import stop, free_ports
from native_smoke import reserve_check


class OwnedSessionTests(unittest.TestCase):
    def test_only_owned_compositor_group_is_killed_after_timeout(self):
        child = Mock(pid=123)
        child.poll.return_value = None
        child.wait.side_effect = [subprocess.TimeoutExpired('owned', 1), 0]
        with patch('owned_process.os.killpg') as kill:
            stop(child, timeout=1)
        self.assertEqual(kill.call_args_list, [unittest.mock.call(123, signal.SIGTERM), unittest.mock.call(123, signal.SIGKILL)])

    def test_already_exited_process_is_not_signaled(self):
        child = Mock(); child.poll.return_value = 0
        with patch('owned_process.os.killpg') as kill:
            stop(child)
        kill.assert_not_called()

    def test_occupied_driver_port_is_rejected_and_ephemeral_ports_differ(self):
        with socket.socket() as occupied:
            occupied.bind(('127.0.0.1', 0)); occupied.listen()
            with self.assertRaises(OSError):
                reserve_check(occupied.getsockname()[1])
        first, second = free_ports()
        self.assertNotEqual(first, second)


class DisplayArgumentTests(unittest.TestCase):
    def test_reject_unsupported_scale_and_keyboard_fixture_before_startup(self):
        import wayland_smoke
        for arguments in (['--scale','3'], ['--keyboard','--denial-fixture']):
            with patch('sys.argv', ['wayland_smoke.py', *arguments]), patch('wayland_smoke.subprocess.Popen') as spawn:
                with self.assertRaises(SystemExit) as error:
                    wayland_smoke.main()
                self.assertEqual(error.exception.code, 2)
                spawn.assert_not_called()

    def test_native_rejects_keyboard_fixture_and_unsupported_dpr(self):
        import native_smoke
        for arguments in (['--expected-dpr','3'], ['--keyboard','--denial-fixture']):
            with patch('sys.argv', ['native_smoke.py', *arguments]), patch('native_smoke.subprocess.Popen') as spawn:
                with self.assertRaises(SystemExit) as error:
                    native_smoke.main()
                self.assertEqual(error.exception.code, 2)
                spawn.assert_not_called()

    def test_explicit_nested_scale_forwards_keys_dpr_and_removes_client_display(self):
        import json
        import os
        from pathlib import Path
        import tempfile
        import wayland_smoke
        with tempfile.TemporaryDirectory() as directory:
            original = Path.cwd()
            try:
                os.chdir(directory)
                Path('artifacts').mkdir()
                Path('artifacts/probe-driver.log').write_text('wl_surface xdg_toplevel')
                process = Mock(); process.wait.return_value = 0
                with patch.dict(os.environ, {'DISPLAY':':99','XAUTHORITY':'private'}), patch('sys.argv', ['wayland_smoke.py','--artifact-prefix','probe','--compositor-backend','x11','--scale','2','--keyboard']), patch('wayland_smoke.Path.is_socket', return_value=True), patch('wayland_smoke.subprocess.check_output', side_effect=['--scale=SCALE','weston 13.0.0']), patch('wayland_smoke.subprocess.run'), patch('wayland_smoke.subprocess.Popen', return_value=process) as spawn, patch('wayland_smoke.stop'):
                    wayland_smoke.main()
                compositor, native = spawn.call_args_list
                self.assertEqual(compositor.args[0][0], 'xvfb-run')
                self.assertIn('--backend=x11-backend.so', compositor.args[0])
                self.assertIn('--scale=2', compositor.args[0])
                command = native.args[0]
                self.assertIn('--keyboard', command)
                self.assertEqual(command[command.index('--expected-dpr')+1], '2')
                self.assertNotIn('DISPLAY', native.kwargs['env'])
                self.assertNotIn('XAUTHORITY', native.kwargs['env'])
                self.assertEqual(native.kwargs['env']['GDK_BACKEND'], 'wayland')
                self.assertTrue(compositor.kwargs['start_new_session'])
                report = json.loads(Path('artifacts/probe-compositor.json').read_text())
                self.assertEqual(report['compositor_backend'], 'x11')
                self.assertFalse(report['hardware_gpu_tested'])
            finally:
                os.chdir(original)

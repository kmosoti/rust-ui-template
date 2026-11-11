"""Real subprocess fixtures test lifecycle only; real APK assertions stay in CI."""
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
import unittest

SCRIPTS = Path(__file__).resolve().parent


class AndroidLifecycleTests(unittest.TestCase):
    def launch(self, folder, boot=True, case_result=0, fail_cleanup=False):
        root = Path(folder); binaries = root/'bin'; binaries.mkdir()
        emulator = binaries/'emulator'
        emulator.write_text('#!'+sys.executable+'\nimport os,signal,time\nfrom pathlib import Path\nsignal.signal(signal.SIGTERM,signal.SIG_IGN)\nPath("emulator.pid").write_text(str(os.getpid()))\nwhile True: time.sleep(1)\n')
        emulator.chmod(0o755)
        adb = binaries/'adb'
        adb.write_text('#!'+sys.executable+'\nimport sys,time,signal\nif "getprop" in sys.argv: print('+repr('1' if boot else '')+')\nelif "kill" in sys.argv:\n signal.signal(signal.SIGTERM,signal.SIG_IGN)\n time.sleep(120)\n')
        adb.chmod(0o755)
        smoke = root/'case.py'
        smoke.write_text('import sys\nfrom pathlib import Path\np=Path("cases.txt")\np.write_text((p.read_text() if p.exists() else "")+("denial" if "--denial" in sys.argv else "production")+"\\n")\nsys.exit('+str(case_result)+')\n')
        code = 'import sys\nsys.path.insert(0,'+repr(str(SCRIPTS))+')\nimport android_emulator_runner as r\nr.SMOKE_SCRIPT='+repr(str(smoke))+'\nr.ADB_SHUTDOWN_TIMEOUT=.05\nr.PROCESS_STOP_TIMEOUT=.05\nr.require_unused_ports=lambda:None\n'
        if fail_cleanup:
            code += 'real_stop=r.stop\ndef broken(p,timeout=5):\n if p is not None and p.args[0]=="emulator": raise OSError("fixture cleanup failure")\n return real_stop(p,timeout)\nr.stop=broken\n'
        code += 'r.main()\n'
        environment = os.environ.copy(); environment['PATH'] = str(binaries)+os.pathsep+environment['PATH']; environment['ANDROID_SERIAL'] = 'emulator-5554'
        return subprocess.Popen([sys.executable, '-c', code], cwd=root, env=environment, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, start_new_session=True)

    def finish(self, process, root):
        try:
            output = process.communicate(timeout=8)[0].decode()
            return output, json.loads((root/'artifacts/android-lifecycle/state.json').read_text())['events']
        finally:
            if process.poll() is None:
                os.killpg(process.pid, signal.SIGKILL); process.wait(timeout=2)
            pid_file = root/'emulator.pid'
            if pid_file.exists():
                try: os.killpg(int(pid_file.read_text()), signal.SIGKILL)
                except ProcessLookupError: pass

    def test_term_resistant_shutdown_is_bounded_after_both_cases(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); child = self.launch(root)
            output, events = self.finish(child, root)
            self.assertEqual(child.returncode, 0, output)
            self.assertEqual((root/'cases.txt').read_text().splitlines(), ['production', 'denial'])
            self.assertIn('shutdown-adb-timeout', [e['phase'] for e in events])
            self.assertEqual(events[-1]['emulator_returncode'], -signal.SIGKILL)
            self.assertEqual(events[-1]['cleanup_errors'], [])

    def test_signal_interruption_stops_only_owned_process_group(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); child = self.launch(root, boot=False)
            deadline = time.monotonic()+3
            while not (root/'emulator.pid').exists() and time.monotonic() < deadline:
                time.sleep(.01)
            bystander = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(120)'], start_new_session=True)
            try:
                self.assertTrue((root/'emulator.pid').exists())
                child.send_signal(signal.SIGTERM)
                output, events = self.finish(child, root)
                self.assertIsNone(bystander.poll())
            finally:
                if child.poll() is None:
                    self.finish(child, root)
                os.killpg(bystander.pid, signal.SIGKILL); bystander.wait(timeout=2)
            self.assertEqual(child.returncode, 143, output)
            self.assertFalse((root/'cases.txt').exists())
            self.assertEqual(events[-1]['original_error'], 'SystemExit')
            self.assertEqual(events[-1]['emulator_returncode'], -signal.SIGKILL)

    def test_cleanup_failure_preserves_original_case_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); child = self.launch(root, case_result=7, fail_cleanup=True)
            output, events = self.finish(child, root)
            self.assertNotEqual(child.returncode, 0)
            failed = next(e for e in events if e['phase']=='failed')
            self.assertEqual((failed['error_type'], failed['returncode']), ('CalledProcessError', 7))
            self.assertEqual(events[-1]['original_error'], 'CalledProcessError')
            self.assertIn('fixture cleanup failure', str(events[-1]['cleanup_errors']))

    def test_cleanup_failure_after_success_is_not_a_pass(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); child = self.launch(root, fail_cleanup=True)
            output, events = self.finish(child, root)
            self.assertNotEqual(child.returncode, 0)
            self.assertIsNone(events[-1]['original_error'])
            self.assertIn('fixture cleanup failure', str(events[-1]['cleanup_errors']))

    def test_existing_listener_is_rejected_before_emulator_actions(self):
        import socket
        from android_emulator_runner import require_unused_ports
        with socket.socket() as listener:
            listener.bind(('127.0.0.1', 0)); listener.listen()
            with self.assertRaises(OSError):
                require_unused_ports((listener.getsockname()[1],))

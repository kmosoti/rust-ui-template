"""Own one Android emulator session; keep assertions and shutdown independently bounded."""
import datetime
import json
import os
from pathlib import Path
import signal
import socket
import subprocess
import sys
import tempfile
import time

from owned_process import stop

SMOKE_SCRIPT = Path(__file__).with_name('android_smoke.py')
ADB_SHUTDOWN_TIMEOUT = 10
PROCESS_STOP_TIMEOUT = 5


class Journal:
    def __init__(self):
        self.path = Path('artifacts/android-lifecycle/state.json')
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.started = time.monotonic()
        self.events = []

    def record(self, phase, **details):
        event = {'phase': phase, 'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'elapsed_seconds': time.monotonic()-self.started, **details}
        self.events.append(event)
        try:
            self.path.write_text(json.dumps({'events': self.events}, indent=2)+'\n')
            print('ANDROID_LIFECYCLE '+phase, flush=True)
        except OSError:
            pass  # Diagnostics must never replace an assertion or cleanup error.


def checked(command, timeout, capture=False):
    # File-backed output avoids a daemon inheriting a pipe and holding timeout
    # collection open after its parent is killed. All waits remain finite.
    with tempfile.TemporaryFile(mode='w+t') as output:
        process = subprocess.Popen(command, start_new_session=True,
                                   stdout=output if capture else None,
                                   stderr=subprocess.STDOUT if capture else None)
        original = None
        try:
            result = process.wait(timeout=timeout)
            if result:
                raise subprocess.CalledProcessError(result, command)
            if capture:
                output.seek(0)
                return output.read(4096)
        except BaseException as error:
            original = error
            raise
        finally:
            try:
                stop(process, timeout=PROCESS_STOP_TIMEOUT)
            except Exception as cleanup_error:
                if original is None:
                    raise
                print('Owned command cleanup failed after original error:', cleanup_error, flush=True)


def boot(emulator, serial):
    deadline = time.monotonic()+600
    while time.monotonic() < deadline:
        if emulator.poll() is not None:
            raise RuntimeError('Owned emulator exited before boot completed')
        try:
            value = checked(['adb', '-s', serial, 'shell', 'getprop', 'sys.boot_completed'], timeout=10, capture=True)
            if value.strip() == '1':
                return
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
            pass  # Readiness only; no application assertion or action is replayed.
        time.sleep(2)
    raise TimeoutError('Android emulator boot timed out')


def shutdown(emulator, serial, journal):
    errors = []
    if emulator is not None and emulator.poll() is None:
        journal.record('shutdown-adb', emulator_pid=emulator.pid)
        client = None
        try:
            client = subprocess.Popen(['adb', '-s', serial, 'emu', 'kill'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
            try:
                client.wait(timeout=ADB_SHUTDOWN_TIMEOUT)
            except subprocess.TimeoutExpired:
                journal.record('shutdown-adb-timeout')
        except Exception as error:
            # A failed graceful request does not replace bounded forced shutdown.
            journal.record('shutdown-adb-unavailable', error=str(error))
        finally:
            try:
                stop(client, timeout=PROCESS_STOP_TIMEOUT)
            except Exception as error:
                errors.append(str(error))
    journal.record('shutdown-process')
    try:
        stop(emulator, timeout=PROCESS_STOP_TIMEOUT)
    except Exception as error:
        errors.append(str(error))
    return errors


def require_unused_ports(ports=(5554, 5555)):
    for port in ports:
        with socket.socket() as probe:
            probe.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            probe.bind(('127.0.0.1', port))


def interrupted(signum, frame):
    raise SystemExit(128+signum)


def main():
    signal.signal(signal.SIGINT, interrupted)
    signal.signal(signal.SIGTERM, interrupted)
    journal = Journal()
    serial = os.environ['ANDROID_SERIAL']
    if serial != 'emulator-5554':
        raise RuntimeError('The owned emulator requires ANDROID_SERIAL=emulator-5554')
    emulator = None
    original = None
    Path('artifacts').mkdir(exist_ok=True)
    with Path('artifacts/android-emulator.log').open('w') as log:
        try:
            require_unused_ports()
            journal.record('emulator-start')
            emulator = subprocess.Popen(['emulator', '-port', '5554', '-avd', 'rust-ui-api36', '-wipe-data', '-no-window', '-gpu', 'swiftshader', '-no-snapshot', '-noaudio', '-no-boot-anim', '-accel', 'on', '-memory', '2048'], stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
            journal.record('boot-start', emulator_pid=emulator.pid)
            boot(emulator, serial)
            journal.record('boot-complete')
            for command in [('input', 'keyevent', '82'), ('settings', 'put', 'global', 'window_animation_scale', '0'), ('settings', 'put', 'global', 'transition_animation_scale', '0'), ('settings', 'put', 'global', 'animator_duration_scale', '0')]:
                checked(['adb', '-s', serial, 'shell', *command], timeout=60)
            for phase, apk, extra in [('production', 'artifacts/rust-ui-android-x86_64-debug.apk', []), ('denial', 'artifacts/android-restricted-fixture.apk', ['--denial'])]:
                journal.record(phase+'-start')
                # The existing helper retains its 240s instrumentation deadline
                # and individual diagnostics deadlines; this is an outer bound.
                checked([sys.executable, str(SMOKE_SCRIPT), '--apk', apk, '--test-apk', 'artifacts/android-instrumentation.apk', *extra], timeout=900)
                journal.record(phase+'-complete')
        except BaseException as error:
            original = error
            journal.record('failed', error_type=type(error).__name__, error=str(error), returncode=getattr(error, 'returncode', None))
            try:
                log.flush()
                print(Path(log.name).read_text(errors='replace')[-8192:], flush=True)
            except OSError:
                pass
            raise
        finally:
            # Finish the finite cleanup after an interrupt; SIGKILL remains an
            # external runner responsibility and cannot execute Python finally.
            signal.signal(signal.SIGINT, signal.SIG_IGN)
            signal.signal(signal.SIGTERM, signal.SIG_IGN)
            errors = shutdown(emulator, serial, journal)
            journal.record('cleanup-complete', original_error=type(original).__name__ if original else None, cleanup_errors=errors, emulator_returncode=emulator.returncode if emulator else None)
            if errors:
                if original is None:
                    raise RuntimeError('Owned Android cleanup failed: '+str(errors))
                print('Cleanup errors retained after original failure:', errors, flush=True)


if __name__ == '__main__':
    main()

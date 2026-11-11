"""Own a software-rendered Weston session and run installed-package smoke tests."""
import argparse
import json
import os
from pathlib import Path
import signal
import socket
import subprocess
import sys
import tempfile
import time


def free_ports():
    sockets = [socket.socket(), socket.socket()]
    try:
        for item in sockets:
            item.bind(('127.0.0.1', 0))
        return [item.getsockname()[1] for item in sockets]
    finally:
        for item in sockets:
            item.close()


def stop(process, timeout=10):
    if process is not None and process.poll() is None:
        os.killpg(process.pid, signal.SIGTERM)
        try:
            process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait(timeout=5)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--artifact-prefix', default='wayland-software')
    parser.add_argument('--atspi', action='store_true')
    parser.add_argument('--application', default='/usr/bin/rust-ui-native')
    parser.add_argument('--denial-fixture', action='store_true')
    args = parser.parse_args()
    artifacts = Path('artifacts'); artifacts.mkdir(exist_ok=True)
    report = artifacts/(args.artifact_prefix+'-compositor.json')
    environment = os.environ.copy()
    environment.pop('DISPLAY', None)
    environment.pop('XAUTHORITY', None)
    environment.update(GDK_BACKEND='wayland', LIBGL_ALWAYS_SOFTWARE='1', GALLIUM_DRIVER='llvmpipe', WEBKIT_DISABLE_DMABUF_RENDERER='1')
    compositor = test = None
    original = None
    with tempfile.TemporaryDirectory(prefix='rust-ui-wayland-') as runtime:
        os.chmod(runtime, 0o700)
        environment.update(XDG_RUNTIME_DIR=runtime, WAYLAND_DISPLAY='rust-ui-owned')
        # No Xwayland and no headless "no-op" renderer: pixman actually paints.
        command = ['weston', '--backend=headless-backend.so', '--renderer=pixman', '--shell=kiosk-shell.so', '--width=1600', '--height=1100', '--socket=rust-ui-owned', '--idle-time=0', '--no-config']
        version = subprocess.check_output(['weston', '--version'], text=True).strip()
        report.write_text(json.dumps({'renderer_configuration': 'Weston pixman; clients forced to Mesa software', 'actual_client_gpu_renderer': 'not measured', 'hardware_gpu_tested': False, 'weston': version, 'command': command, 'display': 'wayland', 'xwayland': False}, indent=2)+'\n')
        with (artifacts/(args.artifact_prefix+'-weston.log')).open('w') as log:
            try:
                compositor = subprocess.Popen(command, env=environment, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
                deadline = time.monotonic()+20
                while not (Path(runtime)/'rust-ui-owned').is_socket():
                    if compositor.poll() is not None:
                        raise RuntimeError('Weston exited before its owned socket became ready')
                    if time.monotonic() > deadline:
                        raise TimeoutError('Weston socket readiness timed out')
                    time.sleep(.1)
                with (artifacts/(args.artifact_prefix+'-wayland-info.log')).open('w') as info:
                    subprocess.run(['wayland-info'], env=environment, stdout=info, stderr=subprocess.STDOUT, check=True, timeout=10)
                if args.atspi:
                    subprocess.run(['gdbus','call','--session','--dest','org.a11y.Bus','--object-path','/org/a11y/bus','--method','org.freedesktop.DBus.Properties.Set','org.a11y.Status','IsEnabled','<true>'], env=environment, check=True, timeout=10)
                    environment['NO_AT_BRIDGE'] = '0'
                environment['WAYLAND_DEBUG'] = 'client'
                port, native_port = free_ports()
                test_command = [sys.executable, 'scripts/native_smoke.py', '--application', args.application, '--artifact-prefix', args.artifact_prefix, '--display-backend', 'wayland', '--port', str(port), '--native-port', str(native_port)]
                if args.atspi:
                    test_command.append('--atspi')
                if args.denial_fixture:
                    test_command.append('--denial-fixture')
                test = subprocess.Popen(test_command, env=environment, start_new_session=True)
                result = test.wait(timeout=240)
                if result:
                    raise RuntimeError(f'Native Wayland checks failed with exit code {result}')
                protocol = (artifacts/(args.artifact_prefix+'-driver.log')).read_text(errors='replace')
                if 'xdg_toplevel' not in protocol or 'wl_surface' not in protocol:
                    raise RuntimeError('Missing actual Wayland surface/toplevel protocol evidence')
            except BaseException as error:
                original = error
                raise
            finally:
                failures = []
                for process in (test, compositor):
                    try:
                        stop(process, timeout=15 if process is test else 5)
                    except Exception as error:
                        failures.append(str(error))
                if failures:
                    (artifacts/(args.artifact_prefix+'-cleanup.json')).write_text(json.dumps({'original_error': str(original) if original else None, 'cleanup_errors': failures})+'\n')
                    if original is None:
                        raise RuntimeError('Owned Wayland cleanup failed')


if __name__ == '__main__':
    # Always own the bus before changing accessibility status. Never change a
    # caller's real desktop bus or accessibility settings.
    if os.environ.get('RUST_UI_WAYLAND_PRIVATE_BUS') != '1':
        environment = os.environ.copy()
        environment['RUST_UI_WAYLAND_PRIVATE_BUS'] = '1'
        os.execvpe('dbus-run-session', ['dbus-run-session','--',sys.executable,str(Path(__file__).resolve()),*sys.argv[1:]], environment)
    def terminate(signum, frame):
        raise SystemExit(128+signum)
    signal.signal(signal.SIGTERM, terminate)
    main()

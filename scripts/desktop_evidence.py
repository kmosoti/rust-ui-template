"""Run installed-app evidence on an existing Linux desktop, without changing it."""
import argparse
import json
import os
from pathlib import Path
import platform
import signal
import subprocess
import sys

from owned_process import free_ports, stop


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--application', default='/usr/bin/rust-ui-native')
    parser.add_argument('--artifact-prefix', default='desktop')
    parser.add_argument('--keyboard', action='store_true')
    parser.add_argument('--atspi', action='store_true', help='Requires accessibility already enabled on this desktop')
    args = parser.parse_args()
    backend = os.environ.get('GDK_BACKEND')
    if backend not in ('x11', 'wayland'):
        parser.error('Set GDK_BACKEND=x11 or wayland explicitly for the desktop under test')
    if backend == 'wayland' and os.environ.get('DISPLAY'):
        parser.error('Use env -u DISPLAY for a forced Wayland evidence run')
    if any(os.environ.get(key) for key in ('LIBGL_ALWAYS_SOFTWARE', 'GALLIUM_DRIVER', 'WEBKIT_DISABLE_DMABUF_RENDERER')):
        parser.error('Remove renderer overrides before a hardware-desktop evidence run')
    artifacts = Path('artifacts'); artifacts.mkdir(exist_ok=True)
    devices = []
    for device in sorted(Path('/sys/class/drm').glob('card[0-9]*/device')):
        row = {'device': str(device.resolve())}
        for field in ('vendor', 'device'):
            source = device/field
            if source.is_file():
                row[field+'_id'] = source.read_text().strip()
        driver = device/'driver'
        row['driver'] = driver.resolve().name if driver.exists() else None
        devices.append(row)
    report = {'system': platform.platform(), 'session': {key: os.environ.get(key) for key in ('XDG_SESSION_TYPE', 'XDG_CURRENT_DESKTOP', 'GDK_BACKEND', 'DISPLAY', 'WAYLAND_DISPLAY')}, 'drm_devices': devices, 'application_renderer': 'not measured: attach compositor/driver evidence manually', 'hardware_gpu_verified': False, 'orca_verified': False}
    (artifacts/(args.artifact_prefix+'-desktop.json')).write_text(json.dumps(report, indent=2)+'\n')
    port, native_port = free_ports()
    command = [sys.executable, 'scripts/native_smoke.py', '--application', args.application, '--display-backend', backend, '--artifact-prefix', args.artifact_prefix, '--port', str(port), '--native-port', str(native_port)]
    if args.keyboard:
        command.append('--keyboard')
    if args.atspi:
        command.append('--atspi')
    child = subprocess.Popen(command, start_new_session=True)
    try:
        if child.wait(timeout=240):
            raise RuntimeError('Installed desktop checks failed; inspect native evidence')
    finally:
        stop(child, timeout=15)


if __name__ == '__main__':
    def terminate(signum, frame):
        raise SystemExit(128+signum)
    signal.signal(signal.SIGTERM, terminate)
    main()

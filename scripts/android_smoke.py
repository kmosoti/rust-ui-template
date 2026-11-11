"""Run AndroidX tests against real installed APKs and retain failure diagnostics."""
import argparse
from pathlib import Path
import re
import subprocess

PACKAGE = 'dev.kmosoti.rustuitemplate'


def adb(*args, timeout=60):
    try:
        result = subprocess.run(['adb', *args], text=True, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, timeout=timeout, check=True)
        return result.stdout
    except subprocess.CalledProcessError as error:
        print(error.stdout)
        raise


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--apk', required=True)
    parser.add_argument('--test-apk', required=True)
    parser.add_argument('--denial', action='store_true')
    args = parser.parse_args()
    phase = 'denial' if args.denial else 'production'
    directory = Path('artifacts/android-' + phase)
    directory.mkdir(parents=True, exist_ok=True)
    try:
        print(adb('install', '-r', args.apk))
        print(adb('install', '-r', args.test_apk))
        adb('shell', 'pm', 'clear', PACKAGE)
        adb('logcat', '-c')
        # Bundled assets and IPC must work without network connectivity.
        adb('shell', 'svc', 'wifi', 'disable')
        adb('shell', 'svc', 'data', 'disable')
        runtime = '\n'.join(adb(*command) for command in [
            ('shell', 'getprop', 'ro.build.version.sdk'),
            ('shell', 'getprop', 'ro.product.cpu.abi'),
            ('shell', 'dumpsys', 'webviewupdate'),
            ('shell', 'dumpsys', 'connectivity'),
        ])
        (directory / 'runtime.txt').write_text(runtime)
        output = adb('shell', 'am', 'instrument', '-w', '-r', '-e', 'denial',
                     str(args.denial).lower(), PACKAGE + '.test/androidx.test.runner.AndroidJUnitRunner', timeout=240)
        (directory / 'instrumentation.txt').write_text(output)
        print(output)
        if not re.search(r'OK \(1 test\)', output) or 'FAILURES!!!' in output or 'INSTRUMENTATION_FAILED' in output:
            raise RuntimeError('Android instrumentation did not report one passing test')
    finally:
        # Collection errors cannot replace the original assertion/transport error.
        for name, command in [
            ('logcat.txt', ('logcat', '-d', '-v', 'threadtime')),
            ('window.txt', ('shell', 'dumpsys', 'window')),
            ('ui.xml', ('exec-out', 'uiautomator', 'dump', '/dev/tty')),
        ]:
            try:
                (directory / name).write_text(adb(*command, timeout=20))
            except Exception as error:
                print('Diagnostic unavailable:', name, type(error).__name__)
        try:
            screen = subprocess.run(['adb', 'exec-out', 'screencap', '-p'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=20, check=True)
            (directory / 'device.png').write_bytes(screen.stdout)
        except Exception as error:
            print('Device screenshot unavailable:', type(error).__name__)
        try:
            result = subprocess.run(['adb', 'exec-out', 'run-as', PACKAGE, 'tar', '-cf', '-', '-C', 'files', 'evidence'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=20, check=True)
            (directory / 'webview-evidence.tar').write_bytes(result.stdout)
            import io, tarfile
            with tarfile.open(fileobj=io.BytesIO(result.stdout)) as archive:
                archive.extractall(directory, filter='data')
        except Exception as error:
            print('WebView evidence unavailable:', type(error).__name__)


if __name__ == '__main__':
    main()

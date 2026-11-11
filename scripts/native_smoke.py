"""Exercise an installed Linux package through tauri-driver + WebKitWebDriver."""
import argparse
import base64
import json
import os
from pathlib import Path
import signal
import socket
import shutil
import sys
import platform
import traceback
import subprocess
import time
import urllib.error
import urllib.request


DRIVER_PORT = 4444


def request(method, path, body=None, timeout=40):
    data = None if body is None else json.dumps(body).encode()
    req = urllib.request.Request(f'http://127.0.0.1:{DRIVER_PORT}' + path, data=data, method=method, headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            result = json.load(response)
    except urllib.error.HTTPError as error:
        try:
            error.webdriver_response = error.read(8192).decode(errors='replace')
        except Exception:
            error.webdriver_response = None
        raise
    value = result.get('value')
    return value


def record_failure(directory, name, phase, error, session):
    """Best-effort artifacts must never replace the original failure."""
    try:
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)
        (directory / (name + '-failure.json')).write_text(json.dumps({
            'phase': phase, 'type': type(error).__name__, 'error': str(error),
            'traceback': traceback.format_exc(), 'session_created': session is not None,
            'webdriver_response': getattr(error, 'webdriver_response', None),
            'python': platform.python_version(), 'system': platform.platform(),
        }, indent=2))
        if session:
            try:
                image = request('GET', '/session/' + session + '/screenshot', timeout=3)
                (directory / (name + '-failure.png')).write_bytes(base64.b64decode(image))
            except Exception:
                pass
    except Exception as capture_error:
        print('Diagnostic capture unavailable:', type(capture_error).__name__)


def cleanup_driver(driver, log, preserve_error):
    errors = []
    try:
        if driver is not None and driver.poll() is None:
            os.killpg(driver.pid, signal.SIGTERM)
            try:
                driver.wait(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(driver.pid, signal.SIGKILL)
                driver.wait(timeout=5)
    except Exception as error:
        errors.append(error)
    try:
        log.close()
    except Exception as error:
        errors.append(error)
    if errors:
        if preserve_error:
            print('Cleanup failed after original failure:', type(errors[0]).__name__)
        else:
            raise errors[0]


def reserve_check(port):
    with socket.socket() as probe:
        probe.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        probe.bind(('127.0.0.1', port))


def main():
    global DRIVER_PORT
    parser = argparse.ArgumentParser()
    parser.add_argument('--application', default='/usr/bin/rust-ui-native')
    parser.add_argument('--denial-fixture', action='store_true')
    parser.add_argument('--artifact-prefix', default='native-linux')
    parser.add_argument('--display-backend', choices=['auto', 'x11', 'wayland'], default='auto')
    parser.add_argument('--atspi', action='store_true', help='Inspect native accessibility using system Python/pyatspi')
    parser.add_argument('--port', type=int, default=4444)
    parser.add_argument('--native-port', type=int, default=4445)
    args = parser.parse_args()
    if args.port == args.native_port or not all(0 < p < 65536 for p in (args.port, args.native_port)):
        parser.error('Driver ports must be distinct values between1 and65535')
    if args.display_backend == 'wayland' and (os.environ.get('GDK_BACKEND') != 'wayland' or os.environ.get('DISPLAY')):
        parser.error('Wayland checks require GDK_BACKEND=wayland and no DISPLAY fallback')
    if args.display_backend == 'x11' and (os.environ.get('GDK_BACKEND') != 'x11' or not os.environ.get('DISPLAY')):
        parser.error('X11 checks require GDK_BACKEND=x11 and DISPLAY')
    for port in (args.port, args.native_port):
        reserve_check(port)
    DRIVER_PORT = args.port
    Path('artifacts').mkdir(exist_ok=True)
    log = open(Path('artifacts') / (args.artifact_prefix + '-driver.log'), 'w')
    phase = 'driver startup'
    session = None
    driver = None
    try:
        driver = subprocess.Popen(['tauri-driver', '--port', str(args.port), '--native-port', str(args.native_port)], start_new_session=True, stdout=log, stderr=subprocess.STDOUT)
        deadline = time.monotonic() + 20
        while True:
            try:
                request('GET', '/status')
                break
            except (urllib.error.URLError, OSError):
                if driver.poll() is not None or time.monotonic() > deadline:
                    raise RuntimeError('tauri-driver did not start')
                time.sleep(.1)
        phase = 'session creation'
        session = request('POST', '/session', {'capabilities': {'alwaysMatch': {'tauri:options': {'application': str(Path(args.application).resolve())}}}}, timeout=90)['sessionId']
        prefix = '/session/' + session
        request('POST', prefix + '/timeouts', {'script': 15000})

        def execute(script):
            return request('POST', prefix + '/execute/sync', {'script': script, 'args': []})

        def wait(predicate):
            end = time.monotonic() + 15
            while not execute('return Boolean(' + predicate + ')'):
                if time.monotonic() > end:
                    raise AssertionError('Timed out: ' + predicate)
                time.sleep(.05)

        def invoke(payload):
            return request('POST', prefix + '/execute/async', {'script': "const done = arguments[arguments.length-1]; window.__TAURI_INTERNALS__.invoke('app_info', {request: " + json.dumps(payload) + "}).then(value=>done({ok:true,value})).catch(error=>done({ok:false,error:String(error)}));", 'args': []})

        phase = 'window and bundled library readiness'
        target = 'restricted' if args.denial_fixture else 'main'
        deadline = time.monotonic() + 15
        while True:
            found = False
            for handle in request('GET', prefix + '/window/handles'):
                request('POST', prefix + '/window', {'handle': handle})
                if execute('return window.__TAURI_INTERNALS__?.metadata?.currentWindow?.label') == target:
                    found = True
                    break
            if found:
                break
            if time.monotonic() > deadline:
                raise AssertionError('Missing expected window: ' + target)
            time.sleep(.05)
        wait("document.querySelector('h1')?.textContent === 'Your library'")
        wait("document.querySelector('[data-testid=featured-art]')?.naturalWidth > 0")
        runtime = execute('return {userAgent:navigator.userAgent,width:innerWidth,height:innerHeight,dpr:devicePixelRatio}')
        runtime['display_backend_requested'] = args.display_backend
        runtime['display_environment'] = {key: os.environ.get(key) for key in ('GDK_BACKEND', 'DISPLAY', 'WAYLAND_DISPLAY', 'LIBGL_ALWAYS_SOFTWARE', 'GALLIUM_DRIVER', 'WEBKIT_DISABLE_DMABUF_RENDERER')}
        runtime['system'] = platform.platform()
        for manager, command in [('dpkg-query', ['dpkg-query','-W','libgtk-3-0t64','libwebkit2gtk-4.1-0','webkit2gtk-driver']), ('rpm',['rpm','-q','gtk3','webkit2gtk4.1','webkitgtk6.0'])]:
            if shutil.which(manager):
                runtime['runtime_packages'] = subprocess.run(command, capture_output=True, text=True, timeout=10).stdout.splitlines()
                break
        Path('artifacts/' + args.artifact_prefix + '-runtime.json').write_text(json.dumps(runtime, indent=2)+'\n')
        Path('artifacts/' + args.artifact_prefix + '-library.png').write_bytes(base64.b64decode(request('GET', prefix + '/screenshot')))
        if args.atspi:
            phase = 'native accessibility tree'
            subprocess.run(['/usr/bin/python3', 'scripts/inspect_atspi.py', '--window', 'Restricted test window' if args.denial_fixture else 'Rust UI Template', '--output', 'artifacts/' + args.artifact_prefix + '-atspi.json'], check=True, timeout=12)
        execute("document.querySelector(\"nav[aria-label='Main navigation'] a[href='#/']\").click()")
        wait("!!document.querySelector('#number')")
        execute("window.__nativeErrors=[]; addEventListener('error', e=>window.__nativeErrors.push(e.message)); addEventListener('unhandledrejection', e=>window.__nativeErrors.push(String(e.reason)));")
        phase = 'typed command validation'
        result = invoke({'schema_version': 1})
        if args.denial_fixture:
            assert result['ok'] is False, result
            assert any(term in result['error'].lower() for term in ['not allowed', 'denied']), result
            execute("location.hash='#/about'")
            wait("document.querySelector('[data-testid=host-info]')?.textContent === 'Application information could not be read.'")
            assert execute('return window.__nativeErrors') == []
            Path('artifacts/' + args.artifact_prefix + '-denied.png').write_bytes(base64.b64decode(request('GET', prefix + '/screenshot')))
            print('PASS: real app_info denial and predictable UI error in restricted window')
            return
        assert result['ok'] and result['value'] == {'schema_version': 1, 'name': 'rust-ui-template', 'version': '0.1.0', 'platform': 'linux'}, result
        for payload in [{'schema_version': 0}, {'schema_version': 1, 'path': '/etc/passwd'}, {}]:
            result = invoke(payload)
            assert result['ok'] is False, result
        assert 'unsupported_version' in invoke({'schema_version': 0})['error']
        phase = 'freshness interaction'
        execute("document.querySelector('#number').value='11'; document.querySelector('#number').dispatchEvent(new Event('input',{bubbles:true})); document.querySelectorAll('button')[0].click();")
        execute("document.querySelector('#number').value='22'; document.querySelector('#number').dispatchEvent(new Event('input',{bubbles:true})); document.querySelectorAll('button')[1].click();")
        wait("document.querySelector('[role=status]')?.textContent.includes('Latest result: 22')")
        time.sleep(1.7)
        wait("document.querySelector('[role=status]')?.textContent.includes('Latest result: 22')")
        assert execute("return getComputedStyle(document.querySelectorAll('button')[1]).backgroundColor") == 'rgb(182, 156, 255)'
        phase = 'CSP enforcement'
        execute("window.__inlineProbe=false; window.__cspEvents=0; addEventListener('securitypolicyviolation',()=>window.__cspEvents++); const script=document.createElement('script'); script.textContent='window.__inlineProbe=true'; document.head.append(script);")
        wait('window.__cspEvents > 0')
        assert execute('return window.__inlineProbe') is False
        phase = 'palette selection and navigation'
        execute("location.hash='#/settings'")
        wait("!!document.querySelector('#color-scheme')")
        execute("const scheme=document.querySelector('#color-scheme'); scheme.value='signal-blue'; scheme.dispatchEvent(new Event('change',{bubbles:true}));")
        wait("document.querySelector('[data-palette]')?.dataset.palette === 'signal-blue'")
        assert execute("return getComputedStyle(document.querySelector('#color-scheme')).colorScheme") == 'light'
        execute("location.hash='#/about'")
        wait("document.querySelector('[data-testid=host-info]')?.textContent.includes('rust-ui-template 0.1.0')")
        assert execute("return getComputedStyle(document.querySelector('[data-palette]')).backgroundColor") == 'rgb(248, 247, 244)'
        assert execute('return window.__nativeErrors') == []
        Path('artifacts').mkdir(exist_ok=True)
        Path('artifacts/' + args.artifact_prefix + '.png').write_bytes(base64.b64decode(request('GET', prefix + '/screenshot')))
        print('PASS: installed Linux package launch, shared CSS/WASM, stale-response behavior, typed IPC validation, CSP enforcement and UI host information')
    except Exception as error:
        try:
            log.flush()
            print('Native driver log tail:', Path(log.name).read_text(errors='replace')[-8192:])
        except Exception:
            pass
        record_failure('artifacts', args.artifact_prefix, phase, error, session)
        raise
    finally:
        if session:
            try:
                request('DELETE', '/session/' + session, timeout=3)
            except Exception:
                pass
        cleanup_driver(driver, log, preserve_error=sys.exc_info()[0] is not None)


if __name__ == '__main__':
    def terminate(signum, frame):
        raise SystemExit(128+signum)
    signal.signal(signal.SIGTERM, terminate)
    main()

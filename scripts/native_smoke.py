"""Exercise an installed Linux package through tauri-driver + WebKitWebDriver."""
import argparse
import base64
import json
import os
from pathlib import Path
import signal
import sys
import platform
import traceback
import subprocess
import time
import urllib.error
import urllib.request


def request(method, path, body=None, timeout=40):
    data = None if body is None else json.dumps(body).encode()
    req = urllib.request.Request('http://127.0.0.1:4444' + path, data=data, method=method, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        result = json.load(response)
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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--application', default='/usr/bin/rust-ui-native')
    parser.add_argument('--denial-fixture', action='store_true')
    parser.add_argument('--artifact-prefix', default='native-linux')
    args = parser.parse_args()
    Path('artifacts').mkdir(exist_ok=True)
    log = open(Path('artifacts') / (args.artifact_prefix + '-driver.log'), 'w')
    phase = 'driver startup'
    session = None
    driver = None
    try:
        driver = subprocess.Popen(['tauri-driver'], start_new_session=True, stdout=log, stderr=subprocess.STDOUT)
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
        record_failure('artifacts', args.artifact_prefix, phase, error, session)
        raise
    finally:
        if session:
            try:
                request('DELETE', '/session/' + session)
            except Exception:
                pass
        cleanup_driver(driver, log, preserve_error=sys.exc_info()[0] is not None)


if __name__ == '__main__':
    main()

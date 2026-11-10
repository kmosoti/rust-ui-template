"""Exercise an installed Linux package through tauri-driver + WebKitWebDriver."""
import argparse
import base64
import json
import os
from pathlib import Path
import signal
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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--application', default='/usr/bin/rust-ui-native')
    parser.add_argument('--denial-fixture', action='store_true')
    args = parser.parse_args()
    session = None
    driver = subprocess.Popen(['tauri-driver'], start_new_session=True)
    try:
        deadline = time.monotonic() + 20
        while True:
            try:
                request('GET', '/status')
                break
            except (urllib.error.URLError, OSError):
                if driver.poll() is not None or time.monotonic() > deadline:
                    raise RuntimeError('tauri-driver did not start')
                time.sleep(.1)
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
        wait("!!document.querySelector('#number')")
        execute("window.__nativeErrors=[]; addEventListener('error', e=>window.__nativeErrors.push(e.message)); addEventListener('unhandledrejection', e=>window.__nativeErrors.push(String(e.reason)));")
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
        execute("document.querySelector('#number').value='11'; document.querySelector('#number').dispatchEvent(new Event('input',{bubbles:true})); document.querySelectorAll('button')[0].click();")
        execute("document.querySelector('#number').value='22'; document.querySelector('#number').dispatchEvent(new Event('input',{bubbles:true})); document.querySelectorAll('button')[1].click();")
        wait("document.querySelector('[role=status]')?.textContent.includes('Latest result: 22')")
        time.sleep(1.7)
        wait("document.querySelector('[role=status]')?.textContent.includes('Latest result: 22')")
        assert execute("return getComputedStyle(document.querySelectorAll('button')[1]).backgroundColor") == 'rgb(49, 87, 183)'
        execute("window.__inlineProbe=false; window.__cspEvents=0; addEventListener('securitypolicyviolation',()=>window.__cspEvents++); const script=document.createElement('script'); script.textContent='window.__inlineProbe=true'; document.head.append(script);")
        wait('window.__cspEvents > 0')
        assert execute('return window.__inlineProbe') is False
        execute("location.hash='#/about'")
        wait("document.querySelector('[data-testid=host-info]')?.textContent.includes('rust-ui-template 0.1.0')")
        assert execute('return window.__nativeErrors') == []
        Path('artifacts').mkdir(exist_ok=True)
        Path('artifacts/native-linux.png').write_bytes(base64.b64decode(request('GET', prefix + '/screenshot')))
        print('PASS: installed Debian package launch, shared CSS/WASM, stale-response behavior, typed IPC validation, CSP enforcement and UI host information')
    finally:
        if session:
            try:
                request('DELETE', '/session/' + session)
            except (OSError, urllib.error.URLError):
                pass
        if driver.poll() is None:
            os.killpg(driver.pid, signal.SIGTERM)
            try:
                driver.wait(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(driver.pid, signal.SIGKILL)
                driver.wait()


if __name__ == '__main__':
    main()

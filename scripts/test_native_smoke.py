"""Regression coverage for the native WebDriver transport/application boundary."""
import io
import json
import unittest
from unittest.mock import patch, Mock
from urllib.error import HTTPError

from native_smoke import request


class NativeTransportTests(unittest.TestCase):
    def connection(self, status, body):
        connection = Mock()
        response = connection.getresponse.return_value
        response.status = status; response.reason = 'test response'; response.headers = {}
        response.read.return_value = body
        return connection

    def test_application_rejection_is_a_successful_webdriver_result(self):
        rejected = {'ok': False, 'error': 'unsupported_version'}
        connection = self.connection(200, json.dumps({'value': rejected}).encode())
        with patch('native_smoke.http.client.HTTPConnection', return_value=connection):
            self.assertEqual(request('POST', '/session/example/execute/async', {}), rejected)
        connection.close.assert_called_once()

    def test_transport_rejection_retains_bounded_response_and_closes_socket(self):
        connection = self.connection(500, b'{"value":{"error":"session not created"}}')
        with patch('native_smoke.http.client.HTTPConnection', return_value=connection):
            with self.assertRaises(HTTPError) as raised:
                request('POST', '/session', {})
        self.assertIn('session not created', raised.exception.webdriver_response)
        connection.getresponse.return_value.read.assert_called_once_with(8192)
        connection.close.assert_called_once()

    def test_timeout_closes_socket_and_is_not_replayed(self):
        connection = Mock()
        connection.getresponse.side_effect = TimeoutError('original timeout')
        with patch('native_smoke.http.client.HTTPConnection', return_value=connection) as constructor:
            with self.assertRaisesRegex(TimeoutError, 'original timeout'):
                request('GET', '/status', timeout=2)
        self.assertEqual(constructor.call_args.kwargs['timeout'], 2)
        connection.request.assert_called_once()
        connection.close.assert_called_once()

    def test_real_http11_wire_does_not_forward_connection_close(self):
        import threading
        from http.server import BaseHTTPRequestHandler, HTTPServer
        import native_smoke
        seen = []
        class Handler(BaseHTTPRequestHandler):
            protocol_version = 'HTTP/1.1'
            def do_GET(self):
                seen.append((self.request_version, self.headers.get('Connection')))
                body = b'{"value":{"error":"wire rejection"}}' if self.path == '/rejected' else b'{"value":true}'
                self.send_response(500 if self.path == '/rejected' else 200); self.send_header('Content-Length', str(len(body)))
                self.end_headers(); self.wfile.write(body)
            def log_message(self, *args):
                pass
        server = HTTPServer(('127.0.0.1', 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
        try:
            with patch.object(native_smoke, 'DRIVER_PORT', server.server_port):
                self.assertTrue(request('GET', '/status'))
                self.assertTrue(request('GET', '/status'))
                with self.assertRaises(HTTPError) as rejected:
                    request('GET', '/rejected')
                self.assertEqual(rejected.exception.code, 500)
                self.assertIn('wire rejection', rejected.exception.webdriver_response)
            self.assertEqual(seen, [('HTTP/1.1', None)]*3)
        finally:
            server.shutdown(); server.server_close(); thread.join(2)


class NativeDiagnosticsTests(unittest.TestCase):
    def test_disconnected_screenshot_does_not_hide_failure_details(self):
        import tempfile
        from pathlib import Path
        from native_smoke import record_failure
        with tempfile.TemporaryDirectory() as directory:
            with patch('native_smoke.request', side_effect=ConnectionError('disconnected')):
                record_failure(directory, 'probe', 'palette selection', ValueError('original'), 'session')
            result = json.loads((Path(directory) / 'probe-failure.json').read_text())
            self.assertEqual(result['type'], 'ValueError')
            self.assertEqual(result['error'], 'original')
            self.assertEqual(result['phase'], 'palette selection')

    def test_unwritable_diagnostics_do_not_raise(self):
        from native_smoke import record_failure
        with patch('native_smoke.Path.mkdir', side_effect=OSError('cannot write')):
            record_failure('/not-used', 'probe', 'startup', RuntimeError('original'), None)


class NativeCleanupTests(unittest.TestCase):
    def test_cleanup_failure_cannot_replace_original_exception(self):
        from native_smoke import cleanup_driver
        from unittest.mock import Mock
        driver = Mock(pid=123)
        driver.poll.return_value = None
        log = Mock()
        log.close.side_effect = OSError('close failed')
        with patch('owned_process.os.killpg', side_effect=OSError('kill failed')):
            with self.assertRaisesRegex(ValueError, 'original'):
                try:
                    raise ValueError('original')
                finally:
                    cleanup_driver(driver, log, preserve_error=True)
        log.close.assert_called_once()

    def test_cleanup_failure_after_success_is_a_failure(self):
        from native_smoke import cleanup_driver
        from unittest.mock import Mock
        log = Mock()
        log.close.side_effect = OSError('close failed')
        with self.assertRaisesRegex(OSError, 'close failed'):
            cleanup_driver(None, log, preserve_error=False)


class OwnedProcessDiagnosticsTests(unittest.TestCase):
    def test_only_descendants_and_whitelisted_fields_are_recorded(self):
        import tempfile
        from pathlib import Path
        from native_smoke import owned_process_snapshot
        with tempfile.TemporaryDirectory() as directory:
            proc = Path(directory)
            for pid, children in ((10, '11'), (11, ''), (99, '')):
                root = proc/str(pid); (root/'task'/str(pid)).mkdir(parents=True)
                (root/'status').write_text('Name: driver\nState: S\nPPid: 1\nThreads: 1\nSecretField: exclude\n')
                (root/'task'/str(pid)/'children').write_text(children)
            result = owned_process_snapshot(10, proc)
            self.assertEqual([p['pid'] for p in result['processes']], [10, 11])
            self.assertNotIn('SecretField', str(result))
            self.assertFalse(result['truncated'])
            self.assertTrue(owned_process_snapshot(10, proc, limit=1)['truncated'])

    def test_application_lookup_binds_exact_owned_executable_and_rejects_ambiguity(self):
        import tempfile
        from pathlib import Path
        from native_smoke import owned_application_pid
        with tempfile.TemporaryDirectory() as directory:
            proc = Path(directory)
            app = proc/'application'; app.touch()
            for pid in (10, 11, 99):
                (proc/str(pid)).mkdir()
                (proc/str(pid)/'exe').symlink_to(app)
            # PID99 matches the binary but is unrelated, so cannot be selected.
            owned = {'processes': [{'pid': 11}], 'truncated': False}
            with patch('native_smoke.owned_process_snapshot', return_value=owned):
                self.assertEqual(owned_application_pid(10, app, proc), 11)
            with patch('native_smoke.owned_process_snapshot', return_value={'processes': [{'pid': 10}, {'pid': 11}], 'truncated': False}):
                with self.assertRaisesRegex(RuntimeError, 'found 2'):
                    owned_application_pid(10, app, proc)
            with patch('native_smoke.owned_process_snapshot', return_value={'processes': [], 'truncated': True}):
                with self.assertRaisesRegex(RuntimeError, 'process bound'):
                    owned_application_pid(10, app, proc)

    def test_process_exit_during_capture_is_diagnostic_only(self):
        import tempfile
        from pathlib import Path
        from native_smoke import owned_process_snapshot
        with tempfile.TemporaryDirectory() as directory:
            result = owned_process_snapshot(123, Path(directory))
            self.assertIn('unavailable', result['processes'][0]['capture'])


if __name__ == '__main__':
    unittest.main()

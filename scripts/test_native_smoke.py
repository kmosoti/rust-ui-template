"""Regression coverage for the native WebDriver transport/application boundary."""
import io
import json
import unittest
from unittest.mock import patch
from urllib.error import HTTPError

from native_smoke import request


class NativeTransportTests(unittest.TestCase):
    def test_application_rejection_is_a_successful_webdriver_result(self):
        rejected = {'ok': False, 'error': 'unsupported_version'}
        response = io.BytesIO(json.dumps({'value': rejected}).encode())
        with patch('native_smoke.urllib.request.urlopen', return_value=response):
            self.assertEqual(request('POST', '/session/example/execute/async', {}), rejected)

    def test_webdriver_http_failure_still_propagates(self):
        failure = HTTPError('http://127.0.0.1:4444/session', 500, 'session not created', {}, None)
        with patch('native_smoke.urllib.request.urlopen', side_effect=failure):
            with self.assertRaises(HTTPError):
                request('POST', '/session', {})

    def test_transport_rejection_retains_bounded_response(self):
        failure = HTTPError('http://127.0.0.1:4444/session', 500, 'session not created', {}, io.BytesIO(b'{"value":{"error":"session not created"}}'))
        with patch('native_smoke.urllib.request.urlopen', side_effect=failure):
            with self.assertRaises(HTTPError) as raised:
                request('POST', '/session', {})
        self.assertIn('session not created', raised.exception.webdriver_response)


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
        with patch('native_smoke.os.killpg', side_effect=OSError('kill failed')):
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


if __name__ == '__main__':
    unittest.main()

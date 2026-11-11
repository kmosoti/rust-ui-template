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


if __name__ == '__main__':
    unittest.main()

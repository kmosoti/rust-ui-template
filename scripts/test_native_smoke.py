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


if __name__ == '__main__':
    unittest.main()

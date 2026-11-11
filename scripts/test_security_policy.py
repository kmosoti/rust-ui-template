import datetime
import unittest
from check_security_policy import check_expiry


class SecurityPolicyTests(unittest.TestCase):
    def test_expired_or_nonmaintenance_exception_fails(self):
        entry = dict(id='RUSTSEC-2000-0001', kind='unmaintained', reason='reviewed reason', expires='2026-11-11')
        with self.assertRaisesRegex(ValueError, 'Expired'):
            check_expiry([entry], datetime.date(2026, 11, 11))
        entry.update(expires='2026-12-01', kind='vulnerability')
        with self.assertRaisesRegex(ValueError, 'maintenance'):
            check_expiry([entry], datetime.date(2026, 11, 11))

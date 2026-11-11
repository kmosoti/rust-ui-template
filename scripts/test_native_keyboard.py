"""Failure boundaries and bounded focus control, independent of WebKit evidence."""
import unittest
from unittest.mock import Mock, patch
from native_keyboard import Keyboard, CONTROL
from native_smoke import assert_dpr


class KeyboardTests(unittest.TestCase):
    def keyboard(self):
        k = Keyboard(Mock(), '/session/example', Mock(), Mock(), 'unit')
        k.save = Mock()
        return k

    def test_unreachable_focus_stops_after_40_tabs_with_target_last_and_trace(self):
        k = self.keyboard()
        k.observe = Mock(return_value={'tag':'BODY','id':'last','visible':True})
        k.matches = Mock(return_value=False)
        with self.assertRaisesRegex(AssertionError, 'Focus target unreachable: #missing; last focus=.*last.*trace='):
            k.reach('#missing')
        self.assertEqual(k.request.call_count, 40)
        self.assertEqual(k.observe.call_count, 41)

    def test_focus_deadline_stops_before_step_limit(self):
        k = self.keyboard(); k.observe = Mock(return_value={'tag':'BODY'})
        k.matches = Mock(return_value=False)
        with patch('native_keyboard.time.monotonic', side_effect=[10,26]):
            with self.assertRaisesRegex(AssertionError, 'unreachable'):
                k.reach('#missing')
        k.request.assert_not_called()

    def test_failed_action_is_not_replayed_and_modifiers_are_released(self):
        k = self.keyboard(); original = RuntimeError('action failed')
        k.request.side_effect = [original, None]
        k.skip = lambda: k.chord(CONTROL, 'a')
        with self.assertRaisesRegex(RuntimeError, 'action failed') as caught:
            k.run()
        self.assertIs(caught.exception, original)
        self.assertEqual([call.args[0] for call in k.request.call_args_list], ['POST','DELETE'])
        self.assertEqual(k.report['failed_checkpoint'], 'fresh-window-skip-link')

    def test_release_and_artifact_errors_preserve_original(self):
        k = self.keyboard(); k.save = Keyboard.save.__get__(k)
        original = AssertionError('original checkpoint')
        k.skip = Mock(side_effect=original)
        k.request.side_effect = RuntimeError('release failed')
        with patch('native_keyboard.Path.write_text', side_effect=OSError('disk full')):
            with self.assertRaisesRegex(AssertionError, 'original checkpoint') as caught:
                k.run()
        self.assertIs(caught.exception, original)
        k.request.assert_called_once_with('DELETE', '/session/example/actions')

    def test_release_failure_after_success_is_a_failure(self):
        k = self.keyboard(); k.checkpoint = Mock()
        k.request.side_effect = RuntimeError('release failed')
        with self.assertRaisesRegex(RuntimeError, 'release failed'):
            k.run()
        self.assertEqual(k.report['failed_checkpoint'], 'release-actions')
        self.assertEqual(k.report['status'], 'failed')

    def test_dpr_mismatch_fails_and_tolerance_is_explicit(self):
        assert_dpr(2.01, 2)
        assert_dpr(1, None)
        with self.assertRaisesRegex(AssertionError, 'DPR mismatch'):
            assert_dpr(1, 2)

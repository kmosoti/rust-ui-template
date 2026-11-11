import socket
import signal
import subprocess
import unittest
from unittest.mock import Mock, patch
from owned_process import stop, free_ports
from native_smoke import reserve_check


class OwnedSessionTests(unittest.TestCase):
    def test_only_owned_compositor_group_is_killed_after_timeout(self):
        child = Mock(pid=123)
        child.poll.return_value = None
        child.wait.side_effect = [subprocess.TimeoutExpired('owned', 1), 0]
        with patch('owned_process.os.killpg') as kill:
            stop(child, timeout=1)
        self.assertEqual(kill.call_args_list, [unittest.mock.call(123, signal.SIGTERM), unittest.mock.call(123, signal.SIGKILL)])

    def test_already_exited_process_is_not_signaled(self):
        child = Mock(); child.poll.return_value = 0
        with patch('owned_process.os.killpg') as kill:
            stop(child)
        kill.assert_not_called()

    def test_occupied_driver_port_is_rejected_and_ephemeral_ports_differ(self):
        with socket.socket() as occupied:
            occupied.bind(('127.0.0.1', 0)); occupied.listen()
            with self.assertRaises(OSError):
                reserve_check(occupied.getsockname()[1])
        first, second = free_ports()
        self.assertNotEqual(first, second)

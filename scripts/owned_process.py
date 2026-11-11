"""Bounded lifecycle helpers for explicitly owned Linux process groups."""
import os
import signal
import socket
import subprocess

def free_ports():
    sockets = [socket.socket(), socket.socket()]
    try:
        for item in sockets:
            item.bind(('127.0.0.1', 0))
        return [item.getsockname()[1] for item in sockets]
    finally:
        for item in sockets:
            item.close()


def stop(process, timeout=10):
    if process is not None and process.poll() is None:
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except ProcessLookupError:
            process.wait(timeout=5)
            return
        try:
            process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            process.wait(timeout=5)


"""Observe the explicitly owned Xvfb framebuffer, then exec its Weston child."""
import ctypes
import json
import os
from pathlib import Path
import sys


def main(report_path, command):
    x11 = ctypes.CDLL('libX11.so.6')
    x11.XOpenDisplay.argtypes = [ctypes.c_char_p]
    x11.XOpenDisplay.restype = ctypes.c_void_p
    x11.XDefaultScreen.argtypes = [ctypes.c_void_p]
    x11.XDefaultScreen.restype = ctypes.c_int
    for name in ('XDisplayWidth', 'XDisplayHeight'):
        function = getattr(x11, name)
        function.argtypes = [ctypes.c_void_p, ctypes.c_int]
        function.restype = ctypes.c_int
    x11.XCloseDisplay.argtypes = [ctypes.c_void_p]
    display = x11.XOpenDisplay(None)
    if not display:
        raise RuntimeError('Owned Xvfb parent display could not be opened')
    try:
        screen = x11.XDefaultScreen(display)
        dimensions = {'width': x11.XDisplayWidth(display, screen), 'height': x11.XDisplayHeight(display, screen)}
        path = Path(report_path)
        report = json.loads(path.read_text())
        report['observed_xvfb_parent_dimensions'] = dimensions
        if dimensions != report['xvfb_parent_dimensions']:
            raise AssertionError(f'Owned Xvfb framebuffer mismatch: {dimensions}')
        path.write_text(json.dumps(report, indent=2)+'\n')
    finally:
        x11.XCloseDisplay(display)
    os.execvp(command[0], command)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2:])

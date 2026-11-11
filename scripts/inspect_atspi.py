"""Read the installed application's native accessibility tree, never the JS DOM."""
import argparse
import json
from pathlib import Path
import time


def snapshot(desktop, window_title, max_nodes=2000):
    pending = [(desktop, 0, False)]
    rows = []
    visited = 0
    while pending and visited < max_nodes:
        node, depth, inside = pending.pop()
        visited += 1
        name = (node.name or '').strip()
        role = node.getRoleName()
        inside = inside or (role in ('frame', 'window') and name == window_title)
        if inside:
            state = node.getState()
            import pyatspi
            rows.append({'name': name, 'role': role, 'depth': depth, 'focused': state.contains(pyatspi.STATE_FOCUSED), 'focusable': state.contains(pyatspi.STATE_FOCUSABLE)})
        if depth >= 24 and node.childCount:
            raise RuntimeError('Accessibility snapshot exceeded its depth bound')
        if depth < 24:
            pending.extend((node.getChildAtIndex(i), depth+1, inside) for i in reversed(range(node.childCount)))
    if pending:
        raise RuntimeError('Accessibility snapshot exceeded its node/depth bound')
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    parser.add_argument('--window', default='Rust UI Template')
    args = parser.parse_args()
    import pyatspi
    deadline = time.monotonic()+6
    required = {('link', 'Library'), ('link', 'Latest response'), ('link', 'Preferences'), ('link', 'About'), ('heading', 'Your library')}
    missing = required
    rows = []
    while time.monotonic() < deadline:
        rows = snapshot(pyatspi.Registry.getDesktop(0), args.window)
        exposed = {(row['role'], row['name']) for row in rows}
        missing = required-exposed
        if not missing:
            break
        time.sleep(.1)
    output = Path(args.output)
    output.write_text(json.dumps({'window': args.window, 'nodes': rows, 'missing': sorted(missing), 'orca_tested': False}, indent=2)+'\n')
    if missing:
        raise SystemExit('Native accessibility roles/names missing: '+str(sorted(missing)))
    print('PASS: native AT-SPI heading/navigation names; no manual Orca claim')


if __name__ == '__main__':
    main()

"""The shared desktop's unrelated trees must not affect owned-app inspection."""
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from inspect_atspi import snapshot


class Node:
    def __init__(self, name='', role='application', children=(), pid=0):
        self.name, self.role, self.children, self.pid = name, role, list(children), pid

    @property
    def childCount(self):
        return len(self.children)

    def getChildAtIndex(self, index):
        return self.children[index]

    def getRoleName(self):
        return self.role

    def get_process_id(self):
        return self.pid

    def getState(self):
        return SimpleNamespace(contains=lambda flag: False)


class Unrelated:
    def get_process_id(self):
        return 99

    def __getattr__(self, key):
        raise AssertionError('Unrelated application content was inspected: '+key)


class SnapshotTests(unittest.TestCase):
    def setUp(self):
        self.modules = patch.dict(sys.modules, pyatspi=SimpleNamespace(STATE_FOCUSED=1, STATE_FOCUSABLE=2))
        self.modules.start(); self.addCleanup(self.modules.stop)

    def test_unrelated_huge_or_unavailable_content_is_never_traversed(self):
        target = Node(children=[Node('Rust UI Template', 'frame', [Node('Your library', 'heading')])], pid=42)
        desktop = Node(children=[Unrelated(), target])
        rows = snapshot(desktop, 'Rust UI Template', 42)
        self.assertEqual([row['name'] for row in rows], ['Rust UI Template', 'Your library'])

    def test_same_title_in_another_process_cannot_supply_evidence(self):
        unrelated = Node(children=[Node('Rust UI Template', 'frame')], pid=99)
        self.assertEqual(snapshot(Node(children=[unrelated]), 'Rust UI Template', 42), [])

    def test_owned_node_and_depth_bounds_are_not_weakened(self):
        wide = Node(children=[Node('Rust UI Template', 'frame', [Node() for _ in range(10)])], pid=42)
        with self.assertRaisesRegex(RuntimeError, 'node/depth bound'):
            snapshot(Node(children=[wide]), 'Rust UI Template', 42, max_nodes=5)
        deep = Node('leaf')
        for _ in range(26):
            deep = Node(children=[deep])
        deep.pid = 42
        with self.assertRaisesRegex(RuntimeError, 'depth bound'):
            snapshot(Node(children=[deep]), 'Rust UI Template', 42)

    def test_duplicate_application_identity_and_discovery_overflow_fail(self):
        with self.assertRaisesRegex(RuntimeError, 'Multiple'):
            snapshot(Node(children=[Node(pid=42), Node(pid=42)]), 'Rust UI Template', 42)
        with self.assertRaisesRegex(RuntimeError, 'discovery'):
            snapshot(Node(children=[Unrelated()]*257), 'Rust UI Template', 42)


if __name__ == '__main__':
    unittest.main()

"""Fixture tests of the metadata checker, not substitutes for Cargo execution."""
import copy
import unittest

from check_core_boundary import violations


class BoundaryTests(unittest.TestCase):
    def setUp(self):
        self.graph = {
            "packages": [{"name": "app-core", "id": "core", "source": None, "dependencies": []}],
            "workspace_members": ["core"],
            "resolve": {"nodes": [{"id": "core", "dependencies": []}]},
        }

    def test_accepts_empty_dependency_graph(self):
        self.assertEqual(violations(self.graph), [])

    def test_missing_core_fails(self):
        self.graph["packages"] = []
        self.assertTrue(violations(self.graph))

    def test_duplicate_core_fails(self):
        self.graph["packages"] *= 2
        self.assertTrue(violations(self.graph))

    def test_external_core_fails(self):
        self.graph["packages"][0]["source"] = "registry+example"
        self.assertTrue(violations(self.graph))

    def test_non_member_fails(self):
        self.graph["workspace_members"] = []
        self.assertTrue(violations(self.graph))

    def test_declared_dependencies_fail_in_every_context(self):
        for kind, target in [(None, None), ("build", None), ("dev", None), (None, "cfg(windows)")]:
            with self.subTest(kind=kind, target=target):
                graph = copy.deepcopy(self.graph)
                graph["packages"][0]["dependencies"] = [{"name": "dependency", "kind": kind, "target": target}]
                self.assertTrue(violations(graph))

    def test_resolved_dependency_fails(self):
        self.graph["resolve"]["nodes"][0]["dependencies"] = ["unexpected"]
        self.assertTrue(violations(self.graph))

    def test_no_deps_metadata_fails(self):
        self.graph["resolve"] = None
        self.assertTrue(violations(self.graph))

    def test_incomplete_package_fails(self):
        del self.graph["packages"][0]["dependencies"]
        self.assertTrue(violations(self.graph))


if __name__ == "__main__":
    unittest.main()

"""Guard the expensive conditional gate against accidentally hidden frontend inputs."""
import ast
import fnmatch
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ReproTriggerCoverage(unittest.TestCase):
    def test_both_event_filters_cover_real_frontend_inputs(self):
        workflow = ROOT/'.github/workflows/reproducibility.yml'
        filters = [ast.literal_eval(line.split('paths-ignore:', 1)[1].strip()) for line in workflow.read_text().splitlines() if 'paths-ignore:' in line]
        self.assertEqual(len(filters), 2)
        tracked = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode().split('\0')
        prefixes = ('crates/', 'styles/', 'public/', 'tests/', 'tools/browser-tests/', '.cargo/')
        inputs = [name for name in tracked if name.startswith(prefixes)]
        inputs += ['Cargo.toml', 'Cargo.lock', 'rust-toolchain.toml', '.gitignore', '.gitattributes', 'index.html', 'Trunk.toml', 'scripts/setup_ci_tools.py', 'scripts/setup_frontend.py', 'scripts/verified_download.py', 'scripts/tool-assets.json', 'scripts/check_css.py', 'scripts/check_frontend_repro.py', 'scripts/test_repro_triggers.py', '.github/workflows/reproducibility.yml']
        for ignored in filters:
            hidden = [name for name in inputs if any(fnmatch.fnmatchcase(name, pattern) for pattern in ignored)]
            self.assertEqual(hidden, [], 'A real frontend/test/setup input would skip the cold gate')

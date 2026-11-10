"""Verify the optional restricted profile's actual pinned-Tailwind output."""
from pathlib import Path
import json
import os
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
source = (root / 'design/restricted-theme.css').read_text().replace('\"../crates/app-ui/src\"', json.dumps((root / 'crates/app-ui/src').as_posix()))
with tempfile.TemporaryDirectory(prefix='design-profile-') as temporary:
    css = Path(temporary) / 'input.css'
    output = Path(temporary) / 'output.css'
    css.write_text(source + '\n@source inline("bg-canvas text-ink rounded-control bg-slate-900 rounded-xl");\n')
    subprocess.run([str(root / ('.tools/tailwindcss.exe' if os.name == 'nt' else '.tools/tailwindcss')), '-i', str(css), '-o', str(output), '--minify'], check=True)
    result = output.read_text()
    for selector in ['.bg-canvas', '.text-ink', '.rounded-control']:
        if selector not in result:
            raise SystemExit('Missing semantic utility: ' + selector)
    for selector in ['.bg-slate-900', '.rounded-xl']:
        if selector in result:
            raise SystemExit('Unexpected default utility: ' + selector)
print('PASS: optional restricted profile emits semantic utilities and omits reset defaults')

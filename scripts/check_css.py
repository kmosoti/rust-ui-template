"""Verify shared component classes are present in the single generated stylesheet."""
from pathlib import Path
css = Path('styles/generated.css').read_text()
for selector in ['.bg-brand', '.text-brand', '.font-bold', '.rounded-2xl']:
    if selector not in css:
        raise SystemExit(f'Missing Tailwind selector: {selector}')
print('PASS: shared UI selectors present')

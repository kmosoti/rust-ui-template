const assert = require('node:assert/strict');
const fs = require('node:fs');
const css = fs.readFileSync('styles/generated.css', 'utf8');
for (const selector of ['.bg-brand', '.text-brand', '.font-bold']) {
  assert.ok(css.includes(selector), `missing Tailwind selector: ${selector}`);
}

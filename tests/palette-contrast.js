() => {
  const root = document.querySelector('[data-palette]');
  // Resolve actual CSS variables in the live document, including inherited overrides.
  const probe = document.createElement('span'); root.append(probe);
  const rgb = name => { probe.style.color = `var(--color-${name})`; return getComputedStyle(probe).color.match(/[\d.]+/g).slice(0,3).map(Number); };
  const luminance = value => value.map(v => { v/=255; return v<=.04045?v/12.92:((v+.055)/1.055)**2.4; }).reduce((s,v,i)=>s+v*[.2126,.7152,.0722][i],0);
  const checks = [];
  const pair = (fg,bg,minimum) => { const a=luminance(rgb(fg)),b=luminance(rgb(bg)); checks.push({fg,bg,minimum,ratio:(Math.max(a,b)+.05)/(Math.min(a,b)+.05)}); };
  for (const bg of ['canvas','sidebar','panel','raised']) {
    for (const fg of ['ink','muted','brand','info','success','warning','danger']) pair(fg,bg,4.5);
    pair('control',bg,3); pair('brand',bg,3); // Required boundaries/focus indicators.
  }
  pair('action-ink','brand',4.5); pair('action-ink','brand-hover',4.5);
  const action = document.querySelector('button[type=submit]');
  const actual = getComputedStyle(action);
  const parse = value => value.match(/[\d.]+/g).slice(0,3).map(Number);
  const a=luminance(parse(actual.color)), b=luminance(parse(actual.backgroundColor));
  checks.push({fg:'actual action text',bg:'actual hovered action',minimum:4.5,ratio:(Math.max(a,b)+.05)/(Math.min(a,b)+.05)});
  const hoverEnabled = matchMedia('(hover: hover)').matches;
  const hoverMatches = parse(actual.backgroundColor).every((value,i)=>value===rgb(hoverEnabled ? 'brand-hover' : 'brand')[i]);
  const focus = getComputedStyle(document.activeElement);
  const focusMatches = parse(focus.outlineColor).every((value,i)=>value===rgb('brand')[i]);
  probe.remove();
  return {hoverEnabled, hoverMatches, focusMatches, palette:root.dataset.palette, colorScheme:getComputedStyle(root).colorScheme, checks, failures:checks.filter(c=>c.ratio<c.minimum)};
}

() => {
  const visible = e => { const r=e.getBoundingClientRect(), s=getComputedStyle(e); return r.width>0 && r.height>0 && s.visibility!=='hidden' && s.display!=='none'; };
  const name = e => e.id ? `#${e.id}` : `${e.tagName.toLowerCase()}${e.getAttribute('data-layout-region') ? `[data-layout-region="${e.getAttribute('data-layout-region')}"]` : ''}`;
  const rectangle = e => { const r=e.getBoundingClientRect(); return {x:r.x,y:r.y+scrollY,width:r.width,height:r.height}; };
  const allowed = (e, type) => { const marked=e.closest(`[data-ui-${type}="allow"]`); return marked && !!marked.dataset.uiReason; };
  const elements=[...document.body.querySelectorAll('*')].filter(visible);
  const clippedText=elements.filter(e => !e.children.length && e.textContent.trim() && !e.matches('input,textarea,select,script,style') && e.clientWidth>0 && !allowed(e,'overflow') && (e.scrollWidth>e.clientWidth+2 || (getComputedStyle(e).overflowY!=='visible' && e.scrollHeight>e.clientHeight+2))).map(e=>({element:name(e),...rectangle(e),scrollWidth:e.scrollWidth,scrollHeight:e.scrollHeight}));
  const controls=elements.filter(e=>e.matches('input,textarea,select,button'));
  const escapedControls=controls.filter(e=>{ const r=e.getBoundingClientRect(), p=e.parentElement.getBoundingClientRect(); return p.width>0 && !allowed(e,'overflow') && (r.left<p.left-2 || r.right>p.right+2); }).map(e=>({element:name(e),...rectangle(e),parent:name(e.parentElement),parentBox:rectangle(e.parentElement)}));
  const regions=elements.filter(e=>e.hasAttribute('data-layout-region'));
  const overlaps=[];
  for(let i=0;i<regions.length;i++) for(let j=i+1;j<regions.length;j++) {
    const a=regions[i],b=regions[j];
    if(a.parentElement!==b.parentElement || allowed(a,'overlap') || allowed(b,'overlap')) continue;
    const x=a.getBoundingClientRect(), y=b.getBoundingClientRect();
    if(Math.min(x.right,y.right)-Math.max(x.left,y.left)>2 && Math.min(x.bottom,y.bottom)-Math.max(x.top,y.top)>2) overlaps.push([name(a),name(b)]);
  }
  const depth=e=>{let n=0;for(;e;e=e.parentElement)n++;return n;};
  const bordered=e=>{const s=getComputedStyle(e);return ['borderTopWidth','borderRightWidth','borderBottomWidth','borderLeftWidth'].some(k=>parseFloat(s[k])>0);};
  return {
    viewport:{width:innerWidth,height:innerHeight}, page:{width:document.documentElement.scrollWidth,height:document.documentElement.scrollHeight},
    horizontalOverflow:document.documentElement.scrollWidth>innerWidth+2,
    clippedText, escapedControls, overlaps, regionCount:regions.length, maxDomDepth:Math.max(0,...elements.map(depth)),
    // Advisory, not an aesthetic failure: control borders and structural rules can be legitimate.
    nestedBorders:elements.filter(e=>bordered(e)&&e.parentElement.closest('main')&&bordered(e.parentElement)).map(name),
    typography:elements.filter(e=>e.matches('h1,h2,h3,button')).map(e=>{const s=getComputedStyle(e);return {element:name(e),text:e.textContent.trim(),font:s.fontFamily,size:s.fontSize,weight:s.fontWeight,lineHeight:s.lineHeight,...rectangle(e)};}),
    controls:controls.map(e=>({element:name(e),...rectangle(e)})),
    regions:regions.map(e=>({element:name(e),...rectangle(e)}))
  };
}

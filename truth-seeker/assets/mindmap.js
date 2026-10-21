// Truth Seeker mind map: a left-to-right flow in columns, from where the work starts to where it ends.
// The page defines three globals before this script runs (see SKILL.md, "Mind map data"):
//   COLS = [[heading, [nodeId, ...], role?], ...]   role: 'start' | 'end' | 'planned' (optional)
//   N    = [[id, label, kind, status, plainEnglish, technical], ...]
//          kind: 'you' | 'source' | 'step' | 'store' | 'search' | 'output' | 'monitor' | 'planned'
//          status: 'w' wired/live · 'h' half-built · 'p' planned · 'g' ghost
//   E    = [[fromId, toId], ...]   data or work flowing from one part to the next
// Needs d3 v7 (cdnjs) and the brand.css variables (Signal theme: --k-* kind colours, --ok/--part/--stop status). Draws into #mm-svg inside #mm-wrap, tooltip #mm-tip, filters #mm-filters.
let mmDone = false;
function drawMindMap() {
  if (mmDone || typeof d3 === 'undefined') return; mmDone = true;
  const css = getComputedStyle(document.documentElement), v = n => css.getPropertyValue(n).trim();
  const C = {ground: v('--ground'), raised: v('--raised'), sunk: v('--sunk'), line: v('--line'), line2: v('--line2'),
             text: v('--text'), muted: v('--muted'), dim: v('--dim'), yellow: v('--yellow'),
             ok: v('--ok'), part: v('--part'), stop: v('--stop')};
  const KIND = {you: v('--yellow'), source: v('--k-source'), step: v('--k-step'), store: v('--k-store'), engine: v('--k-engine'),
                output: v('--k-output'), search: v('--k-search'), monitor: v('--k-monitor'), planned: v('--muted')};
  const wrap = document.getElementById('mm-wrap'), W = wrap.clientWidth, H = wrap.clientHeight;
  const colW = 196, rowH = 54, top = 78;
  const col = {}, row = {};
  COLS.forEach(([, ids], c) => ids.forEach((id, r) => { col[id] = c; row[id] = r; }));
  const tallest = Math.max(...COLS.map(([, ids]) => ids.length));
  const nodes = N.filter(n => n[0] in col).map(([id,label,kind,s,d,t]) => {
    const n = COLS[col[id]][1].length;
    return {id,label,kind,s,d,t, x: 64 + col[id]*colW, y: top + (row[id] + (tallest - n)/2) * rowH};
  });
  const byId = Object.fromEntries(nodes.map(n => [n.id, n]));
  const links = E.map(([s,t]) => ({source: byId[s], target: byId[t]})).filter(l => l.source && l.target);
  const fwd = l => l.target.x > l.source.x;
  const svg = d3.select('#mm-svg').attr('viewBox', [0,0,W,H]).attr('role','img').attr('aria-label','Flow map, read left to right');
  const defs = svg.append('defs');
  [['mmarr', C.line2], ['mmarr-hot', C.yellow]].forEach(([id, col]) => defs.append('marker').attr('id', id)
     .attr('viewBox','0 0 10 10').attr('refX',9).attr('refY',5).attr('markerWidth',6).attr('markerHeight',6).attr('orient','auto')
     .append('path').attr('d','M1,1 L8,5 L1,9').attr('fill','none').attr('stroke', col).attr('stroke-width',1.4));
  const g = svg.append('g');
  const zoom = d3.zoom().scaleExtent([0.3,3]).on('zoom', e => g.attr('transform', e.transform));
  svg.call(zoom);
  // column bands; the start and end columns get an ink frame so the reader sees where it begins and ends
  const bandH = top + tallest*rowH;
  COLS.forEach(([name, , role], c) => {
    const x = 64 + c*colW - 28, edge = role === 'start' || role === 'end';
    g.append('rect').attr('x', x).attr('y', 22).attr('width', colW - 14).attr('height', bandH)
      .attr('fill', c % 2 ? C.ground : C.raised).attr('fill-opacity', role === 'planned' ? .5 : 1)
      .attr('stroke', edge ? C.yellow : 'none').attr('stroke-width', 1.2);
    g.append('text').text(`${String(c+1).padStart(2,'0')} ${name}`).attr('x', x + 12).attr('y', 46)
      .attr('font-size', 10).attr('letter-spacing', 1.2).attr('font-family','JetBrains Mono, monospace')
      .attr('fill', edge ? C.yellow : C.muted).style('text-transform','uppercase');
  });
  const curve = l => {
    const sx = l.source.x + 10, sy = l.source.y, tx = l.target.x - 10, ty = l.target.y;
    if (fwd(l)) { const m = (sx + tx) / 2; return `M${sx},${sy} C${m},${sy} ${m},${ty} ${tx},${ty}`; }
    const dip = Math.max(sy, ty) + 36;   // loops back arc underneath, dotted
    return `M${l.source.x},${sy+9} C${l.source.x},${dip} ${l.target.x},${dip} ${l.target.x},${ty+9}`;
  };
  const link = g.append('g').selectAll('path').data(links).join('path').attr('d', curve).attr('fill','none')
    .attr('stroke', C.line2).attr('stroke-width', l => fwd(l) ? 1.1 : .9)
    .attr('stroke-dasharray', l => fwd(l) ? null : '2 3').attr('marker-end','url(#mmarr)');
  const node = g.append('g').selectAll('g').data(nodes).join('g')
    .attr('transform', d => `translate(${d.x},${d.y})`).style('cursor','pointer');
  // colour + shape = kind (store circle, search diamond, others square); the small dot = status (green live, orange half-built, red ghost)
  const fill = d => d.s === 'p' ? C.ground : KIND[d.kind] || C.muted;
  const stroke = d => d.s === 'g' ? C.stop : d.s === 'p' ? C.muted : C.ground;
  const big = d => d.kind === 'you';
  node.each(function(d) {
    const el = d3.select(this), r = big(d) ? 9 : 7;
    const shape = d.kind === 'store' ? el.append('circle').attr('r', r)
                : d.kind === 'search' ? el.append('rect').attr('x',-r).attr('y',-r).attr('width',2*r).attr('height',2*r).attr('transform','rotate(45)')
                : el.append('rect').attr('x',-r).attr('y',-r).attr('width',2*r).attr('height',2*r);
    shape.attr('fill', fill(d)).attr('stroke', stroke(d)).attr('stroke-width', 1.2)
         .attr('stroke-dasharray', d.s === 'p' ? '2 2' : null);
    if (d.s !== 'p' && d.kind !== 'you') el.append('circle').attr('cx', 9).attr('cy', -9).attr('r', 3.4)
      .attr('fill', d.s === 'w' ? C.ok : d.s === 'h' ? C.part : C.stop).attr('stroke', C.ground).attr('stroke-width', 1);
  });
  node.append('text').text(d => d.label).attr('x', d => big(d) ? 16 : 13).attr('y', 4)
    .attr('font-size', d => big(d) ? 14 : 11).attr('font-weight', d => big(d) ? 800 : 500)
    .attr('letter-spacing', d => big(d) ? '-0.02em' : null)
    .attr('font-family','Custom Sans, Inter Tight, Helvetica Neue, Arial, sans-serif')
    .style('font-variation-settings', d => big(d) ? '"STYL" 0' : '"STYL" 100')
    .attr('fill', d => d.s === 'p' ? C.dim : d.s === 'g' ? C.stop : big(d) ? C.yellow : C.text);
  const tip = document.getElementById('mm-tip');
  const st = {w:'LIVE', h:'HALF-BUILT', p:'PLANNED', g:'GHOST'};
  const esc = s => String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;');
  node.on('mouseenter', (e,d) => {
      tip.innerHTML = `<b>${esc(d.label)}</b>${esc(d.d)}<span class="tech">${st[d.s]} ─ ${esc(d.t)}</span>`;
      tip.style.display = 'block';
      const nb = new Set([d.id]); links.forEach(l => { if (l.source.id===d.id) nb.add(l.target.id); if (l.target.id===d.id) nb.add(l.source.id); });
      node.attr('opacity', n => nb.has(n.id) ? 1 : 0.15);
      link.attr('stroke', l => (l.source.id===d.id||l.target.id===d.id) ? C.yellow : C.line)
          .attr('marker-end', l => (l.source.id===d.id||l.target.id===d.id) ? 'url(#mmarr-hot)' : 'url(#mmarr)');
    })
    .on('mousemove', e => { const r = wrap.getBoundingClientRect(); tip.style.left = Math.min(e.clientX - r.left + 14, r.width - 350) + 'px'; tip.style.top = (e.clientY - r.top + 14) + 'px'; })
    .on('mouseleave', () => { tip.style.display = 'none'; applyFilter(cur); });
  const fullW = 40 + COLS.length*colW, fullH = 24 + bandH + 24, k = Math.min(W/fullW, H/fullH, 1);
  svg.call(zoom.transform, d3.zoomIdentity.translate(Math.max(0, (W - fullW*k)/2), 6).scale(k));
  let cur = 'all';
  function applyFilter(f) {
    cur = f;
    const hit = d => f === 'all' || d.s === f;
    node.attr('opacity', d => hit(d) ? 1 : 0.12);
    link.attr('stroke', C.line2).attr('marker-end','url(#mmarr)')
        .attr('opacity', l => f === 'all' || hit(l.source) || hit(l.target) ? 1 : 0.1);
    document.querySelectorAll('#mm-filters button').forEach(b => b.classList.toggle('on', b.dataset.k === f));
  }
  const fb = document.getElementById('mm-filters');
  [['all','All'],['w','Live'],['h','Half-built'],['p','Planned'],['g','Ghosts']]
    .filter(([k]) => k === 'all' || nodes.some(n => n.s === k))
    .forEach(([k,l]) => { const b = document.createElement('button'); b.type = 'button'; b.textContent = l; b.dataset.k = k; b.onclick = () => applyFilter(k); fb.appendChild(b); });
  applyFilter('all');
}

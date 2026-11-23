/*
 * Co-author network for research-overview.html (ported from the internal Research Overview page,
 * version 2, November 2026). Plain SVG with a small deterministic force layout; no libraries.
 *
 * CoauthorNetwork.mount(root, opts)
 *   root  element holding the controls and the drawing (see the #network section of the page)
 *   opts  { pubs:   [{id, year, theme (1-based), title, venue, link}],
 *           coauth: {record id: [co-author names]}  (data/coauthors.json),
 *           themes: {theme number: name},
 *           color:  theme number -> CSS color,
 *           piName: label of the PI node }
 * Clicking a name highlights its links and lists the papers shared with Dr. Hur below the map.
 */
(function () {
  const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

  function mount(root, opts) {
    const { pubs, coauth, themes, color: col, piName: PI_NAME } = opts;
    const $ = sel => root.querySelector(sel);
    const svg = $('svg.net'), tip = $('.net-tip'), note = $('.net-note'), legend = $('.net-legend'), shared = $('.net-shared');
    const y0 = $('input.y0'), y1 = $('input.y1');
    let netN = 50, netW = 2, netFocus = null, netPI = true, netMix = 'mix', netCache = { key: '', pos: null };

    const ys = pubs.filter(p => coauth[p.id]).map(p => p.year);
    if (!ys.length) { root.hidden = true; return; }
    const a = Math.min(...ys), b = Math.max(...ys);
    [y0, y1].forEach(e => { e.min = a; e.max = b; });
    y0.value = Math.max(a, b - 14); y1.value = b;
    const fill = () => {
      const lo = (+y0.value - a) / (b - a) * 100, hi = (+y1.value - a) / (b - a) * 100;
      const f = $('.dual-fill'); f.style.left = lo + '%'; f.style.width = (hi - lo) + '%';
      $('output.y0o').value = y0.value; $('output.y1o').value = y1.value;
      y0.style.zIndex = (+y0.value >= b - 1) ? 3 : 2;
    };
    y0.addEventListener('input', () => { if (+y0.value > +y1.value) y0.value = y1.value; fill(); draw(); });
    y1.addEventListener('input', () => { if (+y1.value < +y0.value) y1.value = y0.value; fill(); draw(); });
    fill();
    const seg = (attr, set) => root.querySelectorAll(`[${attr}]`).forEach(bt => bt.addEventListener('click', () => {
      set(bt.getAttribute(attr));
      root.querySelectorAll(`[${attr}]`).forEach(x => x.setAttribute('aria-pressed', x === bt));
    }));
    seg('data-n', v => { netN = +v; draw(); });
    seg('data-w', v => { netW = +v; draw(); });
    seg('data-mix', v => { netMix = v; draw(true); });
    $('.net-pi').addEventListener('click', e => { netPI = !netPI; e.currentTarget.setAttribute('aria-pressed', netPI); draw(); });
    $('.net-reset').addEventListener('click', () => { netCache = { key: '', pos: null }; draw(); });
    legend.innerHTML = Object.keys(themes).map(t =>
      `<span class="inline-flex items-center gap-1.5"><span class="h-2.5 w-2.5 rounded-sm" style="background:${col(t)}"></span>${esc(themes[t])}</span>`).join('');

    function showShared(name, ids) {
      if (!name) { shared.hidden = true; shared.innerHTML = ''; return; }
      const list = pubs.filter(p => ids.includes(p.id)).sort((x, y) => y.year - x.year);
      shared.hidden = false;
      shared.innerHTML = `<p class="font-semibold text-gray-900 mb-1">${list.length} ${list.length === 1 ? 'paper' : 'papers'} with ${esc(name)}, ${y0.value} to ${y1.value} <button type="button" class="ml-2 text-xs font-normal text-primary-700 hover:underline net-clear">Clear</button></p>` +
        '<ol class="list-decimal pl-5 space-y-1">' + list.map(p => `<li>${p.link ? `<a href="${esc(p.link)}" target="_blank" rel="noopener" class="hover:text-primary-700 hover:underline">${esc(p.title)}</a>` : esc(p.title)} <span class="text-gray-500 italic">${esc(p.venue || '')}${p.venue ? ', ' : ''}${p.year}</span></li>`).join('') + '</ol>';
      shared.querySelector('.net-clear').addEventListener('click', () => { netFocus = null; draw(true); });
    }

    function draw(keep) {
      const lo = +y0.value, hi = +y1.value;
      const pool = pubs.filter(p => coauth[p.id] && p.year >= lo && p.year <= hi);
      const A = {};
      pool.forEach(p => coauth[p.id].forEach(n => {
        const o = A[n] || (A[n] = { n: 0, th: {}, ids: [], y0: 9999, y1: 0 });
        o.n++; o.th[p.theme] = (o.th[p.theme] || 0) + 1; o.ids.push(p.id); o.y0 = Math.min(o.y0, p.year); o.y1 = Math.max(o.y1, p.year);
      }));
      const names = Object.keys(A).sort((x, y) => A[y].n - A[x].n || x.localeCompare(y)).slice(0, netN);
      if (netPI && pool.length) {
        A[PI_NAME] = { n: pool.length, th: pool.reduce((o, p) => (o[p.theme] = (o[p.theme] || 0) + 1, o), {}), ids: pool.map(p => p.id),
                       y0: Math.min(...pool.map(p => p.year)), y1: Math.max(...pool.map(p => p.year)), pi: true };
        names.unshift(PI_NAME);
      }
      const idx = Object.fromEntries(names.map((n, i) => [n, i]));
      const W = Math.max(640, svg.parentElement.clientWidth - 16), H = Math.min(620, Math.max(420, W * 0.62));
      const E = {};
      pool.forEach(p => {
        const m = [...new Set(coauth[p.id])].filter(n => n in idx);
        for (let i = 0; i < m.length; i++) for (let j = i + 1; j < m.length; j++) {
          const k = idx[m[i]] < idx[m[j]] ? m[i] + '|' + m[j] : m[j] + '|' + m[i]; E[k] = (E[k] || 0) + 1;
        }
      });
      if (netPI && PI_NAME in idx) names.forEach(n => { if (n !== PI_NAME && A[n].n >= netW) E[PI_NAME + '|' + n] = A[n].n; });
      const edges = Object.entries(E).filter(([, w]) => w >= netW).map(([k, w]) => { const [s, d] = k.split('|'); return { s: idx[s], d: idx[d], w }; });
      const N = names.length;
      if (!N) { svg.innerHTML = ''; note.textContent = 'No co-authored papers in this range.'; showShared(null); return; }

      // force layout, deterministic
      const ckey = [lo, hi, netN, netW, W, netPI].join('|'); const reuse = keep && netCache.key === ckey && netCache.pos;
      const nodes = names.map((n, i) => {
        if (reuse && netCache.pos[n]) return { ...netCache.pos[n], vx: 0, vy: 0 };
        const ang = 2 * Math.PI * i / N, r = Math.min(W, H) * 0.36;
        return { x: W / 2 + r * Math.cos(ang), y: H / 2 + r * Math.sin(ang), vx: 0, vy: 0 };
      });
      const k = Math.sqrt(W * H / N) * 0.9; let temp = W / 10;
      const deg = new Array(N).fill(0); edges.forEach(e => { deg[e.s] += e.w; deg[e.d] += e.w; });
      for (let it = 0; it < (reuse ? 0 : 260); it++) {
        for (let i = 0; i < N; i++) { nodes[i].vx = 0; nodes[i].vy = 0; }
        for (let i = 0; i < N; i++) for (let j = i + 1; j < N; j++) {
          let dx = nodes[i].x - nodes[j].x, dy = nodes[i].y - nodes[j].y, d = Math.hypot(dx, dy);
          if (d < 0.5) { dx = (i - j) * 0.37; dy = (j % 3 - 1) * 0.21; d = Math.hypot(dx, dy); }
          if (d > 3 * k) continue;
          const f = k * k / d * ((deg[i] && deg[j]) ? 1 : 0.35); dx /= d; dy /= d;
          nodes[i].vx += dx * f; nodes[i].vy += dy * f; nodes[j].vx -= dx * f; nodes[j].vy -= dy * f;
        }
        edges.forEach(e => {
          let dx = nodes[e.s].x - nodes[e.d].x, dy = nodes[e.s].y - nodes[e.d].y; const d = Math.hypot(dx, dy) || 0.01;
          const f = d * d / k * Math.log(1 + e.w) * 0.6; dx /= d; dy /= d;
          nodes[e.s].vx -= dx * f; nodes[e.s].vy -= dy * f; nodes[e.d].vx += dx * f; nodes[e.d].vy += dy * f;
        });
        nodes.forEach((nd, i) => {
          const g = deg[i] ? 0.16 : 0.3; nd.vx += (W / 2 - nd.x) * g; nd.vy += (H / 2 - nd.y) * g;
          const v = Math.hypot(nd.vx, nd.vy) || 0.01, s = Math.min(v, temp) / v;
          nd.x = Math.max(-W, Math.min(2 * W, nd.x + nd.vx * s)); nd.y = Math.max(-H, Math.min(2 * H, nd.y + nd.vy * s));
        });
        if (netPI && PI_NAME in idx) { nodes[idx[PI_NAME]].x = W / 2; nodes[idx[PI_NAME]].y = H / 2; }
        temp *= 0.975;
      }
      // fit connected nodes into the drawing; park isolated or paired nodes in a strip at the bottom
      const par = nodes.map((_, i) => i); const find = x => par[x] === x ? x : (par[x] = find(par[x]));
      edges.forEach(e => { par[find(e.s)] = find(e.d); });
      const csize = {}; nodes.forEach((_, i) => { const r = find(i); csize[r] = (csize[r] || 0) + 1; });
      const piI = (netPI && PI_NAME in idx) ? idx[PI_NAME] : -1;
      const small = i => csize[find(i)] < 3 && i !== piI;
      const iso = nodes.map((_, i) => i).filter(small).sort((x, y) => find(x) - find(y) || x - y);
      const con = nodes.map((_, i) => i).filter(i => !small(i) && i !== piI);
      const perRow = Math.max(1, Math.floor((W - 80) / 110)), rows = iso.length ? Math.ceil(iso.length / perRow) : 0, strip = rows ? rows * 30 + 14 : 0;
      if (!reuse && con.length) {
        const xs = con.map(i => nodes[i].x), ysn = con.map(i => nodes[i].y);
        const x0 = Math.min(...xs), x1 = Math.max(...xs), yb0 = Math.min(...ysn), yb1 = Math.max(...ysn);
        const sc = Math.min((W - 150) / Math.max(1, x1 - x0), (H - strip - 60) / Math.max(1, yb1 - yb0), 1.6);
        const ox = (W - 110 - 40 - (x1 - x0) * sc) / 2 + 40, oy = (H - strip - 30 - (yb1 - yb0) * sc) / 2 + 30;
        con.forEach(i => { nodes[i].x = ox + (nodes[i].x - x0) * sc; nodes[i].y = oy + (nodes[i].y - yb0) * sc; });
      }
      if (!reuse && piI >= 0) { nodes[piI].x = (W - 110 + 40) / 2; nodes[piI].y = (H - strip) / 2 + 10; }
      if (!reuse) iso.forEach((i, j) => {
        const r = Math.floor(j / perRow), c = j % perRow, nIn = Math.min(perRow, iso.length - r * perRow);
        nodes[i].x = 40 + (c + 0.5) * (W - 80) / nIn; nodes[i].y = H - strip + 22 + r * 30;
      });

      svg.setAttribute('viewBox', `0 0 ${W} ${H}`); svg.setAttribute('width', W); svg.setAttribute('height', H);
      const maxCo = Math.max(...names.filter(n => !A[n].pi).map(n => A[n].n), 1);
      const radOf = n => A[n].pi ? 36 : 4.5 + 23.5 * Math.pow(A[n].n / maxCo, 0.7);
      const dom = n => Object.entries(A[n].th).sort((x, y) => y[1] - x[1])[0][0];
      const focusSet = netFocus !== null && names.includes(netFocus)
        ? new Set([netFocus, ...edges.filter(e => names[e.s] === netFocus || names[e.d] === netFocus).map(e => names[e.s] === netFocus ? names[e.d] : names[e.s])]) : null;
      let s = '';
      edges.forEach(e => {
        const hiE = focusSet && (names[e.s] === netFocus || names[e.d] === netFocus), dim = focusSet && !hiE;
        s += `<line class="${hiE ? 'hi' : dim ? 'dim' : ''}" data-s="${e.s}" data-d="${e.d}" x1="${nodes[e.s].x.toFixed(1)}" y1="${nodes[e.s].y.toFixed(1)}" x2="${nodes[e.d].x.toFixed(1)}" y2="${nodes[e.d].y.toFixed(1)}" stroke-width="${Math.min(6, 0.6 + Math.sqrt(e.w))}"/>`;
      });
      const labelMin = N > 55 ? A[names[Math.min(N - 1, 40)]].n : 0;
      const pie = (n, r, force) => {
        const e = Object.entries(A[n].th).map(([kk, v]) => [+kk, v]).sort((x, y) => x[0] - y[0]); const tot = e.reduce((u, x) => u + x[1], 0);
        if (!force && (netMix !== 'mix' || e.length < 2 || r < 6.5)) return `<circle class="v" r="${r.toFixed(1)}" fill="${col(dom(n))}"/>`;
        let a0 = -Math.PI / 2, o = '';
        e.forEach(([kk, v]) => {
          const a1 = a0 + 2 * Math.PI * v / tot;
          o += `<path d="M0 0L${(r * Math.cos(a0)).toFixed(2)} ${(r * Math.sin(a0)).toFixed(2)}A${r.toFixed(1)} ${r.toFixed(1)} 0 ${(a1 - a0) > Math.PI ? 1 : 0} 1 ${(r * Math.cos(a1)).toFixed(2)} ${(r * Math.sin(a1)).toFixed(2)}Z" fill="${col(kk)}"/>`;
          a0 = a1;
        });
        return o + `<circle class="v ring" r="${r.toFixed(1)}" fill="none"/>`;
      };
      names.forEach((n, i) => {
        const nd = nodes[i], dim = focusSet && !focusSet.has(n), r = radOf(n);
        s += `<g class="n ${dim ? 'dim' : ''} ${A[n].pi ? 'pi' : ''}" data-i="${i}" transform="translate(${nd.x.toFixed(1)},${nd.y.toFixed(1)})"><circle class="hit" r="${(r + 7).toFixed(1)}" fill="transparent" stroke="none"/>` +
          (A[n].pi
            ? `${pie(n, r, true)}<circle class="v" r="${(r * 0.66).toFixed(1)}" fill="#fde047" stroke="#111827" stroke-width="1.5"/><circle class="v" r="${r.toFixed(1)}" fill="none" stroke="#111827" stroke-width="3"/><text y="4" text-anchor="middle" class="pi-label">${esc(n.replace(/^Dr\. /, ''))}</text>`
            : pie(n, r) + ((A[n].n >= labelMin || n === netFocus) ? `<text x="${(r + 3).toFixed(1)}" y="4">${esc(n)} <tspan class="cnt">${A[n].n}</tspan></text>` : '')) + '</g>';
      });
      if (iso.length) s += `<line class="sep" x1="20" x2="${W - 20}" y1="${H - strip - 6}" y2="${H - strip - 6}" stroke-dasharray="3 4"/><text x="${W - 24}" y="${H - strip + 4}" text-anchor="end" class="sep-label">isolated or paired at this threshold</text>`;
      svg.innerHTML = s;
      netCache = { key: ckey, pos: Object.fromEntries(names.map((n, i) => [n, nodes[i]])) };

      svg.querySelectorAll('g.n').forEach(g => {
        const n = names[+g.dataset.i], o = A[n];
        g.addEventListener('mousemove', ev => {
          const r = svg.parentElement.getBoundingClientRect(); tip.hidden = false;
          const th = Object.entries(o.th).sort((x, y) => y[1] - x[1]).map(([t, c]) => `<span style="display:inline-block;width:8px;height:8px;border-radius:2px;background:${col(t)};margin-right:5px"></span>${esc(themes[t])} (${c})`).join('<br>');
          tip.innerHTML = `<b>${esc(n)}</b><br>${o.n} ${o.pi ? 'paper' : 'shared paper'}${o.n > 1 ? 's' : ''}, ${o.y0 === o.y1 ? o.y0 : o.y0 + ' to ' + o.y1}<br>${th}<br><span style="opacity:.7">click to list the shared papers; click again to clear</span>`;
          const tw = tip.offsetWidth, thh = tip.offsetHeight, px = ev.clientX - r.left, py = ev.clientY - r.top;
          let lx = px + 26, ty = py + 22;
          if (lx + tw > r.width - 6) lx = px - tw - 18; if (lx < 6) lx = Math.max(6, Math.min(r.width - tw - 6, px - tw / 2));
          if (ty + thh > r.height - 6) ty = py - thh - 16; if (ty < 6) ty = 6;
          tip.style.left = lx + 'px'; tip.style.top = ty + 'px';
        });
        g.addEventListener('mouseleave', () => { tip.hidden = true; });
        g._toggle = () => { netFocus = netFocus === n ? null : n; draw(true); };
      });
      // drag nodes; a click without movement toggles the highlight
      svg.style.touchAction = 'none';
      svg.querySelectorAll('g.n').forEach(g => {
        const i = +g.dataset.i;
        g.addEventListener('pointerdown', ev => {
          ev.preventDefault(); g.setPointerCapture(ev.pointerId);
          const pt = svg.createSVGPoint(); const toSvg = e => { pt.x = e.clientX; pt.y = e.clientY; return pt.matrixTransform(svg.getScreenCTM().inverse()); };
          const p0 = toSvg(ev), ox = nodes[i].x - p0.x, oy = nodes[i].y - p0.y; let moved = false;
          const mv = e => {
            const p = toSvg(e); const nx = Math.max(12, Math.min(W - 12, p.x + ox)), ny = Math.max(12, Math.min(H - 12, p.y + oy));
            if (Math.hypot(p.x - p0.x, p.y - p0.y) > 4) moved = true; if (!moved) return;
            nodes[i].x = nx; nodes[i].y = ny; g.setAttribute('transform', `translate(${nx.toFixed(1)},${ny.toFixed(1)})`);
            svg.querySelectorAll(`line[data-s="${i}"]`).forEach(l => { l.setAttribute('x1', nx.toFixed(1)); l.setAttribute('y1', ny.toFixed(1)); });
            svg.querySelectorAll(`line[data-d="${i}"]`).forEach(l => { l.setAttribute('x2', nx.toFixed(1)); l.setAttribute('y2', ny.toFixed(1)); });
            g.parentNode.appendChild(g);
          };
          const up = e => {
            g.removeEventListener('pointermove', mv); g.removeEventListener('pointerup', up); g.removeEventListener('pointercancel', up);
            if (!moved && e.type === 'pointerup' && g._toggle) g._toggle();
          };
          g.addEventListener('pointermove', mv); g.addEventListener('pointerup', up); g.addEventListener('pointercancel', up);
        });
      });
      const hasPI = netPI && PI_NAME in idx, totalCo = Object.keys(A).length - (netPI && PI_NAME in A ? 1 : 0);
      note.textContent = `${pool.length} papers from ${lo} to ${hi} with ${totalCo} distinct co-authors; showing the ${N - (hasPI ? 1 : 0)} most frequent${netPI ? ' plus Dr. Hur' : ''}, linked when they share ${netW === 1 ? 'a paper' : netW + ' or more papers'} (${edges.length} links). Node size and the number after each name are the papers shared with Dr. Hur in this period; ${netMix === 'mix' ? "pie slices show each co-author's papers by research area (small nodes show the main area only)" : "color is the co-author's most common research area"}.` + (netFocus ? ` Highlighting ${netFocus}.` : '');
      const f = netFocus && A[netFocus] && !A[netFocus].pi ? netFocus : null;
      showShared(f, f ? A[f].ids : []);
    }

    let rt; window.addEventListener('resize', () => { clearTimeout(rt); rt = setTimeout(() => draw(), 200); });
    draw();
  }

  window.CoauthorNetwork = { mount };
})();

/* Ripple — front end.
   Plain JavaScript on purpose: no build step, no framework, nothing to install.
   The same file can be opened, read and changed by anyone. */

const STEPS = [
  ['Notification',    'Upload or type it in'],
  ['Review fields',   'Check before scanning'],
  ['Repository',      'What will be searched'],
  ['Impact analysis', 'Grouped by production table'],
  ['Dependency map',  'Where the column goes'],
  ['Summary',         'What it means'],
  ['Reply',           'Answer the upstream team'],
];

const S = {
  step: 1, maxStep: 1, view: 'wizard',
  mode: 'email',
  health: null,
  vals: null,          // {source, changeType, changeKind, changeDesc, subject, effectiveDate, poc*, upstream:[{table,attrs}]}
  emailPreview: null,
  scan: null,
  summary: null,
  reply: null,
  savedId: null,
  manRows: [{ table: '', attrs: '' }],
  man: { source: '', changeType: '', effectiveDate: '', changeDesc: '', pocName: '', pocEmail: '', pocTeam: '' },
  busy: false,
  openGroup: 0, openRow: null, graphTab: 0,
};

const MAN_FIELDS = [
  ['source', 'Source system', 'e.g. C360'],
  ['changeType', 'Change type', 'e.g. Attribute decommission'],
  ['effectiveDate', 'Effective date', 'YYYY-MM-DD'],
  ['changeDesc', 'What is changing', 'One line describing the change'],
  ['pocName', 'Contact name', 'Who sent the notice'],
  ['pocEmail', 'Contact email', 'name@corp.example.com'],
  ['pocTeam', 'Contact team', 'e.g. C360 Data Governance'],
];

const CHANGE_KINDS = [
  ['unknown', 'Not specified'],
  ['removal', 'Attribute decommission'],
  ['value_change', 'Value format change'],
  ['type_change', 'Data type change'],
  ['rename', 'Attribute rename'],
];

// ── helpers ───────────────────────────────────────────────────────────────
const $ = (sel, root = document) => root.querySelector(sel);
const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];
const el = (tag, props = {}, ...kids) => {
  const n = Object.assign(document.createElement(tag), props);
  for (const k of kids.flat()) if (k != null) n.append(k.nodeType ? k : String(k));
  return n;
};
const x = (root, name) => root.querySelector(`[data-x="${name}"]`);
const esc = (s) => String(s ?? '');

async function api(path, opts = {}) {
  const r = await fetch(path, opts);
  if (!r.ok) {
    let msg = `${r.status}`;
    try { msg = (await r.json()).detail || msg; } catch {}
    throw new Error(msg);
  }
  return r.json();
}

function fmtDate(iso) {
  if (!iso) return '';
  const d = new Date(iso + (iso.length === 10 ? 'T00:00:00' : ''));
  if (isNaN(d)) return iso;
  return d.toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' });
}
function daysLeft(iso) {
  if (!iso) return null;
  const d = new Date(iso + 'T00:00:00');
  if (isNaN(d)) return null;
  return Math.round((d - new Date(new Date().toDateString())) / 86400000);
}
const RISK = {
  high:   ['red',   'High risk'],
  medium: ['amber', 'Medium risk'],
  low:    ['blue',  'Low risk'],
  none:   ['green', 'No impact'],
};

// ── chrome ────────────────────────────────────────────────────────────────
function renderSteps() {
  const box = $('#steps');
  box.innerHTML = '';
  STEPS.forEach(([label, sub], i) => {
    const n = i + 1;
    const on = S.view === 'wizard' && S.step === n;
    const done = n < S.maxStep && !on;
    const b = el('button', { className: `step${on ? ' on' : ''}${done ? ' done' : ''}` });
    b.disabled = n > S.maxStep;
    b.append(el('span', { className: 'n', textContent: done ? '✓' : String(n) }),
      el('span', {}, el('span', { className: 't', textContent: label }),
        el('span', { className: 's', textContent: sub })));
    b.onclick = () => { if (n <= S.maxStep) { S.view = 'wizard'; S.step = n; render(); } };
    box.append(b);
  });
  $('#navHistory').className = 'navbtn' + (S.view === 'history' ? ' on' : '');
  $('#navSettings').className = 'navbtn' + (S.view === 'settings' ? ' on' : '');
}

function renderStatus() {
  const h = S.health;
  const box = $('#status');
  box.innerHTML = '';
  if (!h) return;
  const repoOk = h.repo.exists && h.repo.files > 0;
  box.append(
    el('div', { className: 'row' },
      el('span', { className: 'dot ' + (repoOk ? 'ok' : 'warn') }),
      el('span', { textContent: repoOk ? `${h.repo.label} · ${h.repo.files} files` : 'No repository found' })),
    el('div', { className: 'row' },
      el('span', { className: 'dot ' + (h.ai.available ? 'ok' : 'off') }),
      el('span', { textContent: h.ai.available ? 'AI on' : 'AI off — rules only' })),
    el('div', { className: 'row' },
      el('span', { className: 'dot ' + (h.sqlDialect === 'generic' ? 'warn' : 'ok') }),
      el('span', { textContent: `SQL read as ${h.sqlDialect}` })),
  );
}

function setHeader(title, sub) { $('#hTitle').textContent = title; $('#hSub').textContent = sub; }

// ── step 1 ────────────────────────────────────────────────────────────────
function step1(root) {
  x(root, 'title').textContent = S.mode === 'manual' ? 'Enter the change by hand' : 'New impact notification';
  x(root, 'sub').textContent = S.mode === 'manual'
    ? 'No notification email? Type the upstream table and attributes yourself.'
    : 'Upload the notification, or paste its text. Nothing is scanned until you confirm.';
  $$('[data-mode]', root).forEach(b => {
    b.className = 'pill' + (b.dataset.mode === S.mode ? ' on' : '');
    b.onclick = () => { S.mode = b.dataset.mode; render(); };
  });
  x(root, 'emailMode').classList.toggle('hide', S.mode !== 'email');
  x(root, 'manualMode').classList.toggle('hide', S.mode !== 'manual');

  if (S.mode === 'email') {
    const ai = S.health?.ai?.available;
    x(root, 'aiState').textContent = ai
      ? `AI is on — the email is read by ${S.health.ai.model}.`
      : 'AI is off — fields are found by matching the repository catalogue.';
    const drop = $('#drop', root), file = $('#file', root);
    drop.onclick = () => file.click();
    drop.ondragover = (e) => { e.preventDefault(); drop.classList.add('over'); };
    drop.ondragleave = () => drop.classList.remove('over');
    drop.ondrop = (e) => {
      e.preventDefault(); drop.classList.remove('over');
      if (e.dataTransfer.files[0]) upload(e.dataTransfer.files[0]);
    };
    file.onchange = () => file.files[0] && upload(file.files[0]);
    $('#doPaste', root).onclick = () => {
      const text = $('#paste', root).value.trim();
      if (!text) return;
      run(async () => {
        const out = await api('/api/read-text', {
          method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text, useAI: true }),
        });
        acceptExtract(out);
      });
    };
    return;
  }

  // manual
  const rows = x(root, 'manRows');
  rows.innerHTML = '';
  S.manRows.forEach((r, i) => {
    const wrap = el('div', { className: 'pad' });
    wrap.style.cssText = 'display:flex;gap:16px;align-items:flex-end' + (i ? ';border-top:1px solid #F0F4F9' : '');
    const t = el('input', { type: 'text', className: 'mono', value: r.table, placeholder: 'CUSTOMER_DEMOGRAPHICS' });
    t.oninput = () => { r.table = t.value; updateManHint(root); };
    const a = el('input', { type: 'text', className: 'mono', value: r.attrs, placeholder: 'MARKET_CODE, MARKET_NAME' });
    a.oninput = () => { r.attrs = a.value; updateManHint(root); };
    wrap.append(
      el('div', { style: 'flex:1;min-width:0' }, el('span', { className: 'lbl', textContent: 'Upstream table name' }), t),
      el('div', { style: 'flex:1;min-width:0' }, el('span', { className: 'lbl', textContent: 'Attributes — comma separated' }), a));
    if (S.manRows.length > 1) {
      const rm = el('button', { className: 'ghost sm', textContent: 'Remove' });
      rm.onclick = () => { S.manRows.splice(i, 1); render(); };
      wrap.append(rm);
    }
    rows.append(wrap);
  });
  x(root, 'addRow').onclick = () => { S.manRows.push({ table: '', attrs: '' }); render(); };

  const fields = x(root, 'manFields');
  fields.innerHTML = '';
  MAN_FIELDS.forEach(([key, label, hint]) => {
    const inp = el('input', { type: 'text', value: S.man[key], placeholder: hint });
    inp.oninput = () => { S.man[key] = inp.value; };
    fields.append(el('div', { className: 'field' }, el('span', { className: 'lbl', textContent: label }), inp));
  });

  x(root, 'manDemo').onclick = () => {
    S.manRows = [{ table: 'CUSTOMER_DEMOGRAPHICS', attrs: 'MARKET_CODE, MARKET_NAME' },
                 { table: 'CUSTOMER_ADDRESS', attrs: 'COUNTRY_CODE' }];
    S.man = { source: 'C360', changeType: 'Value format change', effectiveDate: '2026-09-18',
      changeDesc: "Values change from ISO abbreviations to full country names ('US' becomes 'United States').",
      pocName: 'Priya Raman', pocEmail: 'priya.raman@corp.example.com', pocTeam: 'C360 Data Governance' };
    render();
  };
  x(root, 'manStart').onclick = () => startManual();
  updateManHint(root);
}

function manValid() { return S.manRows.some(r => r.table.trim() && r.attrs.trim()); }
function updateManHint(root) {
  const tables = S.manRows.filter(r => r.table.trim()).length;
  const attrs = S.manRows.reduce((a, r) => a + r.attrs.split(',').map(s => s.trim()).filter(Boolean).length, 0);
  x(root, 'manCount').textContent = tables ? `${tables} table${tables > 1 ? 's' : ''} · ${attrs} attribute${attrs === 1 ? '' : 's'}` : 'Nothing entered yet';
  const ok = manValid();
  x(root, 'manStart').disabled = !ok;
  x(root, 'manHint').textContent = ok
    ? 'Ripple will search the connected repository for these names.'
    : 'Enter at least one table name and one attribute to continue.';
}

function startManual() {
  if (!manValid()) return;
  const kind = (CHANGE_KINDS.find(([, l]) => l.toLowerCase() === S.man.changeType.trim().toLowerCase()) || ['unknown'])[0];
  S.vals = {
    source: S.man.source.trim() || 'Entered manually',
    changeType: S.man.changeType.trim() || 'Not specified',
    changeKind: kind,
    changeDesc: S.man.changeDesc.trim() || 'Entered by hand — no notification email was used.',
    subject: 'Manual impact check — ' + S.manRows.filter(r => r.table.trim()).map(r => r.table.trim()).join(', '),
    effectiveDate: S.man.effectiveDate.trim(),
    pocName: S.man.pocName.trim(), pocEmail: S.man.pocEmail.trim(), pocTeam: S.man.pocTeam.trim(),
    upstream: S.manRows.filter(r => r.table.trim()).map(r => ({
      table: r.table.trim(),
      attrs: r.attrs.split(',').map(s => s.trim()).filter(Boolean),
    })),
    extractedBy: 'manual', warnings: [],
  };
  S.emailPreview = null; S.scan = null; S.summary = null; S.savedId = null;
  goto(2);
}

function upload(f) {
  run(async () => {
    const fd = new FormData();
    fd.append('file', f);
    const out = await api('/api/read-email?useAI=true', { method: 'POST', body: fd });
    acceptExtract(out);
  });
}

function acceptExtract(out) {
  S.emailPreview = out.emailPreview || null;
  S.vals = {
    source: out.source || '', changeType: out.changeType || '', changeKind: out.changeKind || 'unknown',
    changeDesc: out.changeDesc || '', subject: out.subject || '', effectiveDate: out.effectiveDate || '',
    pocName: out.pocName || '', pocEmail: out.pocEmail || '', pocTeam: out.pocTeam || '',
    upstream: (out.upstream || []).map(u => ({ table: u.table, attrs: u.attrs || [] })),
    extractedBy: out.extractedBy || 'rules',
    warnings: out.warnings || [], aiNote: out.aiNote || '',
  };
  S.scan = null; S.summary = null; S.savedId = null;
  goto(2);
}

// ── step 2 ────────────────────────────────────────────────────────────────
function step2(root) {
  const v = S.vals;
  const manual = v.extractedBy === 'manual';
  x(root, 'title').textContent = manual ? 'Change details' : 'What Ripple read';
  x(root, 'sub').textContent = manual
    ? 'The details you entered. Edit anything before scanning.'
    : 'Check every field. Ripple scans on exactly what is here, not on the email.';
  x(root, 'by').textContent = manual ? 'Entered by you — no AI used'
    : v.extractedBy === 'ai' ? 'Read by AI — check it' : 'Found by matching the catalogue — check it';

  const warn = x(root, 'warnings'); warn.innerHTML = '';
  (v.warnings || []).forEach(w => warn.append(el('div', { className: 'note warn', textContent: w, style: 'margin-bottom:12px' })));

  const meta = x(root, 'meta'); meta.innerHTML = '';
  const dl = daysLeft(v.effectiveDate);
  const metaDefs = [
    ['Source system', 'source', 'text'],
    ['Change type', 'changeKind', 'select'],
    ['Effective date', 'effectiveDate', 'date'],
    ['Contact', 'pocName', 'text'],
  ];
  metaDefs.forEach(([label, key, type]) => {
    const card = el('div', { className: 'stat' });
    card.append(el('span', { className: 'lbl', textContent: label }));
    if (type === 'select') {
      const sel = el('select', { style: 'margin-top:7px' });
      CHANGE_KINDS.forEach(([k, l]) => sel.append(el('option', { value: k, textContent: l, selected: k === v.changeKind })));
      sel.onchange = () => { v.changeKind = sel.value; v.changeType = sel.selectedOptions[0].textContent; };
      card.append(sel);
    } else {
      const inp = el('input', { type: type === 'date' ? 'date' : 'text', value: v[key] || '', style: 'margin-top:7px' });
      inp.oninput = () => { v[key] = inp.value; };
      card.append(inp);
      if (key === 'effectiveDate' && dl !== null) {
        card.append(el('span', { className: 'badge ' + (dl <= 21 ? 'amber' : 'blue'),
          textContent: dl < 0 ? 'date has passed' : `${dl} day${dl === 1 ? '' : 's'} left`, style: 'margin-top:8px' }));
      }
      if (key === 'pocName' && v.pocEmail) card.append(el('div', { className: 'small muted', textContent: v.pocEmail, style: 'margin-top:5px' }));
    }
    meta.append(card);
  });

  const subj = x(root, 'subject'); subj.value = v.subject || ''; subj.oninput = () => { v.subject = subj.value; };
  const desc = x(root, 'desc'); desc.value = v.changeDesc || ''; desc.oninput = () => { v.changeDesc = desc.value; };

  renderUpstreamRows(root, v);
  x(root, 'addRow').onclick = () => { v.upstream.push({ table: '', attrs: [] }); render(); };
  x(root, 'next').onclick = () => goto(3);
}

function renderUpstreamRows(root, v) {
  const box = x(root, 'rows'); box.innerHTML = '';
  const tables = v.upstream.filter(u => u.table.trim()).length;
  const attrs = v.upstream.reduce((a, u) => a + (u.attrs || []).length, 0);
  x(root, 'count').textContent = `${tables} table${tables === 1 ? '' : 's'} · ${attrs} attribute${attrs === 1 ? '' : 's'}`;
  v.upstream.forEach((u, i) => {
    const wrap = el('div', { className: 'pad' });
    wrap.style.cssText = 'display:flex;gap:16px;align-items:flex-end' + (i ? ';border-top:1px solid #F0F4F9' : '');
    const t = el('input', { type: 'text', className: 'mono', value: u.table });
    t.oninput = () => { u.table = t.value; };
    const a = el('input', { type: 'text', className: 'mono', value: (u.attrs || []).join(', ') });
    a.oninput = () => { u.attrs = a.value.split(',').map(s => s.trim()).filter(Boolean); };
    const rm = el('button', { className: 'ghost sm', textContent: 'Remove' });
    rm.onclick = () => { v.upstream.splice(i, 1); render(); };
    wrap.append(
      el('div', { style: 'flex:1;min-width:0' }, el('span', { className: 'lbl', textContent: 'Upstream table' }), t),
      el('div', { style: 'flex:1;min-width:0' }, el('span', { className: 'lbl', textContent: 'Attributes' }), a), rm);
    box.append(wrap);
  });
  if (!v.upstream.length) box.append(el('div', { className: 'pad muted', textContent: 'Nothing to scan yet — add a table below.' }));
}

// ── step 3 ────────────────────────────────────────────────────────────────
function step3(root) {
  const h = S.health;
  const r = x(root, 'repo'); r.innerHTML = '';
  if (!h) return;
  r.append(el('span', { className: 'lbl', textContent: 'Repository' }));
  r.append(el('div', { className: 'mono', textContent: h.repo.label, style: 'font-size:16px;font-weight:700;color:var(--blued);margin-top:6px' }));
  r.append(el('div', { className: 'small muted', textContent: h.repo.path, style: 'margin-top:4px;word-break:break-all' }));
  const facts = [
    ['Files indexed', String(h.repo.files)],
    ['Statements understood', String(h.repo.statements)],
    ['Branch', h.repo.branch],
    ['SQL read as', h.sqlDialect],
    ['Renames followed', `${h.maxHops} hops deep`],
  ];
  const t = el('div', { style: 'margin-top:14px' });
  facts.forEach(([k, val]) => t.append(el('div', { style: 'display:flex;padding:6px 0;border-top:1px solid #F0F4F9' },
    el('span', { className: 'small muted', textContent: k, style: 'flex:1' }),
    el('span', { className: 'small', textContent: val, style: 'font-weight:700' }))));
  r.append(t);
  r.append(el('div', { className: 'note good', textContent: 'Read only. Ripple never writes to the repository.', style: 'margin-top:14px' }));

  const c = x(root, 'cat'); c.innerHTML = '';
  api('/api/catalog').then(cat => {
    c.append(el('div', { style: 'display:flex;gap:22px;margin-top:8px' },
      el('div', {}, el('div', { className: 'v', textContent: String(cat.tableCount), style: 'font-size:24px;font-weight:800' }),
        el('div', { className: 'small muted', textContent: 'tables found' })),
      el('div', {}, el('div', { className: 'v', textContent: String(cat.columnCount), style: 'font-size:24px;font-weight:800' }),
        el('div', { className: 'small muted', textContent: 'columns found' }))));
    const g = x(root, 'gaps'); g.innerHTML = '';
    if (cat.gaps.length) {
      const box = el('div', { className: 'note warn' });
      box.append(el('b', { textContent: `${cat.gaps.length} table${cat.gaps.length === 1 ? '' : 's'} Ripple could not fully read` }));
      cat.gaps.forEach(gap => box.append(el('div', { style: 'margin-top:6px' },
        el('span', { className: 'mono', textContent: gap.table }), ' — ' + gap.reason)));
      g.append(box);
    } else {
      g.append(el('div', { className: 'note good', textContent: 'Every table definition was readable.' }));
    }
  });

  x(root, 'reindex').onclick = () => run(async () => { S.health = await api('/api/reindex', { method: 'POST' }); render(); });
  x(root, 'next').onclick = () => runScan();
}

function runScan() {
  run(async () => {
    S.scan = await api('/api/scan', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ upstream: S.vals.upstream, changeKind: S.vals.changeKind || 'unknown' }),
    });
    S.summary = null; S.openGroup = 0; S.openRow = null; S.graphTab = 0;
    goto(4);
  });
}

// ── step 4 ────────────────────────────────────────────────────────────────
function step4(root) {
  const sc = S.scan;
  if (!sc) { x(root, 'progress').append(el('div', { className: 'note info', textContent: 'No scan yet.' })); return; }
  const [cls, label] = RISK[sc.risk] || RISK.none;
  x(root, 'risk').append(el('span', { className: 'badge ' + cls, textContent: label }));

  x(root, 'progress').append(el('div', { className: 'note info' },
    `Read ${sc.filesScanned} files in ${S.health.repo.label}. `,
    el('b', { textContent: `${sc.filesMatched} mention the names you confirmed.` })));

  const st = sc.stats;
  const cards = [
    ['Production tables at risk', st.productionTables, st.productionTables ? 'var(--red)' : 'var(--green)', 'Published by this team'],
    ['Intermediate tables', st.intermediateTables, '', 'Steps along the way'],
    ['Attributes impacted', st.attributesImpacted, '', 'Of those you confirmed'],
    ['Files to change', st.filesWithImpact, '', `Of ${sc.filesScanned} scanned`],
    ['Breaking usages', st.breakingUsages, st.breakingUsages ? 'var(--amber)' : '', 'Filters, joins, ranking'],
    ['Could not read', st.couldNotRead, st.couldNotRead ? 'var(--amber)' : '', 'Must be checked by hand'],
  ];
  const box = x(root, 'stats');
  cards.forEach(([l, v, colour, sub]) => box.append(el('div', { className: 'stat' },
    el('span', { className: 'lbl', textContent: l }),
    el('div', { className: 'v', textContent: String(v), style: colour ? `color:${colour}` : '' }),
    el('div', { className: 's', textContent: sub }))));

  const groups = x(root, 'groups');
  if (!sc.groups.length) {
    groups.append(el('div', { className: 'card pad', style: 'text-align:center;padding:44px' },
      el('div', { style: 'font-size:17px;font-weight:800', textContent: 'No production table depends on these attributes' }),
      el('div', { className: 'muted', style: 'margin-top:7px',
        textContent: 'Nothing in this repository carries them through to a table this team publishes.' })));
  }
  sc.groups.forEach((g, gi) => {
    const card = el('div', { className: 'card group' });
    const open = S.openGroup === gi;
    const head = el('div', { className: 'ghead' + (open ? ' open' : '') });
    head.append(
      el('div', {}, el('span', { className: 'lbl', textContent: 'Production table' }),
        el('div', { className: 'mono', textContent: g.prod, style: 'font-size:15px;font-weight:700;margin-top:2px' })),
      el('span', { className: 'badge red', textContent: `${g.rows.length} impact${g.rows.length === 1 ? '' : 's'}` }),
      el('span', { className: 'small muted', textContent: g.note }),
      el('span', { className: 'caret', textContent: '›' }));
    head.onclick = () => { S.openGroup = open ? null : gi; S.openRow = null; render(); };
    card.append(head);
    if (open) {
      const hr = el('div', { className: 'rowhead' });
      ['Table it lands in', 'Attribute', 'Called', 'What the code does', 'Value', ''].forEach(h => hr.append(el('span', { textContent: h })));
      card.append(hr);
      g.rows.forEach((r, ri) => {
        const key = `${gi}-${ri}`, ro = S.openRow === key;
        const row = el('div', { className: 'row' + (ro ? ' open' : '') });
        row.append(
          el('span', { className: 'mono', textContent: r.inter, style: 'font-weight:700;font-size:13px' }),
          el('span', { className: 'mono', textContent: r.attr, style: 'font-size:12.5px;color:var(--blued)' }),
          el('span', { className: 'mono', textContent: r.alias, style: 'font-size:12.5px' }),
          el('span', {}, el('span', { className: 'badge ' + (r.breaking ? 'red' : 'grey'), textContent: r.logic })),
          el('span', { className: 'small muted', textContent: r.mode }),
          el('span', { className: 'caret', textContent: '›' }));
        row.onclick = () => { S.openRow = ro ? null : key; render(); };
        card.append(row);
        if (ro) card.append(detailFor(r));
      });
    }
    groups.append(card);
  });

  renderGaps(x(root, 'gaps'), sc);
  x(root, 'next').onclick = () => goto(5);
}

function detailFor(r) {
  const d = el('div', { className: 'detail' });
  d.append(el('div', { className: 'note ' + (r.noLocalFix ? 'bad' : r.breaking ? 'warn' : 'info'), style: 'margin-top:14px' },
    el('b', { textContent: r.noLocalFix ? 'No local fix — the upstream team must supply a replacement. ' : r.breaking ? 'This breaks. ' : 'Changes, but does not break. ' }),
    r.impact));
  const code = el('div', { className: 'code' });
  code.append(el('div', { className: 'f' },
    el('span', { textContent: r.file, style: 'font-weight:700' }),
    el('span', { textContent: r.lang, style: 'margin-left:auto' })));
  (r.lines || []).forEach(ln => {
    code.append(el('div', { className: 'ln' + (ln.hit ? ' hit' : '') },
      el('span', { className: 'n', textContent: String(ln.n) }),
      el('span', { className: 't', textContent: ln.t })));
    if (ln.hit) code.append(el('div', { className: 'note', textContent: '▲ ' + ln.hit }));
  });
  d.append(code);
  return d;
}

function renderGaps(box, sc) {
  box.innerHTML = '';
  if (sc.unreadable?.length) {
    const card = el('div', { className: 'card pad', style: 'margin-top:18px;border-color:var(--amberln);background:var(--amberbg)' });
    card.append(el('b', { textContent: `${sc.unreadable.length} file${sc.unreadable.length === 1 ? '' : 's'} Ripple could not read — check these by hand` }));
    card.append(el('div', { className: 'small', style: 'margin-top:5px;color:var(--amber)',
      textContent: 'A clean result is only as good as what could be read. These are not covered by the findings above.' }));
    sc.unreadable.forEach(u => card.append(el('div', { style: 'margin-top:8px;font-size:13px' },
      el('span', { className: 'mono', textContent: u.file, style: 'font-weight:700' }),
      el('span', { className: 'muted', textContent: ' — ' + u.reason }))));
    box.append(card);
  }
  if (sc.mentionsOnly?.length) {
    const card = el('div', { className: 'card pad', style: 'margin-top:14px' });
    card.append(el('span', { className: 'lbl', textContent: `${sc.mentionsOnly.length} file${sc.mentionsOnly.length === 1 ? '' : 's'} mention the name but carry it nowhere` }));
    sc.mentionsOnly.forEach(m => card.append(el('div', { className: 'small mono muted', textContent: m.file, style: 'margin-top:5px' })));
    box.append(card);
  }
}

// ── step 5 ────────────────────────────────────────────────────────────────
function step5(root) {
  const gs = S.scan?.graphs || [];
  const tabs = x(root, 'tabs'), map = x(root, 'map');
  if (!gs.length) {
    map.append(el('div', { className: 'card pad', style: 'text-align:center;padding:44px' },
      el('div', { style: 'font-size:17px;font-weight:800', textContent: 'No downstream lineage found' }),
      el('div', { className: 'muted', style: 'margin-top:7px', textContent: 'These attributes do not feed any table this team publishes.' })));
    x(root, 'next').onclick = () => goto(6);
    return;
  }
  const gi = Math.min(S.graphTab, gs.length - 1);
  gs.forEach((g, i) => {
    const b = el('button', { className: 'pill' + (i === gi ? ' on' : '') });
    b.append(el('span', { textContent: g.attr, className: 'mono' }));
    b.onclick = () => { S.graphTab = i; render(); };
    tabs.append(b);
  });
  const g = gs[gi];
  const card = el('div', { className: 'card pad' });
  card.append(el('span', { className: 'lbl', textContent: 'Upstream source' }));
  card.append(el('div', { className: 'mono', textContent: `${g.table}.${g.attr}`, style: 'font-size:16px;font-weight:700;color:var(--blued);margin-top:4px' }));
  card.append(el('div', { className: 'small muted', style: 'margin-top:3px',
    textContent: `${g.branches.length} branch${g.branches.length === 1 ? '' : 'es'} to production` }));
  g.branches.forEach(br => {
    const line = el('div', { className: 'branch' });
    line.append(nodeEl({ name: g.table, kind: 'Source', alias: g.attr }));
    br.forEach(n => { line.append(el('div', { className: 'arrow', textContent: '→' })); line.append(nodeEl(n)); });
    card.append(line);
  });
  card.append(el('div', { className: 'small muted', style: 'margin-top:16px',
    textContent: 'Each box is a table. The name underneath is what the column is called at that point — that is the rename a word search would miss.' }));
  map.append(card);
  x(root, 'next').onclick = () => makeSummary();
}

function nodeEl(n) {
  const d = el('div', { className: 'node' + (n.prod ? ' prod' : '') });
  d.append(el('div', { className: 'k', textContent: n.kind }),
    el('div', { className: 'nm', textContent: n.name }));
  if (n.alias) d.append(el('div', { className: 'al' }, 'as ', el('b', { textContent: n.alias })));
  return d;
}

// ── step 6 ────────────────────────────────────────────────────────────────
function makeSummary() {
  if (S.summary) { goto(6); return; }
  run(async () => {
    const out = await api('/api/summary', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ scan: S.scan, vals: { ...S.vals, effectiveLabel: fmtDate(S.vals.effectiveDate) }, useAI: true }),
    });
    S.summary = out.summary; S.reply = out.reply; S.aiNote = out.aiNote || '';
    goto(6);
  });
}

function step6(root) {
  const s = S.summary; if (!s) return;
  const [cls, label] = RISK[S.scan.risk] || RISK.none;
  x(root, 'risk').append(el('span', { className: 'badge ' + cls, textContent: label }));
  x(root, 'sub').textContent = s.writtenBy === 'ai'
    ? `Written by ${S.health.ai.model} from the findings — no code was sent to it.`
    : 'Written from the findings without AI.';

  const b = x(root, 'body');
  const main = el('div', { className: 'card pad' });
  main.append(el('div', { style: 'font-size:19px;font-weight:800;line-height:1.3', textContent: s.headline }));
  main.append(el('p', { style: 'margin-top:11px;font-size:14.5px;line-height:1.6;color:#33445E', textContent: s.narrative }));
  const ul = el('ul', { className: 'ticks' });
  (s.bullets || []).forEach(t => ul.append(el('li', {}, t)));
  main.append(ul);
  b.append(main);

  const grid = el('div', { className: 'grid2', style: 'margin-top:18px' });
  const facts = el('div', { className: 'card pad' });
  facts.append(el('span', { className: 'lbl', textContent: 'The change' }));
  const dl = daysLeft(S.vals.effectiveDate);
  [['Source system', S.vals.source], ['Change type', S.vals.changeType],
   ['Tables', S.vals.upstream.map(u => u.table).join(', ')],
   ['Attributes', S.vals.upstream.flatMap(u => u.attrs).join(', ')],
   ['Effective', fmtDate(S.vals.effectiveDate) + (dl !== null ? ` · ${dl} days left` : '')],
   ['Contact', [S.vals.pocName, S.vals.pocTeam].filter(Boolean).join(', ')]].forEach(([k, v]) =>
    facts.append(el('div', { style: 'display:flex;gap:14px;padding:8px 0;border-top:1px solid #F0F4F9' },
      el('span', { className: 'small muted', textContent: k, style: 'width:110px;flex-shrink:0' }),
      el('span', { className: 'small', textContent: v || '—', style: 'font-weight:600;word-break:break-word' }))));
  const acts = el('div', { className: 'card pad' });
  acts.append(el('span', { className: 'lbl', textContent: 'What to do' }));
  const ol = el('ol', { className: 'acts' });
  (s.actions || []).forEach(a => ol.append(el('li', {}, a)));
  acts.append(ol);
  grid.append(facts, acts);
  b.append(grid);
  if (S.scan.unreadable?.length) {
    const g = el('div', { style: 'margin-top:18px' }); renderGaps(g, { unreadable: S.scan.unreadable }); b.append(g);
  }

  x(root, 'next').onclick = () => goto(7);
  x(root, 'saved').textContent = S.savedId ? `Saved as analysis #${S.savedId}.` : '';
  x(root, 'save').onclick = () => run(async () => {
    const out = await api('/api/history', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ vals: S.vals, scan: S.scan, summary: S.summary, mode: S.vals.extractedBy }),
    });
    S.savedId = out.id || null;
    if (!out.saved) alert('History is not available here: ' + (out.reason || ''));
    render();
  });
}

// ── step 7 ────────────────────────────────────────────────────────────────
function step7(root) {
  const r = S.reply || { subject: '', body: '' };
  const subj = x(root, 'subject'); subj.value = r.subject; subj.oninput = () => { r.subject = subj.value; };
  const body = x(root, 'body'); body.value = r.body; body.oninput = () => { r.body = body.value; };
  const ol = x(root, 'acts');
  (S.summary?.actions || []).forEach(a => ol.append(el('li', {}, a)));
  const poc = x(root, 'poc');
  poc.append(el('div', { style: 'font-weight:700', textContent: S.vals.pocName || 'Not specified' }));
  if (S.vals.pocEmail) poc.append(el('div', { className: 'small mono', textContent: S.vals.pocEmail, style: 'color:var(--blued)' }));
  if (S.vals.pocTeam) poc.append(el('div', { className: 'small muted', textContent: S.vals.pocTeam }));
  x(root, 'copy').onclick = async () => {
    await navigator.clipboard.writeText(`Subject: ${r.subject}\n\n${r.body}`);
    x(root, 'copied').textContent = 'Copied — paste it into Outlook.';
  };
  x(root, 'restart').onclick = () => {
    Object.assign(S, { step: 1, maxStep: 1, vals: null, scan: null, summary: null, reply: null,
      savedId: null, emailPreview: null, openGroup: 0, openRow: null, graphTab: 0 });
    render();
  };
}

// ── history & settings ────────────────────────────────────────────────────
function historyView(root) {
  root.append(el('div', { className: 'head' }, el('div', {},
    el('h2', { textContent: 'Past analyses' }),
    el('p', { textContent: 'Everything saved on this server, newest first.' }))));
  const card = el('div', { className: 'card' });
  root.append(card);
  api('/api/history').then(rows => {
    if (!rows.length) { card.append(el('div', { className: 'pad muted', textContent: 'Nothing saved yet.' })); return; }
    const t = el('table', { className: 'hist' });
    const hr = el('tr');
    ['When', 'Subject', 'Source', 'Change', 'Risk', 'Mode', 'Status'].forEach(h => hr.append(el('th', { textContent: h })));
    t.append(hr);
    rows.forEach(r => {
      const [cls, label] = RISK[r.risk] || RISK.none;
      const sel = el('select', { className: 'status' });
      ['New', 'In progress', 'Verified', 'Closed'].forEach(s =>
        sel.append(el('option', { value: s, textContent: s, selected: s === r.status })));
      sel.onchange = () => api(`/api/history/${r.id}`, {
        method: 'PATCH', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: sel.value }),
      });
      t.append(el('tr', {},
        el('td', { className: 'small muted', textContent: (r.created_at || '').replace('T', ' ').slice(0, 16) }),
        el('td', { textContent: r.subject || '—' }),
        el('td', { textContent: r.source || '—' }),
        el('td', { className: 'small', textContent: r.change_type || '—' }),
        el('td', {}, el('span', { className: 'badge ' + cls, textContent: label })),
        el('td', { className: 'small muted', textContent: r.mode || '' }),
        el('td', {}, sel)));
    });
    card.append(t);
  });
}

function settingsView(root) {
  const h = S.health;
  root.append(el('div', { className: 'head' }, el('div', {},
    el('h2', { textContent: 'Settings & checks' }),
    el('p', { textContent: 'What Ripple is connected to, and whether it is working.' }))));
  const grid = el('div', { className: 'grid2' });

  const left = el('div', { className: 'card pad' });
  left.append(el('span', { className: 'lbl', textContent: 'Repository' }));
  [['Folder', h.repo.path], ['Label', h.repo.label], ['Files indexed', String(h.repo.files)],
   ['Statements understood', String(h.repo.statements)], ['Files unreadable', String(h.repo.unreadable)],
   ['SQL dialect', h.sqlDialect], ['Renames followed', `${h.maxHops} hops`]].forEach(([k, v]) =>
    left.append(el('div', { style: 'display:flex;gap:14px;padding:8px 0;border-top:1px solid #F0F4F9' },
      el('span', { className: 'small muted', textContent: k, style: 'width:150px;flex-shrink:0' }),
      el('span', { className: 'small', textContent: v, style: 'font-weight:600;word-break:break-all' }))));
  left.append(el('div', { className: 'note info', style: 'margin-top:14px' },
    'Change any of these with environment variables — ',
    el('span', { className: 'mono', textContent: 'RIPPLE_REPO' }), ', ',
    el('span', { className: 'mono', textContent: 'RIPPLE_SQL_DIALECT' }), ', ',
    el('span', { className: 'mono', textContent: 'GROQ_API_KEY' }), '. See the README.'));

  const right = el('div', { className: 'card pad' });
  right.append(el('span', { className: 'lbl', textContent: 'AI (optional)' }));
  right.append(el('div', { className: 'note ' + (h.ai.available ? 'good' : 'info'), style: 'margin-top:10px' },
    el('b', { textContent: h.ai.available ? 'A key is set. ' : 'No key set. ' }),
    h.ai.available
      ? `The email reader and the summary use ${h.ai.model}. Your source code is never sent to it.`
      : 'Ripple is running on rules alone. Everything works; the wording is just plainer.'));
  const btn = el('button', { className: 'ghost', textContent: 'Test the key', style: 'margin-top:14px' });
  const out = el('div', { style: 'margin-top:12px' });
  btn.onclick = () => run(async () => {
    out.innerHTML = '';
    const res = await api('/api/ai/check', { method: 'POST' });
    out.append(el('div', { className: 'note ' + (res.ok ? 'good' : 'warn') },
      res.ok ? `Working — replied using ${res.model}.` : `Not working — ${res.reason}`));
  });
  right.append(btn, out);

  grid.append(left, right);
  root.append(grid);
}

// ── plumbing ──────────────────────────────────────────────────────────────
function goto(n) { S.step = n; S.maxStep = Math.max(S.maxStep, n); S.view = 'wizard'; render(); }

function run(fn) {
  S.busy = true; render();
  Promise.resolve(fn()).catch(e => {
    alert('Something went wrong: ' + e.message);
  }).finally(() => { S.busy = false; render(); });
}

function render() {
  renderSteps(); renderStatus();
  const view = $('#view'); view.innerHTML = '';
  $('#hRight').innerHTML = '';
  if (S.busy) $('#hRight').append(el('span', { className: 'spin' }));

  if (S.view === 'history') { setHeader('Past analyses', 'Saved on this server'); historyView(view); return; }
  if (S.view === 'settings') { setHeader('Settings & checks', 'Connections and health'); settingsView(view); return; }

  setHeader(STEPS[S.step - 1][0], `Step ${S.step} of ${STEPS.length}`);
  const tpl = $(`#t-step${S.step}`);
  if (!tpl) return;
  const node = tpl.content.cloneNode(true);
  const holder = el('div');
  holder.append(node);
  view.append(holder);
  ({ 1: step1, 2: step2, 3: step3, 4: step4, 5: step5, 6: step6, 7: step7 })[S.step](holder);
}

$('#navHistory').onclick = () => { S.view = 'history'; render(); };
$('#navSettings').onclick = () => { S.view = 'settings'; render(); };

(async function boot() {
  try { S.health = await api('/api/health'); }
  catch (e) { alert('Could not reach the Ripple server: ' + e.message); }
  render();
})();

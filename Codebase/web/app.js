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
  // Repository step. The token is held here only long enough to send it once;
  // it is cleared as soon as the server has accepted it.
  repoTab: null,
  gh: { repo: '', branch: '', token: '' },
  connecting: false, connectMsg: '',
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
    el('div', { className: 'srow' },
      el('span', { className: 'dot ' + (repoOk ? 'ok' : 'warn') }),
      el('span', { textContent: repoOk ? `${h.repo.label} · ${h.repo.files} files` : 'No repository found' })),
    el('div', { className: 'srow' },
      el('span', { className: 'dot ' + (h.ai.available ? 'ok' : 'off') }),
      el('span', { textContent: h.ai.available ? 'AI on' : 'AI off — rules only' })),
    el('div', { className: 'srow' },
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
    const wrap = el('div', { style: 'display:flex;gap:20px;align-items:flex-end;padding:16px 20px' + (i ? ';border-top:1px solid var(--hair)' : '') });
    const t = el('input', { type: 'text', className: 'mono', value: r.table, placeholder: 'CUSTOMER_DEMOGRAPHICS', style: 'margin-top:6px' });
    t.oninput = () => { r.table = t.value; updateManHint(root); };
    const a = el('input', { type: 'text', className: 'mono', value: r.attrs, placeholder: 'MARKET_CODE, MARKET_NAME', style: 'margin-top:6px' });
    a.oninput = () => { r.attrs = a.value; updateManHint(root); };
    wrap.append(
      el('div', { style: 'flex:1;min-width:0' }, el('span', { className: 'lbl faint', textContent: 'Upstream table name' }), t),
      el('div', { style: 'flex:1;min-width:0' }, el('span', { className: 'lbl faint', textContent: 'Attributes — comma separated' }), a));
    if (S.manRows.length > 1) {
      const rm = el('button', { className: 'danger', textContent: 'Remove' });
      rm.onclick = () => { S.manRows.splice(i, 1); render(); };
      wrap.append(rm);
    }
    rows.append(wrap);
  });
  x(root, 'addRow').onclick = () => { S.manRows.push({ table: '', attrs: '' }); render(); };

  const fields = x(root, 'manFields');
  fields.innerHTML = '';
  MAN_FIELDS.forEach(([key, label, hint]) => {
    const inp = el('input', { type: 'text', value: S.man[key], placeholder: hint,
      style: 'margin-top:7px;font-size:12.5px;font-weight:400;color:var(--mute);padding:7px 11px' });
    inp.oninput = () => { S.man[key] = inp.value; };
    fields.append(el('div', { className: 'field' }, el('span', { className: 'lbl faint', textContent: label }), inp));
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
      const sel = el('select', { style: 'margin-top:8px' });
      CHANGE_KINDS.forEach(([k, l]) => sel.append(el('option', { value: k, textContent: l, selected: k === v.changeKind })));
      sel.onchange = () => { v.changeKind = sel.value; v.changeType = sel.selectedOptions[0].textContent; };
      card.append(sel);
    } else {
      const inp = el('input', { type: type === 'date' ? 'date' : 'text', value: v[key] || '', style: 'margin-top:8px' });
      inp.oninput = () => { v[key] = inp.value; };
      card.append(inp);
      if (key === 'effectiveDate' && dl !== null) {
        card.append(el('span', { className: 'badge sm ' + (dl <= 21 ? 'amber' : 'blue'),
          textContent: dl < 0 ? 'date has passed' : `${dl} day${dl === 1 ? '' : 's'} left`, style: 'margin-top:8px' }));
      }
      if (key === 'pocName' && v.pocEmail) card.append(el('div', { className: 'small muted', textContent: v.pocEmail, style: 'margin-top:5px;overflow-wrap:break-word' }));
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
    const wrap = el('div', { style: 'display:flex;gap:24px;align-items:flex-end;padding:16px 20px;animation:fadeUp .3s ease' + (i ? ';border-top:1px solid var(--hair)' : '') });
    const t = el('input', { type: 'text', className: 'mono', value: u.table, style: 'margin-top:6px' });
    t.oninput = () => { u.table = t.value; };
    const a = el('input', { type: 'text', className: 'mono', value: (u.attrs || []).join(', '), style: 'margin-top:6px' });
    a.oninput = () => { u.attrs = a.value.split(',').map(s => s.trim()).filter(Boolean); };
    const rm = el('button', { className: 'danger', textContent: 'Remove' });
    rm.onclick = () => { v.upstream.splice(i, 1); render(); };
    wrap.append(
      el('div', { style: 'width:288px;flex-shrink:0' }, el('span', { className: 'lbl faint', textContent: 'Upstream table name' }), t),
      el('div', { style: 'flex:1;min-width:0' }, el('span', { className: 'lbl faint', textContent: 'Upstream attributes name' }), a), rm);
    box.append(wrap);
  });
  if (!v.upstream.length) box.append(el('div', { className: 'pad muted', textContent: 'Nothing to scan yet — add a table below.' }));
}

// ── step 3 ────────────────────────────────────────────────────────────────
function step3(root) {
  const h = S.health;
  if (!h) return;
  if (S.repoTab === null) S.repoTab = h.source === 'github' ? 'github' : 'folder';
  const onGit = S.repoTab === 'github';
  const live = h.source === 'github';

  x(root, 'title').textContent = onGit ? 'Read a GitHub repository' : 'Connected repository';
  x(root, 'sub').textContent = onGit
    ? 'Point Ripple at a repository and give it an access token. It only ever reads.'
    : 'This is the code Ripple will search. It is read, never written to.';

  $$('[data-src]', root).forEach(b => {
    b.className = 'pill' + (b.dataset.src === S.repoTab ? ' on' : '');
    b.onclick = () => { S.repoTab = b.dataset.src; S.connectMsg = ''; render(); };
  });

  // anything the server wants to say about the last connection attempt
  const alert = x(root, 'alert'); alert.innerHTML = '';
  if (S.connectMsg) {
    alert.append(el('div', { className: 'note bad', style: 'margin-bottom:18px' },
      el('b', { textContent: 'Could not connect. ' }), S.connectMsg));
  } else if (h.connectError) {
    alert.append(el('div', { className: 'note warn', style: 'margin-bottom:18px' },
      el('b', { textContent: 'Reading the folder on this machine instead. ' }), h.connectError));
  }

  x(root, 'left').innerHTML = '';
  x(root, 'left').append(onGit ? gitHubForm(h, live) : repoFacts(h));

  // the same confirmation the prototype shows, on the numbers Ripple really has
  const ready = x(root, 'ready'); ready.innerHTML = '';
  const repoOk = h.repo.exists && h.repo.files > 0;
  // Says which source it means, so a GitHub form beside it can never be
  // mistaken for "connected" when the folder is what is really loaded.
  ready.append(el('div', { className: 'note ' + (repoOk ? 'good' : 'warn') },
    el('b', { textContent: repoOk ? `✓ ${h.repo.label} connected` : `Nothing to scan in ${h.repo.label}`,
      style: 'display:block;font-size:14px' }),
    el('div', { className: 'small', style: 'margin-top:2px;font-weight:600;opacity:.8',
      textContent: live ? 'from GitHub' : 'a folder on this machine' }),
    el('div', { style: 'margin-top:8px;line-height:1.55' },
      live ? 'Commit ' : 'Branch ',
      el('span', { className: 'mono', textContent: live ? (h.github.shortCommit || h.github.branch) : h.repo.branch }),
      repoOk ? ` — ${h.repo.files} file${h.repo.files === 1 ? '' : 's'} ready to scan.`
             : ' — check the repository folder in Settings & checks.')));

  // what kinds of file are in the index — counted, not assumed
  const kinds = x(root, 'kinds'); kinds.innerHTML = '';
  if (h.repo.kinds?.length) {
    kinds.append(el('span', { className: 'lbl', textContent: 'What gets read' }));
    const chips = el('div', { className: 'chips', style: 'margin-top:12px' });
    h.repo.kinds.forEach(k => chips.append(el('span', { className: 'chip', textContent: `${k.lang} · ${k.files}` })));
    kinds.append(chips);
    kinds.append(el('div', { className: 'small muted', style: 'margin-top:14px;line-height:1.55',
      textContent: 'Read-only access. Ripple never writes to your repository.' }));
  }

  const c = x(root, 'cat'); c.innerHTML = '';
  api('/api/catalog').then(cat => {
    c.append(el('div', { style: 'display:flex;gap:26px;margin-top:10px' },
      el('div', {}, el('div', { textContent: String(cat.tableCount), style: 'font-size:26px;font-weight:800;font-variant-numeric:tabular-nums' }),
        el('div', { className: 'small faint', textContent: 'tables found' })),
      el('div', {}, el('div', { textContent: String(cat.columnCount), style: 'font-size:26px;font-weight:800;font-variant-numeric:tabular-nums' }),
        el('div', { className: 'small faint', textContent: 'columns found' }))));
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
  x(root, 'hint').textContent = h.repo.files
    ? `Scanning ${h.repo.label}.`
    : 'Nothing is indexed, so a scan would find nothing.';
  x(root, 'next').disabled = !h.repo.files;
}

/* What Ripple is reading now — the same facts either way. */
function repoFacts(h) {
  const live = h.source === 'github';
  const r = el('div', { className: 'card pad lg' });
  r.append(el('span', { className: 'lbl', textContent: live ? 'GitHub repository' : 'Folder on this machine' }));
  r.append(el('div', { className: 'mono', textContent: h.repo.label,
    style: 'font-size:17px;font-weight:600;color:var(--blued);margin-top:8px;word-break:break-all' }));
  r.append(el('div', { className: 'small faint', textContent: h.repo.path,
    style: 'margin-top:5px;word-break:break-all' }));
  const facts = [
    ['Files indexed', String(h.repo.files)],
    ['Statements understood', String(h.repo.statements)],
    ['Branch', h.repo.branch],
    ['SQL read as', h.sqlDialect],
    ['Renames followed', `${h.maxHops} hops deep`],
  ];
  if (live) {
    facts.splice(3, 0, ['Commit read', h.github.commit ? h.github.commit.slice(0, 12) : 'unknown']);
    facts.push(['Visibility', h.github.private ? 'private' : 'public']);
  }
  const t = el('div', { style: 'margin-top:18px' });
  facts.forEach(([k, val]) => t.append(el('div', { style: 'display:flex;gap:14px;padding:9px 0;border-top:1px solid var(--hair)' },
    el('span', { className: 'small muted', textContent: k, style: 'flex:1' }),
    el('span', { className: 'small' + (k === 'Commit read' ? ' mono' : ''), textContent: val, style: 'font-weight:700' }))));
  r.append(t);
  if (live) {
    const off = el('button', { className: 'ghost sm', textContent: 'Disconnect and forget the token', style: 'margin-top:18px' });
    off.onclick = () => run(async () => {
      S.health = await api('/api/repo/disconnect', { method: 'POST' });
      S.repoTab = 'folder'; S.connectMsg = ''; S.gh.token = '';
      render();
    });
    r.append(off);
  }
  return r;
}

/* The connect form. Nothing here pretends: the button does one real request. */
function gitHubForm(h, live) {
  const card = el('div', { className: 'card pad lg' });
  const envToken = h.tokenFrom === 'environment';

  // Built first so typing a repository name can switch it on straight away,
  // without redrawing the form and throwing away the cursor.
  const btn = el('button', { className: 'pri',
    textContent: S.connecting ? 'Reading the repository…' : (live ? 'Read it again' : 'Connect and read it') });
  const syncBtn = () => { btn.disabled = S.connecting || (!S.gh.repo.trim() && !live); };

  const field = (label, key, opts = {}) => {
    const wrap = el('div', { style: 'margin-bottom:18px' });
    wrap.append(el('label', { className: 'lbl', textContent: label, style: 'display:block;margin-bottom:7px' }));
    const inp = el('input', {
      type: opts.secret ? 'password' : 'text',
      value: S.gh[key], placeholder: opts.hint || '',
      className: opts.mono ? 'mono' : '',
      style: 'padding:12px 14px' + (opts.width ? `;width:${opts.width}` : ''),
    });
    if (opts.secret) inp.autocomplete = 'off';
    inp.oninput = () => { S.gh[key] = inp.value; syncBtn(); };
    inp.onkeydown = (e) => { if (e.key === 'Enter') doConnect(); };
    wrap.append(inp);
    if (opts.note) wrap.append(el('div', { className: 'small faint', textContent: opts.note, style: 'margin-top:6px' }));
    return wrap;
  };

  card.append(field('Repository', 'repo', {
    mono: true, hint: 'owner/repository', note: 'Or paste the address straight from GitHub.' }));
  card.append(field('Branch', 'branch', {
    mono: true, hint: 'leave blank for the default', width: '240px' }));

  if (envToken) {
    card.append(el('div', { style: 'margin-bottom:18px' },
      el('span', { className: 'lbl', style: 'display:block;margin-bottom:7px', textContent: 'Access token' }),
      el('div', { className: 'note good' },
        el('b', { textContent: 'A token is already set on this server. ' }),
        'It was set as an environment variable, so it survives restarts. Leave the box below empty to keep using it.')));
    card.append(field('Use a different token instead', 'token', { secret: true, hint: 'optional' }));
  } else {
    card.append(field('Access token', 'token', {
      secret: true, hint: 'ghp_… or github_pat_…',
      note: 'Needed for a private repository. A public one can be read without a token. '
          + 'Read access is all it needs — Ripple never writes.' }));
  }

  syncBtn();
  btn.onclick = () => doConnect();
  const row = el('div', { className: 'foot', style: 'margin-top:4px' }, btn);
  if (S.connecting) row.append(el('span', { className: 'spin' }),
    el('span', { className: 'small muted', textContent: 'Downloading and indexing. A large repository takes a moment.' }));
  card.append(row);

  card.append(el('div', { className: 'note info', style: 'margin-top:20px' },
    el('b', { textContent: 'Where the token goes. ' }),
    'It is sent to GitHub and held in this server’s memory for as long as it is running. '
    + 'It is never written to disk, never logged, and never sent back to this page.'
    + (h.serverless
      ? ' This copy is running on a serverless host, where the server is replaced often — set the token as an environment variable there so it lasts.'
      : ' Restart the server and you will need to enter it again.')));
  return card;
}

function doConnect() {
  const repo = S.gh.repo.trim() || (S.health?.github?.slug || '');
  if (!repo || S.connecting) return;
  S.connecting = true; S.connectMsg = ''; render();
  api('/api/repo/connect', {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ repo, branch: S.gh.branch.trim(), token: S.gh.token }),
  }).then(out => {
    S.health = out;
    S.gh.token = '';            // the server has it now; do not keep a copy here
    S.gh.repo = out.github?.slug || repo;
    S.gh.branch = '';
    S.connectMsg = '';
    S.scan = null; S.summary = null;   // anything scanned before was another repo
  }).catch(e => {
    S.connectMsg = e.message;
  }).finally(() => { S.connecting = false; render(); });
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

  // What was actually read. Real counts only — the scan has already finished by
  // the time this renders, so there is nothing to animate.
  const done = el('div', { className: 'card pad lg' });
  done.append(el('div', { style: 'display:flex;align-items:center;gap:12px;flex-wrap:wrap' },
    el('span', { className: 'chip mono', textContent: S.health.repo.label }),
    el('span', { className: 'chip', textContent: S.health.repo.branch }),
    el('span', { textContent: sc.stats.filesWithImpact
      ? `Scan complete — ${sc.stats.filesWithImpact} file${sc.stats.filesWithImpact === 1 ? '' : 's'} with impact`
      : 'Scan complete — nothing carries these attributes',
      style: 'margin-left:auto;font-size:13px;font-weight:600;color:var(--blued)' })));
  done.append(el('div', { style: 'display:flex;align-items:baseline;gap:9px;margin-top:18px;flex-wrap:wrap' },
    el('span', { className: 'big', textContent: String(sc.filesScanned) }),
    el('span', { className: 'small muted', textContent: `files read · ${sc.filesMatched} mention the names you confirmed` })));
  x(root, 'progress').append(done);

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
    groups.append(el('div', { className: 'note good', style: 'display:flex;align-items:center;gap:14px;padding:18px 22px' },
      el('span', { textContent: '✓', style: 'width:30px;height:30px;border-radius:50%;background:var(--green);color:#fff;display:flex;align-items:center;justify-content:center;font-weight:700;flex-shrink:0' }),
      el('div', {}, el('b', { textContent: 'No production table depends on these attributes', style: 'display:block' }),
        el('div', { style: 'margin-top:3px', textContent: 'Nothing in this repository carries them through to a table this team publishes.' }))));
  }
  sc.groups.forEach((g, gi) => {
    const card = el('div', { className: 'card clip group' });
    const open = S.openGroup === gi;
    const head = el('div', { className: 'ghead' + (open ? ' open' : '') });
    head.append(
      el('span', { className: 'tag', textContent: 'Production table' }),
      el('div', { className: 'mono', textContent: g.prod, style: 'font-size:15px;font-weight:600' }),
      el('span', { className: 'badge grey', textContent: `${g.rows.length} impact${g.rows.length === 1 ? '' : 's'}` }),
      el('span', { className: 'small muted', textContent: g.note }),
      el('span', { className: 'caret', textContent: '›' }));
    head.onclick = () => { S.openGroup = open ? null : gi; S.openRow = null; render(); };
    card.append(head);
    if (open) {
      const hr = el('div', { className: 'rowhead' });
      ['Table it lands in', 'Attribute impacted', 'Alias used', 'What the code does', 'Value', ''].forEach(h => hr.append(el('span', { textContent: h })));
      card.append(hr);
      g.rows.forEach((r, ri) => {
        const key = `${gi}-${ri}`, ro = S.openRow === key;
        const row = el('div', { className: 'row' + (ro ? ' open' : '') });
        row.append(
          el('span', { className: 'mono', textContent: r.inter, style: 'font-weight:600;font-size:13px;min-width:0;overflow-wrap:break-word' }),
          el('span', { className: 'mono', textContent: r.attr, style: 'font-size:13px;font-weight:600;color:var(--blued);min-width:0;overflow-wrap:break-word' }),
          el('span', {}, el('span', { className: 'chip alias', textContent: r.alias })),
          el('span', {}, el('span', { className: 'badge sm ' + (r.breaking ? 'red' : 'grey'), textContent: r.logic })),
          el('span', {}, el('span', { className: 'badge sm ' + (r.mode === 'Direct pull' ? 'blue' : 'violet'), textContent: r.mode })),
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

/* The address of a finding in the connected repository, or nothing at all.
   Points at the first line that actually matched, not the top of the file. */
function fileUrl(r) {
  const tpl = S.scan?.repo?.urlTemplate;
  if (!tpl || !r.file) return '';
  const hit = (r.lines || []).find(l => l.hit) || (r.lines || [])[0];
  return tpl.replace('{path}', r.file).replace('{line}', String(hit?.n ?? 1));
}

function detailFor(r) {
  const d = el('div', { className: 'detail' });
  d.append(el('div', { className: 'note ' + (r.noLocalFix ? 'bad' : r.breaking ? 'warn' : 'info') },
    el('b', { textContent: r.noLocalFix ? 'No local fix — the upstream team must supply a replacement. ' : r.breaking ? 'This breaks. ' : 'Changes, but does not break. ' }),
    r.impact));
  const code = el('div', { className: 'code' });
  const head = el('div', { className: 'f' },
    el('span', { className: 'name', textContent: r.file }),
    el('span', { className: 'lang', textContent: r.lang }));
  // Only offered when Ripple genuinely knows the address of this code. On a
  // local folder there is nothing to link to, so no link is shown.
  const href = fileUrl(r);
  if (href) {
    head.append(el('a', { href, textContent: 'Open in GitHub ↗', target: '_blank', rel: 'noopener' }));
  }
  code.append(head);
  const body = el('div', { className: 'body' });
  (r.lines || []).forEach(ln => {
    const line = el('div', { className: 'ln' + (ln.hit ? ' hit' : '') },
      el('span', { className: 'n', textContent: String(ln.n) }),
      el('span', { className: 't', textContent: ln.t }));
    // why this line matched, sitting on the line itself rather than under it
    if (ln.hit) line.append(el('span', { className: 'why', textContent: ln.hit }));
    body.append(line);
  });
  code.append(body);
  d.append(code);
  return d;
}

/* The honest half of the report: what Ripple could NOT account for. Styled to
   stand out, never to shrink — a clean finding list is only worth what was read. */
function renderGaps(box, sc) {
  box.innerHTML = '';
  if (sc.unreadable?.length) {
    const card = el('div', { className: 'card clip', style: 'margin-top:20px;border-color:var(--amberln)' });
    card.append(el('div', { className: 'chead', style: 'background:var(--amberbg);border-bottom-color:var(--amberln)' },
      el('span', { className: 'tag', style: 'background:var(--amber);color:#fff', textContent: 'Check by hand' }),
      el('b', { textContent: `${sc.unreadable.length} file${sc.unreadable.length === 1 ? '' : 's'} Ripple could not read` })));
    const p = el('div', { className: 'pad lg' });
    p.append(el('div', { className: 'prose', textContent: 'These are not covered by the findings above. A clean result is only as good as what could be read.' }));
    sc.unreadable.forEach(u => p.append(el('div', { style: 'display:flex;gap:10px;align-items:baseline;margin-top:10px;flex-wrap:wrap' },
      el('span', { className: 'chip mono', textContent: u.file }),
      el('span', { className: 'small muted',
        textContent: u.reason + (u.places > 1 ? ` — in ${u.places} places` : '') }))));
    card.append(p);
    box.append(card);
  }
  if (sc.mentionsOnly?.length) {
    const card = el('div', { className: 'card pad lg', style: 'margin-top:16px' });
    card.append(el('span', { className: 'lbl', textContent: `${sc.mentionsOnly.length} file${sc.mentionsOnly.length === 1 ? '' : 's'} mention the name but carry it nowhere` }));
    const chips = el('div', { className: 'chips', style: 'margin-top:10px' });
    sc.mentionsOnly.forEach(m => chips.append(el('span', { className: 'chip mono', textContent: m.file })));
    card.append(chips);
    box.append(card);
  }
}

// ── step 5 ────────────────────────────────────────────────────────────────
function step5(root) {
  const gs = S.scan?.graphs || [];
  const tabs = x(root, 'tabs'), map = x(root, 'map');
  if (!gs.length) {
    map.append(el('div', { className: 'note good', style: 'max-width:600px;padding:22px 26px' },
      el('b', { textContent: 'No downstream lineage found', style: 'display:block;font-size:15px' }),
      el('div', { style: 'margin-top:6px', textContent: 'These attributes do not feed any table this team publishes.' })));
    x(root, 'next').onclick = () => goto(6);
    return;
  }
  const gi = Math.min(S.graphTab, gs.length - 1);
  tabs.append(el('span', { className: 'lbl faint', textContent: 'Attribute', style: 'margin-right:4px' }));
  gs.forEach((g, i) => {
    const b = el('button', { className: 'pill tab' + (i === gi ? ' on' : '') });
    b.append(el('span', { className: 'mono', textContent: g.attr }),
      el('span', { className: 'sub', textContent: g.table }));
    b.onclick = () => { S.graphTab = i; render(); };
    tabs.append(b);
  });
  const g = gs[gi];
  const card = el('div', { className: 'card pad lg' });
  const row = el('div', { className: 'maprow' });
  const src = el('div', { className: 'mapsrc' });
  src.append(el('div', {},
    el('div', { className: 'k', textContent: 'Upstream source' }),
    el('div', { className: 'tb', textContent: g.table }),
    el('div', { className: 'at', textContent: g.attr }),
    el('div', { className: 'ct', textContent: `${g.branches.length} branch${g.branches.length === 1 ? '' : 'es'} to production` })));
  const branches = el('div', { className: 'branches' });
  g.branches.forEach(br => {
    const line = el('div', { className: 'branch' });
    br.forEach((n, i) => {
      line.append(nodeEl(n));
      if (i < br.length - 1) line.append(el('span', { className: 'arrow', textContent: '→' }));
    });
    branches.append(line);
  });
  row.append(src, branches);
  card.append(row);
  map.append(card);

  const legend = el('div', { className: 'legend' });
  [['var(--redbg)', 'var(--redln)', 'Production table'],
   ['#F4F9FE', '#9CC4EA', 'Intermediate table'],
   ['var(--violetbg)', 'var(--violetln)', 'Alias used for the attribute']].forEach(([bg, ln, label]) =>
    legend.append(el('div', {}, el('i', { style: `background:${bg};border:1px solid ${ln}` }), label)));
  map.append(legend);
  map.append(el('div', { className: 'small muted', style: 'margin-top:12px',
    textContent: 'Each box is a table. The alias is what the column is called at that point — that is the rename a word search would miss.' }));
  x(root, 'next').onclick = () => makeSummary();
}

function nodeEl(n) {
  const d = el('div', { className: 'node' + (n.prod ? ' prod' : '') });
  d.append(el('div', { className: 'top' },
    el('span', { className: 'k', textContent: n.kind }),
    el('span', { className: 'nm', textContent: n.name })));
  if (n.alias) d.append(el('div', { className: 'al' },
    el('span', { textContent: 'alias' }),
    el('span', { className: 'chip alias', textContent: n.alias })));
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
  x(root, 'sub').textContent = s.writtenBy === 'ai'
    ? `Written by ${S.health.ai.model} from the findings — no code was sent to it.`
    : 'Written from the findings without AI.';

  const b = x(root, 'body');
  const grid = el('div', { className: 'grid2', style: 'grid-template-columns:1.7fr 1fr' });

  // ── the summary itself ──
  const main = el('div', { className: 'card clip' });
  main.append(el('div', { className: 'chead', style: 'background:#fff;padding:18px 26px' },
    el('b', { textContent: s.headline, style: 'font-size:16px;font-weight:800;line-height:1.35' }),
    el('span', { className: 'badge ' + cls, textContent: label, style: 'margin-left:auto;flex-shrink:0' })));
  main.append(el('p', { style: 'padding:20px 26px 4px;font-size:14.5px;line-height:1.7;color:var(--body)', textContent: s.narrative }));
  const ul = el('ul', { className: 'ticks', style: 'padding:16px 26px 24px;margin-top:0' });
  (s.bullets || []).forEach(t => ul.append(el('li', {}, t)));
  main.append(ul);
  const fields = el('div', { style: 'padding:0 26px 24px;display:grid;grid-template-columns:1fr 1fr;gap:16px 24px' });
  [['Source system', S.vals.source, false], ['Change type', S.vals.changeType, false],
   ['Upstream tables name', S.vals.upstream.map(u => u.table).join(', '), true],
   ['Upstream attributes name', S.vals.upstream.flatMap(u => u.attrs).join(', '), true]].forEach(([k, v, mono]) =>
    fields.append(el('div', {}, el('span', { className: 'lbl', textContent: k }),
      el('div', { textContent: v || '—',
        style: 'margin-top:5px;font-size:14px;font-weight:600;line-height:1.45;overflow-wrap:break-word;'
          + (mono ? 'font-family:var(--mono);color:var(--blued)' : 'color:var(--ink)') }))));
  main.append(fields);

  // ── right rail ──
  const rail = el('div', { className: 'rail' });
  const dl = daysLeft(S.vals.effectiveDate);
  const dead = el('div', { className: 'card pad' });
  dead.append(el('span', { className: 'lbl', textContent: 'Deadline' }));
  dead.append(el('div', { textContent: fmtDate(S.vals.effectiveDate) || 'Not given',
    style: 'font-size:20px;font-weight:800;margin-top:8px' }));
  if (dl !== null) dead.append(el('span', { className: 'badge sm ' + (dl <= 21 ? 'amber' : 'blue'),
    textContent: dl < 0 ? 'date has passed' : `${dl} day${dl === 1 ? '' : 's'} left`, style: 'margin-top:8px' }));
  if (S.vals.pocName || S.vals.pocTeam) {
    dead.append(el('div', { className: 'small muted', style: 'margin-top:12px;line-height:1.55' },
      'Upstream contact: ', el('b', { textContent: S.vals.pocName || '—', style: 'color:var(--body)' }),
      S.vals.pocTeam ? ', ' + S.vals.pocTeam : ''));
  }

  const st = S.scan.stats;
  const radius = el('div', { className: 'card pad' });
  radius.append(el('span', { className: 'lbl', textContent: 'Blast radius' }));
  [[st.productionTables, 'production tables impacted'], [st.intermediateTables, 'intermediate tables in the path'],
   [st.filesWithImpact, 'code files to change'], [st.couldNotRead, 'files that must be checked by hand']]
    .forEach(([n, lab]) => radius.append(el('div', { style: 'display:flex;align-items:baseline;gap:10px;padding:6px 0' },
      el('span', { textContent: String(n), style: 'font-size:18px;font-weight:800;color:var(--blued);font-variant-numeric:tabular-nums;min-width:26px' }),
      el('span', { style: 'font-size:13px;color:var(--body)', textContent: lab }))));

  const acts = el('div', { className: 'card pad' });
  acts.append(el('span', { className: 'lbl', textContent: 'What to do' }));
  const ol = el('ol', { className: 'acts' });
  (s.actions || []).forEach(a => ol.append(el('li', {}, a)));
  acts.append(ol);

  rail.append(dead, radius, acts);
  grid.append(main, rail);
  b.append(grid);
  if (S.scan.unreadable?.length) {
    const g = el('div'); renderGaps(g, { unreadable: S.scan.unreadable }); b.append(g);
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

  // who the reply is for — real values only, and nothing here sends anything
  const to = x(root, 'to');
  to.append(el('span', { className: 'small', textContent: 'To', style: 'font-weight:700;color:var(--mute);flex-shrink:0' }));
  to.append(el('span', { className: 'chip',
    textContent: [S.vals.pocName, S.vals.pocEmail].filter(Boolean).join(' · ') || 'No contact was given' }));
  if (S.vals.pocTeam) to.append(el('span', { className: 'badge sm blue', textContent: S.vals.pocTeam }));

  if (S.scan) {
    const [cls, label] = RISK[S.scan.risk] || RISK.none;
    x(root, 'risk').append(el('span', { className: 'badge ' + cls, textContent: label }));
  }
  const dl = daysLeft(S.vals.effectiveDate);
  if (S.vals.effectiveDate) {
    x(root, 'deadline').append(el('div', { className: 'note info', style: 'padding:14px 18px' },
      el('span', { className: 'lbl', style: 'color:var(--blued);display:block', textContent: 'Respond by' }),
      el('div', { style: 'font-size:15px;font-weight:700;margin-top:6px;color:var(--ink)',
        textContent: fmtDate(S.vals.effectiveDate) + (dl !== null ? ` · ${dl} day${dl === 1 ? '' : 's'} left` : '') })));
  }

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
  const card = el('div', { className: 'card clip' });
  root.append(card);
  api('/api/history').then(rows => {
    if (!rows.length) { card.append(el('div', { className: 'pad lg muted', textContent: 'Nothing saved yet.' })); return; }
    const t = el('table', { className: 'hist' });
    const hr = el('tr');
    ['When', 'Subject', 'Source', 'Change', 'Risk', 'Mode', 'Status'].forEach(h => hr.append(el('th', { textContent: h })));
    t.append(hr);
    rows.forEach(r => {
      const [cls, label] = RISK[r.risk] || RISK.none;
      const sel = el('select', { className: 'statussel' });
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
  const grid = el('div', { className: 'grid2 even' });

  const left = el('div', { className: 'card pad lg' });
  left.append(el('span', { className: 'lbl', textContent: 'Repository' }));
  [['Folder', h.repo.path], ['Label', h.repo.label], ['Files indexed', String(h.repo.files)],
   ['Statements understood', String(h.repo.statements)], ['Files unreadable', String(h.repo.unreadable)],
   ['SQL dialect', h.sqlDialect], ['Renames followed', `${h.maxHops} hops`]].forEach(([k, v]) =>
    left.append(el('div', { style: 'display:flex;gap:14px;padding:9px 0;border-top:1px solid var(--hair)' },
      el('span', { className: 'small muted', textContent: k, style: 'width:150px;flex-shrink:0' }),
      el('span', { className: 'small', textContent: v, style: 'font-weight:600;word-break:break-all' }))));
  left.append(el('div', { className: 'note info', style: 'margin-top:18px' },
    'Change any of these with environment variables — ',
    el('span', { className: 'mono', textContent: 'RIPPLE_REPO' }), ', ',
    el('span', { className: 'mono', textContent: 'RIPPLE_SQL_DIALECT' }), ', ',
    el('span', { className: 'mono', textContent: 'GROQ_API_KEY' }), '. See the README.'));

  const right = el('div', { className: 'card pad lg' });
  right.append(el('span', { className: 'lbl', textContent: 'AI (optional)' }));
  right.append(el('div', { className: 'note ' + (h.ai.available ? 'good' : 'info'), style: 'margin-top:12px' },
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

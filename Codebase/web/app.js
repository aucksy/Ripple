/* Ripple — front end.
   Plain JavaScript on purpose: no build step, no framework, nothing to install.
   The same file can be opened, read and changed by anyone. */

//<online-only>
// This file is also the front end of Ripple Offline, which is built from it
// rather than being a second copy — a copy would drift, and the drifting one
// would be the build running where nobody can check it. The lines between
// //<online-only> and //</online-only> are deleted from that build: they are
// the parts that reach out (the GitHub source and the AI key form), which must
// not merely be unused offline but absent. Deleting those lines has to leave
// working JavaScript, so each block is written to read correctly with its
// marked lines gone. The offline build then checks the result for the words
// that should be gone, and fails with the line it found rather than shipping a
// key box onto a locked-down machine. Moving a marker is safe; quietly dropping
// one is not. See Ripple Offline/ripple_offline/webbuild.py.
//</online-only>

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
  //<online-only>
  aiMsg: null,        // result of the last AI key action, kept across redraws
  //</online-only>
  manRows: [{ table: '', attrs: '' }],
  man: { source: '', changeKind: 'unknown', effectiveDate: '', changeDesc: '',
         pocName: '', pocEmail: '', pocTeam: '' },
  busy: false, busyWhat: '',
  openGroup: 'p0', openRow: null, graphTab: 0,
  //<online-only>
  // Repository step. The token is held here only long enough to send it once;
  // it is cleared as soon as the server has accepted it.
  repoTab: null,
  gh: { repo: '', branch: '', token: '' },
  connecting: false, connectMsg: '',
  //</online-only>
};

// Typed by hand, so the awkward ones are given the right control rather than a
// box and a format to remember: a real calendar for the date, the same list of
// change types the scan actually understands, and a contact box that takes as
// many addresses as you care to paste in.
const MAN_FIELDS = [
  ['source', 'Source system', 'text', 'e.g. C360'],
  ['changeKind', 'Change type', 'kind', ''],
  ['effectiveDate', 'Effective date', 'date', ''],
  ['changeDesc', 'What is changing', 'text', 'One line describing the change'],
  ['pocName', 'Contact name', 'text', 'Who sent the notice'],
  ['pocEmail', 'Contact email', 'emails', 'name@corp.example.com, other@corp.example.com'],
  ['pocTeam', 'Contact team', 'text', 'e.g. C360 Data Governance'],
];

const CHANGE_KINDS = [
  ['unknown', 'Not specified'],
  ['removal', 'Attribute decommission'],
  ['value_change', 'Value format change'],
  ['type_change', 'Data type change'],
  ['rename', 'Attribute rename'],
];
const kindLabel = (id) => (CHANGE_KINDS.find(([k]) => k === id) || CHANGE_KINDS[0])[1];

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

/* Every email address in a blob of text, once each.
   People do not type addresses one at a time into a form. They copy the To line
   out of Outlook, which arrives as "Priya Raman <priya@corp.com>; Marcus Hale
   <marcus@corp.com>", or they paste a comma-separated list. Rather than telling
   anyone which of those is allowed, the addresses are picked out of whatever
   arrives and shown back as separate values, so it is obvious what was
   understood. */
const EMAIL_RE = /[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}/g;
function emailList(text) {
  const found = String(text ?? '').match(EMAIL_RE) || [];
  return [...new Set(found.map(a => a.toLowerCase()))];
}

/* A box that takes any number of addresses, showing what it found underneath.
   It updates itself rather than redrawing the screen, which would throw the
   cursor out of the box on every keystroke. */
function emailField(value, onchange, opts = {}) {
  const wrap = el('div');
  const inp = el('input', { type: 'text', value: value || '', placeholder: opts.hint || '',
    style: opts.style || '' });
  const chips = el('div', { className: 'chips', style: 'margin-top:8px' });
  const note = el('div', { className: 'small faint', style: 'margin-top:5px;line-height:1.5' });
  const sync = () => {
    const found = emailList(inp.value);
    chips.innerHTML = '';
    found.forEach(a => chips.append(el('span', { className: 'chip mono', textContent: a })));
    note.textContent = found.length
      ? `${found.length} address${found.length === 1 ? '' : 'es'} read. Separate with commas, or paste the whole To line.`
      : (inp.value.trim() ? 'No email address in what is typed here.' : '');
    onchange(inp.value, found);
  };
  inp.oninput = sync;
  sync();
  wrap.append(inp, chips, note);
  return wrap;
}

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
/* Typing the change in by hand and then being shown "check what Ripple read"
   is being asked to check your own typing. In that mode step 1 is the review,
   so the review step is not in the wizard at all -- rather than being in it,
   greyed out, or silently skipped past while the count still says 7. */
function manualFlow() {
  if (S.step === 1) return S.mode === 'manual';
  return S.vals ? S.vals.extractedBy === 'manual' : false;
}
function stepNumbers() {
  return manualFlow() ? [1, 3, 4, 5, 6, 7] : [1, 2, 3, 4, 5, 6, 7];
}
function nextStepAfter(n) {
  const list = stepNumbers();
  return list[Math.min(list.indexOf(n) + 1, list.length - 1)];
}

function renderSteps() {
  const box = $('#steps');
  box.innerHTML = '';
  stepNumbers().forEach((n, i) => {
    const [label, sub] = STEPS[n - 1];
    const on = S.view === 'wizard' && S.step === n;
    const done = n < S.maxStep && !on;
    const b = el('button', { className: `step${on ? ' on' : ''}${done ? ' done' : ''}` });
    b.disabled = n > S.maxStep;
    b.append(el('span', { className: 'n', textContent: done ? '✓' : String(i + 1) }),
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
    //<online-only>
    el('div', { className: 'srow' },
      el('span', { className: 'dot ' + (h.ai.available ? 'ok' : 'off') }),
      el('span', { textContent: h.ai.available ? 'AI on' : 'AI off — rules only' })),
    //</online-only>
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
    //<online-only>
    const ai = S.health?.ai?.available;
    x(root, 'aiState').textContent = ai
      ? `AI is on — the email is read by ${S.health.ai.modelLabel}.`
      : 'AI is off — fields are found by matching the repository catalogue.';
    //</online-only>
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
      }, 'Reading the pasted notification…');
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
  const small = 'margin-top:7px;font-size:12.5px;font-weight:400;color:var(--mute);padding:7px 11px';
  MAN_FIELDS.forEach(([key, label, type, hint]) => {
    const field = el('div', { className: 'field' }, el('span', { className: 'lbl faint', textContent: label }));
    if (type === 'kind') {
      const sel = el('select', { style: 'margin-top:7px;padding:7px 11px;font-size:12.5px' });
      CHANGE_KINDS.forEach(([k, l]) => sel.append(el('option', { value: k, textContent: l, selected: k === S.man.changeKind })));
      sel.onchange = () => { S.man.changeKind = sel.value; };
      field.append(sel);
    } else if (type === 'emails') {
      field.append(emailField(S.man.pocEmail, (raw) => { S.man.pocEmail = raw; },
        { hint, style: small }));
    } else {
      const inp = el('input', { type: type === 'date' ? 'date' : 'text',
        value: S.man[key], placeholder: hint, style: small });
      inp.oninput = () => { S.man[key] = inp.value; };
      field.append(inp);
      // A date typed in a box is a date somebody has to work out. The picker is
      // the control; this is the answer in words, so a slip is visible.
      if (type === 'date') {
        const said = el('div', { className: 'small faint', style: 'margin-top:5px' });
        const sayDate = () => {
          const dl = daysLeft(inp.value);
          said.textContent = inp.value
            ? fmtDate(inp.value) + (dl === null ? '' : dl < 0 ? ' — that date has passed'
              : ` — ${dl} day${dl === 1 ? '' : 's'} away`)
            : '';
        };
        inp.addEventListener('input', sayDate);
        sayDate();
        field.append(said);
      }
    }
    fields.append(field);
  });

  x(root, 'manDemo').onclick = () => {
    S.manRows = [{ table: 'CUSTOMER_DEMOGRAPHICS', attrs: 'MARKET_CODE, MARKET_NAME' },
                 { table: 'CUSTOMER_ADDRESS', attrs: 'COUNTRY_CODE' }];
    S.man = { source: 'C360', changeKind: 'value_change', effectiveDate: '2026-09-18',
      changeDesc: "Values change from ISO abbreviations to full country names ('US' becomes 'United States').",
      pocName: 'Priya Raman',
      pocEmail: 'priya.raman@corp.example.com, dl-c360-governance@corp.example.com',
      pocTeam: 'C360 Data Governance' };
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
  S.vals = {
    source: S.man.source.trim() || 'Entered manually',
    changeType: kindLabel(S.man.changeKind),
    changeKind: S.man.changeKind || 'unknown',
    changeDesc: S.man.changeDesc.trim() || 'Entered by hand — no notification email was used.',
    subject: 'Manual impact check — ' + S.manRows.filter(r => r.table.trim()).map(r => r.table.trim()).join(', '),
    effectiveDate: S.man.effectiveDate.trim(),
    pocName: S.man.pocName.trim(),
    pocEmail: S.man.pocEmail.trim(), pocEmails: emailList(S.man.pocEmail),
    pocTeam: S.man.pocTeam.trim(),
    upstream: S.manRows.filter(r => r.table.trim()).map(r => ({
      table: r.table.trim(),
      attrs: r.attrs.split(',').map(s => s.trim()).filter(Boolean),
    })),
    extractedBy: 'manual', warnings: [],
  };
  S.emailPreview = null; S.scan = null; S.summary = null; S.savedId = null;
  // Straight to the repository. There is nothing on the review step that was
  // not just typed on this one.
  goto(3);
}

function upload(f) {
  // Check the size here as well as on the server. A hosted copy sits behind a
  // host that rejects an oversized upload itself, and its refusal is a bare
  // number with no explanation — so say it properly before sending anything.
  const cap = S.health?.limits?.maxUploadBytes || 25000000;
  if (f.size > cap) {
    alert(`That file is ${(f.size / 1e6).toFixed(1)} MB. The most this copy of Ripple accepts is `
      + `${Math.round(cap / 1e6)} MB.`
      + (S.health?.serverless
        ? ' It is running on a serverless host, which refuses anything bigger before Ripple'
          + ' sees it. Save the email as .eml, or paste the text into the box below instead.'
        : ''));
    return;
  }
  run(async () => {
    const fd = new FormData();
    fd.append('file', f);
    const out = await api('/api/read-email?useAI=true', { method: 'POST', body: fd });
    acceptExtract(out);
  }, 'Reading the notification…');
}

function acceptExtract(out) {
  S.emailPreview = out.emailPreview || null;
  S.vals = {
    source: out.source || '', changeType: out.changeType || '', changeKind: out.changeKind || 'unknown',
    changeDesc: out.changeDesc || '', subject: out.subject || '', effectiveDate: out.effectiveDate || '',
    pocName: out.pocName || '', pocEmail: out.pocEmail || '', pocEmails: emailList(out.pocEmail),
    pocTeam: out.pocTeam || '',
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
    //<online-only>
    : v.extractedBy === 'ai' ? 'Read by AI — check it'
    //</online-only>
    : 'Found by matching the catalogue — check it';

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
      // Every address, editable, and as many as there are. A notification is
      // often sent by one person on behalf of a mailbox, and the reply has to
      // go to both.
      if (key === 'pocName') {
        card.append(emailField(v.pocEmail, (raw, found) => { v.pocEmail = raw; v.pocEmails = found; },
          { hint: 'name@corp.example.com, other@corp.example.com', style: 'margin-top:8px' }));
      }
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
/* Anything worth saying about the repository before anything is scanned, or
   nothing at all. Online that is a failed connection; offline it is a folder
   that has been moved or deleted since it was chosen, so the offline build
   replaces this whole function rather than sharing it. */
//<online-only>
function repoAlert(h) {
  if (S.connectMsg) {
    return el('div', { className: 'note bad', style: 'margin-bottom:18px' },
      el('b', { textContent: 'Could not connect. ' }), S.connectMsg);
  }
  if (h.connectError) {
    return el('div', { className: 'note warn', style: 'margin-bottom:18px' },
      el('b', { textContent: 'Reading the folder on this machine instead. ' }), h.connectError);
  }
  return null;
}
//</online-only>

function step3(root) {
  const h = S.health;
  if (!h) return;
  //<online-only>
  if (S.repoTab === null) S.repoTab = h.source === 'github' ? 'github' : 'folder';
  const onGit = S.repoTab === 'github';
  const live = h.source === 'github';
  //</online-only>

  x(root, 'title').textContent =
    //<online-only>
    onGit ? 'Read a GitHub repository' :
    //</online-only>
    'Connected repository';
  x(root, 'sub').textContent =
    //<online-only>
    onGit ? 'Point Ripple at a repository and give it an access token. It only ever reads.' :
    //</online-only>
    'This is the code Ripple will search. It is read, never written to.';

  //<online-only>
  $$('[data-src]', root).forEach(b => {
    b.className = 'pill' + (b.dataset.src === S.repoTab ? ' on' : '');
    b.onclick = () => { S.repoTab = b.dataset.src; S.connectMsg = ''; render(); };
  });
  //</online-only>

  const alert = x(root, 'alert'); alert.innerHTML = '';
  const said = repoAlert(h);
  if (said) alert.append(said);

  x(root, 'left').innerHTML = '';
  x(root, 'left').append(
    //<online-only>
    onGit ? gitHubForm(h, live) :
    //</online-only>
    repoFacts(h));

  // the same confirmation the prototype shows, on the numbers Ripple really has
  const ready = x(root, 'ready'); ready.innerHTML = '';
  const repoOk = h.repo.exists && h.repo.files > 0;
  // Where the code came from, and the one fact that pins down which version of
  // it was read. A folder that was never a git checkout has no branch, and says
  // nothing rather than claiming "main" because that is the usual answer.
  let where = 'a folder on this machine';
  let pin = h.repo.branch ? ['Branch ', el('span', { className: 'mono', textContent: h.repo.branch })] : [];
  //<online-only>
  // Pulled from a hosted repository instead, where the commit is the exact
  // version. Naming the source here is what stops a connect form sitting beside
  // this note from being mistaken for "connected" when the folder is what is
  // really loaded.
  if (live) {
    where = 'from GitHub';
    pin = ['Commit ', el('span', { className: 'mono', textContent: h.github.shortCommit || h.github.branch })];
  }
  //</online-only>
  ready.append(el('div', { className: 'note ' + (repoOk ? 'good' : 'warn') },
    el('b', { textContent: repoOk ? `✓ ${h.repo.label} connected` : `Nothing to scan in ${h.repo.label}`,
      style: 'display:block;font-size:14px' }),
    el('div', { className: 'small', style: 'margin-top:2px;font-weight:600;opacity:.8',
      textContent: where }),
    el('div', { style: 'margin-top:8px;line-height:1.55' },
      pin,
      (pin.length ? ' — ' : '') + (repoOk
        ? `${h.repo.files} file${h.repo.files === 1 ? '' : 's'} ready to scan.`
        : 'check the repository folder in Settings & checks.'))));
  ready.append(neverOpenedNote(h.repo.heldOnline || 0, h.repo.pathTooLong || 0));

  // what kinds of file are in the index — counted, not assumed
  const kinds = x(root, 'kinds'); kinds.innerHTML = '';
  // Nothing indexed means nothing to list, and an empty card sitting there
  // reads as a panel that failed to load.
  kinds.classList.toggle('hide', !h.repo.kinds?.length);
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
    } else if (!cat.tableCount) {
      // "Every table definition was readable" is technically true of nothing at
      // all, and reads as a clean bill of health for a repository that was
      // never read.
      g.append(el('div', { className: 'note info',
        textContent: 'No table definitions were read, so there is no catalogue to check.' }));
    } else if ((h.repo.heldOnline || 0) + (h.repo.pathTooLong || 0)) {
      // The same trap one branch up, one step subtler. "Every table definition
      // was readable" is true of the files that were opened, and sitting in
      // green under a warning that some were not, it reads as a clean bill of
      // health for the repository. It has to say which repository it means.
      g.append(el('div', { className: 'note info', textContent:
        'Every table definition in the files that could be opened was readable. '
        + 'The files above were not opened, so nothing is known about them.' }));
    } else {
      g.append(el('div', { className: 'note good', textContent: 'Every table definition was readable.' }));
    }
  });

  const reread = x(root, 'reindex');
  reread.disabled = S.busy;
  if (S.busy) reread.textContent = 'Reading the repository…';
  reread.onclick = () => run(async () => {
    S.health = await api('/api/reindex', { method: 'POST' });
    render();
  }, `Reading every file in ${h.repo.label}…`);
  x(root, 'next').onclick = () => runScan();
  x(root, 'next').disabled = S.busy;
  x(root, 'hint').textContent = S.busy
    ? 'Reading every file. On a large repository this takes a few seconds — the counts above update when it finishes.'
    : repoOk
      ? `Scanning ${h.repo.label}.`
      : 'Nothing is indexed, so a scan would find nothing.';
  // Both halves matter. Files can be indexed from a folder that has since been
  // moved or deleted, and offering to scan it would be scanning a memory.
  x(root, 'next').disabled = !repoOk || S.busy;
}

/* What Ripple is reading now — the same facts either way. */
function repoFacts(h) {
  //<online-only>
  const live = h.source === 'github';
  //</online-only>
  const r = el('div', { className: 'card pad lg' });
  r.append(el('span', { className: 'lbl', textContent:
    //<online-only>
    live ? 'GitHub repository' :
    //</online-only>
    'Folder on this machine' }));
  r.append(el('div', { className: 'mono', textContent: h.repo.label,
    style: 'font-size:17px;font-weight:600;color:var(--blued);margin-top:8px;word-break:break-all' }));
  r.append(el('div', { className: 'small faint', textContent: h.repo.path,
    style: 'margin-top:5px;word-break:break-all' }));
  const facts = [
    ['Files indexed', String(h.repo.files)],
    // Only when there are some. "Files indexed 1,770" is the number somebody
    // reads to decide the whole folder was covered, so when it was not, the
    // row saying so has to sit directly underneath it.
    ...(((h.repo.heldOnline || 0) + (h.repo.pathTooLong || 0))
      ? [['Files never opened', String((h.repo.heldOnline || 0) + (h.repo.pathTooLong || 0))]]
      : []),
    ['Statements understood', String(h.repo.statements)],
    // A folder that was never a git checkout has no branch, and an empty row
    // would read as a missing answer rather than as "there isn't one".
    ...(h.repo.branch ? [['Branch', h.repo.branch]] : []),
    ['SQL read as', h.sqlDialect],
    ['Renames followed', `${h.maxHops} hops deep`],
  ];
  //<online-only>
  if (live) {
    facts.splice(3, 0, ['Commit read', h.github.commit ? h.github.commit.slice(0, 12) : 'unknown']);
    facts.push(['Visibility', h.github.private ? 'private' : 'public']);
  }
  //</online-only>
  const t = el('div', { style: 'margin-top:18px' });
  facts.forEach(([k, val]) => t.append(el('div', { style: 'display:flex;gap:14px;padding:9px 0;border-top:1px solid var(--hair)' },
    el('span', { className: 'small muted', textContent: k, style: 'flex:1' }),
    el('span', { className: 'small' + (k === 'Commit read' ? ' mono' : ''), textContent: val, style: 'font-weight:700' }))));
  r.append(t);
  //<online-only>
  if (live) {
    const off = el('button', { className: 'ghost sm', textContent: 'Disconnect and forget the token', style: 'margin-top:18px' });
    off.onclick = () => run(async () => {
      S.health = await api('/api/repo/disconnect', { method: 'POST' });
      S.repoTab = 'folder'; S.connectMsg = ''; S.gh.token = '';
      render();
    });
    r.append(off);
  }
  //</online-only>
  return r;
}

/* The connect form. Nothing here pretends: the button does one real request. */
//<online-only>
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
//</online-only>

function runScan() {
  run(async () => {
    S.scan = await api('/api/scan', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ upstream: S.vals.upstream, changeKind: S.vals.changeKind || 'unknown' }),
    });
    S.summary = null; S.openGroup = 'p0'; S.openRow = null; S.graphTab = 0;
    goto(4);
  }, 'Searching every file for these names…');
}

// ── step 4 ────────────────────────────────────────────────────────────────
function step4(root) {
  const sc = S.scan;
  if (!sc) { x(root, 'progress').append(el('div', { className: 'note info', textContent: 'No scan yet.' })); return; }
  const [cls, label] = RISK[sc.risk] || RISK.none;
  x(root, 'risk').append(el('span', { className: 'badge ' + cls, textContent: label }));
  // The line under the title has to be true of the screen underneath it, and
  // "grouped under the production table" is not true when there is not one.
  x(root, 'sub').textContent = sc.groups.length
    ? 'Every finding grouped under the production table it puts at risk.'
    : (sc.reached || []).length || (sc.other || []).length
      ? 'Nothing matched your published-table rule. Every table the change does reach is below.'
      : 'What the change touches in this repository, and what could not be read.';

  // What was actually read. Real counts only — the scan has already finished by
  // the time this renders, so there is nothing to animate.
  const done = el('div', { className: 'card pad lg' });
  done.append(el('div', { style: 'display:flex;align-items:center;gap:12px;flex-wrap:wrap' },
    el('span', { className: 'chip mono', textContent: S.health.repo.label }),
    // A folder that was never a git checkout has no branch, and an empty chip
    // sitting there reads as something that failed to load.
    S.health.repo.branch ? el('span', { className: 'chip', textContent: S.health.repo.branch }) : null,
    el('span', { textContent: sc.stats.filesWithImpact
      ? `Scan complete — ${sc.stats.filesWithImpact} file${sc.stats.filesWithImpact === 1 ? '' : 's'} with impact`
      : 'Scan complete — nothing carries these attributes',
      style: 'margin-left:auto;font-size:13px;font-weight:600;color:var(--blued)' })));
  done.append(el('div', { style: 'display:flex;align-items:baseline;gap:9px;margin-top:18px;flex-wrap:wrap' },
    el('span', { className: 'big', textContent: String(sc.filesScanned) }),
    el('span', { className: 'small muted', textContent: `files read · ${sc.filesMatched} mention the names you confirmed` })));
  x(root, 'progress').append(done);

  const st = sc.stats;
  const reached = sc.reached || [], other = sc.other || [];
  const cards = [
    ['Production tables at risk', st.productionTables, st.productionTables ? 'var(--red)' : 'var(--green)', 'Matched your published-table rule'],
    ['Other tables reached', st.tablesReached ?? 0, (st.tablesReached ? 'var(--amber)' : ''), 'The chain ends at these'],
    ['Attributes impacted', st.attributesImpacted, '', 'Of those you confirmed'],
    ['Files to change', st.filesWithImpact, '', `Of ${sc.filesScanned} scanned`],
    ['Breaking usages', st.breakingUsages, st.breakingUsages ? 'var(--amber)' : '', 'Filters, joins, ranking'],
    ['To check by hand', st.couldNotRead, st.couldNotRead ? 'var(--amber)' : '', 'Ripple could not follow these'],
  ];
  // Only ever shown when there are some. A "0 never opened" card would be a
  // reassurance nobody asked for, taking room from the six that carry a result.
  if (st.neverOpened) {
    cards.push(['Never opened', st.neverOpened, 'var(--red)', 'Not on this machine, or path too long']);
  }
  const box = x(root, 'stats');
  cards.forEach(([l, v, colour, sub]) => box.append(el('div', { className: 'stat' },
    el('span', { className: 'lbl', textContent: l }),
    el('div', { className: 'v', textContent: String(v), style: colour ? `color:${colour}` : '' }),
    el('div', { className: 's', textContent: sub }))));

  const groups = x(root, 'groups');
  // The clean result is only ever offered when there is genuinely nothing:
  // no production table, no other table, and no loose usage anywhere. Anything
  // less than that and a green tick is the tool lying to your face.
  if (!sc.groups.length && !reached.length && !other.length) {
    groups.append(el('div', { className: 'note good', style: 'display:flex;align-items:center;gap:14px;padding:18px 22px' },
      el('span', { textContent: '✓', style: 'width:30px;height:30px;border-radius:50%;background:var(--green);color:#fff;display:flex;align-items:center;justify-content:center;font-weight:700;flex-shrink:0' }),
      el('div', {}, el('b', { textContent: 'Nothing in this repository uses these attributes', style: 'display:block' }),
        el('div', { style: 'margin-top:3px', textContent: 'No table is built from them, and no code reads them. Check the list below to confirm the names were the right ones.' }))));
  }
  // With nothing on the production list, the first table the change reaches is
  // the most important thing on the screen, so it opens rather than sitting
  // shut behind a caret like a footnote.
  if (!sc.groups.length && reached.length && S.openGroup === 'p0') S.openGroup = 'r0';
  sc.groups.forEach((g, gi) => groups.append(groupCard(g, `p${gi}`, 'Production table', '')));

  if (reached.length) {
    // These used to be thrown away. A chain that ends at a table nobody has
    // told Ripple is published is not a chain that goes nowhere.
    groups.append(el('div', { className: 'note warn', style: 'margin-top:20px' },
      el('b', { textContent: `The change reaches ${reached.length} more table${reached.length === 1 ? '' : 's'}, `
        + `${sc.groups.length ? 'beyond the ones above' : 'none of them on your published list'}. ` }),
      'Ripple decides which tables are the ones your team publishes from a naming rule — '
      + `currently ${S.health?.production || 'not set'}. Nothing below matches it, so Ripple `
      + 'cannot tell you whether anyone outside your team reads these. If they are your published '
      + 'tables, correct the rule on the settings screen and run the scan again.'));
    reached.forEach((g, gi) => groups.append(groupCard(g, `r${gi}`, 'Chain ends here', 'background:var(--amber);color:#fff')));
  }

  if (other.length) {
    const card = el('div', { className: 'card clip', style: 'margin-top:20px' });
    card.append(el('div', { className: 'chead' },
      el('b', { textContent: `${other.length} more usage${other.length === 1 ? '' : 's'} that build no table` })));
    const p = el('div', { className: 'pad lg' });
    p.append(el('div', { className: 'prose', textContent:
      'The attribute is read here, but this code does not write a table Ripple can name — a bare query, or a job whose destination is set somewhere it cannot see. Real usages all the same.' }));
    other.forEach((r, ri) => {
      const key = `o${ri}`, ro = S.openRow === key;
      const line = el('div', { style: 'display:flex;gap:10px;align-items:baseline;margin-top:10px;flex-wrap:wrap;cursor:pointer' },
        el('span', { className: 'chip mono', textContent: r.file }),
        el('span', { className: 'badge sm ' + (r.breaking ? 'red' : 'grey'), textContent: r.logic }),
        el('span', { className: 'small muted', textContent: `on ${r.attr}` }));
      line.onclick = () => { S.openRow = ro ? null : key; render(); };
      p.append(line);
      if (ro) p.append(detailFor(r));
    });
    card.append(p);
    groups.append(card);
  }

  x(root, 'gaps').innerHTML = '';
  renderChecks(x(root, 'gaps'), sc);
  renderGaps(x(root, 'gaps'), sc);
  x(root, 'next').onclick = () => goto(5);
}

/* One production table, or one table a chain ends at. The same rows either
   way -- what differs is what Ripple is able to claim about the table. */
function groupCard(g, key, tag, tagStyle) {
  const card = el('div', { className: 'card clip group' });
  const open = S.openGroup === key;
  const head = el('div', { className: 'ghead' + (open ? ' open' : '') });
  head.append(
    el('span', { className: 'tag', textContent: tag, style: tagStyle }),
    el('div', { className: 'mono', textContent: g.prod, style: 'font-size:15px;font-weight:600' }),
    el('span', { className: 'badge grey', textContent: `${g.rows.length} impact${g.rows.length === 1 ? '' : 's'}` }),
    el('span', { className: 'small muted', textContent: g.note }),
    el('span', { className: 'caret', textContent: '›' }));
  head.onclick = () => { S.openGroup = open ? null : key; S.openRow = null; render(); };
  card.append(head);
  if (!open) return card;
  const hr = el('div', { className: 'rowhead' });
  ['Table it lands in', 'Attribute impacted', 'Alias used', 'What the code does', 'Value', ''].forEach(h => hr.append(el('span', { textContent: h })));
  card.append(hr);
  g.rows.forEach((r, ri) => {
    const rowKey = `${key}-${ri}`, ro = S.openRow === rowKey;
    const row = el('div', { className: 'row' + (ro ? ' open' : '') });
    row.append(
      el('span', { className: 'mono', textContent: r.inter, style: 'font-weight:600;font-size:13px;min-width:0;overflow-wrap:break-word' }),
      el('span', { className: 'mono', textContent: r.attr, style: 'font-size:13px;font-weight:600;color:var(--blued);min-width:0;overflow-wrap:break-word' }),
      el('span', {}, el('span', { className: 'chip alias', textContent: r.alias })),
      // The second badge goes inside the same cell rather than adding a column,
      // so a row that has it lines up with the rows that do not.
      el('span', {}, el('span', { className: 'badge sm ' + (r.breaking ? 'red' : 'grey'), textContent: r.logic }),
        r.certain === false
          ? el('span', { className: 'badge sm grey', style: 'margin-left:6px',
              textContent: 'table not stated' })
          : null),
      el('span', {}, el('span', { className: 'badge sm ' + (r.mode === 'Direct pull' ? 'blue' : 'violet'), textContent: r.mode })),
      el('span', { className: 'caret', textContent: '›' }));
    row.onclick = () => { S.openRow = ro ? null : rowKey; render(); };
    card.append(row);
    if (ro) card.append(detailFor(r));
  });
  return card;
}

/* Attribute by attribute: what was looked for and what came back.
   "It said no impact and I have no way to check" is answered here rather than
   by asking anyone to trust the headline. An attribute that is not written
   down anywhere in the repository looks nothing like one that is used in nine
   files, and both used to end up behind the same green tick. */
function renderChecks(box, sc) {
  const rows = sc.attributes || [];
  if (!rows.length) return;
  const card = el('div', { className: 'card clip', style: 'margin-top:20px' });
  card.append(el('div', { className: 'chead' },
    el('b', { textContent: 'Every attribute you asked about, and what came back' })));
  const p = el('div', { className: 'pad lg' });
  p.append(el('div', { className: 'prose', textContent:
    `Searched ${sc.filesScanned} file${sc.filesScanned === 1 ? '' : 's'}. This is how to check the result: `
    + 'an attribute nobody writes down anywhere is the usual reason a scan comes back clean.' }));
  rows.forEach(a => {
    const used = a.found > 0;
    const badge = a.reachesProduction
      ? ['red', 'reaches a published table']
      : used
        ? ['amber', `used in ${a.files} file${a.files === 1 ? '' : 's'}`]
        : a.mentionedIn
          ? ['grey', `named in ${a.mentionedIn} file${a.mentionedIn === 1 ? '' : 's'}, never read from`]
          : ['grey', 'this name is not in the repository at all'];
    p.append(el('div', { style: 'display:flex;gap:10px;align-items:baseline;margin-top:10px;flex-wrap:wrap' },
      el('span', { className: 'chip mono', textContent: `${a.table}.${a.attr}` }),
      el('span', { className: 'badge sm ' + badge[0], textContent: badge[1] }),
      (a.endsAt || []).length
        ? el('span', { className: 'small muted', textContent: 'ends at ' + a.endsAt.join(', ') })
        : null));
    // How widely the name is used as a name. A scan for a column half the
    // warehouse shares looks identical on screen to a scan for one only this
    // table has, and the two are not remotely the same answer: the first
    // produces a long list because the name is everywhere, the second because
    // something is badly wrong. Only said when the name really is widespread —
    // "this name is in 1 of 60 tables" is a fact nobody needs.
    if (a.nameInTables > 1 && a.tablesRead) {
      const share = a.nameInTables / a.tablesRead;
      if (share >= 0.25) {
        p.append(el('div', { className: 'small muted', style: 'margin:4px 0 0 4px;line-height:1.55',
          textContent: `"${a.attr}" is a column name in ${a.nameInTables} of the ${a.tablesRead} `
            + `tables Ripple could read. The findings below follow it out of ${a.table} only, `
            + 'so a long list here is the name being common rather than the change being bigger.' }));
      }
    }
    if (a.uncertain) {
      p.append(el('div', { className: 'small muted', style: 'margin:4px 0 0 4px;line-height:1.55',
        textContent: `${a.uncertain} of these are on a line where the SQL did not say which table `
          + `the ${a.attr} came from, and more than one table in that statement has one. They are `
          + 'marked "table not stated" below — real usages, on that line, with the table inferred.' }));
    }
  });
  card.append(p);
  box.append(card);
}

/* The address of a finding in the connected repository, or nothing at all.
   Points at the first line that actually matched, not the top of the file. */
//<online-only>
function fileUrl(r) {
  const tpl = S.scan?.repo?.urlTemplate;
  if (!tpl || !r.file) return '';
  const hit = (r.lines || []).find(l => l.hit) || (r.lines || [])[0];
  return tpl.replace('{path}', r.file).replace('{line}', String(hit?.n ?? 1));
}
//</online-only>

function detailFor(r) {
  const d = el('div', { className: 'detail' });
  d.append(el('div', { className: 'note ' + (r.noLocalFix ? 'bad' : r.breaking ? 'warn' : 'info') },
    el('b', { textContent: r.noLocalFix ? 'No local fix — the upstream team must supply a replacement. ' : r.breaking ? 'This breaks. ' : 'Changes, but does not break. ' }),
    r.impact));
  // The usage is on that line and it is real. What is inferred is which table
  // the column came from, and in a warehouse where the same key columns are in
  // nearly every table that is worth stating rather than glossing.
  if (r.certain === false) {
    d.append(el('div', { className: 'note info', style: 'margin-top:10px' },
      el('b', { textContent: 'The table is inferred here. ' }),
      `This statement reads more than one table with a column called ${r.attr}, and the SQL `
      + `does not say which one this is. Ripple has counted it as ${r.from}'s. Worth a look at `
      + 'the code below before acting on it.'));
  }
  const code = el('div', { className: 'code' });
  const head = el('div', { className: 'f' },
    el('span', { className: 'name', textContent: r.file }),
    el('span', { className: 'lang', textContent: r.lang }));
  // Only offered when Ripple genuinely knows the address of this code. On a
  // local folder there is nothing to link to, so no link is shown.
  //<online-only>
  const href = fileUrl(r);
  if (href) {
    head.append(el('a', { href, textContent: 'Open in GitHub ↗', target: '_blank', rel: 'noopener' }));
  }
  //</online-only>
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

/* Files that were never opened at all.

   Not the same thing as a file that was read and not understood, and much
   worse. A file Ripple could not parse is on the "check by hand" list and
   somebody goes and looks at it. A file that was never opened leaves no trace
   anywhere: the finding list is shorter, the tick is green, and nothing on the
   screen is false — it is just answering a question about half a repository.

   So this says the number, says why, and says the one thing that fixes it. */
function neverOpenedNote(heldOnline, tooLong) {
  const total = (heldOnline || 0) + (tooLong || 0);
  if (!total) return el('span', { className: 'hide' });
  const note = el('div', { className: 'note warn', style: 'margin-top:12px' });
  note.append(el('b', { style: 'display:block;font-size:14px',
    textContent: `${total} file${total === 1 ? '' : 's'} here ${total === 1 ? 'was' : 'were'} never opened` }));
  if (heldOnline) {
    note.append(el('div', { style: 'margin-top:8px;line-height:1.55', textContent:
      `${heldOnline} file${heldOnline === 1 ? ' is' : 's are'} not really on this machine — `
      + 'OneDrive is holding them online-only, and this copy has no internet to fetch them. '
      + 'Nothing in them was read, so nothing in them can appear in a result.' }));
    note.append(el('div', { className: 'small', style: 'margin-top:6px;line-height:1.55', textContent:
      'To fix it: in File Explorer, right-click the repository folder and choose '
      + '"Always keep on this device", wait for OneDrive to finish, then read the repository again.' }));
  }
  if (tooLong) {
    note.append(el('div', { style: 'margin-top:8px;line-height:1.55', textContent:
      `${tooLong} file${tooLong === 1 ? ' has a path that is' : 's have paths that are'} `
      + 'too long for Windows to open on this machine. Nothing in them was read.' }));
    note.append(el('div', { className: 'small', style: 'margin-top:6px;line-height:1.55', textContent:
      'To fix it: move the repository nearer the top of the drive — C:\\repo rather than a '
      + 'deep folder inside Documents — then read it again.' }));
  }
  return note;
}

/* The honest half of the report: what Ripple could NOT account for. Styled to
   stand out, never to shrink — a clean finding list is only worth what was read. */
function renderGaps(box, sc) {
  if (sc.heldOnline?.length || sc.pathTooLong?.length) {
    const card = el('div', { className: 'card pad lg', style: 'margin-top:20px;border-color:var(--amberln)' });
    card.append(neverOpenedNote(sc.heldOnline?.length || 0, sc.pathTooLong?.length || 0));
    const names = [...(sc.heldOnline || []), ...(sc.pathTooLong || [])];
    const chips = el('div', { className: 'chips', style: 'margin-top:12px' });
    names.slice(0, 200).forEach(f => chips.append(el('span', { className: 'chip mono', textContent: f })));
    card.append(chips);
    if (names.length > 200) {
      card.append(el('div', { className: 'small muted', style: 'margin-top:8px',
        textContent: `and ${names.length - 200} more, not listed here to keep this page readable.` }));
    }
    box.append(card);
  }
  if (sc.unreadable?.length) {
    const card = el('div', { className: 'card clip', style: 'margin-top:20px;border-color:var(--amberln)' });
    card.append(el('div', { className: 'chead', style: 'background:var(--amberbg);border-bottom-color:var(--amberln)' },
      el('span', { className: 'tag', style: 'background:var(--amber);color:#fff', textContent: 'Check by hand' }),
      el('b', { textContent: `${sc.unreadable.length} file${sc.unreadable.length === 1 ? '' : 's'} to check by hand` })));
    const p = el('div', { className: 'pad lg' });
    p.append(el('div', { className: 'prose', textContent:
      'Ripple either could not read these, or found your name in them somewhere it cannot follow — inside a procedure call, a loop, or written as text. They are not covered by the findings above, and a clean result is only as good as what could be followed.' }));
    // The point of this list is that somebody opens those files and checks
    // them, so it gives them the line to open at and the line itself. "Could
    // not parse" sends a person hunting through a thousand-line file.
    sc.unreadable.forEach(u => {
      const item = el('div', { style: 'margin-top:14px' });
      item.append(el('div', { style: 'display:flex;gap:10px;align-items:baseline;flex-wrap:wrap' },
        el('span', { className: 'chip mono', textContent: u.file }),
        el('span', { className: 'small muted',
          textContent: u.reason + (u.places > 1 ? ` — in ${u.places} places` : '') })));
      if (u.snippet) {
        item.append(el('div', { className: 'mono small',
          style: 'margin-top:6px;padding:8px 12px;background:var(--amberbg);border:1px solid var(--amberln);'
            + 'border-radius:6px;overflow-x:auto;white-space:pre' },
          `line ${u.line} · ${u.snippet}`));
      }
      if (u.hint) {
        item.append(el('div', { className: 'small muted', style: 'margin-top:6px;line-height:1.55', textContent: u.hint }));
      }
      p.append(item);
    });
    card.append(p);
    box.append(card);
  }
  if (sc.mentionsOnly?.length) {
    const card = el('div', { className: 'card pad lg', style: 'margin-top:16px' });
    card.append(el('span', { className: 'lbl',
      textContent: sc.mentionsOnly.length === 1
        ? '1 file mentions the name but carries it nowhere'
        : `${sc.mentionsOnly.length} files mention the name but carry it nowhere` }));
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
    // The summary is written here, not on the summary step. Sending someone
    // straight on to step 6 left that screen with nothing to draw and two
    // buttons that did nothing -- which only ever happened on a clean result,
    // exactly when somebody most wants to get to the reply.
    x(root, 'next').onclick = () => makeSummary();
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
  const ends = g.endBranches || [];
  const all = g.branches.concat(ends);
  const card = el('div', { className: 'card pad lg' });
  const row = el('div', { className: 'maprow' });
  const src = el('div', { className: 'mapsrc' });
  src.append(el('div', {},
    el('div', { className: 'k', textContent: 'Upstream source' }),
    el('div', { className: 'tb', textContent: g.table }),
    el('div', { className: 'at', textContent: g.attr }),
    el('div', { className: 'ct', textContent: `${all.length} branch${all.length === 1 ? '' : 'es'} followed`
      + (g.branches.length ? ` · ${g.branches.length} to production` : '') })));
  const branches = el('div', { className: 'branches' });
  all.forEach(br => {
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
  if (ends.length) {
    map.append(el('div', { className: 'note warn', style: 'margin-top:14px' },
      el('b', { textContent: `${ends.length} of these branch${ends.length === 1 ? ' ends' : 'es end'} at a table `
        + 'that does not match your published-table rule. ' }),
      'They are drawn because the change reaches them either way — Ripple simply cannot say '
      + 'whether anyone outside your team reads them.'));
  }

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
  }, 'Writing the summary…');
}

function step6(root) {
  const s = S.summary;
  // A screen with nothing on it and two buttons that do nothing is the worst
  // way to say "the summary has not been written yet". If we ever arrive here
  // without one, say so and offer the one button that fixes it.
  if (!s) {
    x(root, 'sub').textContent = 'The summary has not been written yet.';
    const b = x(root, 'body');
    const go = el('button', { className: 'pri', textContent: 'Write the summary now' });
    go.onclick = () => makeSummary();
    b.append(el('div', { className: 'note info', style: 'max-width:620px' },
      el('b', { textContent: 'Nothing to show yet. ', style: 'display:block' }),
      'The summary is written from the findings when you leave the dependency map. '
      + 'It has not been written for this scan.'), el('div', { style: 'margin-top:14px' }, go));
    x(root, 'next').onclick = () => makeSummary();
    x(root, 'save').disabled = true;
    x(root, 'saved').textContent = 'Nothing to save until the summary is written.';
    return;
  }
  const [cls, label] = RISK[S.scan.risk] || RISK.none;
  x(root, 'sub').textContent =
    //<online-only>
    s.writtenBy === 'ai' ? `Written by ${S.health.ai.modelLabel} from the findings — no code was sent to it.` :
    //</online-only>
    'Written from the findings without AI.';

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
  // "Saved" has to mean saved. Where it does not really last, say so in the
  // same breath rather than letting the word stand on its own. This sits in a
  // row between two buttons, so it stays one short line -- the full
  // explanation is on the Past analyses screen.
  const saved = x(root, 'saved');
  saved.textContent = '';
  if (S.savedId) {
    saved.append(el('span', { className: 'badge sm green', textContent: `Saved as analysis #${S.savedId}` }));
    if (S.health?.limits?.historyKept === false) {
      saved.append(el('span', { className: 'small faint',
        textContent: ' This host wipes saved analyses — copy out anything you need to keep.' }));
    }
  }
  x(root, 'save').onclick = () => run(async () => {
    const out = await api('/api/history', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ vals: S.vals, scan: S.scan, summary: S.summary, mode: S.vals.extractedBy }),
    });
    S.savedId = out.id || null;
    if (!out.saved) alert('History is not available here: ' + (out.reason || ''));
    render();
  }, 'Saving this analysis…');
}

// ── step 7 ────────────────────────────────────────────────────────────────
function step7(root) {
  const r = S.reply || { subject: '', body: '' };
  const subj = x(root, 'subject'); subj.value = r.subject; subj.oninput = () => { r.subject = subj.value; };
  const body = x(root, 'body'); body.value = r.body; body.oninput = () => { r.body = body.value; };
  const ol = x(root, 'acts');
  (S.summary?.actions || []).forEach(a => ol.append(el('li', {}, a)));

  // who the reply is for — real values only, and nothing here sends anything.
  // Every address, one chip each, so a list of four is not one long unreadable
  // string that hides a typo in the middle of it.
  const to = x(root, 'to');
  const addresses = S.vals.pocEmails?.length ? S.vals.pocEmails : emailList(S.vals.pocEmail);
  to.append(el('span', { className: 'small', textContent: 'To', style: 'font-weight:700;color:var(--mute);flex-shrink:0' }));
  if (S.vals.pocName) to.append(el('span', { className: 'chip', textContent: S.vals.pocName }));
  addresses.forEach(a => to.append(el('span', { className: 'chip mono', textContent: a })));
  if (!S.vals.pocName && !addresses.length) {
    to.append(el('span', { className: 'chip', textContent: 'No contact was given' }));
  }
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
    // The addresses go with it. Copying a reply and then having to gather the
    // recipients again by hand is half a job.
    const head = addresses.length ? `To: ${addresses.join('; ')}\n` : '';
    await navigator.clipboard.writeText(`${head}Subject: ${r.subject}\n\n${r.body}`);
    x(root, 'copied').textContent = addresses.length
      ? `Copied, with ${addresses.length} recipient${addresses.length === 1 ? '' : 's'} — paste it into Outlook.`
      : 'Copied — paste it into Outlook.';
  };
  x(root, 'restart').onclick = () => {
    Object.assign(S, { step: 1, maxStep: 1, vals: null, scan: null, summary: null, reply: null,
      savedId: null, emailPreview: null, openGroup: 'p0', openRow: null, graphTab: 0 });
    render();
  };
}

// ── history & settings ────────────────────────────────────────────────────
function historyView(root) {
  const kept = S.health?.limits?.historyKept !== false;
  root.append(el('div', { className: 'head' }, el('div', {},
    el('h2', { textContent: 'Past analyses' }),
    el('p', { textContent: kept
      ? 'Everything saved on this server, newest first.'
      : 'Newest first — but this list does not last on this host. See the note below.' }))));
  // A hosted copy is replaced constantly and takes its saved rows with it.
  // An empty list would otherwise look like a bug or like lost work.
  if (!kept) {
    root.append(el('div', { className: 'note warn', style: 'margin-bottom:18px' },
      el('b', { textContent: 'Saved analyses do not survive here. ' }),
      'This copy of Ripple runs on a serverless host, which replaces the machine behind '
      + 'the site constantly and wipes anything saved on it. An analysis can vanish within '
      + 'minutes, and the list can look different from one refresh to the next. Nothing is '
      + 'broken and nothing is being deleted on purpose — there is simply nowhere permanent '
      + 'to write. Copy out anything you need to keep before you leave the page.'));
  }
  const card = el('div', { className: 'card clip' });
  root.append(card);
  api('/api/history').then(rows => {
    if (!rows.length) {
      card.append(el('div', { className: 'pad lg muted', textContent: kept
        ? 'Nothing saved yet.'
        : 'Nothing here — either nothing has been saved yet, or this host has already been replaced.' }));
      return;
    }
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

/* Settings, and the AI key form that is most of it. The offline build replaces
   this whole screen: it has no key to set, and it has two settings of its own
   that online reads from environment variables — which folder to scan, and
   which SQL dialect to read it as. */
//<online-only>
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
   ...(((h.repo.heldOnline || 0) + (h.repo.pathTooLong || 0))
     ? [['Files never opened', String((h.repo.heldOnline || 0) + (h.repo.pathTooLong || 0))]]
     : []),
   ['SQL dialect', h.sqlDialect], ['Renames followed', `${h.maxHops} hops`],
   ['Tables you publish', h.production || 'not set']].forEach(([k, v]) =>
    left.append(el('div', { style: 'display:flex;gap:14px;padding:9px 0;border-top:1px solid var(--hair)' },
      el('span', { className: 'small muted', textContent: k, style: 'width:150px;flex-shrink:0' }),
      el('span', { className: 'small', textContent: v, style: 'font-weight:600;word-break:break-all' }))));
  // The one setting on this screen that can turn a real impact into a clean
  // result, so it is explained rather than listed.
  left.append(el('div', { className: 'note warn', style: 'margin-top:18px' },
    el('b', { textContent: 'What "tables you publish" decides. ' }),
    'A finding counts as production impact only if the table it ends at matches that rule. '
    + 'If your published tables are not named that way, Ripple will still list every table the '
    + 'change reaches — but it will not call any of them production, and the headline will read '
    + 'far calmer than the truth.'));
  left.append(el('div', { className: 'note info', style: 'margin-top:14px' },
    'Change any of these with environment variables — ',
    el('span', { className: 'mono', textContent: 'RIPPLE_REPO' }), ', ',
    el('span', { className: 'mono', textContent: 'RIPPLE_SQL_DIALECT' }), ', ',
    el('span', { className: 'mono', textContent: 'RIPPLE_PROD_TABLES' }), ', ',
    el('span', { className: 'mono', textContent: 'GROQ_API_KEY' }), '. See the README.'));

  grid.append(left, aiCard(h));
  root.append(grid);
}

/* Turning the AI on from the screen. Same rules as the GitHub token: the key
   goes to the server, is held in memory only, and never comes back to this
   page — so this form can show whether one is set, never what it is. */
function aiCard(h) {
  const card = el('div', { className: 'card pad lg' });
  const on = h.ai.available;
  const fromEnv = h.ai.keyFrom === 'environment';

  card.append(el('span', { className: 'lbl', textContent: 'AI (optional)' }));
  card.append(el('div', { className: 'note ' + (on ? 'good' : 'info'), style: 'margin-top:12px' },
    el('b', { textContent: on ? `AI is on — ${h.ai.modelLabel}. ` : 'No key set. ' }),
    on
      ? (fromEnv
        ? 'The key came from this server’s settings, so it survives restarts. Only the notification text and the findings are sent — never your source code.'
        : 'The key was typed in here. Only the notification text and the findings are sent — never your source code.')
      : 'Ripple is running on rules alone. Everything works; the wording is just plainer.'));

  // Model first: it applies whether the key is typed in or already set.
  card.append(el('label', { className: 'lbl', style: 'display:block;margin:18px 0 7px',
    textContent: 'Model' }));
  const sel = el('select', { className: 'statussel', style: 'width:100%;padding:11px 12px' });
  (h.ai.models || []).forEach(m => sel.append(el('option', {
    value: m.id, textContent: m.label, selected: m.id === h.ai.model })));
  // The description goes underneath rather than inside the dropdown, which
  // would cut it off at whatever width the box happens to be.
  const why = el('div', { className: 'small faint', style: 'margin-top:6px' });
  const showWhy = () => {
    const m = (h.ai.models || []).find(x => x.id === sel.value);
    why.textContent = m ? m.note : '';
  };
  sel.onchange = showWhy;
  showWhy();
  card.append(sel, why);

  card.append(el('label', { className: 'lbl', style: 'display:block;margin:18px 0 7px',
    textContent: fromEnv ? 'Use a different key instead' : 'Groq API key' }));
  const key = el('input', { type: 'password', autocomplete: 'off', placeholder: 'gsk_…',
    style: 'padding:12px 14px' });
  card.append(key);
  card.append(el('div', { className: 'small faint', style: 'margin-top:6px' },
    'Create one free at console.groq.com. Ripple only ever reads with it.'));

  // The answer is kept in state, not written straight into the page. Every
  // action here ends in a redraw, which would throw away anything appended to
  // this card -- which is why pressing a button used to look like it did
  // nothing at all.
  const out = el('div', { style: 'margin-top:14px' });
  if (S.aiMsg) {
    out.append(el('div', { className: 'note ' + (S.aiMsg.ok ? 'good' : 'warn'), textContent: S.aiMsg.text }));
  }
  const say = (ok, text) => { S.aiMsg = { ok, text }; };

  const save = el('button', { className: 'pri', textContent: on ? 'Save and re-test' : 'Turn the AI on' });
  save.onclick = () => run(async () => {
    S.aiMsg = null;
    try {
      S.health = await api('/api/ai/connect', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ key: key.value, model: sel.value }),
      });
      key.value = '';                    // the server has it; keep no copy here
      say(true, `AI is on. The model answered, using ${S.health.ai.modelLabel}.`);
    } catch (e) { say(false, 'That did not work — ' + e.message); }
  });

  const test = el('button', { className: 'ghost', textContent: 'Test the key' });
  test.onclick = () => run(async () => {
    const res = await api('/api/ai/check', { method: 'POST' });
    say(res.ok, res.ok ? `Working — the model replied, using ${res.model}.` : `Not working — ${res.reason}`);
  });

  const row = el('div', { className: 'foot', style: 'margin-top:16px' }, save, test);
  if (on && h.ai.keyFrom === 'entered') {
    const forget = el('button', { className: 'ghost', textContent: 'Forget the key' });
    forget.onclick = () => run(async () => {
      S.health = await api('/api/ai/forget', { method: 'POST' });
      S.aiMsg = { ok: true, text: 'Key forgotten. Ripple is back to rules alone.' };
    });
    row.append(forget);
  }
  card.append(row, out);

  // On a host that is replaced constantly, a typed key does not last -- and
  // while it does last, every other visitor to this copy is spending it.
  if (h.ai.keyLasts === false) {
    card.append(el('div', { className: 'note warn', style: 'margin-top:18px' },
      el('b', { textContent: 'A key typed in here is shared, and temporary. ' }),
      'This copy of Ripple runs on a serverless host that anyone with the address can open. '
      + 'While your key is loaded, other people using this site will be spending it, and it '
      + 'disappears whenever the machine behind the site is replaced — often within minutes. '
      + 'For anything beyond a demonstration, run Ripple on your own machine, or set the key '
      + 'as an environment variable on the host so it is at least not typed into a public page.'));
  }
  return card;
}
//</online-only>

// ── plumbing ──────────────────────────────────────────────────────────────
function goto(n) { S.step = n; S.maxStep = Math.max(S.maxStep, n); S.view = 'wizard'; render(); }

/* Everything slow goes through here, and everything slow says what it is doing.
   Reading a repository takes seconds on a big one, and a spinning dot in the
   far corner is not an answer -- numbers that change by themselves a while
   later read as a page that did something on its own. */
function run(fn, what) {
  S.busy = true; S.busyWhat = what || 'Working…'; render();
  Promise.resolve(fn()).catch(e => {
    alert('Something went wrong: ' + e.message);
  }).finally(() => { S.busy = false; S.busyWhat = ''; render(); });
}

function render() {
  renderSteps(); renderStatus();
  const view = $('#view'); view.innerHTML = '';
  $('#hRight').innerHTML = '';
  if (S.busy) {
    $('#hRight').append(el('span', { className: 'spin' }),
      el('span', { className: 'small', textContent: S.busyWhat,
        style: 'margin-left:9px;font-weight:600;color:var(--blued)' }));
  }

  if (S.view === 'history') {
    setHeader('Past analyses', S.health?.limits?.historyKept === false
      ? 'Kept only until this host is replaced' : 'Saved on this server');
    historyView(view); return;
  }
  if (S.view === 'settings') { setHeader('Settings & checks', 'Connections and health'); settingsView(view); return; }

  const list = stepNumbers();
  setHeader(STEPS[S.step - 1][0], `Step ${list.indexOf(S.step) + 1} of ${list.length}`);
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

/* Run once, after the server has answered and before the first screen is drawn.
   Nothing to do online. The offline build replaces this to open on the settings
   screen the very first time, when no repository folder has been chosen yet —
   there, that is a question that has to be asked rather than a default that can
   be assumed. */
//<online-only>
function afterBoot() {}
//</online-only>

(async function boot() {
  try { S.health = await api('/api/health'); }
  catch (e) { alert('Could not reach the Ripple server: ' + e.message); }
  afterBoot();
  render();
})();

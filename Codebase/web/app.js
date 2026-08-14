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

/* ── the tables your team publishes ───────────────────────────────────────
   The most expensive setting in Ripple: a finding only counts as production
   impact when the table it ends at is on this list, so a list that is wrong
   turns a change that really breaks three published tables into a calm "no
   production impact". The same control is used on both settings screens —
   online it is held by the running server, offline it is written to the
   settings file beside the program — so there is one of it, here.

   The list can be pasted from wherever it lives: an Excel column, a Slack
   message, a Confluence page, a query result. Nothing is tidied silently:
   whatever the reader declined to use comes back with a reason, and every
   table on the list that Ripple has never seen in the repository is said out
   loud, because that is the one thing that has to be known before a result
   from this list is believed. */
function productionState() {
  if (!S.prod) {
    S.prod = { text: S.health?.productionRule?.text ?? '', report: null,
               checking: false, msg: null, loaded: false, timer: null };
  }
  return S.prod;
}

const PROD_HELP =
  'Paste the real list of tables your team publishes — one per line, or however it '
  + 'arrives from Excel, Slack or Confluence. Ripple reads it as written. A naming '
  + 'pattern still works alongside: a word starting with an underscore matches the end '
  + 'of a table name (_PROD matches sales_prod), * matches anything (PROD_*), and * on '
  + 'its own means treat every table as published.';

function productionCard(opts = {}) {
  const p = productionState();
  const card = el('div', { className: 'card pad lg' });
  card.append(el('span', { className: 'lbl', textContent: 'The tables your team publishes' }));
  card.append(el('div', { className: 'small faint', style: 'margin-top:6px;line-height:1.55',
    textContent: PROD_HELP }));

  const ta = el('textarea', { className: 'mono', rows: 8, value: p.text,
    placeholder: 'cust360_customer_demographics\nfoundation.cust360_customer_address\n_PROD',
    style: 'margin-top:12px;font-size:12.5px;line-height:1.6;resize:vertical' });
  card.append(ta);

  const out = el('div', { style: 'margin-top:14px' });
  const paint = () => { out.innerHTML = ''; out.append(productionReport(p, opts)); };

  const check = () => {
    p.checking = true; paint();
    api('/api/production/read', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: p.text }),
    }).then(r => { p.report = r; })
      .catch(e => { p.report = null; p.msg = { ok: false, text: e.message }; })
      .finally(() => { p.checking = false; paint(); });
  };

  ta.oninput = () => {
    p.text = ta.value; p.msg = null;
    // Checked as it is typed rather than behind a button, but not on every
    // keystroke: the check walks the repository, which is not free.
    clearTimeout(p.timer);
    p.timer = setTimeout(check, 600);
  };
  if (opts.onSave) {
    const row = el('div', { className: 'foot', style: 'margin-top:14px' });
    const save = el('button', { className: 'pri', textContent: 'Save and use this list' });
    save.onclick = () => run(async () => {
      try {
        await opts.onSave(p.text);
        p.msg = { ok: true, text: opts.savedNote || 'Saved. Every scan from now on uses this list.' };
      } catch (e) { p.msg = { ok: false, text: e.message }; }
      p.report = null; p.loaded = false;
    });
    row.append(save);
    if (opts.persistNote) row.append(el('span', { className: 'small faint', textContent: opts.persistNote }));
    card.append(row);
  }
  card.append(out);
  // The list already in force is checked the moment the screen opens, rather
  // than waiting for somebody to touch the box. A rule that matches nothing is
  // worth knowing about before it is edited, not after.
  if (!p.loaded) { p.loaded = true; check(); } else { paint(); }
  return card;
}

/* What Ripple made of the list: what it read, what it ignored and why, and —
   the point of the whole thing — which of these tables it has never seen. */
function productionReport(p, opts = {}) {
  const box = el('div');
  if (p.msg) {
    box.append(el('div', { className: 'note ' + (p.msg.ok ? 'good' : 'bad'), style: 'margin-bottom:12px' },
      p.msg.text));
  }
  if (p.checking && !p.report) {
    box.append(el('div', { className: 'foot' }, el('span', { className: 'spin' }),
      el('span', { className: 'small muted', textContent: 'Reading the list and checking it against the repository…' })));
    return box;
  }
  const r = p.report;
  if (!r) return box;
  if (p.checking) {
    box.append(el('div', { className: 'small faint', style: 'margin-bottom:8px' },
      el('span', { className: 'spin' }), ' Re-checking…'));
  }

  if (!r.entries.length) {
    box.append(el('div', { className: 'note bad' },
      el('b', { textContent: 'Nothing in that box was read as a table name. ' }),
      'Ripple falls back to its own guess — names ending _PROD, _PRD or _PUBLISHED — which '
      + 'is almost certainly not how your tables are named. Paste the list again, one table '
      + 'per line.'));
    if (r.notes.length) box.append(productionNotes(r));
    return box;
  }

  // ── what was read ──
  const head = el('div', { style: 'display:flex;gap:10px;align-items:baseline;flex-wrap:wrap' });
  head.append(el('b', { style: 'font-size:14px', textContent:
    r.nameCount
      ? `${r.nameCount} table name${r.nameCount === 1 ? '' : 's'} read`
      : 'No exact table names — patterns only' }));
  if (r.patternCount) {
    head.append(el('span', { className: 'badge sm violet',
      textContent: `${r.patternCount} pattern${r.patternCount === 1 ? '' : 's'}` }));
  }
  box.append(head);

  const chips = el('div', { className: 'chips scrollbox', style: 'margin-top:10px' });
  r.entries.forEach(e => {
    const chip = el('span', { className: 'chip mono' + (e.isPattern ? ' pattern' : ''),
      textContent: e.given });
    if (e.isPattern) chip.title = e.kind === 'glob'
      ? 'A pattern — matched against the whole table name'
      : 'A pattern — matches the end of a table name';
    chips.append(chip);
  });
  box.append(chips);
  if (r.patternCount) {
    box.append(el('div', { className: 'small faint', style: 'margin-top:8px;line-height:1.5',
      textContent: 'The outlined ones are patterns, not table names. Everything else is matched exactly.' }));
  }

  if (r.notes.length) box.append(productionNotes(r));
  box.append(productionCheck(r));
  return box;
}

function productionNotes(r) {
  const wrap = el('div', { className: 'note info', style: 'margin-top:12px' });
  wrap.append(el('b', { style: 'display:block', textContent: 'What was left out of that paste' }));
  r.notes.forEach(n => {
    const line = el('div', { style: 'margin-top:6px;line-height:1.55' }, n.text);
    if (n.examples && n.examples.length) {
      line.append(el('span', { className: 'small faint',
        textContent: ' — ' + n.examples.join(' · ') }));
    }
    wrap.append(line);
  });
  return wrap;
}

/* The important one. If fifty tables are pasted and Ripple has only ever seen
   forty-four of them, the other six are either misspelled or built somewhere it
   could not read — and either way a clean result for those six means nothing. */
function productionCheck(r) {
  const c = r.check;
  const wrap = el('div');
  if (!c || !c.checked) {
    wrap.append(el('div', { className: 'note warn', style: 'margin-top:12px' },
      el('b', { textContent: 'This list has not been checked against a repository. ' }),
      'Nothing has been read yet, so Ripple cannot say whether these tables exist. '
      + 'Choose the repository, then come back to this box.'));
    return wrap;
  }
  const missing = c.missing || [];
  const total = c.foundCount + missing.length;
  if (total) {
    wrap.append(el('div', { className: 'note ' + (missing.length ? 'bad' : 'good'), style: 'margin-top:12px' },
      el('b', { style: 'display:block;font-size:14px', textContent: missing.length
        ? `${missing.length} of the ${total} table${total === 1 ? '' : 's'} on this list `
          + `${missing.length === 1 ? 'is' : 'are'} not in this repository`
        : `All ${total} table${total === 1 ? '' : 's'} on this list were found in this repository` }),
      el('div', { style: 'margin-top:6px;line-height:1.55', textContent: missing.length
        ? `Ripple read ${c.tablesKnown.toLocaleString()} table names out of the code it could `
          + 'understand, and these are not among them. Either the name is spelled differently '
          + 'here, or the table is built somewhere Ripple could not read. Until that is settled, '
          + 'a clean result for these tables means nothing.'
        : `Checked against the ${c.tablesKnown.toLocaleString()} table names Ripple read out of `
          + 'this repository.' })));
    // Grouped rather than listed one sentence at a time. Sixty rows each saying
    // the same thing is a page nobody scrolls to the end of, and the two groups
    // send a person to two completely different places.
    [['nowhere', 'Not written anywhere in this repository',
      'A misspelling, a table from another repository, or one no code here names at all.'],
     ['written', 'The name is here, but nothing Ripple could read builds it',
      'Something creates these somewhere it could not follow — a procedure, a generated statement, or a job it has never seen.'],
    ].forEach(([state, title, why]) => {
      const group = missing.filter(m => m.state === state);
      if (!group.length) return;
      wrap.append(el('div', { style: 'margin-top:12px' },
        el('span', { className: 'lbl', textContent: `${title} — ${group.length}` }),
        el('div', { className: 'small faint', style: 'margin-top:4px;line-height:1.5', textContent: why })));
      const chips = el('div', { className: 'chips scrollbox', style: 'margin-top:8px' });
      group.forEach(m => chips.append(el('span', { className: 'chip mono', textContent: m.given })));
      wrap.append(chips);
    });
    // A name nobody uses as a table may have been meant as a naming rule. Said
    // rather than guessed at: quietly re-reading it as a pattern is how a rule
    // stops meaning what it says.
    const meant = missing.filter(m => m.endsWith);
    if (meant.length) {
      const note = el('div', { className: 'note warn', style: 'margin-top:12px' },
        el('b', { style: 'display:block', textContent: meant.length === 1
          ? `No table is called ${meant[0].given} — but ${meant[0].endsWith} table`
            + `${meant[0].endsWith === 1 ? '' : 's'} end with it`
          : `${meant.length} of those names are the end of a real table name here` }),
        el('div', { style: 'margin-top:6px;line-height:1.55', textContent:
          'Ripple is treating them as exact table names, so they match nothing. If they were '
          + 'meant as a naming rule, write each one with an underscore or a star in front — '
          + `${meant.slice(0, 3).map(m => '_' + m.given).join(', ')} — and it will match the `
          + 'end of a name instead.' }));
      wrap.append(note);
    }
  }
  const dead = (c.patterns || []).filter(x => !x.matches);
  if (dead.length) {
    wrap.append(el('div', { className: 'note warn', style: 'margin-top:12px' },
      el('b', { style: 'display:block', textContent: dead.length === 1
        ? `The pattern ${dead[0].given} matches no table in this repository`
        : `${dead.length} of your patterns match no table in this repository` }),
      el('div', { style: 'margin-top:6px;line-height:1.55',
        textContent: (dead.length === 1 ? 'It is' : `They are (${dead.map(d => d.given).join(', ')})`)
          + ' doing nothing at all. If your published tables are not named that way, '
          + 'every finding will be reported as reaching a table Ripple cannot call production — '
          + 'the headline will read far calmer than the truth.' })));
  }
  const live = (c.patterns || []).filter(x => x.matches);
  if (live.length) {
    live.forEach(x => wrap.append(el('div', { className: 'small muted', style: 'margin-top:8px;line-height:1.55' },
      el('span', { className: 'chip mono pattern', textContent: x.given }),
      ` matches ${x.matches} table${x.matches === 1 ? '' : 's'} here — ${x.examples.join(', ')}`
        + (x.matches > x.examples.length ? ' and others' : ''))));
  }
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
  if (h.repo.inSkippedDirs) {
    ready.append(el('div', { className: 'note warn', style: 'margin-top:12px' },
      el('b', { style: 'display:block',
        textContent: `${h.repo.inSkippedDirs} file${h.repo.inSkippedDirs === 1 ? '' : 's'} skipped `
          + 'because of the folder they are in' }),
      el('div', { style: 'margin-top:6px;line-height:1.55', textContent:
        'Ripple walks past folders called ' + (h.repo.skippedDirNames || []).join(', ')
        + ' — in most repositories those hold generated output. If yours holds real pipeline '
        + 'code, none of it has been read.' })));
  }

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
    // A DAG that runs a query kept in a separate .sql file holds no SQL of its
    // own, so it used to be indistinguishable from a config file with nothing
    // in it. The query itself is read on its own account — this is the link
    // between the two, said so that "Python · 240" is not read as 240 files
    // Ripple learned nothing from.
    if (h.repo.runsSqlFrom) {
      kinds.append(el('div', { className: 'small muted', style: 'margin-top:14px;line-height:1.55',
        textContent: `${h.repo.runsSqlFrom} of these run SQL that is kept in a separate .sql file `
          + 'rather than written inside them. Those .sql files were read on their own account. '
          + 'Any that name a file which is not in this repository are listed as gaps after a scan.' }));
    }
    kinds.append(el('div', { className: 'small muted', style: 'margin-top:14px;line-height:1.55',
      textContent: 'Read-only access. Ripple never writes to your repository.' }));
  }

  const c = x(root, 'cat'); c.innerHTML = '';
  // Until the answer arrives this card has a heading and nothing under it. On a
  // repository of a few thousand files the read takes minutes, and for all of
  // them that is an empty box sitting on the screen. It says what it is waiting
  // for instead — and gets replaced, not added to, when the answer comes.
  c.append(el('div', { className: 'small faint', style: 'margin-top:10px',
    textContent: 'Counted once every file has been read.' }));
  api('/api/catalog').then(cat => {
    c.innerHTML = '';
    c.append(el('div', { style: 'display:flex;gap:26px;margin-top:10px' },
      el('div', {}, el('div', { textContent: String(cat.tableCount), style: 'font-size:26px;font-weight:800;font-variant-numeric:tabular-nums' }),
        el('div', { className: 'small faint', textContent: 'tables found' })),
      el('div', {}, el('div', { textContent: String(cat.columnCount), style: 'font-size:26px;font-weight:800;font-variant-numeric:tabular-nums' }),
        el('div', { className: 'small faint', textContent: 'columns found' }))));
    const g = x(root, 'gaps'); g.innerHTML = '';
    if (cat.gaps.length) {
      // This list used to be headed "tables Ripple could not fully read", which
      // read as a list of dead ends — and while the scan really did stop at
      // them, that was true. It no longer is: a scan follows the column
      // straight through a SELECT * and marks every step past it. Leaving the
      // old heading up would have somebody reading this page as the reason a
      // result was short, when it is not.
      const box = el('div', { className: 'note info' });
      box.append(el('b', { textContent: `${cat.gaps.length} table${cat.gaps.length === 1 ? '' : 's'} `
        + `here ${cat.gaps.length === 1 ? 'has' : 'have'} no column list written down` }));
      box.append(el('div', { style: 'margin-top:6px;line-height:1.55', textContent:
        'A scan still follows your attribute through these — a SELECT * carries every column, '
        + 'so the trail does not stop here. What Ripple cannot do is name the columns inside '
        + 'them, so every step past one is marked on the result as worked out rather than read. '
        + 'This is a fact about how the code is written, not a gap in the scan.' }));
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
    // Measured on a repository the size of his: a couple of thousand files and
    // statements six hundred lines long take minutes, not seconds. Saying
    // "a few seconds" and then taking four minutes is how a working program
    // gets reported as hung.
    ? (progressText(S.progress)
       || 'Reading every file. On a repository of a few thousand files this takes '
          + 'a few minutes — the count appears as soon as the first files are read.')
    : repoOk
      ? `The scan will search ${h.repo.label}.`
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
    // reads to decide the whole folder was covered, so when it was not, every
    // row saying otherwise has to sit directly underneath it.
    ...(((h.repo.heldOnline || 0) + (h.repo.pathTooLong || 0))
      ? [['Files never opened', String((h.repo.heldOnline || 0) + (h.repo.pathTooLong || 0))]]
      : []),
    ...(h.repo.unreadable ? [['Files that would not parse', String(h.repo.unreadable)]] : []),
    ...(h.repo.inSkippedDirs
      ? [['Files in folders Ripple skips', String(h.repo.inSkippedDirs)]] : []),
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

/* deeper is set when a trail was cut short by the hop limit and the person
   asked for it to be followed further. It applies to that one scan; the setting
   on the settings screen is left where it was. */
function runScan(deeper) {
  run(async () => {
    S.scan = await api('/api/scan', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        upstream: S.vals.upstream,
        changeKind: S.vals.changeKind || 'unknown',
        ...(deeper ? { maxHops: deeper } : {}),
      }),
    });
    S.summary = null; S.openGroup = 'p0'; S.openRow = null; S.graphTab = 0;
    goto(4);
  }, deeper
    ? `Following the same attributes again, up to ${deeper} renames deep…`
    : 'Searching every file for these names…');
}

// ── step 4 ────────────────────────────────────────────────────────────────
function step4(root) {
  const sc = S.scan;
  if (!sc) { x(root, 'progress').append(el('div', { className: 'note info', textContent: 'No scan yet.' })); return; }
  // Nothing was read, so there is no result to grade. A green "No impact" over
  // an empty folder is a statement about the folder wearing the clothes of a
  // statement about the pipeline.
  const nothingRead = !sc.filesScanned;
  const [cls, label] = nothingRead ? ['amber', 'Nothing was scanned']
    : (RISK[sc.risk] || RISK.none);
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
    el('span', { textContent: nothingRead
      ? 'No files were read'
      : sc.stats.filesWithImpact
        ? `Scan complete — ${sc.stats.filesWithImpact} file${sc.stats.filesWithImpact === 1 ? '' : 's'} with impact`
        : 'Scan complete — nothing carries these attributes',
      style: 'margin-left:auto;font-size:13px;font-weight:600;color:var(--blued)' })));
  done.append(el('div', { style: 'display:flex;align-items:baseline;gap:9px;margin-top:18px;flex-wrap:wrap' },
    el('span', { className: 'big', textContent: String(sc.filesScanned) }),
    el('span', { className: 'small muted', textContent: `files read · ${sc.filesMatched} mention the names you confirmed` })));
  x(root, 'progress').append(done);

  const st = sc.stats;
  const reached = sc.reached || [], other = sc.other || [];
  // Two rows under two headings, rather than seven cards in one row that wraps
  // six-and-one. They are not the same kind of number: the first row is the
  // answer, the second is how much of the repository the answer covers — and
  // the second one is the one that decides whether the first can be believed.
  const box = x(root, 'stats');
  const statCard = ([l, v, colour, sub]) => el('div', { className: 'stat' },
    el('span', { className: 'lbl', textContent: l }),
    el('div', { className: 'v', textContent: String(v), style: colour ? `color:${colour}` : '' }),
    el('div', { className: 's', textContent: sub }));

  box.append(el('span', { className: 'lbl', style: 'display:block;margin-bottom:10px',
    textContent: 'What the change reaches' }));
  const reach = el('div', { className: 'stats five' });
  [['Production tables at risk', st.productionTables, st.productionTables ? 'var(--red)' : 'var(--green)', 'On your published-table list'],
   ['Other tables reached', st.tablesReached ?? 0, (st.tablesReached ? 'var(--amber)' : ''), 'The chain ends at these'],
   ['Attributes impacted', st.attributesImpacted, '', 'Of those you confirmed'],
   ['Files to change', st.filesWithImpact, '', `Of ${sc.filesScanned} scanned`],
   ['Breaking usages', st.breakingUsages, st.breakingUsages ? 'var(--amber)' : '', 'Filters, joins, ranking'],
  ].forEach(c => reach.append(statCard(c)));
  box.append(reach);

  const uncovered = [
    ['To check by hand', st.couldNotRead, st.couldNotRead ? 'var(--amber)' : '', 'Ripple could not follow these'],
  ];
  // A trail Ripple gave up on is not a trail that ended, and a table it cannot
  // see inside is not a table it has read. Both used to be invisible on this
  // screen, so a result built on either looked exactly like one built on the
  // whole picture.
  if (st.trailsCutShort) {
    uncovered.push(['Trails cut short', st.trailsCutShort, 'var(--red)',
      `Stopped at ${sc.maxHops} renames deep`]);
  }
  if (st.tablesNotVisible) {
    uncovered.push(['Tables not fully readable', st.tablesNotVisible, 'var(--amber)',
      'Built with SELECT * — no column list']);
  }
  // Only ever shown when there are some. A "0 never opened" card would be a
  // reassurance nobody asked for.
  if (st.neverOpened) {
    uncovered.push(['Never opened', st.neverOpened, 'var(--red)', 'Not on this machine, or path too long']);
  }
  if (S.health?.repo?.inSkippedDirs) {
    uncovered.push(['In folders Ripple skips', S.health.repo.inSkippedDirs, 'var(--amber)',
      (S.health.repo.skippedDirNames || []).join(', ')]);
  }
  box.append(el('span', { className: 'lbl', style: 'display:block;margin:22px 0 10px',
    textContent: 'What this result does not cover' }));
  const gaps3 = el('div', { className: 'stats ' + (uncovered.length > 3 ? 'five' : 'three') });
  uncovered.forEach(c => gaps3.append(statCard(c)));
  box.append(gaps3);
  // Only a reassurance when there was something to be reassured about. "Every
  // file was opened and read" is true of no files at all, and reads as a clean
  // bill of health for a repository that was never there.
  if (!st.couldNotRead && uncovered.length === 1 && !nothingRead) {
    gaps3.append(el('div', { className: 'note good', style: 'grid-column:span 2;align-self:stretch;display:flex;align-items:center' },
      el('div', {}, el('b', { style: 'display:block', textContent: 'Every file was opened and read.' }),
        'Nothing was skipped, and nothing was left for a person to follow by hand.')));
  }

  // Before the findings, not after them: this is the card that says how much of
  // the repository the findings are a statement about.
  renderNeverOpened(box, sc);
  renderTrailGaps(box, sc);

  const groups = x(root, 'groups');
  groups.append(el('span', { className: 'lbl', style: 'display:block;margin-bottom:2px',
    textContent: 'The findings' }));
  // The clean result is only ever offered when there is genuinely nothing:
  // no production table, no other table, and no loose usage anywhere. Anything
  // less than that and a green tick is the tool lying to your face.
  if (nothingRead) {
    groups.append(el('div', { className: 'note bad', style: 'padding:18px 22px' },
      el('b', { style: 'display:block;font-size:15px', textContent: 'No files were read, so nothing was searched' }),
      el('div', { style: 'margin-top:5px', textContent:
        'This is not a result about your pipeline — it is a result about an empty folder. '
        + 'Point Ripple at the folder holding the code on the settings screen, then run the '
        + 'scan again.' })));
  } else if (!sc.groups.length && !reached.length && !other.length) {
    groups.append(el('div', { className: 'note good', style: 'display:flex;align-items:center;gap:14px;padding:18px 22px' },
      el('span', { textContent: '✓', style: 'width:30px;height:30px;border-radius:50%;background:var(--green);color:#fff;display:flex;align-items:center;justify-content:center;font-weight:700;flex-shrink:0' }),
      el('div', {}, el('b', { textContent: 'Nothing in this repository uses these attributes', style: 'display:block' }),
        el('div', { style: 'margin-top:3px', textContent: 'No table is built from them, and no code reads them. Check the list below to confirm the names were the right ones.' }))));
  }
  // With nothing on the production list, the first table the change reaches is
  // the most important thing on the screen, so it opens rather than sitting
  // shut behind a caret like a footnote.
  if (!sc.groups.length && reached.length && S.openGroup === 'p0') S.openGroup = 'r0';
  drawGroups(groups, sc.groups, 'p', 'Production table', '',
             'production table', 'production tables');

  if (reached.length) {
    // These used to be thrown away. A chain that ends at a table nobody has
    // told Ripple is published is not a chain that goes nowhere.
    groups.append(el('div', { className: 'note warn', style: 'margin-top:20px' },
      el('b', { textContent: `The change reaches ${reached.length} more table${reached.length === 1 ? '' : 's'}, `
        + `${sc.groups.length ? 'beyond the ones above' : 'none of them on your published list'}. ` }),
      'Ripple only calls a table production when it is on the published-table list — '
      + `currently ${S.health?.production || 'not set'}. Nothing below is on it, so Ripple `
      + 'cannot tell you whether anyone outside your team reads these. If they are your published '
      + 'tables, add them on the settings screen and run the scan again.'));
    drawGroups(groups, reached, 'r', 'Chain ends here', 'background:var(--amber);color:#fff',
               'table the chain ends at', 'tables the chain ends at');
  }

  if (other.length) {
    const card = el('div', { className: 'card clip', style: 'margin-top:20px' });
    card.append(el('div', { className: 'chead' },
      el('b', { textContent: other.length === 1
        ? '1 more usage that builds no table'
        : `${other.length} more usages that build no table` })));
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

  const gapBox = x(root, 'gaps');
  gapBox.innerHTML = '';
  gapBox.append(el('span', { className: 'lbl', style: 'display:block;margin:26px 0 2px',
    textContent: 'How to check this result' }));
  renderChecks(gapBox, sc);
  renderGaps(gapBox, sc);
  x(root, 'next').onclick = () => goto(5);
}

/* A run of table cards, with a readable number of them drawn.

   Measured on a repository the size of the one this was built for: following a
   key column reaches over two hundred tables, and two hundred identical
   collapsed cards is a page nobody scrolls to the end of — so the tables at the
   bottom of it are, in practice, hidden. Nothing is dropped: the ones with the
   most impacts are drawn (they are sorted that way), and every remaining table
   is named, with its count, in a list underneath. */
const GROUPS_DRAWN = 20;

function drawGroups(box, list, prefix, tag, tagStyle, one, many) {
  list.slice(0, GROUPS_DRAWN).forEach((g, gi) =>
    box.append(groupCard(g, `${prefix}${gi}`, tag, tagStyle)));
  const rest = list.slice(GROUPS_DRAWN);
  if (!rest.length) return;
  const card = el('div', { className: 'card pad lg', style: 'margin-top:16px' });
  card.append(el('span', { className: 'lbl', textContent:
    `${rest.length} more ${rest.length === 1 ? one : many}` }));
  card.append(el('div', { className: 'small muted', style: 'margin-top:6px;line-height:1.55',
    textContent: `The ${GROUPS_DRAWN} with the most impacts are shown above, opened one at a `
      + 'time. The rest are named here with their counts — nothing has been left out of the '
      + 'analysis, only out of the cards.' }));
  const chips = el('div', { className: 'chips scrollbox', style: 'margin-top:10px' });
  rest.forEach(g => chips.append(el('span', { className: 'chip mono',
    textContent: `${g.prod} · ${g.rows.length}` })));
  card.append(chips);
  box.append(card);
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
    // Two hops down the chain the column is no longer called what the person
    // typed into the notification, so a row can read "mc" on a scan of three
    // attributes with nothing to say which of them it belongs to. The
    // attribute that was asked about is named whenever it differs.
    const other = (r.roots || []).filter(n => n.toUpperCase() !== (r.attr || '').toUpperCase());
    row.append(
      el('span', { className: 'mono', textContent: r.inter, style: 'font-weight:600;font-size:13px;min-width:0;overflow-wrap:break-word' }),
      el('span', { style: 'min-width:0' },
        el('span', { className: 'mono', textContent: r.attr,
          style: 'font-size:13px;font-weight:600;color:var(--blued);overflow-wrap:break-word' }),
        other.length
          ? el('span', { className: 'small faint', style: 'display:block;margin-top:3px',
              textContent: 'from ' + other.join(', ') })
          : null),
      el('span', {}, el('span', { className: 'chip alias', textContent: r.alias })),
      // The second badge goes inside the same cell rather than adding a column,
      // so a row that has it lines up with the rows that do not.
      el('span', {}, el('span', { className: 'badge sm ' + (r.breaking ? 'red' : 'grey'), textContent: r.logic }),
        r.certain === false
          ? el('span', { className: 'badge sm grey', style: 'margin-left:6px',
              textContent: 'table not stated' })
          : null,
        // The chain got here through a table whose column list is not written
        // down. The row is real; what is inferred is that the column still
        // travels under this name on the far side of the star.
        r.inferredHops
          ? el('span', { className: 'badge sm amber', style: 'margin-left:6px',
              textContent: r.viaStar ? 'column list not visible' : 'inferred' })
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
        : null,
      // Kept apart from "ends at" on purpose. They read the same and mean
      // opposite things: one is where the code ran out, the other is where
      // Ripple stopped looking.
      (a.cutShortAt || []).length
        ? el('span', { className: 'badge sm red',
            textContent: 'still going at ' + a.cutShortAt.join(', ') })
        : null));
    if ((a.cutShortAt || []).length) {
      p.append(el('div', { className: 'small muted', style: 'margin:4px 0 0 4px;line-height:1.55',
        textContent: `Ripple follows ${sc.maxHops} renames and then stops. This trail had not `
          + 'finished, so whether it reaches a published table is not something this scan '
          + 'can tell you. There is a button above to follow it further.' }));
    }
    if ((a.notVisible || []).length) {
      p.append(el('div', { className: 'small muted', style: 'margin:4px 0 0 4px;line-height:1.55',
        textContent: `The trail goes through ${a.notVisible.join(', ')}, which `
          + `${a.notVisible.length === 1 ? 'is' : 'are'} built with SELECT * — every column `
          + `carried, none of them named. ${a.inferred} of the findings below sit past that `
          + 'point and are worked out rather than read.' }));
    }
    // How widely the name is used as a name. A scan for a column half the
    // warehouse shares looks identical on screen to a scan for one only this
    // table has, and the two are not remotely the same answer: the first
    // produces a long list because the name is everywhere, the second because
    // something is badly wrong. Only said when the name really is widespread —
    // "this name is in 1 of 60 tables" is a fact nobody needs.
    // Two conditions, and both matter. A big share says the name is common;
    // a real count says the repository is big enough for that to mean anything.
    // "3 of the 3 tables" is a fact about a folder with three files in it, and
    // printing it there teaches somebody to skip the line in the repository
    // where it is the whole point.
    if (a.nameInTables >= 8 && a.tablesRead) {
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
  // How much of the path to this row was read and how much was worked out. A
  // row two hops past a SELECT * is exactly as real as the code below it, and
  // exactly as uncertain about what the column is called by the time it lands.
  if (r.inferredHops) {
    d.append(el('div', { className: 'note warn', style: 'margin-top:10px' },
      el('b', { textContent: r.viaStar
        ? 'This step is a SELECT *. '
        : `${r.inferredHops} step${r.inferredHops === 1 ? '' : 's'} on the way here could not be read. ` }),
      r.viaStar
        ? `The statement takes every column, so ${r.attr} is carried into ${r.inter} without `
          + 'ever being named. The hop is real — that is what SELECT * does — but Ripple cannot '
          + 'read the column list of the table it builds, so anything past this point is worked '
          + 'out rather than read.'
        : `A table earlier in this chain is built with SELECT *, so its column list is not in `
          + `the code. This row is a real usage on a real line; what Ripple cannot promise is `
          + `that ${r.attr} is still the name the column carries by the time it gets here.`));
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

/* Files that were never opened. Drawn directly under the counts rather than at
   the bottom of the page, because it is the one card that decides whether every
   number above it can be believed — and the bottom of a long page is where a
   caveat goes to be missed. */
function renderNeverOpened(box, sc) {
  if (sc.heldOnline?.length || sc.pathTooLong?.length) {
    const card = el('div', { className: 'card pad lg', style: 'margin-top:20px;border-color:var(--amberln)' });
    card.append(neverOpenedNote(sc.heldOnline?.length || 0, sc.pathTooLong?.length || 0));
    const names = [...(sc.heldOnline || []), ...(sc.pathTooLong || [])];
    const chips = el('div', { className: 'chips scrollbox', style: 'margin-top:12px' });
    names.slice(0, 300).forEach(f => chips.append(el('span', { className: 'chip mono', textContent: f })));
    card.append(chips);
    if (names.length > 300) {
      card.append(el('div', { className: 'small muted', style: 'margin-top:8px',
        textContent: `and ${names.length - 300} more, not listed here to keep this page readable.` }));
    }
    box.append(card);
  }
  // A whole folder of code walked past because of what it is called. In most
  // repositories "build" and "target" hold generated output; in a few they hold
  // the pipeline, and then this is a scan of half a repository with a green
  // tick on it.
  const skipped = S.health?.repo?.inSkippedDirs || 0;
  if (skipped) {
    box.append(el('div', { className: 'note warn', style: 'margin-top:16px' },
      el('b', { style: 'display:block;font-size:14px',
        textContent: `${skipped} file${skipped === 1 ? '' : 's'} Ripple can read `
          + `${skipped === 1 ? 'was' : 'were'} skipped because of the folder ${skipped === 1 ? 'it is' : 'they are'} in` }),
      el('div', { style: 'margin-top:6px;line-height:1.55', textContent:
        'Ripple walks past folders called '
        + (S.health.repo.skippedDirNames || []).join(', ')
        + ', because in most repositories those hold generated output. If yours holds real '
        + 'pipeline code, nothing in it has been read and nothing in it can appear in a result.' })));
  }
}

/* Three ways a trail can be shorter than the truth, all of them invisible until
   now, and all of them producing a calm answer over less than the whole picture.

   These are drawn on the RESULT, beside the findings they qualify. Two of them
   were already known somewhere else in the app — the repository screen has
   listed the tables built with SELECT * for months — and a warning on another
   screen is a warning nobody reads while they are deciding whether to worry. */
function renderTrailGaps(box, sc) {
  // 1. The hop limit stopped the walk. This is a setting, and until now it was
  //    reported as a fact: "the chain ends at t4 and does not reach production".
  if (sc.cutShort?.length) {
    const deeper = Math.min((sc.maxHops || 4) * 2, 25);
    const card = el('div', { className: 'card pad lg', style: 'margin-top:20px;border-color:var(--redln)' });
    card.append(el('b', { style: 'display:block;font-size:14px', textContent:
      `${sc.cutShort.length} trail${sc.cutShort.length === 1 ? '' : 's'} `
      + `stopped because of a setting, not because the code ran out` }));
    card.append(el('div', { style: 'margin-top:8px;line-height:1.55', textContent:
      `Ripple follows a column through ${sc.maxHops} renames and then stops. `
      + `${sc.cutShort.length === 1 ? 'This trail was' : 'These trails were'} still going. `
      + 'Anything past this point has not been looked at, so "does not reach a published '
      + 'table" is not something this result can tell you about them.' }));
    const chips = el('div', { className: 'chips scrollbox', style: 'margin-top:12px' });
    sc.cutShort.forEach(c => chips.append(el('span', { className: 'chip mono',
      textContent: `${c.table} · ${c.attr}` })));
    card.append(chips);
    if (sc.maxHops < 25) {
      const again = el('button', { className: 'ghost', style: 'margin-top:14px',
        textContent: `Follow these ${deeper} renames deep instead` });
      again.onclick = () => runScan(deeper);
      card.append(again);
      card.append(el('div', { className: 'small muted', style: 'margin-top:8px;line-height:1.55',
        textContent: 'This runs the same scan again on the code already read — no files are '
          + 'read a second time. It changes nothing on the settings screen.' }));
    }
    box.append(card);
  }

  // 2. A table built with SELECT * carries every column and names none of them.
  if (sc.starTables?.length) {
    const n = sc.starTables.length;
    const card = el('div', { className: 'card pad lg', style: 'margin-top:20px;border-color:var(--amberln)' });
    card.append(el('b', { style: 'display:block;font-size:14px', textContent:
      `${n} table${n === 1 ? '' : 's'} on this trail ${n === 1 ? 'has' : 'have'} no column list to read` }));
    card.append(el('div', { style: 'margin-top:8px;line-height:1.55', textContent:
      `${n === 1 ? 'It is' : 'They are'} built with SELECT *, which takes every column and writes `
      + `none of them down. The attribute really does travel through — that is what SELECT * does — `
      + 'so Ripple follows it and marks every step past that point as worked out rather than read.' }));
    card.append(el('div', { className: 'small muted', style: 'margin-top:6px;line-height:1.55',
      textContent: 'Ripple used to stop dead here instead, which turned a change that breaks a '
        + 'published table into a clean result. What it cannot promise is that the column is '
        + 'still called the same thing on the far side.' }));
    const chips = el('div', { className: 'chips scrollbox', style: 'margin-top:12px' });
    sc.starTables.forEach(s => chips.append(el('span', { className: 'chip mono',
      textContent: `${s.table} — from ${s.from}` })));
    card.append(chips);
    box.append(card);
  }

  // 3. One name, more than one table, and nothing in the SQL to tell them apart.
  if (sc.mergedNames?.length) {
    const n = sc.mergedNames.length;
    const card = el('div', { className: 'card pad lg', style: 'margin-top:20px' });
    card.append(el('span', { className: 'lbl', textContent:
      `${n} table name${n === 1 ? '' : 's'} here may stand for more than one table` }));
    card.append(el('div', { style: 'margin-top:8px;line-height:1.55', textContent:
      'Ripple followed all of them, because missing a chain is worse than showing a row you '
      + 'can dismiss by opening the file. Findings under these names may be about either '
      + 'table, so check before acting on one.' }));
    const chips = el('div', { className: 'chips', style: 'margin-top:10px' });
    sc.mergedNames.forEach(m => chips.append(el('span', { className: 'chip mono',
      textContent: m.reason === 'capitals'
        ? `${m.spellings.join('  vs  ')} — same name, different capitals`
        : `${m.table} — in ${m.datasets.join(', ')}` })));
    card.append(chips);
    if (sc.mergedNames.some(m => m.reason === 'capitals')) {
      card.append(el('div', { className: 'small muted', style: 'margin-top:8px;line-height:1.55',
        textContent: 'BigQuery treats capitals as significant, so two names differing only by '
          + 'case really are two tables there. Ripple cannot tell whether that is what your '
          + 'code means or just how it was typed.' }));
    }
    box.append(card);
  }
}

/* The honest half of the report: what Ripple could NOT account for. Styled to
   stand out, never to shrink — a clean finding list is only worth what was read. */
function renderGaps(box, sc) {
  if (sc.unreadable?.length) {
    const card = el('div', { className: 'card clip', style: 'margin-top:20px;border-color:var(--amberln)' });
    card.append(el('div', { className: 'chead', style: 'background:var(--amberbg);border-bottom-color:var(--amberln)' },
      el('span', { className: 'tag', style: 'background:var(--amber);color:#fff', textContent: 'Check by hand' }),
      el('b', { textContent: `${sc.unreadable.length} file${sc.unreadable.length === 1 ? '' : 's'} to check by hand` })));
    const p = el('div', { className: 'pad lg' });
    p.append(el('div', { className: 'prose', textContent:
      'Ripple either could not read these, or found your name in them somewhere it cannot follow — inside a procedure call, a loop, or written as text. They are not covered by the findings above, and a clean result is only as good as what could be followed.' }));
    // The advice is usually the same sentence on every entry — "this repository
    // is being read as generic SQL", on sixty-eight files. Printed sixty-eight
    // times it stops being advice and becomes wallpaper the eye skips, taking
    // the file names with it. Anything said more than once is said once, here.
    const counts = {};
    sc.unreadable.forEach(u => { if (u.hint) counts[u.hint] = (counts[u.hint] || 0) + 1; });
    const shared = Object.keys(counts).filter(h => counts[h] > 1);
    shared.forEach(h => p.append(el('div', { className: 'note info', style: 'margin-top:12px' },
      el('b', { textContent: `Applies to ${counts[h]} of these files. ` }), h)));
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
      if (u.hint && !shared.includes(u.hint)) {
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
  // The line under the title has to be true of the picture underneath it, and
  // "to the production tables it feeds" is not true of a branch that ends at a
  // table Ripple has not been told is published — which is most of them when
  // the published-table list is wrong, exactly when it matters most.
  const anyProd = gs.some(g => (g.branches || []).length);
  // "None of these reach a published table" is a claim, and it is not one this
  // picture can make while some of its branches were cut short by a setting.
  const anyCut = (S.scan?.cutShort || []).length;
  x(root, 'sub').textContent = anyProd
    ? 'Where the changed attribute travels, what it is called at each step, and which published tables it reaches.'
    : anyCut
      ? `Where the changed attribute travels, and what it is called at each step. Ripple stopped `
        + `following ${anyCut === 1 ? 'one branch' : `${anyCut} branches`} at ${S.scan.maxHops} `
        + `renames deep, so where ${anyCut === 1 ? 'it ends' : 'they end'} is not known.`
      : 'Where the changed attribute travels, and what it is called at each step. None of these branches reach a table on your published list.';
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
  // Measured on a repository the size of the one this was built for: following
  // one of the key columns produces about 1,500 branches. Drawing all of them
  // is a wall of boxes nobody can read, and a map nobody can read is the same
  // as no map. So a readable number is drawn — the ones that reach a published
  // table first, because those are the ones that matter — and the rest are
  // COUNTED OUT LOUD rather than quietly left off. Nothing is lost: every
  // branch here is already a finding in the list on the previous step.
  const DRAWN = 40;
  all.slice(0, DRAWN).forEach(br => {
    const line = el('div', { className: 'branch' });
    br.forEach((n, i) => {
      line.append(nodeEl(n));
      if (i < br.length - 1) line.append(el('span', { className: 'arrow', textContent: '→' }));
    });
    branches.append(line);
  });
  row.append(src, branches);
  card.append(row);
  if (all.length > DRAWN) {
    card.append(el('div', { className: 'note info', style: 'margin-top:14px' },
      el('b', { textContent: `${all.length - DRAWN} more branches are not drawn here. ` }),
      `${all.length} were followed in total and every one of them is in the findings on the `
      + 'previous step, grouped by published table. The ones drawn above are those that reach '
      + 'a published table, longest first — drawing all of them makes a picture nobody can read.'));
  }
  map.append(card);
  if (ends.length) {
    map.append(el('div', { className: 'note warn', style: 'margin-top:14px' },
      el('b', { textContent: ends.length === 1
        ? 'One of these branches ends at a table that is not on your published list. '
        : `${ends.length} of these branches end at a table that is not on your published list. ` }),
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
  // The two things a box on this map can hide. Drawn on the box itself, because
  // a picture of a chain is exactly where somebody reads "and then it stops".
  if (n.inferred) {
    d.append(el('div', { className: 'small muted', style: 'margin-top:5px;line-height:1.4',
      textContent: 'built with SELECT * — column list not visible' }));
  }
  if (n.cut) {
    d.append(el('div', { className: 'small', style: 'margin-top:5px;line-height:1.4;color:var(--red)',
      textContent: 'Ripple stopped here — hop limit, not the end of the chain' }));
  }
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
    // "On this server" is wrong in the copy that runs as a program on somebody's
    // own laptop, where there is no server and nothing is shared with anyone.
    el('p', { textContent: kept
      ? (S.health?.offline
        ? 'Everything saved on this machine, newest first. They stay in the folder beside Ripple.'
        : 'Everything saved on this server, newest first.')
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

  // First, and on its own: the one setting on this screen that can turn a real
  // impact into a clean result.
  root.append(productionCard({
    onSave: (text) => api('/api/production', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text }),
    }).then(out => { S.health = out; }),
    persistNote: 'Held by this server while it runs. Set RIPPLE_PROD_TABLES to keep it after a restart.',
    savedNote: 'Saved. Every scan from now on uses this list — until this server restarts.',
  }));
  if (h.productionFrom === 'default') {
    root.append(el('div', { className: 'note warn', style: 'margin:14px 0 24px' },
      el('b', { textContent: 'Nobody has said which tables you publish. ' }),
      'Ripple is guessing from names ending _PROD, _PRD or _PUBLISHED. If your published '
      + 'tables are not named that way, every finding will be reported as reaching a table '
      + 'Ripple cannot call production, and the headline will read far calmer than the truth.'));
  } else {
    root.append(el('div', { style: 'height:24px' }));
  }

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
    left.append(el('div', { className: 'factrow' },
      el('span', { className: 'small muted', textContent: k }),
      el('span', { className: 'small', textContent: v }))));
  left.append(el('div', { className: 'note info', style: 'margin-top:14px' },
    'Set on the host with environment variables — ',
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
  S.busy = true; S.busyWhat = what || 'Working…'; S.progress = null; render();
  watchProgress();
  Promise.resolve(fn()).catch(e => {
    alert('Something went wrong: ' + e.message);
  }).finally(() => { S.busy = false; S.busyWhat = ''; S.progress = null; render(); });
}

/* Ask the running program what it is doing, twice a second, for as long as it
   is doing something.

   On a repository of a few thousand files, reading it takes minutes and a scan
   takes about a minute. A spinner and a fixed sentence for that long is
   indistinguishable from a program that has hung, and the usual answer to that
   is a progress bar with a number nobody can check underneath it. This shows
   only what the engine has actually counted: files really read, statements
   really followed. Where there is no total — a chain looks at as many
   statements as it turns out to need — it says the count and no fraction,
   because a fraction would need a denominator nobody knows. */
function watchProgress() {
  if (S.progressTimer) return;
  S.progressTimer = setInterval(async () => {
    if (!S.busy) { clearInterval(S.progressTimer); S.progressTimer = null; S.progress = null; return; }
    try {
      const p = await api('/api/progress');
      const was = progressText(S.progress);
      S.progress = p.job ? p : null;
      if (progressText(S.progress) !== was) render();
    } catch { /* the request it belongs to will report the real failure */ }
  }, 500);
}

function progressText(p) {
  if (!p || !p.job) return '';
  const label = p.label || ({ reading: 'Reading the files',
                              parsing: 'Understanding the SQL',
                              scanning: 'Following the column' })[p.job] || 'Working';
  if (p.total > 0) return `${label} — ${p.done.toLocaleString()} of ${p.total.toLocaleString()}`;
  if (p.done > 0) return `${label} — ${p.done.toLocaleString()} so far`;
  return label;
}

function render() {
  renderSteps(); renderStatus();
  const view = $('#view'); view.innerHTML = '';
  $('#hRight').innerHTML = '';
  if (S.busy) {
    // The counted line if there is one, the fixed sentence until there is.
    $('#hRight').append(el('span', { className: 'spin' }),
      el('span', { className: 'small', textContent: progressText(S.progress) || S.busyWhat,
        style: 'margin-left:9px;font-weight:600;color:var(--blued)' }));
  }

  if (S.view === 'history') {
    setHeader('Past analyses', S.health?.limits?.historyKept === false
      ? 'Kept only until this host is replaced'
      : S.health?.offline ? 'Saved beside Ripple, on this machine' : 'Saved on this server');
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

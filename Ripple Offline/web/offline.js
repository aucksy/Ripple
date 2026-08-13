/* Ripple Offline — the screens that only exist here.

   Appended to the shared front end when the offline build is made. Everything
   else on screen is the shared file, unchanged, so the two editions cannot
   drift apart. What is here is what genuinely differs: online, the folder to
   scan and the SQL dialect are environment variables set by whoever deploys
   the thing. Offline there is nobody to set them, so they are asked for on
   screen and remembered in a file beside the program.

   These three functions replace ones of the same name in the shared file.
   JavaScript hoists every function declaration in a file before running any of
   it, so the later ones — these — are the ones that run. */

// ── the first run ─────────────────────────────────────────────────────────
/* Nothing has been chosen yet, so the first thing on screen is the question,
   rather than a wizard that would scan nothing and say nothing was found. */
function afterBoot() {
  if (S.health && !S.health.configured) S.view = 'settings';
}

// ── what step 3 says when the folder is not there ─────────────────────────
/* Online this reports a connection that failed. Offline there is no connection
   to fail — but a folder chosen last week can be moved, renamed or deleted, and
   that is an ordinary Tuesday on a locked-down machine, not an exception. */
function repoAlert(h) {
  const f = h.folder;
  if (!f || f.ok) return null;
  const box = el('div', { className: 'note bad', style: 'margin-bottom:18px' },
    el('b', { textContent: f.state === 'unset' ? 'No repository folder chosen yet. ' : 'Nothing can be scanned. ' }),
    f.message);
  const go = el('button', { className: 'ghost sm', textContent: 'Choose the folder', style: 'margin-top:12px' });
  go.onclick = () => { S.view = 'settings'; render(); };
  box.append(el('div', {}, go));
  return box;
}

// ── settings ──────────────────────────────────────────────────────────────
function offState() {
  const h = S.health;
  if (!S.off) {
    S.off = {
      path: (h && h.repo.path) || '',
      dialect: (h && h.sqlDialectId) || '',
      hops: (h && h.maxHops) || 4,
      prod: (h && h.production) || '',
      check: null,        // the answer to "check this folder", before saving
      msg: null,          // the answer to the last save
      working: '',        // which button is busy: 'check', 'browse' or 'save'
    };
  }
  return S.off;
}

/* Slow work here has to be visible on the button that started it. The header
   spinner is across the screen from whatever was pressed, and a folder being
   read is the one moment on this screen where nothing happens for a while and
   then several numbers change at once. */
function offRun(which, fn) {
  const o = offState();
  o.working = which;
  run(async () => {
    try { await fn(); } finally { o.working = ''; }
  }, which === 'save' ? 'Reading every file in the folder…'
    : which === 'check' ? 'Counting what is in the folder…'
    : 'Waiting for the folder picker…');
}

function settingsView(root) {
  const h = S.health;
  const o = offState();
  // The shared header says "Connections and health", and offline there are no
  // connections to have.
  setHeader('Settings & checks', h.configured
    ? 'What Ripple reads, and where it keeps things'
    : 'Choose the folder to scan');
  root.append(el('div', { className: 'head' }, el('div', {},
    el('h2', { textContent: 'Settings & checks' }),
    el('p', { textContent: h.configured
      ? 'What Ripple is reading, and where it keeps what it saves.'
      : 'Two things to choose before the first scan.' }))));

  if (!h.configured) {
    root.append(el('div', { className: 'note info', style: 'margin-bottom:18px' },
      el('b', { textContent: 'Choose the repository folder to get started. ' }),
      'Ripple reads a copy of the code that is already on this machine — it does not '
      + 'download anything and it never writes to your code. Point it at the folder, '
      + 'check the SQL dialect underneath, and save.'));
  }

  const grid = el('div', { className: 'grid2 even' });
  grid.append(el('div', {}, folderCard(h, o), dialectCard(h, o), productionCard(h, o), saveRow(h, o)),
              el('div', { className: 'rail' }, whereCard(h), guardCard(), factsCard(h)));
  root.append(grid);
}

/* Which tables are the ones this team publishes.
   The setting that decides whether "no production table is impacted" is a
   result or an accident. Ripple ships knowing about names ending _PROD, and a
   repository that names nothing _PROD gets a clean bill of health for a change
   that breaks it. There is nobody here to set an environment variable, so it
   is asked for on screen like the other two. */
function productionCard(h, o) {
  const card = el('div', { className: 'card pad lg', style: 'margin-top:18px' });
  card.append(el('span', { className: 'lbl', textContent: 'The tables your team publishes' }));
  card.append(el('div', { className: 'small faint', style: 'margin-top:6px;line-height:1.55',
    textContent: 'How your published tables are named. Separate with commas. A plain word matches '
      + 'the end of a table name, so _PROD matches sales_prod. Use * for anything else: '
      + 'PROD_* matches prod_sales, and * on its own means treat every table as published.' }));
  const inp = el('input', { type: 'text', className: 'mono', value: o.prod,
    placeholder: '_PROD, _PRD, _PUBLISHED', style: 'margin-top:12px;padding:12px 14px' });
  inp.oninput = () => { o.prod = inp.value; };
  inp.onkeydown = (e) => { if (e.key === 'Enter') saveOfflineSettings(); };
  card.append(inp);
  card.append(el('div', { className: 'note warn', style: 'margin-top:14px' },
    el('b', { textContent: 'Get this wrong and a real impact reads as a clean result. ' }),
    'A finding is only counted as production impact when the table it ends at matches this. '
    + 'Nothing is hidden either way — every table the change reaches is still listed — but '
    + 'the headline, the risk level and the drafted reply all follow this line.'));
  return card;
}

/* The folder to scan. Typing a path always works; the picker is only offered
   when this machine actually has one to open. */
function folderCard(h, o) {
  const card = el('div', { className: 'card pad lg' });
  card.append(el('span', { className: 'lbl', textContent: 'Repository folder' }));
  card.append(el('div', { className: 'small faint', style: 'margin-top:6px;line-height:1.55',
    textContent: 'The folder holding the code to search. Ripple reads every file in it and '
      + 'never writes to any of them.' }));

  const inp = el('input', { type: 'text', className: 'mono', value: o.path,
    placeholder: 'D:\\code\\our-pipelines', style: 'margin-top:12px;padding:12px 14px' });
  inp.oninput = () => { o.path = inp.value; o.check = null; };
  inp.onkeydown = (e) => { if (e.key === 'Enter') checkFolder(); };
  card.append(inp);

  const row = el('div', { className: 'foot', style: 'margin-top:14px' });
  if (h.canBrowse) {
    const browse = el('button', { className: 'ghost',
      textContent: o.working === 'browse' ? 'Waiting for the picker…' : 'Browse…' });
    browse.disabled = !!o.working;
    browse.onclick = () => browseForFolder();
    row.append(browse);
  }
  const check = el('button', { className: 'ghost',
    textContent: o.working === 'check' ? 'Counting the files…' : 'Check this folder' });
  check.disabled = !!o.working;
  check.onclick = () => checkFolder();
  row.append(check);
  if (o.working === 'check') {
    row.append(el('span', { className: 'spin' }),
      el('span', { className: 'small muted', textContent: 'Walking the folder. A large one takes a moment.' }));
  }
  card.append(row);

  // A note with nothing in it is an empty coloured box, which reads as
  // something that failed to load rather than as an answer.
  if (o.check && o.check.message) {
    card.append(el('div', { className: 'note ' + (o.check.ok ? 'good' : 'bad'), style: 'margin-top:14px' },
      o.check.message));
  }
  return card;
}

/* The dialect. This is the setting that looks cosmetic and is not. */
function dialectCard(h, o) {
  const card = el('div', { className: 'card pad lg', style: 'margin-top:18px' });
  card.append(el('span', { className: 'lbl', textContent: 'How the SQL is read' }));
  const sel = el('select', { className: 'statussel', style: 'width:100%;padding:11px 12px;margin-top:12px' });
  (h.dialects || []).forEach(d => sel.append(el('option', {
    value: d.id, textContent: d.label, selected: d.id === o.dialect })));
  const why = el('div', { className: 'small faint', style: 'margin-top:6px;line-height:1.55' });
  const showWhy = () => {
    const d = (h.dialects || []).find(x => x.id === sel.value);
    why.textContent = d ? d.note : '';
  };
  sel.onchange = () => { o.dialect = sel.value; showWhy(); };
  showWhy();
  card.append(sel, why);
  card.append(el('div', { className: 'note warn', style: 'margin-top:14px' },
    el('b', { textContent: 'This matters more than it looks. ' }),
    'Read as generic SQL, a BigQuery pipeline in Ripple\u2019s own tests parsed 2 of its 5 '
    + 'files and reported no impact on a change that really broke two things. That is not '
    + 'a vaguer answer than the right one — it is the opposite answer.'));
  return card;
}

function saveRow(h, o) {
  const row = el('div', { className: 'card pad lg foot', style: 'margin-top:18px' });
  const busy = o.working === 'save';
  const save = el('button', { className: 'pri',
    textContent: busy ? 'Reading the folder…'
      : h.configured ? 'Save and read the repository again' : 'Save and read the repository' });
  save.disabled = !!o.working;
  save.onclick = () => saveOfflineSettings();
  row.append(save);
  if (busy) {
    // Reading a real repository is thousands of files. Without this the screen
    // sits still and then several numbers change on their own, which reads as
    // the page having done something by itself.
    row.append(el('span', { className: 'spin' }),
      el('span', { className: 'small muted',
        textContent: 'Reading every file and parsing the SQL. On a large repository this takes '
          + 'a few seconds — the counts on the right update when it finishes.' }));
  } else {
    row.append(el('span', { className: 'small faint',
      textContent: 'Saved to the settings file beside Ripple, so it is remembered next time.' }));
  }
  const box = el('div', {}, row);
  if (o.msg) {
    box.append(el('div', { className: 'note ' + (o.msg.ok ? 'good' : 'bad'), style: 'margin-top:14px' },
      o.msg.text));
  }
  return box;
}

/* Where the two files Ripple writes actually are. Nobody should have to guess,
   and "somewhere in your user profile" is not an answer. */
function whereCard(h) {
  const card = el('div', { className: 'card pad' });
  card.append(el('span', { className: 'lbl', textContent: 'What Ripple writes' }));
  [['Settings', h.settingsFile], ['Saved analyses', h.historyFile]].forEach(([k, v]) =>
    card.append(el('div', { style: 'padding:9px 0;border-top:1px solid var(--hair);margin-top:8px' },
      el('div', { className: 'small muted', textContent: k }),
      el('div', { className: 'small mono', textContent: v,
        style: 'margin-top:3px;font-weight:600;word-break:break-all' }))));
  card.append(el('div', { className: 'small faint', style: 'margin-top:12px;line-height:1.55',
    textContent: 'Both sit in the folder you copied across. Take that folder to another machine '
      + 'and your settings and saved analyses go with it. Delete it and Ripple is gone.' }));
  return card;
}

/* Whether this copy really is sealed off, asked of the running program rather
   than asserted on a screen. */
function guardCard() {
  const card = el('div', { className: 'card pad' });
  card.append(el('span', { className: 'lbl', textContent: 'Nothing leaves this machine' }));
  const state = el('div', { style: 'margin-top:12px' },
    el('span', { className: 'small muted', textContent: 'Checking…' }));
  card.append(state);
  card.append(el('div', { className: 'small faint', style: 'margin-top:12px;line-height:1.55',
    textContent: 'This copy has no connection to anywhere and no AI — there is nothing here to '
      + 'type a key or an address into. It reads the folder above and writes the two files listed.' }));
  api('/api/offline-check').then(g => {
    state.innerHTML = '';
    if (g.guardInstalled) {
      state.append(el('div', { className: 'note good' },
        el('b', { textContent: 'Outbound connections are blocked. ' }),
        'Anything in this program that tried to call out would fail on the spot, not '
        + 'succeed quietly because this machine happens to have internet.'));
    } else {
      state.append(el('div', { className: 'note warn' },
        el('b', { textContent: 'The block is not switched on in this copy. ' }),
        'Ripple still has nothing in it that calls out, but that is not being enforced '
        + 'here. Start Ripple the normal way to switch it back on.'));
    }
    if (g.attempts && g.attempts.length) {
      state.append(el('div', { className: 'note bad', style: 'margin-top:10px' },
        el('b', { textContent: `${g.attempts.length} attempt${g.attempts.length === 1 ? '' : 's'} to reach the network were refused: ` }),
        g.attempts.slice(0, 5).join(', ')));
    }
  }).catch(() => {
    state.innerHTML = '';
    state.append(el('div', { className: 'note warn', textContent: 'Could not ask this copy whether the block is on.' }));
  });
  return card;
}

function factsCard(h) {
  const card = el('div', { className: 'card pad' });
  card.append(el('span', { className: 'lbl', textContent: 'What was read' }));
  [['Files indexed', String(h.repo.files)],
   ['Statements understood', String(h.repo.statements)],
   ['Files unreadable', String(h.repo.unreadable)],
   ['Tables found', String(h.catalog.tables)],
   ['SQL read as', h.sqlDialect],
   ['Renames followed', `${h.maxHops} hops`],
   ['Tables you publish', h.production || 'not set']].forEach(([k, v]) =>
    card.append(el('div', { style: 'display:flex;gap:14px;padding:9px 0;border-top:1px solid var(--hair)' },
      el('span', { className: 'small muted', textContent: k, style: 'flex:1' }),
      el('span', { className: 'small', textContent: v, style: 'font-weight:700' }))));
  return card;
}

// ── the three things those buttons do ─────────────────────────────────────
function checkFolder() {
  const o = offState();
  offRun('check', async () => {
    o.check = await api('/api/settings/check', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ path: o.path.trim() }),
    });
  });
}

function browseForFolder() {
  const o = offState();
  offRun('browse', async () => {
    const out = await api('/api/settings/browse', { method: 'POST' });
    if (out.path) { o.path = out.path; o.check = null; o.msg = null; }
  });
}

function saveOfflineSettings() {
  const o = offState();
  offRun('save', async () => {
    try {
      S.health = await api('/api/settings', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ repoPath: o.path.trim(), sqlDialect: o.dialect,
                               maxHops: o.hops, prodTables: o.prod.trim() }),
      });
      o.prod = S.health.production || o.prod;
      // The saved message below says what happened. Leaving the "check this
      // folder" answer up as well puts an empty green box on screen, because
      // once it has been saved there is nothing left for it to report.
      o.check = null;
      o.msg = { ok: true, text: `Saved. ${S.health.repo.files} file`
        + `${S.health.repo.files === 1 ? '' : 's'} indexed from ${S.health.repo.label}, `
        + `read as ${S.health.sqlDialect}. ${S.health.repo.statements} statement`
        + `${S.health.repo.statements === 1 ? '' : 's'} understood, ${S.health.repo.unreadable} file`
        + `${S.health.repo.unreadable === 1 ? '' : 's'} could not be read. `
        + `Published tables: ${S.health.production}.` };
      // Whatever was scanned before came from a different folder or a different
      // dialect, so it is dropped rather than left on screen looking current.
      S.scan = null; S.summary = null; S.reply = null;
    } catch (e) {
      o.msg = { ok: false, text: e.message };
    }
  });
}

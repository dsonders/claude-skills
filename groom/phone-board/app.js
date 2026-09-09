(function(){
  var DATA = JSON.parse(document.getElementById('board-data').textContent);
  var CARDS = DATA.cards, BY = {}; CARDS.forEach(function(c){ BY[c.key]=c; });
  var rulings = {}, notes = {}, db = null, mode = 'local', unsubs = [];
  var LS = 'groomphone.v1', LSC = 'groomphone.collapsed.v1', collapsed = {}, expandedDesk = {};
  try { collapsed = JSON.parse(localStorage.getItem(LSC)||'{}')||{}; } catch(e){ collapsed = {}; }
  function saveCollapsed(){ try { localStorage.setItem(LSC, JSON.stringify(collapsed)); } catch(e){} }
  var mq = window.matchMedia('(min-width: 900px)');
  function isDesk(){ return mq.matches; }
  function esc(s){ return String(s==null?'':s).replace(/[&<>"]/g, function(ch){ return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[ch]; }); }
  function loadLocal(){ try { var o = JSON.parse(localStorage.getItem(LS)||'{}'); rulings = o.rulings||{}; notes = o.notes||{}; } catch(e){ rulings={}; notes={}; } }
  function saveLocal(){ try { localStorage.setItem(LS, JSON.stringify({rulings:rulings, notes:notes})); } catch(e){} }
  function now(){ return new Date().toISOString(); }
  function fmt(iso){ try { var d=new Date(iso); return d.toLocaleDateString(undefined,{day:'numeric',month:'short'})+' '+d.toLocaleTimeString(undefined,{hour:'numeric',minute:'2-digit'}); } catch(e){ return ''; } }
  var STAGE_OPTS = [['advance','Advance to grooming'],['keep','Keep in backlog'],['icebox','Send to Icebox']];
  function stageId(c){ return c.key+'-stage'; }
  function stageRuling(c){ return rulings[stageId(c)] || null; }
  function stageLabel(v){ var o = STAGE_OPTS.filter(function(x){ return x[0]===v; })[0]; return o ? o[1] : v; }
  function isRuled(d){ if (d.baked) return true; var r = rulings[d.id]; if (!r) return false; return d.text ? !!(r.words && r.words.trim()) : !!r.choice; }
  function allBaked(c){ return c.decisions.length > 0 && c.decisions.every(function(d){ return !!d.baked; }); }
  function openCount(c){ if (c.stage==='triage') return stageRuling(c) ? 0 : 1; return c.decisions.filter(function(d){ return !isRuled(d); }).length; }
  function waitingGroom(c){ return c.stage==='triage' && !stageRuling(c); }
  function writeRuling(id, body){ if (!db) body.offline = true; rulings[id] = body; saveLocal(); setTimeout(updateDeskPills, 0); if (db) { db.doc('rulings/'+id).set(body).catch(function(e){ console.warn('ruling save failed', e); setStatus('local'); }); } }
  function clearRuling(id){ delete rulings[id]; saveLocal(); setTimeout(updateDeskPills, 0); if (db) { db.doc('rulings/'+id).delete().catch(function(e){ console.warn(e); }); } }
  function writeNote(key, text){ var body = {text:text, at:now()}; if (!db) body.offline = true; notes[key] = body; saveLocal(); if (db) { db.doc('notes/'+key).set(body).catch(function(e){ console.warn('note save failed', e); setStatus('local'); }); } }
  function setStatus(m){ mode = m; document.querySelectorAll('.m-status').forEach(function(el){ el.className = 'm-status '+m; el.innerHTML = '<i></i>' + (m==='live' ? 'Rulings save to the board — the next session files them' : m==='wait' ? 'Connecting to the board…' : 'Saving on this device only — the board’s store is not reachable from here'); }); }
  function chev(){ return '<span class="m-chev"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="m9 6 6 6-6 6"/></svg></span>'; }
  var DOWN = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="m6 9 6 6 6-6"/></svg>';

  // ---------- routing ----------
  function currentItemKey(){ var m = (location.hash||'').match(/^#\/item\/(.+)$/); return m ? decodeURIComponent(m[1]) : null; }
  function route(){
    var key = currentItemKey();
    if (isDesk()) { if (key && BY[key]) { expandedDesk[key] = true; collapsed[BY[key].section] = false; saveCollapsed(); } renderDash(); if (key) { var el = document.querySelector('[data-card="'+CSS.escape(key)+'"]'); if (el) el.scrollIntoView({block:'start'}); } else window.scrollTo(0,0); return; }
    if (key) renderItem(key); else renderDash();
    window.scrollTo(0,0);
  }
  window.addEventListener('hashchange', route);
  mq.addEventListener ? mq.addEventListener('change', route) : mq.addListener(route);

  // ---------- dashboard (phone: list of rows; desktop: same list, rows expand in place) ----------
  function renderDash(){
    var total = 0, items = 0, waiting = 0;
    CARDS.forEach(function(c){ var n = openCount(c); total += n; if (n) items++; if (waitingGroom(c)) waiting++; });
    var h = '<div class="m-hero"><div class="m-cap">Grooming board · '+esc(DATA.built)+'</div><h1>Backlog</h1><div class="m-total">'+total+' open decision'+(total===1?'':'s')+' on '+items+' item'+(items===1?'':'s')+(waiting?' · <span style="color:var(--amber)">'+waiting+' waiting on a groom call</span>':'')+'</div></div>';
    h += '<div class="m-status '+mode+'"><i></i></div>';
    DATA.sections.forEach(function(sec){
      var rows = '';
      DATA.ruled.filter(function(r){ return r.section===sec; }).forEach(function(r){
        rows += '<div class="m-row ruled"><span class="key soft">'+esc(r.key)+'</span><span class="t">'+esc(r.title)+'</span><span class="m-done" title="'+esc(r.status)+'">ruled</span></div>' + (isDesk() && r.status ? '<div class="m-legacy-status">'+esc(r.status)+'</div>' : '');
      });
      CARDS.filter(function(c){ return c.section===sec; }).forEach(function(c){
        var n = openCount(c), hasNote = !!(notes[c.key] && notes[c.key].text && notes[c.key].text.trim());
        var pill, keycls;
        if (c.stage==='triage') { var sr = stageRuling(c); pill = sr ? '<span class="m-done">'+esc(stageLabel(sr.choice))+'</span>' : '<span class="m-groom">groom?</span>'; keycls = sr ? ' soft' : ' amber'; }
        else if (allBaked(c)) { pill = '<span class="m-done">ruled · queued</span>'; keycls = ' soft'; }
        else { pill = n ? '<span class="m-open">'+n+' open</span>' : '<span class="m-done">ruled · here</span>'; keycls = n ? '' : ' soft'; }
        var inner = '<span class="key'+keycls+'">'+esc(c.key)+'</span><span class="t">'+esc(c.title)+'</span>'+(hasNote?'<span class="m-note-dot" title="You staged a note"></span>':'')+pill+chev();
        if (isDesk()) {
          var open = !!expandedDesk[c.key];
          rows += '<div class="m-deskcard'+(open?' open':'')+'" data-card="'+esc(c.key)+'"><div class="m-row m-deskhead'+(n?'':' ruled')+'" role="button" tabindex="0" data-expand="'+esc(c.key)+'">'+inner+'</div>'+(open?'<div class="m-deskbody" data-item="'+esc(c.key)+'"></div>':'')+'</div>';
        } else {
          rows += '<a class="m-row'+(n?'':' ruled')+'" href="#/item/'+encodeURIComponent(c.key)+'">'+inner+'</a>';
        }
      });
      if (!rows) return;
      var secItems = DATA.ruled.filter(function(r){ return r.section===sec; }).length, secRuled = secItems;
      CARDS.filter(function(c){ return c.section===sec; }).forEach(function(c){ secItems++; if (!openCount(c)) secRuled++; });
      var col = (sec in collapsed) ? !!collapsed[sec] : true, allDone = secRuled===secItems;
      h += '<div class="m-sec'+(col?' collapsed':'')+'" data-sec="'+esc(sec)+'"><button class="m-sechead" aria-expanded="'+(!col)+'"><span class="m-h2">'+esc(sec)+'</span><span class="m-badge'+(allDone?' done':'')+'" title="items ruled / items in this section">'+secRuled+'/'+secItems+'</span><span class="m-chev">'+DOWN+'</span></button><div class="m-card">'+rows+'</div></div>';
    });
    if (isDesk() && DATA.legacy) {
      ['risk','icebox','archive'].forEach(function(k){ var L = DATA.legacy[k]; if (!L) return; var col = (k in collapsed) ? !!collapsed[k] : true; h += '<div class="m-sec'+(col?' collapsed':'')+'" data-sec="'+k+'"><button class="m-sechead" aria-expanded="'+(!col)+'"><span class="m-h2">'+esc(L.title)+'</span><span class="m-chev">'+DOWN+'</span></button><div class="m-card m-legacy"><article class="card">'+L.html+'</article></div></div>'; });
    } else {
      h += '<div class="m-sec"><div class="m-h2">Icebox</div><div class="m-card"><div class="m-row ruled"><span class="t">'+esc(DATA.icebox)+'</span></div></div></div>';
      h += '<div class="m-sec"><div class="m-empty">'+esc(DATA.archive)+'</div></div>';
    }
    var app = document.getElementById('app'); app.innerHTML = h; setStatus(mode);
    app.querySelectorAll('.m-sechead').forEach(function(b){ b.addEventListener('click', function(){ var sec = b.parentNode.getAttribute('data-sec'); var cur = (sec in collapsed) ? !!collapsed[sec] : true; collapsed[sec] = !cur; saveCollapsed(); var y = window.scrollY; renderDash(); window.scrollTo(0, y); }); });
    app.querySelectorAll('[data-expand]').forEach(function(b){ b.addEventListener('click', function(){ var k = b.getAttribute('data-expand'); expandedDesk[k] = !expandedDesk[k]; var y = window.scrollY; renderDash(); window.scrollTo(0, y); }); b.addEventListener('keydown', function(ev){ if (ev.key==='Enter'||ev.key===' ') { ev.preventDefault(); b.click(); } }); });
    app.querySelectorAll('.m-deskbody').forEach(function(body){ var k = body.getAttribute('data-item'); body.innerHTML = itemHTML(k, true); wireItem(body, k); sizeGalleries(body); });
  }

  // ---------- item ----------
  var flipState = {};
  function renderItem(key){ var c = BY[key]; if (!c) { location.hash = '#/'; return; } var app = document.getElementById('app'); app.innerHTML = itemHTML(key, false); wireItem(app, key); sizeGalleries(app); }
  function sizeGalleries(root){ requestAnimationFrame(function(){ root.querySelectorAll('.m-gallery:not(.one) .m-gal-frame').forEach(function(f){ var inner = f.querySelector('.m-gal-inner'); var w = f.getBoundingClientRect().width; var sc = w / 390; inner.style.transform = 'scale('+sc+')'; f.style.height = Math.ceil(inner.scrollHeight * sc) + 'px'; }); }); }
  var FEEDBACK_LBL = 'Questions / feedback for the next session';
  function itemHTML(key, embedded){
    var c = BY[key], idx = CARDS.indexOf(c), next = CARDS[idx+1], desk = isDesk();
    var h = '<div class="m-item" data-key="'+esc(key)+'">';
    if (!embedded) {
      h += '<div class="m-top"><div style="display:flex;align-items:center;justify-content:space-between"><a class="m-back" href="#/">'+'<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="m15 6-6 6 6 6"/></svg><span>Board</span></a><span class="m-cap">'+(idx+1)+' of '+CARDS.length+'</span></div>';
      h += '<div class="m-title"><span class="key">'+esc(c.key)+'</span><div>'+esc(c.title)+'</div></div><div class="m-sub">'+esc(c.sub)+'</div></div>';
    } else {
      h += '<div class="m-top" style="padding-top:6px"><div class="m-sub" style="margin-top:0">'+esc(c.sub)+'</div></div>';
    }
    var note0 = notes[key] && notes[key].text || '';
    var foot = function(detailsLabel, extraDetails){ return '<div class="m-foot"><details class="m-details"><summary>'+DOWN+'<span>'+detailsLabel+'</span></summary><div>'+esc(c.dims.join(' · '))+(c.pop?'<br><b>Who hits it</b> '+esc(c.pop):'')+(extraDetails||'')+'</div></details>'+(embedded?'':(next?'<a class="m-next" href="#/item/'+encodeURIComponent(next.key)+'">Next: '+esc(next.key)+' '+chev()+'</a>':'<a class="m-next" href="#/">Back to the board '+chev()+'</a>'))+'</div>'; };
    var feedback = function(){ return '<div class="m-dec m-feedback"><div class="m-q">'+FEEDBACK_LBL+'</div><textarea class="m-field'+(note0.trim()?' filled':'')+'" data-note="'+esc(key)+'" rows="4">'+esc(note0)+'</textarea><div class="m-hint" data-note-hint="'+esc(key)+'">'+(note0.trim()?'Staged '+fmt(notes[key].at):'')+'</div></div>'; };
    if (c.stage==='triage') {
      var sr = stageRuling(c);
      h += '<div class="m-stage triage'+(sr?' ruled':'')+'" data-stage-block="'+esc(key)+'"><div class="m-stage-lbl"><i></i>Not yet groomed</div></div>';
      if (c.triageMock) h += '<div class="m-frame m-trimock">'+c.triageMock.html+'</div><div class="m-frame-cap">'+esc(c.triageMock.caption)+'</div>';
      h += '<div class="m-dec" data-stage-dec="'+esc(key)+'"><div class="m-q">What happens to this item?</div><div class="m-opts m-opts-stage">';
      STAGE_OPTS.forEach(function(o){ h += '<button class="m-btn'+(sr&&sr.choice===o[0]?' chosen':'')+'" data-stage="'+o[0]+'">'+esc(o[1])+'</button>'; });
      h += '</div><div class="m-ruled-line" data-rl-stage="'+esc(key)+'">'+(sr?'<span>'+esc(stageLabel(sr.choice))+' · '+fmt(sr.at)+'</span><button data-stage-clear="1">clear</button>':'')+'</div></div>';
      h += feedback();
      var qlist = c.decisions.map(function(d){ return '<li>'+esc(d.q)+'</li>'; }).join('');
      h += foot('Details — what grooming would settle', qlist?'<ul style="margin:8px 0 0;padding-left:18px">'+qlist+'</ul>':'');
    } else {
      h += '<div class="m-stage"><div class="m-stage-lbl"><i></i>'+(allBaked(c)?'Ruled and filed — queued for the next build':'Groomed — ready to rule')+'</div></div>';
      if (c.ruled && c.ruled.length) { h += '<div style="padding:10px 16px 0"><div class="m-empty" style="border-style:solid;border-color:var(--teal);color:var(--ink-2)"><span class="m-cap" style="color:var(--teal)">Already ruled</span><br>'+c.ruled.map(esc).join('<br>')+'</div></div>'; }
      if (c.frames.kind !== 'none') {
        if (desk) {
          if (c.frames.kind === 'walk') h += '<div class="m-both"><div><div class="m-frame-cap m-both-cap">What happens today — '+esc(c.frames.caption)+'</div>'+c.frames.today+'</div><div><div class="m-frame-cap m-both-cap">Proposed — '+esc(c.frames.caption)+'</div>'+c.frames.proposed+'</div></div>';
          else h += '<div class="m-both"><div><div class="m-frame-cap m-both-cap">Today</div><div class="m-frame">'+c.frames.today+'</div></div><div><div class="m-frame-cap m-both-cap">Proposed</div><div class="m-frame">'+c.frames.proposed+'</div></div></div><div class="m-frame-cap">'+esc(c.frames.caption)+'</div>';
        } else {
          var st = flipState[key] || 'proposed';
          h += '<div class="m-seg" role="tablist"><button data-flip="today" class="'+(st==='today'?'on':'')+'">Today</button><button data-flip="proposed" class="'+(st==='proposed'?'on':'')+'">Proposed</button></div>';
          if (c.frames.kind === 'walk') h += '<div class="m-frame-cap" style="margin-top:12px"><span class="m-cap">'+(st==='today'?'What happens today':'Proposed')+' — '+esc(c.frames.caption)+'</span></div><div class="m-flipbody">'+c.frames[st]+'</div>';
          else h += '<div class="m-flipbody"><div class="m-frame">'+c.frames[st]+'</div><div class="m-frame-cap">'+esc(c.frames.caption)+'</div></div>';
        }
      } else if (c.blocks) {
        h += '<div class="m-blocks">'+c.blocks+'</div>';
      } else if (!c.visual) {
        h += '<div style="padding:14px 16px 0"><div class="m-empty">No screen changes — nothing to draw.</div></div>';
      }
      c.decisions.forEach(function(d){ h += decisionHTML(c, d); });
      h += feedback();
      h += foot('Details', '');
    }
    return h + '</div>';
  }
  function decisionHTML(c, d){
    var r = rulings[d.id] || {}, ruled = isRuled(d);
    if (d.baked) { r = {choice: d.baked.choice, words: ''}; }
    var h = '<div class="m-dec'+(ruled?' ruled':'')+(d.baked?' baked':'')+'" id="dec-'+esc(d.id)+'"><div class="m-cap">Decision '+esc(c.key)+' · '+d.n+'</div><div class="m-q">'+esc(d.q)+'</div>';
    if (d.context) h += '<div class="m-ctx">'+esc(d.context)+'</div>';
    if (d.gallery && d.gallery.length) { var wide = isDesk() || d.gallery.length <= 3 || d.galleryWide; h += '<div class="m-gallery'+(wide?' one':'')+(isDesk()?' desk':'')+(d.galleryFull?' full':'')+'">'; d.gallery.forEach(function(g){ h += '<figure class="m-gal"><figcaption><b>'+esc(g.label)+'</b>'+(g.note?'<span>'+esc(g.note)+'</span>':'')+'</figcaption><div class="m-gal-frame"><div class="m-gal-inner">'+g.html+'</div></div></figure>'; }); h += '</div>'; }
    h += '<div class="m-opts">';
    d.options.forEach(function(o){ h += '<div class="m-btn'+(o.rec?' is-rec':'')+(r.choice===o.l?' chosen':'')+((o.frame||o.why)?' has-vis':'')+'" role="button" tabindex="0" data-dec="'+esc(d.id)+'" data-choose="'+esc(o.l)+'"><div class="m-optrow"><span class="m-opt">'+esc(o.l)+'</span><span>'+esc(o.t)+'</span>'+(o.rec?'<span class="m-rec">rec</span>':'')+'</div>'+(o.frame?'<div class="m-optframe">'+o.frame+'</div>':'')+(o.why?'<div class="m-why">'+esc(o.why)+'</div>':'')+'</div>'; });
    h += '</div>';
    if (d.baked) { h += '<div class="m-ruled-line"><span>Ruled · '+esc(d.baked.choice)+' · '+esc(d.baked.note)+'</span></div></div>'; return h; }
    h += '<textarea class="m-field'+(r.words&&r.words.trim()?' filled':'')+'" rows="2" data-words="'+esc(d.id)+'" placeholder="'+(d.text?'Your answer — filed verbatim':'In your words — optional, filed verbatim')+'">'+esc(r.words||'')+'</textarea>';
    h += '<div class="m-ruled-line" id="rl-'+esc(d.id)+'">'+(ruled?'<span>Ruled'+(r.choice?' · '+esc(r.choice):'')+' · '+fmt(r.at)+'</span><button data-clear="'+esc(d.id)+'">clear</button>':'')+'</div></div>';
    return h;
  }
  function wireItem(root, key){
    var c = BY[key];
    root.querySelectorAll('[data-flip]').forEach(function(b){ b.addEventListener('click', function(){ flipState[key] = b.getAttribute('data-flip'); var y = window.scrollY; if (root.id === 'app') renderItem(key); else { root.innerHTML = itemHTML(key, true); wireItem(root, key); sizeGalleries(root); } window.scrollTo(0, y); }); });
    root.querySelectorAll('.m-dec:not(.baked) [data-choose]').forEach(function(b){ b.addEventListener('click', function(){ var id = b.getAttribute('data-dec'), l = b.getAttribute('data-choose'); var prev = rulings[id] || {}; writeRuling(id, {choice:l, words:prev.words||'', at:now()}); refreshDecision(c, id); }); b.addEventListener('keydown', function(ev){ if (ev.key==='Enter'||ev.key===' ') { ev.preventDefault(); b.click(); } }); });
    root.querySelectorAll('[data-clear]').forEach(function(b){ b.addEventListener('click', function(){ var id = b.getAttribute('data-clear'); clearRuling(id); refreshDecision(c, id); }); });
    root.querySelectorAll('[data-words]').forEach(function(t){ var timer; t.addEventListener('input', function(){ clearTimeout(timer); var id = t.getAttribute('data-words'); timer = setTimeout(function(){ var prev = rulings[id] || {}; var words = t.value; if (!words.trim() && !prev.choice) { if (rulings[id]) clearRuling(id); } else { writeRuling(id, {choice:prev.choice||'', words:words, at:now()}); } refreshDecision(c, id, true); }, 600); }); });
    var nf = root.querySelector('[data-note="'+CSS.escape(key)+'"]'); if (nf) { var nt; nf.addEventListener('input', function(){ clearTimeout(nt); nt = setTimeout(function(){ writeNote(key, nf.value); var filled = !!nf.value.trim(); nf.classList.toggle('filled', filled); var hint = root.querySelector('[data-note-hint="'+CSS.escape(key)+'"]'); if (hint) hint.textContent = filled ? 'Staged '+fmt(notes[key].at) : ''; }, 600); }); }
    var blk = root.querySelector('[data-stage-dec="'+CSS.escape(key)+'"]'); if (blk) {
      blk.querySelectorAll('[data-stage]').forEach(function(b){ b.addEventListener('click', function(){ writeRuling(stageId(c), {choice:b.getAttribute('data-stage'), words:'', at:now()}); refreshStage(c); }); });
      var cl = blk.querySelector('[data-stage-clear]'); if (cl) cl.addEventListener('click', function(){ clearRuling(stageId(c)); refreshStage(c); });
    }
  }
  function refreshStage(c){ var blk = document.querySelector('[data-stage-dec="'+CSS.escape(c.key)+'"]'); if (!blk) return; var sr = stageRuling(c);
    blk.querySelectorAll('[data-stage]').forEach(function(b){ b.classList.toggle('chosen', !!(sr && sr.choice===b.getAttribute('data-stage'))); });
    blk.classList.toggle('ruled', !!sr); var sb = document.querySelector('[data-stage-block="'+CSS.escape(c.key)+'"]'); if (sb) sb.classList.toggle('ruled', !!sr);
    var rl = document.querySelector('[data-rl-stage="'+CSS.escape(c.key)+'"]'); rl.innerHTML = sr ? '<span>'+esc(stageLabel(sr.choice))+' · '+fmt(sr.at)+'</span><button data-stage-clear="1">clear</button>' : '';
    var cl = blk.querySelector('[data-stage-clear]'); if (cl) cl.addEventListener('click', function(){ clearRuling(stageId(c)); refreshStage(c); }); }
  function refreshDecision(c, id, keepFocus){
    var d = c.decisions.filter(function(x){ return x.id===id; })[0]; var old = document.getElementById('dec-'+id); if (!old) return;
    if (keepFocus) { var r = rulings[id] || {}, ruled = isRuled(d); old.classList.toggle('ruled', ruled);
      document.getElementById('rl-'+id).innerHTML = ruled ? '<span>Ruled'+(r.choice?' · '+esc(r.choice):'')+' · '+fmt(r.at)+'</span><button data-clear="'+esc(id)+'">clear</button>' : '';
      var cb0 = old.querySelector('[data-clear]'); if (cb0) cb0.addEventListener('click', function(){ clearRuling(id); refreshDecision(c, id); });
      old.querySelector('[data-words]').classList.toggle('filled', !!(r.words&&r.words.trim())); return; }
    var tmp = document.createElement('div'); tmp.innerHTML = decisionHTML(c, d); var nw = tmp.firstChild; old.replaceWith(nw);
    nw.querySelectorAll('[data-choose]').forEach(function(b){ b.addEventListener('click', function(){ var l = b.getAttribute('data-choose'); var prev = rulings[id] || {}; writeRuling(id, {choice:l, words:prev.words||'', at:now()}); refreshDecision(c, id); }); });
    var cb = nw.querySelector('[data-clear]'); if (cb) cb.addEventListener('click', function(){ clearRuling(id); refreshDecision(c, id); });
    var t = nw.querySelector('[data-words]'); if (t) { var timer; t.addEventListener('input', function(){ clearTimeout(timer); timer = setTimeout(function(){ var prev = rulings[id] || {}; var words = t.value; if (!words.trim() && !prev.choice) { if (rulings[id]) clearRuling(id); } else { writeRuling(id, {choice:prev.choice||'', words:words, at:now()}); } refreshDecision(c, id, true); }, 600); }); }
    sizeGalleries(nw);
  }
  // live updates: change only what changed, never re-route (route() scrolls)
  function syncView(prev, notesToo){
    var keys = isDesk() ? Object.keys(expandedDesk).filter(function(k){ return expandedDesk[k]; }) : (currentItemKey() ? [currentItemKey()] : []);
    if (!keys.length) { var y = window.scrollY; renderDash(); window.scrollTo(0, y); return; }
    keys.forEach(function(key){ var c = BY[key]; if (!c) return;
      if (JSON.stringify(prev[stageId(c)]||null) !== JSON.stringify(rulings[stageId(c)]||null)) refreshStage(c);
      c.decisions.forEach(function(d){ var a = JSON.stringify(prev[d.id]||null), b = JSON.stringify(rulings[d.id]||null); if (a === b) return; var el = document.getElementById('dec-'+d.id); var typing = el && document.activeElement && el.contains(document.activeElement); refreshDecision(c, d.id, !!typing); });
      if (notesToo) { var nf = document.querySelector('[data-note="'+CSS.escape(key)+'"]'); if (nf && document.activeElement !== nf) { var t = notes[key] && notes[key].text || ''; nf.value = t; nf.classList.toggle('filled', !!t.trim()); var hint = document.querySelector('[data-note-hint="'+CSS.escape(key)+'"]'); if (hint) hint.textContent = t.trim() ? 'Staged '+fmt(notes[key].at) : ''; } }
    });
    updateDeskPills();
  }
  function updateDeskPills(){
    if (!isDesk()) return;
    var total = 0, items = 0, waiting = 0; CARDS.forEach(function(c){ var n = openCount(c); total += n; if (n) items++; if (waitingGroom(c)) waiting++; });
    var tot = document.querySelector('.m-total'); if (tot) tot.innerHTML = total+' open decision'+(total===1?'':'s')+' on '+items+' item'+(items===1?'':'s')+(waiting?' · <span style="color:var(--amber)">'+waiting+' waiting on a groom call</span>':'');
    document.querySelectorAll('.m-deskhead').forEach(function(hd){ var k = hd.getAttribute('data-expand'); var c = BY[k]; var n = openCount(c); var pill = hd.querySelector('.m-open, .m-done, .m-groom'); if (!pill) return; hd.classList.toggle('ruled', !n); if (c.stage==='triage') { var sr = stageRuling(c); pill.outerHTML = sr ? '<span class="m-done">'+esc(stageLabel(sr.choice))+'</span>' : '<span class="m-groom">groom?</span>'; } else if (!allBaked(c)) { pill.outerHTML = n ? '<span class="m-open">'+n+' open</span>' : '<span class="m-done">ruled · here</span>'; } });
    document.querySelectorAll('.m-sec[data-sec]').forEach(function(sec){ var name = sec.getAttribute('data-sec'); var badge = sec.querySelector('.m-badge'); if (!badge) return; var secItems = DATA.ruled.filter(function(r){ return r.section===name; }).length, secRuled = secItems; CARDS.filter(function(c){ return c.section===name; }).forEach(function(c){ secItems++; if (!openCount(c)) secRuled++; }); badge.textContent = secRuled+'/'+secItems; badge.classList.toggle('done', secRuled===secItems); });
  }

  // ---------- store ----------
  loadLocal(); route(); setStatus('wait');
  var useP = (window.claude && typeof window.claude.use === 'function') ? window.claude.use('db') : Promise.resolve(null);
  useP.then(function(ns){
    if (!ns) { setStatus('local'); return; }
    db = ns;
    Promise.all([db.collection('rulings').get(), db.collection('notes').get()]).then(function(res){
      var r = {}, n = {};
      res[0].docs.forEach(function(s){ if (s.exists) r[s.id] = s.data(); });
      res[1].docs.forEach(function(s){ if (s.exists) n[s.id] = s.data(); });
      // the store wins. Only docs written while the store was unreachable are pushed up — a doc the store no longer
      // has was SWEPT (filed and cleared by a session) and must not come back.
      var pushes = [], BAKED_IDS = {}; CARDS.forEach(function(c){ c.decisions.forEach(function(d){ if (d.baked) BAKED_IDS[d.id] = true; }); });
      Object.keys(rulings).forEach(function(id){ var l = rulings[id]; if (!r[id] && l && l.offline && !BAKED_IDS[id]) { delete l.offline; r[id] = l; pushes.push(db.doc('rulings/'+id).set(l)); } });
      Object.keys(notes).forEach(function(k){ var l = notes[k]; if (!n[k] && l && l.offline && l.text && l.text.trim()) { delete l.offline; n[k] = l; pushes.push(db.doc('notes/'+k).set(l)); } });
      var prevR = rulings; rulings = r; notes = n; saveLocal(); setStatus('live'); syncView(prevR, true);
      Promise.all(pushes).catch(function(e){ console.warn(e); });
      unsubs.push(db.collection('rulings').onSnapshot(function(snap){ var m = {}; snap.docs.forEach(function(s){ if (s.exists) m[s.id] = s.data(); }); var prev = rulings; rulings = m; saveLocal(); syncView(prev); }, function(e){ console.warn(e); setStatus('local'); }));
      unsubs.push(db.collection('notes').onSnapshot(function(snap){ var m = {}; snap.docs.forEach(function(s){ if (s.exists) m[s.id] = s.data(); }); notes = m; saveLocal(); }, function(e){ console.warn(e); }));
    }).catch(function(e){ console.warn('store read failed', e); setStatus('local'); });
  }).catch(function(){ setStatus('local'); });
})();

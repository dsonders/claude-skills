import os, json, html, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import ro_panel, owner_page, step, sil
from parts_card import parts_card
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'admin_card.py')).read())
from decisions import DEC
O=os.path.dirname(os.path.abspath(__file__))
cards=json.load(open(O+'/cards.json'))
board_css=open(O+'/board.css').read()

SECTION_ORDER=["MPI & Video","Parts page & queue","RO page — advisor, admin, tech","Dashboards","Customer page","Store settings — labor rates & money","Platform & tooling"]

# ---- frames for the three drawn items ----
def frames_for(key):
    if key=="SA-6b":
        return dict(kind="flip", caption="The advisor, opening the line after close.",
            today=ro_panel("Declined by the customer"), proposed=ro_panel("Declined at close", ring=True))
    if key=="U":
        return dict(kind="flip", caption="The customer, back on their own page after the drop — inline, the amount only.",
            today=owner_page(), proposed=owner_page(note=True))
    if key=="P":
        today = (step(1,"The parts counter,","on the parts page, adds the recall part to the line — number, name, stock still “?”, no price yet.", parts_card())
              + step(2,"The admin,","opening the same RO two minutes later, sees the line’s money card locked — and empty.", ADMIN_CARD("today_locked"))
              + step(3,"The admin","taps the edit control to price the line. Only now does the counter’s part appear.", ADMIN_CARD("today_edit"), last=True))
        prop = (step(1,"The parts counter,","on the parts page, adds the recall part to the line — number, name, stock still “?”, no price yet.", parts_card())
              + step(2,"The admin,","opening the same RO two minutes later, sees the counter’s part on the locked card — every field the counter sees, read-only; the row scrolls sideways for stock, note, qty and price, as on the parts page.", ADMIN_CARD("proposed_locked"))
              + step(3,"The admin","taps the edit control only to change pricing — nothing new appears, nothing was hidden.", ADMIN_CARD("proposed_edit"), last=True))
        return dict(kind="walk", caption="Same line, two minutes apart", today=f'<div class="m-steps">{today}</div>', proposed=f'<div class="m-steps">{prop}</div>')
    return dict(kind="none")

data_cards=[]
for c in cards:
    decs=[]
    for i,(q,opts) in enumerate(DEC[c['key']],1):
        decs.append(dict(id=f"{c['key']}-{i}", n=i, q=q, options=[dict(l=l,t=t,rec=r) for l,t,r in opts], text=(len(opts)==0)))
    fr=frames_for(c['key'])
    blocks=''.join(c['blocks']) if fr['kind']=='none' else ''
    data_cards.append(dict(key=c['key'], section=c['section'], title=c['title'], sub=c['sub'], dims=c['dims'], pop=c['pop'], ruled=c['ruled'], blocks=blocks, frames=fr, decisions=decs))

# ruled / queued items for the dashboard (from the live board)
ruled_items=[
 ("MPI & Video","OL","Dictation: “no leaks” leaves Oil and/or Fluid Leaks Pending — the one row whose all-clear is a negation","ruled 7 Sep"),
 ("MPI & Video","FC","Dictation: “All brake lights are good” puts four brake-pad rows on the review sheet and leaves the lights Pending","ruled 7 Sep"),
 ("MPI & Video","VG","Video: “All the belts look good” greens Drive Belts from a video, while the same words by dictation go through the new fixed list","ruled 7 Sep"),
 ("MPI & Video","UW","Dictation: the battery check stands down when the AI reader’s note uses a defect word it has never heard of","ruled 7 Sep"),
 ("MPI & Video","VR","Video review sheet: the copy Dave marked up on the 7 Sep sheet, and the split of matched and unmatched items into two steps","ruled 7–8 Sep"),
 ("MPI & Video","CT","Video: a “Couldn’t place” row can be titled “There is a rattle coming from” — a clipped fragment","ruled 8 Sep"),
 ("MPI & Video","SQ","Video: a stitched quote can refuse the tech’s own “brake pads” sentence","ruled 8 Sep"),
 ("MPI & Video","VC","Video cue cards: have the AI reader hand back the tech’s own sentences","ruled 7 Sep — back to the drawing board"),
 ("Store settings — labor rates & money","SA-19","Saving a new labor rate re-prices every open RO in the store — with no question asked","ruled 30 Aug"),
]

DATA=dict(sections=SECTION_ORDER, cards=data_cards, ruled=[dict(section=s,key=k,title=t,status=st) for s,k,t,st in ruled_items], icebox="Waiting on something specific", archive="Archive — 56 items shipped since the 29 Aug board", built="8 Sep 2026")

PAGE_CSS = """
/* ---------- phone board: type scale (Dave 9/8: bigger) ---------- */
.m-wrap{font-size:16px}
.m-row .t{font-size:15.5px}
.m-open{font-size:12.5px}
.m-title{font-size:19px}
.m-sub{font-size:15.5px}
.m-q{font-size:16.5px}
.m-btn{font-size:16px;min-height:52px}
.m-btn .m-opt{font-size:12.5px}
.m-field{font-size:16px}
.m-hint,.m-details,.m-frame-cap,.m-ruled-line,.m-ruled-line button{font-size:14px}
.m-cap{font-size:11px}
.m-steps > div > div:first-of-type + div,.m-steps span{font-size:15px}
.m-blocks .viz{font-size:15px}
.m-blocks table,.m-blocks .story li,.m-blocks .viz-foot,.m-blocks .scap{font-size:14.5px}
.m-empty{font-size:14.5px}
.m-total{font-size:15.5px}
.m-status{font-size:13px}
/* ---------- phone board ---------- */
.app{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;color:#0f172a;line-height:1.35}
.sil{display:inline-block;height:10px;border-radius:3px;background:#cbd5e1;vertical-align:middle}
.ring{box-shadow:0 0 0 3px rgba(56,189,248,.45);border-radius:3px}
body{padding:0}
.m-wrap{max-width:560px;margin:0 auto;padding:0 0 40px;overflow-x:hidden}
html,body{overflow-x:hidden}
#flip-body,.m-steps,.m-steps .frame,.m-frame{max-width:100%;overflow:hidden;min-width:0}
.m-cap{font-family:"IBM Plex Mono",ui-monospace,SFMono-Regular,Menlo,monospace;font-size:10px;letter-spacing:.1em;text-transform:uppercase;color:var(--muted)}
.m-h2{font-family:"IBM Plex Mono",ui-monospace,monospace;font-size:14px;font-weight:600;letter-spacing:.1em;text-transform:uppercase;color:var(--ink);line-height:1.3}
.m-badge{flex:none;font-family:"IBM Plex Mono",ui-monospace,monospace;font-size:12px;font-weight:600;font-variant-numeric:tabular-nums;color:var(--accent);background:var(--accent-soft);border:1px solid var(--accent);border-radius:999px;padding:2px 9px;white-space:nowrap}
.m-badge.done{color:var(--teal);background:var(--teal-soft);border-color:var(--teal)}
.m-card{background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);box-shadow:var(--shadow);display:flex;flex-direction:column}
.m-row{display:flex;gap:10px;align-items:center;padding:11px 12px 11px 14px;border-top:1px solid var(--line-2);min-height:52px;color:inherit;text-decoration:none;cursor:pointer;-webkit-tap-highlight-color:transparent}
.m-row:first-child{border-top:0}
.m-row:active{background:var(--surface-2)}
.m-row .t{flex:1 1 auto;min-width:0;font-size:14px;line-height:1.35;color:var(--ink);display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.m-row.ruled .t{color:var(--muted)}
.m-row .key.soft{background:var(--teal-soft);color:var(--teal)}
.m-open{flex:none;font-family:"IBM Plex Mono",ui-monospace,monospace;font-size:11.5px;font-weight:600;color:var(--accent);background:var(--accent-soft);border:1px solid var(--accent);border-radius:999px;padding:2px 9px;white-space:nowrap}
.m-done{flex:none;font-family:"IBM Plex Mono",ui-monospace,monospace;font-size:10px;letter-spacing:.08em;text-transform:uppercase;color:var(--teal);background:var(--teal-soft);border-radius:999px;padding:3px 8px;white-space:nowrap}
.m-note-dot{flex:none;width:8px;height:8px;border-radius:999px;background:var(--amber)}
.m-chev{flex:none;color:var(--muted)}
.m-top{padding:calc(14px + env(safe-area-inset-top)) 16px 0}
.m-back{display:inline-flex;align-items:center;gap:4px;color:var(--accent);font-size:14px;min-height:44px;text-decoration:none}
.m-title{display:flex;gap:10px;align-items:flex-start;font-size:17px;font-weight:600;line-height:1.3;letter-spacing:-.01em}
.m-sub{font-size:13.5px;color:var(--ink-2);line-height:1.45;margin-top:6px;max-width:none}
.m-seg{display:flex;border:1px solid var(--line);border-radius:999px;padding:3px;background:var(--surface);font-size:13px;font-weight:500;margin:14px 16px 0}
.m-seg button{flex:1;text-align:center;padding:7px 0;border-radius:999px;color:var(--muted);min-height:38px;border:0;background:none;font:inherit;cursor:pointer}
.m-seg button.on{background:var(--ink);color:#fff}
.m-frame{margin:10px 16px 0;border:1px solid var(--line);border-radius:6px;overflow:hidden;background:#fff}
.m-frame-cap{margin:6px 16px 0;font-size:12.5px;color:var(--muted);line-height:1.45}
.m-steps{padding:6px 16px 0;display:flex;flex-direction:column;gap:14px}
.m-steps .frame{border:1px solid var(--line);border-radius:6px;overflow:hidden;background:#fff}
.m-blocks{padding:0 16px}
.m-blocks .viz{margin-top:14px}
.m-dec{padding:18px 16px 0;display:flex;flex-direction:column;gap:8px}
.m-q{font-size:15px;font-weight:600;line-height:1.4}
.m-btn{display:flex;align-items:center;gap:10px;min-height:48px;padding:10px 14px;border-radius:var(--radius);border:1px solid var(--line);background:var(--surface);font:inherit;font-size:14.5px;line-height:1.35;color:var(--ink);text-align:left;width:100%;cursor:pointer;-webkit-tap-highlight-color:transparent}
.m-btn .m-opt{font-family:"IBM Plex Mono",ui-monospace,monospace;font-size:11.5px;font-weight:600;color:var(--accent);border:1px solid var(--accent);border-radius:3px;padding:1px 6px;background:var(--accent-soft);flex:none}
.m-btn .m-rec{font-family:"IBM Plex Mono",ui-monospace,monospace;font-size:10px;letter-spacing:.08em;text-transform:uppercase;color:var(--teal);background:var(--surface);border:1px solid var(--teal);border-radius:999px;padding:0 6px;white-space:nowrap;flex:none;line-height:18px;margin-left:auto}
.m-btn.is-rec{border-color:var(--teal);background:var(--teal-soft)}
.m-btn.is-rec .m-opt{color:var(--teal);border-color:var(--teal);background:var(--surface)}
.m-dec.ruled .m-btn{opacity:.45}
.m-dec.ruled .m-btn.chosen{opacity:1;border-color:var(--ink);box-shadow:inset 0 0 0 1px var(--ink)}
.m-dec.ruled .m-btn.chosen .m-opt{color:#fff;background:var(--ink);border-color:var(--ink)}
.m-ruled-line{display:flex;align-items:center;justify-content:space-between;gap:8px;font-size:12.5px;color:var(--teal)}
.m-ruled-line button{border:0;background:none;color:var(--muted);font:inherit;font-size:12.5px;text-decoration:underline;cursor:pointer;min-height:32px;padding:0}
.m-field{width:100%;min-height:48px;border:1px dashed var(--line);border-radius:var(--radius);background:var(--surface-2);padding:12px 14px;font:inherit;font-size:14px;color:var(--ink);resize:vertical;box-sizing:border-box}
.m-field::placeholder{color:var(--muted)}
.m-field:focus{outline:2px solid var(--accent);outline-offset:1px;border-style:solid}
.m-field.filled{border-style:solid;background:var(--surface)}
.m-hint{font-size:12px;color:var(--muted)}
.m-foot{margin-top:22px;padding:14px 16px 24px;border-top:1px solid var(--line-2);display:flex;align-items:center;justify-content:space-between;gap:10px}
.m-next{display:inline-flex;align-items:center;gap:4px;color:var(--accent);font-size:14px;font-weight:500;white-space:nowrap;text-decoration:none;min-height:44px}
.m-details{font-size:12.5px;color:var(--muted);line-height:1.45}
.m-details summary{cursor:pointer;min-height:44px;display:flex;align-items:center;gap:6px;list-style:none}
.m-details summary::-webkit-details-marker{display:none}
.m-status{margin:10px 16px 0;font-size:12px;color:var(--muted);display:flex;align-items:center;gap:6px}
.m-status i{width:8px;height:8px;border-radius:999px;background:var(--line);display:inline-block}
.m-status.live i{background:var(--teal)}
.m-status.local i{background:var(--amber)}
.m-empty{border:1px dashed var(--line);border-radius:var(--radius);padding:12px 14px;font-size:13px;color:var(--muted);line-height:1.45}
.m-hero{padding:calc(20px + env(safe-area-inset-top)) 16px 0;display:flex;flex-direction:column;gap:4px}
.m-hero h1{font-size:30px;margin:0;letter-spacing:-.02em}
.m-total{font-size:14px;color:var(--muted)}
.m-sec{padding:14px 16px 0;display:flex;flex-direction:column;gap:6px}
.m-sechead{display:flex;align-items:center;gap:10px;width:100%;min-height:44px;padding:0 2px;border:0;background:none;font:inherit;text-align:left;cursor:pointer;-webkit-tap-highlight-color:transparent}
.m-sechead .m-h2{flex:1 1 auto}
.m-sechead .m-chev{transition:transform .15s ease}
.m-sec.collapsed .m-sechead .m-chev{transform:rotate(-90deg)}
.m-sec.collapsed .m-card{display:none}
@media (prefers-reduced-motion: reduce){.m-sechead .m-chev{transition:none}}
"""

JS = r"""
(function(){
  var DATA = JSON.parse(document.getElementById('board-data').textContent);
  var CARDS = DATA.cards, BY = {}; CARDS.forEach(function(c){ BY[c.key]=c; });
  var rulings = {}, notes = {}, db = null, mode = 'local', unsubs = [];
  var LS = 'groomphone.v1', LSC = 'groomphone.collapsed.v1', collapsed = {};
  try { collapsed = JSON.parse(localStorage.getItem(LSC)||'{}')||{}; } catch(e){ collapsed = {}; }
  function saveCollapsed(){ try { localStorage.setItem(LSC, JSON.stringify(collapsed)); } catch(e){} }
  function esc(s){ return String(s==null?'':s).replace(/[&<>"]/g, function(ch){ return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[ch]; }); }
  function loadLocal(){ try { var o = JSON.parse(localStorage.getItem(LS)||'{}'); rulings = o.rulings||{}; notes = o.notes||{}; } catch(e){ rulings={}; notes={}; } }
  function saveLocal(){ try { localStorage.setItem(LS, JSON.stringify({rulings:rulings, notes:notes})); } catch(e){} }
  function now(){ return new Date().toISOString(); }
  function fmt(iso){ try { var d=new Date(iso); return d.toLocaleDateString(undefined,{day:'numeric',month:'short'})+' '+d.toLocaleTimeString(undefined,{hour:'numeric',minute:'2-digit'}); } catch(e){ return ''; } }
  function isRuled(d){ var r = rulings[d.id]; if (!r) return false; return d.text ? !!(r.words && r.words.trim()) : !!r.choice; }
  function openCount(c){ return c.decisions.filter(function(d){ return !isRuled(d); }).length; }
  function writeRuling(id, body){ rulings[id] = body; saveLocal(); if (db) { db.doc('rulings/'+id).set(body).catch(function(e){ console.warn('ruling save failed', e); setStatus('local'); }); } }
  function clearRuling(id){ delete rulings[id]; saveLocal(); if (db) { db.doc('rulings/'+id).delete().catch(function(e){ console.warn(e); }); } }
  function writeNote(key, text){ var body = {text:text, at:now()}; notes[key] = body; saveLocal(); if (db) { db.doc('notes/'+key).set(body).catch(function(e){ console.warn('note save failed', e); setStatus('local'); }); } }
  function setStatus(m){ mode = m; var el = document.querySelector('.m-status'); if (!el) return; el.className = 'm-status '+m; el.innerHTML = '<i></i>' + (m==='live' ? 'Rulings save to the board — the next session files them' : m==='wait' ? 'Connecting to the board…' : 'Saving on this phone only — the board’s store is not reachable from here'); }

  // ---------- routing ----------
  function route(){ var h = location.hash || '#/'; var m = h.match(/^#\/item\/(.+)$/); if (m) renderItem(decodeURIComponent(m[1])); else renderDash(); window.scrollTo(0,0); }
  window.addEventListener('hashchange', route);

  // ---------- dashboard ----------
  function renderDash(){
    var total = 0, items = 0;
    CARDS.forEach(function(c){ var n = openCount(c); total += n; if (n) items++; });
    var h = '<div class="m-hero"><div class="m-cap">Grooming board · '+esc(DATA.built)+'</div><h1>Backlog</h1><div class="m-total">'+total+' open decision'+(total===1?'':'s')+' on '+items+' item'+(items===1?'':'s')+'</div></div>';
    h += '<div class="m-status '+mode+'"><i></i></div>';
    DATA.sections.forEach(function(sec){
      var rows = '';
      DATA.ruled.filter(function(r){ return r.section===sec; }).forEach(function(r){
        rows += '<div class="m-row ruled"><span class="key soft">'+esc(r.key)+'</span><span class="t">'+esc(r.title)+'</span><span class="m-done">ruled</span></div>';
      });
      CARDS.filter(function(c){ return c.section===sec; }).forEach(function(c){
        var n = openCount(c), hasNote = !!(notes[c.key] && notes[c.key].text && notes[c.key].text.trim());
        rows += '<a class="m-row'+(n?'':' ruled')+'" href="#/item/'+encodeURIComponent(c.key)+'"><span class="key'+(n?'':' soft')+'">'+esc(c.key)+'</span><span class="t">'+esc(c.title)+'</span>'+(hasNote?'<span class="m-note-dot" title="You staged a note"></span>':'')+(n?'<span class="m-open">'+n+' open</span>':'<span class="m-done">ruled · phone</span>')+chev()+'</a>';
      });
      if (!rows) return;
      var secItems = DATA.ruled.filter(function(r){ return r.section===sec; }).length, secRuled = secItems;
      CARDS.filter(function(c){ return c.section===sec; }).forEach(function(c){ secItems++; if (!openCount(c)) secRuled++; });
      var col = !!collapsed[sec], allDone = secRuled===secItems;
      h += '<div class="m-sec'+(col?' collapsed':'')+'" data-sec="'+esc(sec)+'"><button class="m-sechead" aria-expanded="'+(!col)+'"><span class="m-h2">'+esc(sec)+'</span><span class="m-badge'+(allDone?' done':'')+'" title="items ruled / items in this section">'+secRuled+'/'+secItems+'</span><span class="m-chev"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="m6 9 6 6 6-6"/></svg></span></button><div class="m-card">'+rows+'</div></div>';
    });
    h += '<div class="m-sec"><div class="m-h2">Icebox</div><div class="m-card"><div class="m-row ruled"><span class="t">'+esc(DATA.icebox)+'</span></div></div></div>';
    h += '<div class="m-sec"><div class="m-empty">'+esc(DATA.archive)+'</div></div>';
    document.getElementById('app').innerHTML = h; setStatus(mode);
    document.querySelectorAll('.m-sechead').forEach(function(b){ b.addEventListener('click', function(){ var sec = b.parentNode.getAttribute('data-sec'); collapsed[sec] = !collapsed[sec]; saveCollapsed(); var y = window.scrollY; renderDash(); window.scrollTo(0, y); }); });
  }
  function chev(){ return '<span class="m-chev"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="m9 6 6 6-6 6"/></svg></span>'; }

  // ---------- item ----------
  var flipState = {};
  function renderItem(key){
    var c = BY[key]; if (!c) { location.hash = '#/'; return; }
    var idx = CARDS.indexOf(c), next = CARDS[idx+1];
    var h = '<div class="m-top"><div style="display:flex;align-items:center;justify-content:space-between"><a class="m-back" href="#/">'+'<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="m15 6-6 6 6 6"/></svg><span>Board</span></a><span class="m-cap">'+(idx+1)+' of '+CARDS.length+'</span></div>';
    h += '<div class="m-title"><span class="key">'+esc(c.key)+'</span><div>'+esc(c.title)+'</div></div><div class="m-sub">'+esc(c.sub)+'</div></div>';
    if (c.ruled && c.ruled.length) { h += '<div style="padding:10px 16px 0"><div class="m-empty" style="border-style:solid;border-color:var(--teal);color:var(--ink-2)"><span class="m-cap" style="color:var(--teal)">Already ruled</span><br>'+c.ruled.map(esc).join('<br>')+'</div></div>'; }
    if (c.frames.kind !== 'none') {
      var st = flipState[key] || 'proposed';
      h += '<div class="m-seg" role="tablist"><button data-flip="today" class="'+(st==='today'?'on':'')+'">Today</button><button data-flip="proposed" class="'+(st==='proposed'?'on':'')+'">Proposed</button></div>';
      if (c.frames.kind === 'walk') { h += '<div class="m-frame-cap" style="margin-top:12px"><span class="m-cap">'+(st==='today'?'What happens today':'Proposed')+' — '+esc(c.frames.caption)+'</span></div><div id="flip-body">'+c.frames[st]+'</div>'; }
      else { h += '<div id="flip-body"><div class="m-frame">'+c.frames[st]+'</div><div class="m-frame-cap">'+esc(c.frames.caption)+'</div></div>'; }
    } else if (c.blocks) {
      h += '<div class="m-blocks">'+c.blocks+'</div>';
    } else {
      h += '<div style="padding:14px 16px 0"><div class="m-empty">No screen changes — nothing to draw.</div></div>';
    }
    c.decisions.forEach(function(d){ h += decisionHTML(c, d); });
    var note = notes[key] && notes[key].text || '';
    h += '<div class="m-dec"><div class="m-q">Questions &amp; feedback — staged for the next session</div><textarea class="m-field'+(note.trim()?' filled':'')+'" id="note-field" rows="4" placeholder="Anything to work through before you can rule — a question about a frame, a redraw you want, a concern…">'+esc(note)+'</textarea><div class="m-hint" id="note-hint">'+(note.trim()?'Staged '+fmt(notes[key].at):'Saves as you type. The next session answers it here, in the frames.')+'</div></div>';
    h += '<div class="m-foot"><details class="m-details"><summary><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="m6 9 6 6 6-6"/></svg><span>Details</span></summary><div>'+esc(c.dims.join(' · '))+(c.pop?'<br><b>Who hits it</b> '+esc(c.pop):'')+'</div></details>'+(next?'<a class="m-next" href="#/item/'+encodeURIComponent(next.key)+'">Next: '+esc(next.key)+' '+chev()+'</a>':'<a class="m-next" href="#/">Back to the board '+chev()+'</a>')+'</div>';
    var app = document.getElementById('app'); app.innerHTML = h;
    // wire
    app.querySelectorAll('[data-flip]').forEach(function(b){ b.addEventListener('click', function(){ flipState[key] = b.getAttribute('data-flip'); renderItem(key); }); });
    app.querySelectorAll('[data-choose]').forEach(function(b){ b.addEventListener('click', function(){ var id = b.getAttribute('data-dec'), l = b.getAttribute('data-choose'); var prev = rulings[id] || {}; writeRuling(id, {choice:l, words:prev.words||'', at:now()}); refreshDecision(c, id); }); });
    app.querySelectorAll('[data-clear]').forEach(function(b){ b.addEventListener('click', function(){ var id = b.getAttribute('data-clear'); clearRuling(id); refreshDecision(c, id); }); });
    app.querySelectorAll('[data-words]').forEach(function(t){ var timer; t.addEventListener('input', function(){ clearTimeout(timer); var id = t.getAttribute('data-words'); timer = setTimeout(function(){ var prev = rulings[id] || {}; var d = c.decisions.filter(function(x){ return x.id===id; })[0]; var words = t.value; if (!words.trim() && !prev.choice) { if (rulings[id]) clearRuling(id); } else { writeRuling(id, {choice:prev.choice||'', words:words, at:now()}); } refreshDecision(c, id, true); }, 600); }); });
    var nf = document.getElementById('note-field'); var nt; nf.addEventListener('input', function(){ clearTimeout(nt); nt = setTimeout(function(){ writeNote(key, nf.value); nf.classList.toggle('filled', !!nf.value.trim()); document.getElementById('note-hint').textContent = nf.value.trim() ? 'Staged '+fmt(notes[key].at) : 'Saves as you type. The next session answers it here, in the frames.'; }, 600); });
  }
  function decisionHTML(c, d){
    var r = rulings[d.id] || {}, ruled = isRuled(d);
    var h = '<div class="m-dec'+(ruled?' ruled':'')+'" id="dec-'+esc(d.id)+'"><div class="m-cap">Decision '+esc(c.key)+' · '+d.n+'</div><div class="m-q">'+esc(d.q)+'</div>';
    d.options.forEach(function(o){ h += '<button class="m-btn'+(o.rec?' is-rec':'')+(r.choice===o.l?' chosen':'')+'" data-dec="'+esc(d.id)+'" data-choose="'+esc(o.l)+'"><span class="m-opt">'+esc(o.l)+'</span><span>'+esc(o.t)+'</span>'+(o.rec?'<span class="m-rec">rec</span>':'')+'</button>'; });
    h += '<textarea class="m-field'+(r.words&&r.words.trim()?' filled':'')+'" rows="2" data-words="'+esc(d.id)+'" placeholder="'+(d.text?'Your answer — filed verbatim':'In your words — optional, filed verbatim')+'">'+esc(r.words||'')+'</textarea>';
    h += '<div class="m-ruled-line" id="rl-'+esc(d.id)+'">'+(ruled?'<span>Ruled'+(r.choice?' · '+esc(r.choice):'')+' · '+fmt(r.at)+'</span><button data-clear="'+esc(d.id)+'">clear</button>':'')+'</div></div>';
    return h;
  }
  function refreshDecision(c, id, keepFocus){
    var d = c.decisions.filter(function(x){ return x.id===id; })[0]; var old = document.getElementById('dec-'+id); if (!old) return;
    if (keepFocus) { // only update the ruled line + classes, keep the textarea
      var r = rulings[id] || {}, ruled = isRuled(d); old.classList.toggle('ruled', ruled);
      document.getElementById('rl-'+id).innerHTML = ruled ? '<span>Ruled'+(r.choice?' · '+esc(r.choice):'')+' · '+fmt(r.at)+'</span><button data-clear="'+esc(id)+'">clear</button>' : '';
      var cb = old.querySelector('[data-clear]'); if (cb) cb.addEventListener('click', function(){ clearRuling(id); refreshDecision(c, id); });
      old.querySelector('[data-words]').classList.toggle('filled', !!(r.words&&r.words.trim()));
      return;
    }
    var tmp = document.createElement('div'); tmp.innerHTML = decisionHTML(c, d); var nw = tmp.firstChild; old.replaceWith(nw);
    nw.querySelectorAll('[data-choose]').forEach(function(b){ b.addEventListener('click', function(){ var l = b.getAttribute('data-choose'); var prev = rulings[id] || {}; writeRuling(id, {choice:l, words:prev.words||'', at:now()}); refreshDecision(c, id); }); });
    var cb = nw.querySelector('[data-clear]'); if (cb) cb.addEventListener('click', function(){ clearRuling(id); refreshDecision(c, id); });
    var t = nw.querySelector('[data-words]'); var timer; t.addEventListener('input', function(){ clearTimeout(timer); timer = setTimeout(function(){ var prev = rulings[id] || {}; var words = t.value; if (!words.trim() && !prev.choice) { if (rulings[id]) clearRuling(id); } else { writeRuling(id, {choice:prev.choice||'', words:words, at:now()}); } refreshDecision(c, id, true); }, 600); });
  }


  function currentItemKey(){ var m = (location.hash||'').match(/^#\/item\/(.+)$/); return m ? decodeURIComponent(m[1]) : null; }
  function syncView(prev, notesToo){
    var key = currentItemKey();
    if (!key) { var y = window.scrollY; renderDash(); window.scrollTo(0, y); return; }
    var c = BY[key]; if (!c) return;
    c.decisions.forEach(function(d){
      var a = JSON.stringify(prev[d.id]||null), b = JSON.stringify(rulings[d.id]||null);
      if (a === b) return;
      var el = document.getElementById('dec-'+d.id);
      var typing = el && document.activeElement && el.contains(document.activeElement);
      refreshDecision(c, d.id, !!typing);
    });
    if (notesToo) { var nf = document.getElementById('note-field'); if (nf && document.activeElement !== nf) { var t = notes[key] && notes[key].text || ''; nf.value = t; nf.classList.toggle('filled', !!t.trim()); var hint = document.getElementById('note-hint'); if (hint) hint.textContent = t.trim() ? 'Staged '+fmt(notes[key].at) : 'Saves as you type. The next session answers it here, in the frames.'; } }
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
      // the store wins; anything only on this phone is pushed up once
      var pushes = [];
      Object.keys(rulings).forEach(function(id){ if (!r[id]) { r[id] = rulings[id]; pushes.push(db.doc('rulings/'+id).set(rulings[id])); } });
      Object.keys(notes).forEach(function(k){ if (!n[k]) { n[k] = notes[k]; pushes.push(db.doc('notes/'+k).set(notes[k])); } });
      var prevR = rulings; rulings = r; notes = n; saveLocal(); setStatus('live'); syncView(prevR, true);
      Promise.all(pushes).catch(function(e){ console.warn(e); });
      unsubs.push(db.collection('rulings').onSnapshot(function(snap){ var m = {}; snap.docs.forEach(function(s){ if (s.exists) m[s.id] = s.data(); }); var prev = rulings; rulings = m; saveLocal(); syncView(prev); }, function(e){ console.warn(e); setStatus('local'); }));
      unsubs.push(db.collection('notes').onSnapshot(function(snap){ var m = {}; snap.docs.forEach(function(s){ if (s.exists) m[s.id] = s.data(); }); notes = m; saveLocal(); }, function(e){ console.warn(e); }));
    }).catch(function(e){ console.warn('store read failed', e); setStatus('local'); });
  }).catch(function(){ setStatus('local'); });
})();
"""

DATA_JSON = json.dumps(DATA).replace("</", "<\\/")
page = f"""<title>Grooming Board</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap">
<style>
{board_css}
{PAGE_CSS}
</style>
<div class="m-wrap"><div id="app"></div></div>
<script id="board-data" type="application/json">{DATA_JSON}</script>
<script>{JS}</script>
"""
open(O+'/grooming-board-phone.html','w').write(page)
print('bytes', len(page), 'cards', len(data_cards), 'decisions', sum(len(c['decisions']) for c in data_cards))

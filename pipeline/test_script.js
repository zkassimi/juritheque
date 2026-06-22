
var TOKEN = 'QxUh-UOziZszCL75';
var activeES = null;
var jobRunning = false;
var activeJobId = null;
var elapsedStart = null;
var elapsedTimer = null;

document.cookie = 'dashboard_token=' + TOKEN + '; path=/';
document.getElementById('token-hint').textContent = 'Token: ' + TOKEN;

// ── Navigation SPA ────────────────────────────────────────────────────────────
function showPage(pageId) {
  var pages = document.querySelectorAll('.page');
  for (var i = 0; i < pages.length; i++) pages[i].classList.remove('active');
  var t = document.getElementById('page-' + pageId);
  if (t) t.classList.add('active');
  var links = document.querySelectorAll('.nav-link');
  for (var i = 0; i < links.length; i++)
    links[i].classList.toggle('nav-active', links[i].dataset.page === pageId);
  try { localStorage.setItem('dash_page', pageId); } catch(e) {}
}

function toggleFullscreen() {
  document.body.classList.toggle('fullscreen');
  var btn = document.getElementById('btn-fullscreen');
  btn.textContent = document.body.classList.contains('fullscreen') ? '⊡ Réduire' : '⛶ Plein écran';
}

// ── Elapsed timer ─────────────────────────────────────────────────────────────
function startElapsed() {
  elapsedStart = Date.now();
  if (elapsedTimer) clearInterval(elapsedTimer);
  elapsedTimer = setInterval(function() {
    if (!elapsedStart) return;
    var s = Math.floor((Date.now() - elapsedStart) / 1000);
    document.getElementById('log-elapsed').textContent =
      Math.floor(s/60) + 'm' + (s%60 < 10 ? '0' : '') + (s%60) + 's';
  }, 1000);
}
function stopElapsed() {
  if (elapsedTimer) clearInterval(elapsedTimer);
  elapsedTimer = null; elapsedStart = null;
  document.getElementById('log-elapsed').textContent = '';
}

function stopActiveJob() {
  if (activeJobId) stopJob(activeJobId);
}

// ── Bouton script ─────────────────────────────────────────────────────────────
function handleBtnClick(btn) {
  var scriptId = btn.getAttribute('data-id');
  var risk     = btn.getAttribute('data-risk') || 'safe';
  var isDanger = btn.getAttribute('data-danger') === 'true';
  var aiCost   = btn.getAttribute('data-ai-cost') || '';
  var label    = btn.getAttribute('data-label') || scriptId;

  clearLogs();
  appendLog('>>> CLIC : ' + scriptId + ' [risk=' + risk + ']', 'log-info');

  if (jobRunning) {
    appendLog('>>> BLOQUÉ : un job tourne déjà', 'log-warn');
    showToast('Un job est déjà en cours. Arrêtez-le avant.', 'err');
    return;
  }

  if (isDanger || risk === 'ai') {
    document.getElementById('modal-title').textContent =
      risk === 'ai' ? '🤖 Action IA (coût API)' : '⚠️ Action sensible';
    document.getElementById('modal-msg').textContent =
      label + (isDanger ? ` peut modifier des données importantes.` : ` utilise l'API Gemini.`) + ` Confirmer ?`;
    var costDiv = document.getElementById('modal-ai-cost');
    if (aiCost) { document.getElementById('modal-ai-cost-text').textContent = aiCost; costDiv.style.display = 'block'; }
    else { costDiv.style.display = 'none'; }
    document.getElementById('modal').style.display = 'flex';
    document.getElementById('modal-confirm').onclick = function() { closeModal(); launchScript(scriptId, btn); };
    return;
  }
  launchScript(scriptId, btn);
}

function launchScript(scriptId, btn) {
  if (!btn) btn = document.querySelector('[data-id="' + scriptId + '"]');
  var label = btn.getAttribute('data-label') || scriptId;
  jobRunning = true;
  btn.disabled = true;
  btn.classList.add('btn-running');
  var allBtns = document.querySelectorAll('.script-btn');
  for (var i = 0; i < allBtns.length; i++) allBtns[i].disabled = true;

  clearLogs();
  setLogsTitle(label, 'running');
  startElapsed();
  appendLog('>>> Lancement : ' + scriptId, 'log-info');
  appendLog('>>> Envoi requête POST /run/' + scriptId + ' ...', 'log-info');

  var xhr = new XMLHttpRequest();
  xhr.open('POST', '/run/' + scriptId, true);
  xhr.setRequestHeader('X-Dashboard-Token', TOKEN);
  xhr.onload = function() {
    if (xhr.status === 200) {
      try {
        var data = JSON.parse(xhr.responseText);
        activeJobId = data.job_id;
        document.getElementById('btn-log-stop').style.display = 'inline-block';
        appendLog('>>> Job ID : ' + data.job_id, 'log-ok');
        appendLog('>>> Connexion SSE ...', 'log-info');
        streamLogs(data.job_id, btn, label);
      } catch(ex) { appendLog('ERREUR parse JSON : ' + xhr.responseText, 'log-err'); resetBtns(btn); }
    } else {
      appendLog('ERREUR HTTP ' + xhr.status + ' : ' + xhr.responseText, 'log-err');
      resetBtns(btn);
    }
  };
  xhr.onerror = function() { appendLog('ERREUR RÉSEAU — le dashboard est-il arrêté ?', 'log-err'); resetBtns(btn); };
  xhr.send();
}

function resetBtns(btn) {
  jobRunning = false; activeJobId = null;
  stopElapsed();
  document.getElementById('btn-log-stop').style.display = 'none';
  if (btn) { btn.disabled = false; btn.classList.remove('btn-running'); }
  var allBtns = document.querySelectorAll('.script-btn');
  for (var i = 0; i < allBtns.length; i++) allBtns[i].disabled = false;
}

// ── SSE Stream ────────────────────────────────────────────────────────────────
function streamLogs(jobId, btn, label) {
  if (activeES) activeES.close();
  document.getElementById('logs-area').innerHTML = '';
  var es = new EventSource('/stream/' + jobId + '?token=' + TOKEN);
  activeES = es;
  es.onmessage = function(e) {
    var line = e.data;
    if (line.indexOf('[DONE:') === 0) {
      var m = line.match(/[0-9]+/);
      var code = m ? parseInt(m[0]) : -1;
      resetBtns(btn);
      setLogsTitle(label, code === 0 ? 'done' : 'error');
      appendLog(line, code === 0 ? 'log-done' : 'log-err');
      es.close(); loadStatus(); return;
    }
    var cls = '';
    if (/OK|done|termin|✅/.test(line)) cls = 'log-ok';
    else if (/error|erreur|failed|traceback/i.test(line)) cls = 'log-err';
    else if (/warning|attention/.test(line)) cls = 'log-warn';
    else if (/═|─|info/.test(line)) cls = 'log-info';
    appendLog(line, cls);
  };
  es.onerror = function() { resetBtns(btn); setLogsTitle(label, 'error'); es.close(); loadStatus(); };
}

function appendLog(text, cls) {
  var a = document.getElementById('logs-area');
  var d = document.createElement('div');
  if (cls) d.className = cls;
  d.textContent = text;
  a.appendChild(d);
  a.scrollTop = a.scrollHeight;
}

function clearLogs() { document.getElementById('logs-area').innerHTML = ''; }

function copyLogs() {
  var kids = document.getElementById('logs-area').children;
  var lines = [];
  for (var i = 0; i < kids.length; i++) lines.push(kids[i].textContent);
  var text = lines.join('\n');
  if (!text.trim()) { showToast('Aucun log à copier', 'err'); return; }
  if (navigator.clipboard) navigator.clipboard.writeText(text).then(function() { showToast('Logs copiés !', 'ok'); });
}

// ── Status polling ─────────────────────────────────────────────────────────────
function loadStatus() {
  var xhr = new XMLHttpRequest();
  xhr.open('GET', '/status', true);
  xhr.setRequestHeader('X-Dashboard-Token', TOKEN);
  xhr.onload = function() {
    if (xhr.status !== 200) return;
    try {
      var jobs = JSON.parse(xhr.responseText);
      var list = document.getElementById('jobs-list');
      var entries = Object.entries(jobs).sort(function(a,b) { return b[1].elapsed - a[1].elapsed; }).slice(0, 6);
      if (entries.length === 0) { list.innerHTML = '<div class="no-jobs">Aucun job lancé</div>'; return; }
      var html = '';
      for (var i = 0; i < entries.length; i++) {
        var jid = entries[i][0]; var job = entries[i][1];
        var m = Math.floor(job.elapsed/60); var s = job.elapsed % 60;
        var sBtn = job.status === 'running'
          ? `<button class="btn-stop-sm" onclick="stopJob('${jid}')">Stop</button>` : ``;
        html += '<div class="job-item ' + job.status + '"><div class="job-hd">'
          + '<span class="job-name">' + job.label + '</span>'
          + '<span class="job-badge ' + job.status + '">' + job.status + '</span>'
          + sBtn + '</div><div class="job-elapsed">'
          + m + 'm' + (s < 10 ? '0' : '') + s + 's</div></div>';
      }
      list.innerHTML = html;
    } catch(ex) {}
  };
  xhr.send();
}

function stopJob(jobId) {
  var xhr = new XMLHttpRequest();
  xhr.open('POST', '/stop/' + jobId, true);
  xhr.setRequestHeader('X-Dashboard-Token', TOKEN);
  xhr.onload = function() { showToast('Job arrêté', 'ok'); loadStatus(); };
  xhr.send();
}

function loadStats() {
  var xhr = new XMLHttpRequest();
  xhr.open('GET', '/stats', true);
  xhr.setRequestHeader('X-Dashboard-Token', TOKEN);
  xhr.onload = function() {
    if (xhr.status !== 200) return;
    try {
      var s = JSON.parse(xhr.responseText);
      var set = function(id, val, warn) {
        var el = document.getElementById(id);
        if (!el) return;
        el.textContent = (val === undefined || val === null) ? '?' : val;
        if (warn && parseInt(val) > 0) el.style.color = 'var(--amber)';
        if (warn && parseInt(val) === 0) el.style.color = 'var(--green)';
      };
      set('stat-pdf-pending', s.pdf_pending);
      set('stat-pdf-done',    s.pdf_done);
      set('stat-pdf-errors',  s.pdf_errors, true);
      set('stat-total',      s.total);
      set('stat-public',     s.public_idx);
      set('stat-content-fr', s.with_content_fr);
      set('stat-content-ar', s.with_content_ar);
      set('stat-no-domain',  s.no_domain, true);
      set('stat-no-slug',    s.no_slug,   true);
      set('stat-sum-fr',    s.has_sum_fr);
      set('stat-no-sum-fr', s.no_sum_fr, true);
      set('stat-sum-ar',    s.has_sum_ar);
      set('stat-totrans',   s.to_translate, true);
      set('stat-guides',  s.guide_count);
      set('stat-indexed', s.indexed_today);
    } catch(ex) { console.error('stats error', ex); }
  };
  xhr.send();
}

function setLogsTitle(label, status) {
  document.getElementById('log-job-label').textContent = 'Logs — ' + label;
  document.getElementById('logs-dot').className = 'logs-dot ' + status;
}

function closeModal() { document.getElementById('modal').style.display = 'none'; }

function showToast(msg, type) {
  var t = document.createElement('div');
  t.className = 'toast toast-' + type;
  t.textContent = msg;
  document.body.appendChild(t);
  setTimeout(function() { t.parentNode && t.parentNode.removeChild(t); }, 3000);
}

// ── Init ──────────────────────────────────────────────────────────────────────
var savedPage = 'stats';
try { savedPage = localStorage.getItem('dash_page') || 'stats'; } catch(e) {}
showPage(savedPage);
loadStats();
loadStatus();
setInterval(loadStatus, 4000);
setInterval(loadStats,  60000);

"""Génère un fichier HTML avec tous les liens non conformes cliquables."""
import os, requests
from dotenv import load_dotenv
load_dotenv()
load_dotenv("pipeline/.env", override=True)

URL = (os.getenv("SUPABASE_URL") or os.getenv("VITE_SUPABASE_URL", "")).rstrip("/")
KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY") or os.getenv("VITE_SUPABASE_ANON_KEY", "")
H = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}
SITE = "https://juritheque.com"
ALLOWED = set("abcdefghijklmnopqrstuvwxyz0123456789-")

all_rows, offset = [], 0
while True:
    r = requests.get(f"{URL}/rest/v1/laws",
        headers={**H, "Range": f"{offset}-{offset+999}"},
        params={"select": "id,number,title_fr,canonical_slug,source_name,type,date"},
        timeout=20)
    if r.status_code not in (200, 206): break
    chunk = r.json()
    if not chunk: break
    all_rows.extend(chunk)
    if len(chunk) < 1000: break
    offset += 1000

bad = [x for x in all_rows
       if x.get("canonical_slug") and
       any(c not in ALLOWED for c in x["canonical_slug"])]

bad.sort(key=lambda r: r.get("canonical_slug", ""))

# Regrouper par type
groups = {}
for x in bad:
    t = x.get("type") or "Autre"
    groups.setdefault(t, []).append(x)

html = """<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<title>701 slugs non conformes — JuriThèque</title>
<style>
  body { font-family: monospace; font-size: 13px; max-width: 1200px; margin: 0 auto; padding: 20px; background: #f8f8f8; }
  h1 { font-size: 18px; color: #1a2e4a; }
  h2 { font-size: 14px; color: #555; margin-top: 30px; border-bottom: 1px solid #ccc; padding-bottom: 4px; }
  .stats { background: #1a2e4a; color: white; padding: 12px; border-radius: 4px; margin-bottom: 20px; }
  table { border-collapse: collapse; width: 100%; margin-bottom: 10px; background: white; }
  th { background: #1a2e4a; color: white; padding: 6px 10px; text-align: left; font-size: 12px; }
  td { padding: 5px 10px; border-bottom: 1px solid #eee; vertical-align: top; }
  tr:hover td { background: #f0f4ff; }
  a { color: #1a56db; text-decoration: none; }
  a:hover { text-decoration: underline; }
  .num { color: #888; font-size: 11px; }
  .slug-bad { color: #c00; }
  .type-badge { background: #e8eaf6; padding: 2px 6px; border-radius: 3px; font-size: 11px; }
  .date { color: #888; font-size: 11px; }
  .filter { margin: 15px 0; }
  input { padding: 6px 10px; border: 1px solid #ccc; border-radius: 4px; width: 300px; font-size: 13px; }
</style>
<script>
function filterRows() {
  const q = document.getElementById('search').value.toLowerCase();
  document.querySelectorAll('tr.data-row').forEach(tr => {
    tr.style.display = tr.dataset.search.includes(q) ? '' : 'none';
  });
}
</script>
</head>
<body>
<h1>🔴 701 slugs non conformes — JuriThèque</h1>
<div class="stats">
  Tous proviennent de la source <strong>Adala</strong> · Aucun n'a de vrai numéro de loi marocain<br>
  Convention attendue : <code>tout-en-minuscule-avec-tirets</code><br>
  Lien vers le site : cliquer sur le slug pour ouvrir la page
</div>
<div class="filter">
  <input type="text" id="search" placeholder="Filtrer par numéro, slug, type..." oninput="filterRows()">
</div>
"""

for grp_name, rows in sorted(groups.items(), key=lambda x: -len(x[1])):
    html += f'<h2>{grp_name} ({len(rows)} textes)</h2>\n'
    html += '<table>\n'
    html += '<tr><th>#</th><th>N° interne</th><th>Slug actuel (URL cassée)</th><th>Lien</th><th>Date</th></tr>\n'
    for i, x in enumerate(rows, 1):
        num   = x.get("number") or "—"
        slug  = x.get("canonical_slug") or ""
        date  = x.get("date") or "—"
        link  = f"{SITE}/loi/{slug}"
        search_data = f"{num} {slug} {grp_name} {date}".lower()
        html += (f'<tr class="data-row" data-search="{search_data}">'
                 f'<td class="num">{i}</td>'
                 f'<td class="num">{num}</td>'
                 f'<td class="slug-bad">{slug}</td>'
                 f'<td><a href="{link}" target="_blank">{link}</a></td>'
                 f'<td class="date">{date}</td>'
                 f'</tr>\n')
    html += '</table>\n'

html += "</body></html>"

out = "pipeline/bad_slugs_links.html"
with open(out, "w", encoding="utf-8") as f:
    f.write(html)
print(f"✅ Fichier généré : {out}")
print(f"   Ouvrir avec : start {out}")

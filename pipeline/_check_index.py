import json, re
from pathlib import Path

idx = json.loads(Path("pipeline/adala_index.json").read_text(encoding="utf-8"))
print(f"Total entrées index: {len(idx)}")

# Voir le format d'une entrée
sample_key = list(idx.keys())[0]
sample_val = idx[sample_key]
print(f"Format valeur (type={type(sample_val).__name__}): {repr(sample_val)[:120]}\n")

def normalize(n):
    return re.sub(r"[\.\-\s/]+", "-", n.strip().lower()).strip("-")

def get_entry(num):
    key = normalize(num)
    val = idx.get(key)
    if val is None:
        return None, key
    # Si la valeur est une string (ancien format = juste title_ar)
    if isinstance(val, str):
        return {"title_ar": val, "pdf_url": None}, key
    return val, key

for num in ["2.03.530", "2.84.93", "2.22.431", "1.02.172", "2.03.729"]:
    entry, key = get_entry(num)
    if entry:
        print(f"  ✅ {num} → clé={key}")
        print(f"     title_ar: {entry.get('title_ar','')[:80]}")
        pdf = entry.get('pdf_url') or entry.get('source_url') or ''
        print(f"     pdf_url : {pdf[:80]}")
    else:
        print(f"  ❌ {num} → clé={key}: ABSENT")

print(f"\n--- Stats ---")
print(f"Total entrées : {len(idx)}")
print(f"Pages couvertes (≈{len(idx)//18} pages × 18/page)")

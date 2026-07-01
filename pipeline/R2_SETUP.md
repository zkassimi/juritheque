# Migration PDFs Supabase → Cloudflare R2

**But** : sortir les ~933 PDFs stockés dans Supabase Storage vers Cloudflare R2
(egress **gratuit**, 10 Go free) pour libérer le plan free Supabase épuisé.
Les ~6 700 lois servies en direct depuis `source_url` (gov.ma) via le pdf-proxy
restent **inchangées**.

Domaine `juritheque.com` : DNS géré par **Cloudflare** (nameservers
`*.ns.cloudflare.com`, devant Vercel) → domaine custom R2 trivial, pas de
migration DNS.

---

## Étape 1 — Côté Cloudflare (toi, ~10 min)

1. **Activer R2** : dashboard Cloudflare → R2 → *Enable* (une carte est demandée
   même pour le free tier, mais c'est **0 €** sous 10 Go / 10 M lectures/mois).
2. **Créer le bucket** : nom `juritheque-pdfs`.
3. **Domaine public** : bucket → *Settings → Custom Domains* → ajouter
   `pdfs.juritheque.com`. Cloudflare crée le CNAME + SSL automatiquement.
   *(Alternative rapide : activer le sous-domaine `r2.dev` du bucket.)*
4. **Token API** : R2 → *Manage R2 API Tokens* → *Create* (permission *Object
   Read & Write*). Note l'**Access Key ID** et le **Secret Access Key**.
5. **Account ID** : visible dans l'URL du dashboard R2 ou la page d'accueil R2.

## Étape 2 — Variables dans `pipeline/.env` (toi)

```
R2_ACCOUNT_ID=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
R2_ACCESS_KEY_ID=xxxxxxxxxxxxxxxxxxxx
R2_SECRET_ACCESS_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
R2_BUCKET=juritheque-pdfs
R2_PUBLIC_DOMAIN=pdfs.juritheque.com
```

## Étape 3 — Dépendance

```
pip install boto3
```

## Étape 4 — Migration (moi, scripts prêts)

```powershell
# 1. Aperçu (aucune écriture)
python -X utf8 pipeline/migrate_pdfs_to_r2.py --dry-run

# 2. Test sur 20 PDFs
python -X utf8 pipeline/migrate_pdfs_to_r2.py --limit 20
#    → vérifier https://pdfs.juritheque.com/<un-fichier>.pdf s'ouvre

# 3. Migration complète
python -X utf8 pipeline/migrate_pdfs_to_r2.py

# 4. Mettre à jour les pdf_url en base (vérifie la présence R2 avant de patcher)
python -X utf8 pipeline/update_pdf_urls_r2.py --dry-run
python -X utf8 pipeline/update_pdf_urls_r2.py
```

Les octets sont pris du **mirror local** si disponible (0 egress Supabase),
sinon téléchargés depuis Supabase. `update_pdf_urls_r2.py` écrit une sauvegarde
CSV des anciennes URLs dans `pipeline/audit_results/` (rollback possible).

## Étape 5 — Déploiement front

- `api/pdf-proxy.js` accepte déjà `pdfs.juritheque.com` et `r2.dev`
  (ALLOWED_ORIGINS) → le viewer marche dès que `pdf_url` pointe vers R2.
- `npm run build` → déployer (push Vercel).

## Étape 6 — Nettoyage (optionnel, après vérif)

Une fois quelques PDFs R2 confirmés en ligne : vider le bucket
`legal-documents` de Supabase Storage → quota libéré.

---

## Rollback

`update_pdf_urls_r2.py` produit `pipeline/audit_results/pdf_url_backup_*.csv`
(id, ancienne_url, nouvelle_url). Pour revenir en arrière : re-PATCH `pdf_url`
avec `old_pdf_url` depuis ce CSV (tant que le bucket Supabase n'est pas vidé).

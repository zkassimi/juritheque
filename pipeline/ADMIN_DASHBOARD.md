# JuriThèque — Admin Dashboard

Interface locale pour gérer les scripts du pipeline de données.

## Lancement

```bash
python -X utf8 pipeline/dashboard.py
```

→ Ouvre automatiquement http://127.0.0.1:8000  
→ Le token de sécurité est affiché dans le terminal ET dans le header du dashboard  
→ Arrêt : `Ctrl+C` dans le terminal

---

## Niveaux de risque

Chaque bouton affiche un badge coloré indiquant son niveau de risque :

| Badge | Couleur | Signification |
|-------|---------|---------------|
| `safe` | 🟢 Vert | Action rapide, sans effet de bord, répétable sans risque |
| `⏱ long` | 🟡 Jaune | Action longue (plusieurs minutes), ne pas interrompre |
| `⚠ sensible` | 🔴 Rouge | Modifie beaucoup de données — confirmation obligatoire |
| `🤖 IA` | 🔵 Bleu | Appelle l'API Gemini (crédits OpenRouter) — estimation coût affichée |

---

## Actions disponibles

### 📥 Import & Crawl

| Action | Risk | Script | Durée estimée |
|--------|------|--------|---------------|
| Crawler Adala (justice.gov.ma) | ⏱ long | `crawl_adala.py` | 30-60 min |
| Crawler SGG | ⏱ long | `crawl_sgg.py` | 10-20 min |
| Scraper toutes sources | ⚠ sensible | `scraper.py --source all` | 60+ min |
| Importer lois JSON | ⚠ sensible | `import_lois_adala.py --limit 500` | 5-10 min |
| Fetch métadonnées lois | ⏱ long | `build_lois_adala.py --limit 500` | 15-30 min |
| Extraire texte PDFs | ⏱ long | `extract.py --limit 100` | 10-20 min |
| Extraire URLs sources | safe | `extract_source_url.py` | 2-5 min |

### 🧠 Enrichissement IA

| Action | Risk | Script | Coût estimé |
|--------|------|--------|-------------|
| Enrichir lois (résumés + TOC) | 🤖 IA | `enrich.py --limit 200` | ~$0.40/batch |
| Générer résumés manquants | 🤖 IA | `generate_adala_summaries.py --mode null` | ~$0.04/batch |
| **Améliorer résumés génériques** | 🤖 IA | `generate_adala_summaries.py --mode placeholders` | ~$0.04/batch |
| **Traduction AR (résumés)** | 🤖 IA | `translate_summaries_ar.py --limit 500` | ~$0.03/batch |
| Traduction titres FR | 🤖 IA | `translate_titles_batch.py --limit 200` | ~$0.01/batch |
| Traduction titres AR→FR | 🤖 IA | `translate_titles_adala.py --limit 200` | ~$0.01/batch |
| Nettoyer titres mal formatés | ⚠ sensible | `fix_adala_batch.py --titles` | < 1 min |
| Auto-assigner domaines | safe | `assign_domains.py --limit 500` | 2-5 min |
| Enrichir sources | safe | `enrich_sources.py --limit 500` | 2-5 min |
| Ajouter métadonnées | safe | `add_metadata_laws.py` | 2-5 min |

### 🔍 SEO & Index

| Action | Risk | Script | Durée estimée |
|--------|------|--------|---------------|
| Générer sitemap.xml | safe | `generate_sitemap.py` | 1-2 min |
| Rebuilder index recherche | safe | `build_site_search_index.py` | 2-5 min |
| Masquer textes sensibles (dry-run) | ⚠ sensible | `hide_sensitive_texts.py --dry-run` | 5 min |

### 📰 Bulletins Officiels

| Action | Risk | Script | Durée estimée |
|--------|------|--------|---------------|
| Surveiller nouveaux BO | safe | `bo_monitor.py --dry-run` | < 1 min |
| Scraper Bulletins Officiels | ⏱ long | `scrape_bulletins.py` | 20-40 min |
| Rebuilder index BO | ⏱ long | `build_bo_links.py --limit 100` | 10-20 min |

### 🔨 Build & Deploy

| Action | Risk | Script | Durée estimée |
|--------|------|--------|---------------|
| npm run build | safe | `npm run build` | 1-2 min |
| Générer favicon | safe | `generate_favicon.py` | < 1 min |

---

## Ordre recommandé pour la traduction AR

1. **Améliorer résumés génériques** (🤖) → remplace les placeholders par de vrais résumés
2. **Traduction AR (résumés)** (🤖) → traduit les bons résumés FR en arabe
3. Répéter chaque batch jusqu'à 0 résumés restants (visible dans la sidebar)

---

## Arrêter un job

- Bouton **■ Stop** dans la sidebar "Jobs récents"
- Ou `Ctrl+C` dans le terminal (arrête le dashboard entier)

⚠️ Un seul job peut tourner à la fois. Le dashboard bloque le lancement d'un 2ème job.

---

## Logs

- Affichés en temps réel dans la zone noire en bas
- Bouton **📋 Copier** : copie tous les logs dans le presse-papiers
- Bouton **Effacer** : vide l'affichage
- ⚠️ Les logs ne sont pas sauvegardés sur disque — perdus au redémarrage du dashboard

---

## Bonnes pratiques

### Avant un import massif
- Vérifier les crédits OpenRouter : https://openrouter.ai/settings/credits
- Vérifier la limite mensuelle de la clé API (ne pas dépasser le budget)
- Tester avec `--limit 10` d'abord si possible

### Avant une traduction IA
- Vérifier que les résumés FR sont de bonne qualité (pas de texte générique)
- Lancer d'abord **"Améliorer résumés génériques"** si des lois Adala sont concernées

### En cas d'erreur 403 OpenRouter
- Vérifier le solde : https://openrouter.ai/settings/credits
- Vérifier la limite mensuelle de la clé API

---

## Sécurité

- Le dashboard écoute **uniquement sur 127.0.0.1** (jamais accessible depuis le réseau)
- Un **token aléatoire** est généré à chaque démarrage
- Seuls les scripts de la **whitelist** peuvent être exécutés (pas de commande libre)

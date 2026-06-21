# JuriThèque — Documentation Technique Complète

> **Plateforme de base de données juridique marocaine bilingue (FR/AR)**  
> URL : [juritheque.com](https://juritheque.com)  
> Dernière mise à jour : Juin 2026

---

## Table des matières

1. [Vue d'ensemble](#1-vue-densemble)
2. [Architecture technique](#2-architecture-technique)
3. [Stack technique détaillé](#3-stack-technique-détaillé)
4. [Structure des fichiers](#4-structure-des-fichiers)
5. [Installation complète](#5-installation-complète)
6. [Base de données — Schéma](#6-base-de-données--schéma)
7. [Scripts pipeline — Référence](#7-scripts-pipeline--référence)
8. [Sécurité](#8-sécurité)
9. [Déploiement](#9-déploiement)
10. [Projections & Roadmap](#10-projections--roadmap)
11. [Besoins identifiés](#11-besoins-identifiés)

---

## 1. Vue d'ensemble

### Présentation

**JuriThèque** (nom de domaine : `juritheque.com`, nom interne du repo : `lexbase`) est une plateforme numérique de centralisation et de vulgarisation du droit marocain.

**Mission :** Rendre accessibles les 7 400+ textes juridiques marocains (lois, dahirs, décrets, codes, arrêtés) en version bilingue français/arabe, avec résumés IA, assistant juridique intelligent, et contenus pédagogiques.

### Chiffres clés (Juin 2026)

| Indicateur | Valeur |
|------------|--------|
| Textes juridiques indexés | 7 400+ |
| Domaines juridiques | 16 |
| Sources officielles | 11 sites gouvernementaux |
| Résumés en arabe | ~5 015 |
| Résumés à améliorer (Adala) | ~6 896 |
| Scripts pipeline | 28 |
| Pages React | 21 |
| Composants React | 18 |
| Migrations SQL | 16 |

### Public cible

- Étudiants en droit
- Juristes et avocats
- Fonctionnaires et élus
- Chercheurs et enseignants
- Citoyens marocains (MRE inclus)
- Investisseurs étrangers

---

## 2. Architecture technique

JuriThèque repose sur une architecture **JAMstack** à 3 couches :

```
┌─────────────────────────────────────────────────┐
│             FRONTEND (React SPA)                │
│   React 18 + Vite 5 + Tailwind CSS              │
│   Hébergé sur Hostinger (dist/ statique)        │
└────────────────────┬────────────────────────────┘
                     │ REST API (clé anon publique)
                     │ Supabase JS SDK
┌────────────────────▼────────────────────────────┐
│             BACKEND (Supabase Cloud)            │
│   PostgreSQL + Auth JWT + Storage + PostgREST   │
│   Projet : bmargdbbcnhkrjeidmvh — Région EU     │
└────────────────────┬────────────────────────────┘
                     │ service_role key
                     │ (pipeline seulement — JAMAIS public)
┌────────────────────▼────────────────────────────┐
│         PIPELINE DE DONNÉES (Python local)      │
│   28 scripts : crawl, scrape, extract, enrich   │
│   translate, build, generate, dashboard         │
│   LLM : OpenRouter → Gemini 2.5 Flash Lite      │
│   Dashboard admin : FastAPI local (port 8000)   │
└─────────────────────────────────────────────────┘
```

### Flux de données

```
Sites officiels (11)
      │
      ▼
scraper.py / crawl_adala.py / crawl_sgg.py
      │ PDFs + métadonnées
      ▼
extract.py
      │ Texte brut
      ▼
enrich.py / generate_adala_summaries.py
      │ Résumés FR (Gemini 2.5 Flash Lite)
      ▼
translate_summaries_ar.py
      │ Résumés AR
      ▼
Supabase PostgreSQL
      │ REST API (anon key)
      ▼
Frontend React → juritheque.com
```

---

## 3. Stack technique détaillé

### Frontend

| Technologie | Version | Rôle |
|-------------|---------|------|
| React | 18.2.0 | Framework UI (SPA) |
| Vite | 5.1.0 | Bundler + dev server |
| React Router DOM | 6.22.0 | Navigation client-side |
| Tailwind CSS | 3.4.1 | Styling utility-first |
| Lucide React | 0.344.0 | Bibliothèque d'icônes |
| @supabase/supabase-js | 2.105.1 | Client Supabase |

**Polices :** Playfair Display (titres) + Inter (texte courant) via Google Fonts

**Couleurs principales :**
- Navy : `#1a2e4a`
- Gold : `#c9a84c`
- Fond clair : `#f8fafc`

### Backend (Supabase)

| Composant | Rôle |
|-----------|------|
| PostgreSQL | Base de données principale |
| Supabase Auth | JWT, email/password, rôles |
| PostgREST | API REST auto-générée |
| Supabase Storage | PDFs (bucket `legal-documents`) |
| Row Level Security | Contrôle d'accès par rôle |

**URL projet :** `https://bmargdbbcnhkrjeidmvh.supabase.co`

### Pipeline Python

| Package | Rôle |
|---------|------|
| `requests` | HTTP scraping + appels API |
| `pdfplumber` ≥ 0.10.3 | Extraction texte PDF (primaire) |
| `PyMuPDF (fitz)` ≥ 1.23.0 | Extraction texte PDF (fallback) |
| `python-dotenv` ≥ 1.0.0 | Chargement variables `.env` |
| `rich` ≥ 13.7.0 | Affichage console formaté |
| `fastapi` | Dashboard web admin |
| `uvicorn` | Serveur ASGI pour FastAPI |
| `supabase` 2.3.4 | Client Python Supabase |
| `beautifulsoup4` | Parsing HTML |
| `httpx` | Client HTTP async |

### APIs externes

| Service | Usage | Modèle / Coût |
|---------|-------|---------------|
| OpenRouter | Résumés juridiques FR + traductions AR | Gemini 2.5 Flash Lite — ~$0.00006/1K tokens |
| Supabase | Base de données + Auth + Storage | Plan Pro Cloud |
| huquqai.ma | Métadonnées lois Adala | Gratuit |
| 11 sites gouvernementaux | Scraping PDFs | Gratuit |

---

## 4. Structure des fichiers

```
lexbase/
├── src/
│   ├── pages/              (21 pages React)
│   │   ├── Home.jsx
│   │   ├── Base.jsx
│   │   ├── LawDetail.jsx
│   │   ├── Domaines.jsx
│   │   ├── DomainDetail.jsx
│   │   ├── Assistant.jsx
│   │   ├── Login.jsx
│   │   ├── Profile.jsx
│   │   ├── Admin.jsx
│   │   ├── Videos.jsx
│   │   ├── BulletinsOfficiels.jsx
│   │   ├── VeilleJuridique.jsx
│   │   ├── Guides.jsx
│   │   ├── GuideDetail.jsx
│   │   └── ...
│   ├── components/         (18 composants réutilisables)
│   │   ├── Navbar.jsx
│   │   ├── Footer.jsx
│   │   ├── SearchBar.jsx
│   │   ├── LawCard.jsx
│   │   ├── DomainCard.jsx
│   │   ├── VideoCard.jsx
│   │   ├── VideoModal.jsx
│   │   ├── JsonLD.jsx
│   │   └── ...
│   ├── contexts/
│   │   ├── AuthContext.jsx   (auth JWT + rôles)
│   │   └── LangContext.jsx   (FR/AR + RTL toggle)
│   ├── hooks/
│   │   └── useSEO.js         (meta tags dynamiques)
│   ├── lib/
│   │   ├── api.js            (fetchLaws, fetchDomains, etc.)
│   │   ├── supabase.js       (client Supabase)
│   │   └── lawUtils.js       (helpers formatage)
│   └── data/
│       ├── translations.js   (strings FR/AR)
│       ├── mockData.js       (fallback si Supabase offline)
│       └── seoIntentPages.js (guides SEO thématiques)
│
├── pipeline/
│   ├── dashboard.py              (Admin UI — FastAPI + SSE)
│   ├── scraper.py                (11 sources → PDFs)
│   ├── crawl_adala.py            (justice.gov.ma — 7 867 textes)
│   ├── crawl_sgg.py              (sgg.gov.ma consolidés)
│   ├── extract.py                (PDF → texte → Supabase)
│   ├── enrich.py                 (Résumés + TOC via IA)
│   ├── generate_adala_summaries.py  (Résumés FR lois Adala)
│   ├── translate_summaries_ar.py    (FR→AR via Gemini)
│   ├── translate_titles_batch.py    (Titres FR→AR)
│   ├── translate_titles_adala.py    (Titres AR→FR)
│   ├── assign_domains.py         (Auto-classification domaines)
│   ├── enrich_sources.py         (Métadonnées sources)
│   ├── add_metadata_laws.py      (Métadonnées supplémentaires)
│   ├── build_lois_adala.py       (Fetch métadonnées Adala)
│   ├── import_lois_adala.py      (Import JSON → Supabase)
│   ├── fix_adala_batch.py        (Nettoyage titres)
│   ├── extract_source_url.py     (Extraction URLs sources)
│   ├── generate_sitemap.py       (Génère sitemap.xml)
│   ├── build_site_search_index.py   (Index recherche interne)
│   ├── hide_sensitive_texts.py   (Masquage textes sensibles)
│   ├── bo_monitor.py             (Surveillance Bulletins Officiels)
│   ├── scrape_bulletins.py       (Scraping BO)
│   ├── build_bo_links.py         (Index liens BO)
│   ├── generate_favicon.py       (Génère favicon.ico)
│   ├── requirements.txt          (Dépendances Python)
│   ├── .env                      ⚠️ SECRETS — jamais sur Git
│   └── pdfs/                     ⚠️ PDFs locaux — gitignored
│
├── supabase/
│   └── migrations/           (16 fichiers SQL, 001 → 016)
│       ├── 001_lexbase_schema.sql
│       ├── 002_profiles.sql
│       ├── 003_domains_seed.sql
│       └── ...
│
├── public/
│   ├── sitemap.xml           (généré par generate_sitemap.py)
│   ├── robots.txt
│   ├── seo-preview.php       (SSR meta tags pour bots sociaux)
│   ├── .htaccess             (SPA routing + compression)
│   └── data/
│       ├── bulletins-officiels.json
│       └── lois-adala.json
│
├── dist/                     (Build production → upload Hostinger)
├── .env                      (VITE_SUPABASE_URL, VITE_SUPABASE_ANON_KEY)
├── .env.example              (Template — variables sans valeurs)
├── .gitignore
├── package.json
├── vite.config.js
└── tailwind.config.js
```

---

## 5. Installation complète

### Prérequis système

| Outil | Version minimale | Vérification |
|-------|-----------------|--------------|
| Node.js | ≥ 18.x | `node --version` |
| npm | ≥ 9.x | `npm --version` |
| Python | ≥ 3.11 | `python --version` |
| Git | ≥ 2.x | `git --version` |

### Étape 1 — Cloner le dépôt

```bash
git clone https://github.com/[votre-username]/lexbase.git
cd lexbase
```

### Étape 2 — Installer les dépendances frontend

```bash
npm install
```

### Étape 3 — Créer le fichier `.env` (frontend)

Créer un fichier `.env` à la racine du projet :

```env
VITE_SUPABASE_URL=https://bmargdbbcnhkrjeidmvh.supabase.co
VITE_SUPABASE_ANON_KEY=sb_publishable_QmGOC1wxyEHXpbAN4p6NaA_85FoIih5
VITE_OPENROUTER_KEY=[votre clé OpenRouter — pour l'assistant IA]
```

> **Note :** `VITE_SUPABASE_ANON_KEY` est une clé publique sécurisée (lecture seule, protégée par RLS). Elle peut être partagée.

### Étape 4 — Lancer en développement

```bash
npm run dev
# → http://localhost:5173
```

### Étape 5 — Installer le pipeline Python

```bash
cd pipeline
pip install -r requirements.txt
pip install fastapi uvicorn
```

> Sur Windows, ajouter `python -X utf8` devant chaque commande pour éviter les erreurs d'encodage avec les caractères arabes/accentués.

### Étape 6 — Créer `pipeline/.env` (secrets)

```env
SUPABASE_URL=https://bmargdbbcnhkrjeidmvh.supabase.co
SUPABASE_SERVICE_KEY=[clé service_role — droits admin complets]
OPENROUTER_KEY=[clé OpenRouter]
```

> ⚠️ **Ce fichier ne doit JAMAIS être commité sur Git.** Il contient la clé `service_role` qui donne un accès total à la base de données.

### Étape 7 — Lancer le dashboard admin

```bash
python -X utf8 pipeline/dashboard.py
# → http://127.0.0.1:8000
# Le token de sécurité est affiché dans le terminal
```

### Étape 8 — Build et déploiement

```bash
npm run build
# → génère dist/ (fichiers statiques)
# Uploader dist/ sur Hostinger via FTP ou cPanel File Manager
```

---

## 6. Base de données — Schéma

### Tables principales

| Table | Rôle | Lignes (estimé) |
|-------|------|-----------------|
| `laws` | Textes juridiques (table centrale) | 7 400+ |
| `domains` | 16 domaines juridiques | 16 |
| `profiles` | Utilisateurs (étend `auth.users`) | Variable |
| `favorites` | Favoris par utilisateur | Variable |
| `videos` | Vidéos YouTube éducatives | Variable |
| `site_search_index` | Index de recherche interne | ~7 500 |
| `bulletins_officiels` | Bulletins Officiels du Royaume | Variable |
| `subscribers` | Newsletter | Variable |

### Colonnes clés de `laws`

```sql
id                  UUID PRIMARY KEY DEFAULT gen_random_uuid()
number              TEXT            -- Ex: "103-12", "1-11-91"
type                TEXT            -- Loi | Dahir | Décret | Arrêté | Code | Circulaire
title_fr            TEXT            -- Titre en français
title_ar            TEXT            -- Titre en arabe
simple_summary_fr   TEXT            -- Résumé IA en français (350-450 chars)
simple_summary_ar   TEXT            -- Résumé IA en arabe
domain_id           TEXT            -- FK → domains.id (domaine principal)
domain_ids          TEXT[]          -- Domaines secondaires (tableau)
status              TEXT            -- En vigueur | Abrogé | Modifié
date                DATE            -- Date du texte
language            TEXT            -- Français | Arabe | Bilingue
content_fr          TEXT            -- Texte intégral extrait du PDF
content_ar          TEXT            -- Texte intégral en arabe
source_name         TEXT            -- Ex: "Adala", "SGG", "BKAM"
source_url          TEXT            -- URL de la source officielle
pdf_url             TEXT            -- URL du PDF original
tags                TEXT[]          -- Mots-clés thématiques
views               INTEGER DEFAULT 0
quality_score       SMALLINT        -- Score qualité 0-100
created_at          TIMESTAMPTZ DEFAULT now()
updated_at          TIMESTAMPTZ DEFAULT now()
```

### Colonnes de `domains`

```sql
id          TEXT PRIMARY KEY   -- Ex: "civil", "penal", "commercial"
name_fr     TEXT               -- "Droit civil"
name_ar     TEXT               -- "القانون المدني"
icon        TEXT               -- Nom icône Lucide React
law_count   INTEGER            -- Nombre de lois (mis à jour périodiquement)
color       TEXT               -- Couleur hex pour l'UI
description TEXT
```

### 16 Domaines juridiques

`civil` · `penal` · `commercial` · `administratif` · `travail` · `fiscal` · `constitutionnel` · `numerique` · `bancaire` · `international` · `finances_publiques` · `collectivites` · `transport` · `environnement` · `sante` · `education`

### Appliquer les migrations (nouveau projet Supabase)

Dans le Supabase SQL Editor, exécuter dans l'ordre :

```
supabase/migrations/001_lexbase_schema.sql
supabase/migrations/002_profiles.sql
supabase/migrations/003_domains_seed.sql
supabase/migrations/004_rls_policies.sql
...
supabase/migrations/016_[dernière migration].sql
```

---

## 7. Scripts pipeline — Référence complète

### Lancement via le dashboard

```bash
python -X utf8 pipeline/dashboard.py
# → Ouvrir http://127.0.0.1:8000
```

### Ou en ligne de commande directe

#### 🕷️ Collecte de données

| Script | Commande | Durée | Description |
|--------|----------|-------|-------------|
| `scraper.py` | `python -X utf8 pipeline/scraper.py --source all` | 60+ min | 11 sources officielles, ~706 PDFs |
| `crawl_adala.py` | `python -X utf8 pipeline/crawl_adala.py` | 30-60 min | justice.gov.ma — 7 867 textes |
| `crawl_sgg.py` | `python -X utf8 pipeline/crawl_sgg.py` | 10-20 min | sgg.gov.ma textes consolidés |
| `extract.py` | `python -X utf8 pipeline/extract.py --limit 100` | 10-20 min | PDF → texte → Supabase |
| `extract_source_url.py` | `python -X utf8 pipeline/extract_source_url.py` | 2-5 min | Extraction URLs sources |
| `build_lois_adala.py` | `python -X utf8 pipeline/build_lois_adala.py --limit 500` | 15-30 min | Fetch métadonnées Adala |
| `import_lois_adala.py` | `python -X utf8 pipeline/import_lois_adala.py --limit 500` | 5-10 min | Import JSON → Supabase |

#### 🧠 Enrichissement IA (OpenRouter — coût réel)

| Script | Commande | Coût estimé |
|--------|----------|-------------|
| `enrich.py` | `python -X utf8 pipeline/enrich.py --limit 200` | ~$0.40/200 lois |
| `generate_adala_summaries.py` | `python -X utf8 pipeline/generate_adala_summaries.py --mode placeholders --limit 500` | ~$0.04/500 lois |
| `translate_summaries_ar.py` | `python -X utf8 pipeline/translate_summaries_ar.py --limit 500` | ~$0.03/500 lois |
| `translate_titles_batch.py` | `python -X utf8 pipeline/translate_titles_batch.py --limit 200` | ~$0.01/200 lois |
| `translate_titles_adala.py` | `python -X utf8 pipeline/translate_titles_adala.py --limit 200` | ~$0.01/200 lois |

> **Modèle IA :** `google/gemini-2.5-flash-lite` via OpenRouter  
> **Avant chaque run IA :** Vérifier le solde sur https://openrouter.ai/settings/credits

**Modes de `generate_adala_summaries.py` :**

```bash
--mode null          # Lois sans résumé (nouveaux imports)
--mode placeholders  # Remplace les résumés génériques (6 896 à traiter)
--mode all           # Les deux
--dry-run            # Simulation sans écriture
--limit N            # Limiter à N lois (test avec --limit 10)
```

**Ordre recommandé pour la chaîne de traitement :**

```
1. generate_adala_summaries.py --mode placeholders  → Résumés FR qualitatifs
2. translate_summaries_ar.py                        → Traduit FR→AR
3. Répéter jusqu'à 0 restants
```

#### 🔧 Maintenance & SEO

| Script | Commande | Description |
|--------|----------|-------------|
| `generate_sitemap.py` | `python -X utf8 pipeline/generate_sitemap.py` | Régénère `public/sitemap.xml` |
| `build_site_search_index.py` | `python -X utf8 pipeline/build_site_search_index.py` | Reconstruit l'index de recherche |
| `assign_domains.py` | `python -X utf8 pipeline/assign_domains.py --limit 500` | Auto-classifie les lois par domaine |
| `enrich_sources.py` | `python -X utf8 pipeline/enrich_sources.py --limit 500` | Enrichit les métadonnées sources |
| `add_metadata_laws.py` | `python -X utf8 pipeline/add_metadata_laws.py` | Ajoute des métadonnées manquantes |
| `fix_adala_batch.py` | `python -X utf8 pipeline/fix_adala_batch.py --titles` | Nettoie les titres mal formatés |
| `hide_sensitive_texts.py` | `python -X utf8 pipeline/hide_sensitive_texts.py --dry-run` | Masque les textes sensibles |

#### 📰 Bulletins Officiels

| Script | Commande | Description |
|--------|----------|-------------|
| `bo_monitor.py` | `python -X utf8 pipeline/bo_monitor.py --dry-run` | Surveille les nouveaux BO |
| `scrape_bulletins.py` | `python -X utf8 pipeline/scrape_bulletins.py` | Scrape les Bulletins Officiels |
| `build_bo_links.py` | `python -X utf8 pipeline/build_bo_links.py --limit 100` | Reconstruit l'index BO |

#### ⚙️ Outils admin

| Script | Commande | Description |
|--------|----------|-------------|
| `dashboard.py` | `python -X utf8 pipeline/dashboard.py` | Interface admin locale (port 8000) |
| `generate_favicon.py` | `python pipeline/generate_favicon.py` | Génère favicon.ico |

### Commandes npm (frontend)

```bash
npm run dev       # Démarrage serveur de développement → http://localhost:5173
npm run build     # Build production → dist/
npm run preview   # Preview du build local → http://localhost:4173
npm run lint      # Lint ESLint
```

---

## 8. Sécurité

### Mesures en place ✅

| Mesure | Détail |
|--------|--------|
| **RLS Supabase** | Row Level Security activée sur toutes les tables |
| **Clés séparées** | `anon key` (public, lecture seule) vs `service_role` (pipeline uniquement) |
| **`.gitignore`** | `.env`, `pipeline/.env`, `pipeline/pdfs/`, rapports exclus du dépôt |
| **JWT Auth** | Tokens expirables, gestion via Supabase Auth |
| **Dashboard localhost** | Port 8000 lié à `127.0.0.1` uniquement, jamais accessible depuis le réseau |
| **Token dashboard** | Token aléatoire généré à chaque démarrage |
| **Whitelist scripts** | Seuls les scripts autorisés peuvent être lancés depuis le dashboard |
| **robots.txt** | `/admin`, `/connexion`, `/profil` exclus des crawlers |
| **seo-preview.php** | PHP côté serveur, ne divulgue aucune clé API |

### Variables d'environnement

#### ⚠️ Secrets — NE JAMAIS publier

```env
# pipeline/.env uniquement — droits admin complets sur la BDD
SUPABASE_SERVICE_KEY=sb_secret_[...]

# pipeline/.env et .env.local — facturé à l'usage
OPENROUTER_KEY=sk-or-v1-[...]
```

#### ✅ Safe pour le public (frontend)

```env
# .env — clé publique, protégée par RLS
VITE_SUPABASE_URL=https://bmargdbbcnhkrjeidmvh.supabase.co
VITE_SUPABASE_ANON_KEY=sb_publishable_[...]
```

### Recommandations pour GitHub

1. **Ne jamais committer** : `pipeline/.env`, `.env.local`, `pipeline/pdfs/`
2. Utiliser `.env.example` comme template (noms de variables, pas de valeurs)
3. Activer **Dependabot alerts** sur le repo GitHub
4. Utiliser **GitHub Secrets** pour les clés en CI/CD
5. Protéger la branche `main` (require PR + review avant merge)
6. Créer 2 branches minimum : `main` (production) et `dev` (développement)
7. Effectuer une **rotation des clés API tous les 6 mois**

### Fichier `.gitignore` recommandé

```gitignore
# Secrets
.env
.env.local
pipeline/.env
pipeline/reports/
pipeline/pdfs/

# Build
dist/
node_modules/

# Python
__pycache__/
*.pyc
.venv/

# OS
.DS_Store
Thumbs.db
```

---

## 9. Déploiement

### Frontend — Actuel (Hostinger)

```bash
# 1. Build
npm run build       # → génère dist/

# 2. Upload via FTP ou cPanel File Manager
# Uploader le contenu de dist/ dans public_html/

# 3. Vérifier le .htaccess (SPA routing)
# Le fichier est généré automatiquement par Vite
```

**Configuration requise sur Hostinger :**
- PHP ≥ 7.4 (pour seo-preview.php)
- `.htaccess` : mod_rewrite activé (SPA routing)
- SSL/HTTPS : Certificat Let's Encrypt (activé via hPanel)

### Frontend — Recommandé (Vercel ou Netlify)

```bash
# 1. Connecter le repo GitHub → auto-deploy à chaque push sur main
# 2. Configurer les variables d'environnement dans le panel
# 3. Avantages : HTTPS automatique, CDN mondial, rollback en 1 clic
```

**Variables à configurer dans Vercel/Netlify :**
```
VITE_SUPABASE_URL
VITE_SUPABASE_ANON_KEY
VITE_OPENROUTER_KEY
```

### Pipeline — Actuel (Windows local)

Le pipeline tourne sur la machine Windows locale. Pour automatiser :

```batch
REM Exemple : run_translation.bat
python -X utf8 C:\...\pipeline\translate_summaries_ar.py --limit 500
```

Planification via **Windows Task Scheduler** pour les tâches récurrentes.

### Pipeline — Futur (VPS Linux)

```bash
# Installation sur Ubuntu 22.04+
git clone https://github.com/[user]/lexbase.git
cd lexbase/pipeline
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Cron jobs
crontab -e
# 0 2 * * * /path/to/.venv/bin/python -X utf8 /path/pipeline/bo_monitor.py

# systemd service pour le dashboard
sudo systemctl enable juritheque-dashboard.service
```

### SEO post-déploiement

```bash
# 1. Régénérer le sitemap
python -X utf8 pipeline/generate_sitemap.py

# 2. Soumettre le sitemap à Google Search Console
# → https://search.google.com/search-console
# → Sitemaps → Soumettre → https://juritheque.com/sitemap.xml

# 3. Vérifier le rendu des bots sociaux
# → https://juritheque.com/seo-preview.php?url=/loi/[id]
```

---

## 10. Projections & Roadmap

### Court terme (0–3 mois)

- [ ] **Résumés Adala** : Compléter les 6 896 résumés génériques (`--mode placeholders`)
- [ ] **Traductions AR** : Compléter les 2 336 résumés sans version arabe
- [ ] **Upload Hostinger** : Déployer le build `dist/` actuel
- [ ] **Google Search Console** : Soumettre `sitemap.xml`
- [ ] **Jurisprudence** : Module arrêts Cour de Cassation + Cour Administrative Suprême
- [ ] **Newsletter** : Alertes nouvelles lois par domaine (abonnement email)

### Moyen terme (3–12 mois)

- [ ] **Module QCM** : Questions/réponses juridiques pour étudiants en droit
- [ ] **Espace contributeurs** : Juristes peuvent soumettre résumés/corrections
- [ ] **CI/CD GitHub Actions** : Build + tests automatiques à chaque push
- [ ] **Application mobile** : React Native (iOS + Android)
- [ ] **API publique JuriThèque** : Pour universités et LegalTech marocaines
- [ ] **Comparateur de versions** : Historique des modifications des textes

### Long terme (1 an+)

- [ ] **Chatbot avancé** : Mémoire de conversation + citations précises
- [ ] **Indexation jurisprudence arabe** : Cour Suprême, décisions administratives
- [ ] **Tests unitaires** : Vitest pour React, pytest pour le pipeline
- [ ] **Monitoring** : Sentry (erreurs frontend) + logs serveur
- [ ] **Sitemap dynamique** : Généré côté serveur, pas statique

### Objectifs chiffrés

| Métrique | Actuel (Juin 2026) | Objectif 1 an |
|----------|-------------------|---------------|
| Textes indexés | 7 400 | 15 000+ |
| Résumés AR | 5 015 | 15 000 |
| Domaines | 16 | 16 + jurisprudence |
| Sources | 11 | 20+ |
| Visiteurs/mois | — | 10 000+ |

---

## 11. Besoins identifiés

### Techniques

- [ ] Migrer vers **Vercel ou Netlify** (CI/CD automatique, au lieu du FTP Hostinger manuel)
- [ ] **VPS Linux** pour le pipeline (éviter la dépendance au PC Windows local)
- [ ] Mettre en place des **tests automatisés** avant chaque déploiement
- [ ] **Backup automatique** Supabase (vérifier et activer les backups Supabase Pro)
- [ ] **CDN** pour les assets et PDFs (Cloudflare ou Supabase Storage CDN)

### Contenu

- [ ] Compléter les **2 336 résumés arabes manquants**
- [ ] Remplacer les **6 896 résumés génériques Adala** par de vrais résumés IA
- [ ] Ajouter des **descriptions pour chaque domaine** (actuellement vides pour certains)
- [ ] Enrichir la base avec des **textes de jurisprudence**

### Sécurité

- [ ] **Rotation des clés API** tous les 6 mois (OpenRouter + Supabase service_role)
- [ ] **Audit RLS** : Tester les policies avec un compte utilisateur standard
- [ ] Activer les **Dependabot alerts** GitHub pour les dépendances vulnérables
- [ ] Mettre en place un **monitoring des erreurs** (Sentry ou similaire)

---

## Annexe — Ressources utiles

| Ressource | URL |
|-----------|-----|
| Supabase Dashboard | https://supabase.com/dashboard/project/bmargdbbcnhkrjeidmvh |
| OpenRouter Credits | https://openrouter.ai/settings/credits |
| Google Search Console | https://search.google.com/search-console |
| Hostinger hPanel | https://hpanel.hostinger.com |
| Vite Documentation | https://vitejs.dev/guide/ |
| Supabase Docs | https://supabase.com/docs |
| Tailwind CSS Docs | https://tailwindcss.com/docs |

---

*Documentation générée le 17 Juin 2026 — JuriThèque v2.0*

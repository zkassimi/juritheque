# Audit du projet existant

Audit realise en lecture seule dans le projet `lexbase`. Aucun fichier existant
n'a ete modifie.

## Stack observee

- Frontend : Vite, React 18, React Router, Tailwind, lucide-react.
- Backend/data : Supabase, table principale `laws`, migrations SQL dans
  `lexbase/supabase/migrations`.
- Pipeline : Python, scripts dans `lexbase/pipeline`.
- PDF : `pdfplumber`, PyMuPDF (`fitz`), OCR optionnel via `pytesseract` et
  `pdf2image` dans `extract.py`.
- IA : Anthropic/OpenRouter selon les scripts.
- Recherche interne : table `site_search_index`, FTS Supabase, pages SEO guide.

Fichiers principaux consultes :

- `lexbase/package.json`
- `lexbase/pipeline/extract.py`
- `lexbase/pipeline/crawl_sgg.py`
- `lexbase/pipeline/crawl_adala.py`
- `lexbase/pipeline/import_from_queue.py`
- `lexbase/pipeline/enrich.py`
- `lexbase/pipeline/score_utils.py`
- `lexbase/pipeline/detect_title_mismatches.py`
- `lexbase/pipeline/fix_imported_titles.py`
- `lexbase/pipeline/run_pipeline.py`
- `lexbase/src/lib/api.js`
- `lexbase/src/pages/LawDetail.jsx`
- `lexbase/src/pages/Admin.jsx`
- `lexbase/supabase/migrations/001_lexbase_schema.sql`
- `lexbase/supabase/migrations/008_enrichment_fields.sql`
- `lexbase/supabase/migrations/010_sources_and_bulletins.sql`
- `lexbase/supabase/migrations/011_slug_history.sql`
- `lexbase/supabase/migrations/018_clean_canonical_slugs.sql`
- `lexbase/supabase/migrations/019_verification_status.sql`
- `lexbase/supabase/migrations/020_import_queue_rls.sql`
- `lexbase/supabase/migrations/021_confidence_scores.sql`

## Structure fonctionnelle

La table `laws` contient deja les champs essentiels :

- identite juridique : `number`, `type`, `date`, `status`, `domain_id`,
  `title_fr`, `title_ar`;
- contenu : `content_fr`, `content_ar`, `pdf_url`, `source_url`;
- enrichissement : `simple_summary_fr`, `simple_summary_ar`,
  `table_of_contents_fr`, `important_articles`, `legal_keywords`;
- SEO : `canonical_slug`, `seo_title_fr`, `seo_description_fr`,
  `is_publicly_indexable`;
- qualite : `extraction_confidence_score`, `extraction_status`,
  `needs_human_review`, `verification_status`;
- pipeline : `source_confidence`, `metadata_score`, `duplicate_score`,
  `legal_status_score`, `summary_score`, `seo_score`,
  `global_confidence_score`, `pipeline_mode`, `pipeline_notes`.

La base possede donc deja une bonne fondation. La proposition doit completer,
pas remplacer.

## Pipeline PDF et sources

### `extract.py`

`extract.py` traite des PDF locaux :

- extraction texte avec `pdfplumber` sur les 30 premieres pages ;
- fallback PyMuPDF si moins de 200 caracteres ;
- OCR optionnel si PDF scanne ;
- split FR/AR heuristique ;
- appel IA pour metadonnees ;
- upload Supabase Storage ;
- insertion ou patch en DB.

Point fort : OCR et fallback existent deja.

Risque : le prompt d'extraction produit directement `number`, `type`, `date`,
`title_fr`, `title_ar`. Il manque une phase explicite de confrontation avec la
premiere page du PDF, la fiche source et les regles juridiques marocaines.

### `crawl_sgg.py`

`crawl_sgg.py` decouvre les PDF SGG, les telecharge, extrait le texte avec
PyMuPDF, detecte numero/type/date depuis l'URL, le fichier ou le titre, puis
insere dans `laws`.

Point fort : SGG est une source officielle forte et les noms de fichiers sont
utilises comme signal stable.

Risque : le type et le numero peuvent etre derives du fichier alors que le PDF
contient parfois un dahir de promulgation, une loi promulguee et une date de BO.
Ces trois niveaux doivent etre separes.

### `crawl_adala.py`

`crawl_adala.py` scrape les fiches Adala et insere de nombreux textes en
`metadata_only`. Les PDF restent souvent externes via `source_url`. Les lignes
sont marquees avec `extraction_confidence_score` bas et `needs_human_review`.

Point fort : couverture large.

Risque : une fiche HTML peut etre moins fiable qu'un PDF officiel pour titre,
type, numero et date. Il faut comparer fiche et PDF avant enrichissement.

### `import_from_queue.py`

Lit `import_queue`, telecharge les PDF, extrait PyMuPDF, uploade vers Storage,
insere `laws`, puis applique `score_utils`.

Point fort : architecture semi-automatisee deja presente.

Risque : extraction PDF sans OCR dans ce script, et `extraction_status` peut
etre `pending` au moment ou les scores/decisions se calculent. Le moteur
canonique doit etre insere avant la decision de publication.

### `enrich.py`

Calcule `extraction_confidence_score`, articles, mots-cles, TOC, resumes,
champs SEO, slug canonique et scores globaux.

Point fort : enrichissement complet et protections contre l'ecrasement manuel.

Risque majeur : SEO, slug et resume peuvent etre generes sur des metadonnees
juridiques non encore arbitrees.

## Frontend public

### `LawDetail.jsx`

La page detail :

- resout par `canonical_slug`, ID, `slug_history`, fallback `number`;
- affiche titre, type, statut, source, PDF, TOC, articles importants, resumes ;
- utilise `pdf_url || source_url` ;
- genere SEO via `useSEO` et JSON-LD ;
- masque certains resumes generiques ;
- affiche un badge qualite selon `extraction_confidence_score`.

Point fort : bonne experience utilisateur et fallback PDF.

Risque : la page peut donner une apparence de fiabilite a un texte dont les
metadonnees fondamentales n'ont pas ete validees.

### `Admin.jsx`

L'admin contient deja :

- tableau de bord ;
- textes juridiques ;
- veille et import queue ;
- qualite ;
- pipeline ;
- signalements ;
- edition manuelle de certains champs.

Point fort : beaucoup de briques pour une future revue humaine existent deja.

Risque : la qualite mesure surtout presence de donnees, scores et pipeline. Il
manque une vue explicite "controle juridique" : fiche vs PDF, type, numero,
date, source officielle, decision et justification.

## Migrations existantes utiles

- `008_enrichment_fields.sql` ajoute resumes, TOC, important articles, SEO,
  `canonical_slug`, extraction confidence, review flags.
- `010_sources_and_bulletins.sql` ajoute `source_name`, `source_url`,
  `bo_number`, `bo_date`.
- `011_slug_history.sql` garde les anciens slugs.
- `018_clean_canonical_slugs.sql` corrige certains slugs hash/Adala.
- `019_verification_status.sql` ajoute `verification_status`,
  `effective_from`, `effective_to`, `replaces_id`.
- `021_confidence_scores.sql` ajoute scores multidimensionnels et
  `pipeline_runs`.

## Diagnostic synthetique

Le systeme est techniquement avance, mais l'autorite juridique est dispersee.
Les scripts savent extraire, enrichir et corriger, mais aucune couche centrale
ne dit : "voici l'identite officielle du texte, avec preuve et score".

Le bon chantier est donc une couche canonique non destructive, construite sur
les champs existants et ajoutee avant :

1. generation de slug ;
2. generation de resume ;
3. generation SEO ;
4. publication/indexation ;
5. exposition RAG.


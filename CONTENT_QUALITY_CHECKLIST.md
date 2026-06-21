# Checklist qualité du contenu — JuriThèque

_Dernière mise à jour : Juin 2026_

## Pour chaque guide thématique (`seoIntentPages.js`)

### Champs obligatoires
- [ ] `lastUpdated` — mois/année de dernière vérification
- [ ] `slug` — unique, en français, kebab-case
- [ ] `title` — 50-60 caractères, contient le mot-clé principal
- [ ] `metaDescription` — 140-155 caractères, appel à l'action implicite
- [ ] `h1` — différent du title, naturel à la lecture
- [ ] `intro` — 2-3 phrases, résume l'utilité de la page
- [ ] `legalDomain` — correspond à un domaine existant en DB Supabase
- [ ] `keywords[]` — 6-10 mots-clés naturels, longue traîne incluse
- [ ] `searchTerms[]` — 2-4 termes pour requêtes Supabase
- [ ] `relatedSlugs[]` — au moins 2 guides proches
- [ ] `faq[]` — au moins 2 questions pertinentes

### Champs recommandés
- [ ] `sections[]` — contenu éditorial riche (800+ mots au total)
- [ ] `specificNumbers[]` — numéros de lois ciblées
- [ ] `featuredVideoIds[]` — si une vidéo YouTube correspond

### Règles de contenu
- [ ] Ne jamais inventer de règles juridiques
- [ ] Toujours orienter vers les textes officiels ou l'assistant IA
- [ ] Les FAQ doivent répondre à de vraies questions de recherche
- [ ] L'intro ne doit pas dupliquer la metaDescription mot pour mot

---

## Pour chaque texte juridique (pipeline Python)

### Données obligatoires
- [ ] `title_fr` ou `title_ar` — non vide
- [ ] `type` — Loi | Dahir | Décret | Arrêté | Circulaire | Code | Règlement
- [ ] `status` — En vigueur | Abrogé | Modifié
- [ ] `domain_id` — domaine valide
- [ ] `source_name` — nom lisible de la source
- [ ] `source_url` — URL officielle du texte

### Données recommandées
- [ ] `number` — numéro du texte (ex: "103-12")
- [ ] `date` — date de publication
- [ ] `content_fr` — texte extrait du PDF (pour la recherche full-text)
- [ ] `simple_summary_fr` — résumé court (150-250 mots)
- [ ] `doc_url` — lien direct vers le PDF officiel

---

## Contrôle qualité mensuel

1. **Vérifier les textes "Abrogés"** — mettre à jour le statut si nécessaire
2. **Tester les liens PDF** — s'assurer que `doc_url` est toujours accessible
3. **Relire les FAQ** — actualiser si la législation a changé
4. **Mettre à jour `lastUpdated`** dans `seoIntentPages.js`
5. **Vérifier les erreurs 404** dans Google Search Console
6. **Contrôler le sitemap** — nouvelles lois incluses ?

---

## Avertissements à ne jamais supprimer

Les mentions suivantes doivent toujours être présentes :

1. **Sur les guides** : "Ce guide est fourni à titre informatif uniquement. Il ne constitue pas un conseil juridique."
2. **Sur la page Méthodologie** : "Seul le texte officiel fait référence juridique."
3. **Sur À propos** : Avertissement sur la nature documentaire (non-conseil)
4. **Sur les synthèses** : "En cas de divergence, c'est le texte officiel qui prévaut."

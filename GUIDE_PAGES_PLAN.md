# Plan des pages guides — JuriThèque

_Dernière mise à jour : Juin 2026_

## Architecture actuelle

Les 20 guides thématiques sont définis dans `src/data/seoIntentPages.js`.
Chaque entrée supporte les champs suivants :

```js
{
  lastUpdated:     '2026-06',    // affiché sous le H1
  slug:            '...',        // URL : /fr/guides/:slug
  category:        '...',        // regroupement thématique
  title:           '...',        // <title> SEO
  metaDescription: '...',        // <meta description>
  h1:              '...',        // Titre visible H1
  intro:           '...',        // Paragraphe d'intro
  legalDomain:     '...',        // FK domaine Supabase
  keywords:        [...],        // Tags affichés + SEO
  searchTerms:     [...],        // Termes de recherche Supabase
  specificNumbers: [...],        // Numéros de lois ciblés
  relatedSlugs:    [...],        // Guides proches
  featuredVideoIds:[...],        // YouTube IDs prioritaires
  sections:        [...],        // Contenu éditorial riche (optionnel)
  faq:             [...],        // Questions/réponses (FAQPage JSON-LD)
}
```

## Rendu par SEOIntentPage.jsx

1. **En-tête** : fil d'Ariane, H1, date, intro, mots-clés
2. **Sections éditoriales** : prose longue depuis `sections[]` (si renseigné)
3. **Textes liés** : 3 stratégies Supabase (numéros, keywords, domaine)
4. **FAQ** accordéon + FAQPage JSON-LD
5. **Disclaimer juridique** ⚠️
6. **Vidéos pédagogiques** (si disponibles en DB)
7. **CTA** : IA + Base de données
8. **Guides proches** (depuis `relatedSlugs`)
9. **Signaler une erreur**

## Guides à enrichir en priorité (sections manquantes)

Les guides MRE ont des `sections[]` complètes.
Les guides travail/commercial/civil/famille manquent de sections éditoriales riches.

| Guide | sections[] | Priorité |
|-------|-----------|----------|
| code-du-travail-maroc | ❌ absent | 🔴 haute |
| code-de-la-famille-maroc | ❌ absent | 🔴 haute |
| divorce-maroc | ❌ absent | 🟠 moyenne |
| creation-societe-maroc | ❌ absent | 🟠 moyenne |
| procedure-civile-maroc | ❌ absent | 🟡 faible |

## Ajouter un nouveau guide

1. Ajouter l'entrée dans `SEO_INTENT_PAGES` dans `seoIntentPages.js`
2. Ajouter le `slug` dans `public/sitemap.xml`
3. Créer les liens depuis `relatedSlugs` des guides proches
4. Vérifier que `legalDomain` correspond à un domaine existant en DB

# Plan de maillage interne — JuriThèque

_Dernière mise à jour : Juin 2026_

## Maillage actuel (en place)

### Guide → Textes juridiques
- Chaque guide charge dynamiquement les textes liés via `getRelatedLawsForIntent()`
- 3 stratégies : numéros de loi (`specificNumbers`), termes (`searchTerms`), domaine (`legalDomain`)

### Guide → Guides proches
- `relatedSlugs[]` dans chaque entrée de `seoIntentPages.js`
- Rendu : section "Guides proches" en bas de chaque guide

### Guide → Domaine
- Lien "Tous les textes du domaine" → `/domaine/:legalDomain`
- Lien "Veille juridique liée" → `/fr/veille-juridique?domain=...`

### Domaine → Guides
- `getGuidesForDomain(slug)` — section "Guides liés à ce domaine"
- Filtre sur `category` ou `legalDomain` correspondant

### Domaine → Base
- Lien "Filtrer dans la base" → `/base?domain=:slug`

### Texte juridique → Domaine
- LawCard inclut le domaine (lien implicite via navigation)

---

## Matrice de maillage inter-guides

| Domaine | Guides liés |
|---------|-------------|
| travail | code-du-travail-maroc ↔ licenciement-maroc ↔ procedure-civile-maroc |
| commercial | code-de-commerce-maroc ↔ sarl-maroc ↔ bail-commercial-maroc ↔ creation-societe-maroc ↔ recouvrement-maroc ↔ cheque-sans-provision-maroc |
| civil | code-de-la-famille-maroc ↔ divorce-maroc ↔ delai-de-prescription-maroc ↔ procedure-civile-maroc |
| collectivites | collectivites-territoriales-maroc ↔ revocation-elu-maroc |
| MRE | mre-droits-juridiques-maroc ↔ heritage-succession-mre-maroc ↔ investir-maroc-mre ↔ achat-immobilier-maroc-mre ↔ double-nationalite-droit-maroc |

---

## Opportunités de maillage à développer

### 1. Texte juridique → Guide thématique
Actuellement : aucun lien depuis la page d'un texte vers le guide correspondant.
**À faire** : dans `LawDetail.jsx`, détecter le domaine et suggérer le guide correspondant.
```jsx
// Exemple : si law.domain_id === 'travail', afficher lien vers
// /fr/guides/code-du-travail-maroc
```

### 2. Page d'accueil → Guides
Les guides ne sont pas mis en avant en page d'accueil.
**À faire** : ajouter une section "Guides populaires" avec 3-4 guides phares.

### 3. Veille juridique → Guides
Les articles de veille pourraient pointer vers les guides correspondants.

### 4. Glossaire → Guides
Les termes juridiques du glossaire pourraient linker vers les guides thématiques.

---

## Règles de maillage à respecter

- Maximum 5-6 liens par page vers d'autres pages internes (hors navigation)
- Ancre descriptive et contextuelle (pas de "cliquez ici")
- Toujours linker vers la page la plus pertinente, pas la plus proche dans le code
- Ne pas créer de liens circulaires directs (A → B → A)

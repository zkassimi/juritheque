# Stratégie SEO — JuriThèque

_Dernière mise à jour : Juin 2026_

## Objectif

Positionner JuriThèque comme la référence numérique francophone et arabophone pour le droit marocain en ligne, en capitalisant sur :
- Le volume de textes officiels (7 400+ textes, 11 sources, 16 domaines)
- La spécificité thématique (droit marocain uniquement)
- Le bilinguisme FR/AR avec RTL

---

## Architecture SEO en place

### Contenu
- **Sitemap XML** (`public/sitemap.xml`) — 44 000+ URLs générées
- **20 guides thématiques** (`/fr/guides/:slug`) — intro, FAQ, textes liés, JSON-LD
- **16 pages domaines** (`/domaine/:slug`) — lois paginées, guides liés, FAQ
- **Pages institutionnelles** : Méthodologie, Mentions légales, Confidentialité, À propos, Contact

### Technique
- **JSON-LD** : 7 types (WebSite, Organization, Legislation, FAQPage, Dataset, BreadcrumbList, CollectionPage)
- **Meta tags** : title, description, canonical, OG, Twitter Card — via `useSEO()` hook
- **robots.txt** : crawl rules configurées
- **Performance** : Vite SPA, lazy loading, code splitting

---

## Intentions de recherche ciblées (20 guides)

| Slug | Domaine | Volume estimé |
|------|---------|---------------|
| code-du-travail-maroc | travail | élevé |
| licenciement-maroc | travail | élevé |
| code-de-commerce-maroc | commercial | élevé |
| sarl-maroc | commercial | moyen |
| bail-commercial-maroc | commercial | moyen |
| creation-societe-maroc | commercial | élevé |
| recouvrement-maroc | commercial | moyen |
| cheque-sans-provision-maroc | penal | moyen |
| code-de-la-famille-maroc | civil | élevé |
| divorce-maroc | civil | élevé |
| delai-de-prescription-maroc | civil | moyen |
| procedure-civile-maroc | civil | moyen |
| collectivites-territoriales-maroc | collectivites | faible |
| revocation-elu-maroc | collectivites | faible |
| mre-droits-juridiques-maroc | civil | moyen |
| heritage-succession-mre-maroc | civil | moyen |
| investir-maroc-mre | commercial | moyen |
| achat-immobilier-maroc-mre | civil | élevé |
| double-nationalite-droit-maroc | civil | moyen |
| investissement-etranger-maroc | commercial | moyen |

---

## Signaux E-E-A-T implémentés

- [x] Page "Méthodologie" avec liste des 11 sources officielles
- [x] Page "À propos" avec mission et valeurs
- [x] Disclaimer juridique sur chaque guide
- [x] "Dernière mise à jour" visible sur les guides
- [x] Lien vers source officielle sur chaque texte
- [x] JSON-LD Organization avec URL canonique

---

## Axes de croissance à prioriser

1. **Création de contenu** : enrichir les `sections[]` des 20 guides (prose longue, 800+ mots)
2. **Backlinking** : partenariats universités droit marocain, associations juridiques
3. **YouTube → Site** : liens depuis descriptions vidéo vers guides correspondants
4. **Core Web Vitals** : audit Lighthouse régulier post-déploiement
5. **Jurisprudence** : section future — fort potentiel de long-tail (noms d'arrêts, numéros de décisions)

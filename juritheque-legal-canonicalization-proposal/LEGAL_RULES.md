# Regles juridiques de canonicalisation

Ces regles guident le moteur. Elles ne remplacent pas une validation humaine
pour les textes ambigus.

## Regle 1 - Dahir de promulgation vs loi promulguee

Un document peut avoir :

- un dahir qui promulgue une loi ;
- une loi avec son propre numero ;
- un titre usuel de loi ou de code.

Exemple conceptuel :

- `Dahir n 1-24-XX du ... portant promulgation de la loi n 59-24 ...`

Dans ce cas :

- `formal_instrument_type = "Dahir"`
- `dahir_number = "1-24-XX"`
- `subject_text_type = "Loi"`
- `law_number = "59-24"`
- `official_number` depend de la fiche publique choisie :
  - si la page represente la loi : `59-24` ;
  - si la page represente l'acte de promulgation : `1-24-XX`.

Recommandation JuriTheque : pour les pages grand public, privilegier la loi
promulguee si le document est principalement consulte comme loi. Garder le
dahir dans un champ dedie.

## Regle 2 - "Code" n'est pas toujours un type formel

`Code du travail`, `Code de la famille`, `Code penal`, etc. sont souvent des
titres usuels ou consolidations. Le type formel peut etre `Loi` ou `Dahir`.

Decision :

- `type` public peut rester `Code` si c'est utile UX/SEO.
- `formal_instrument_type` doit garder le type juridique publie.
- `subject_text_type` peut etre `Code` si le texte codifie un code.

## Regle 3 - Numeros separes

Ne pas melanger :

- numero de dahir ;
- numero de loi ;
- numero de decret ;
- numero BO ;
- numero de fichier/fiche.

Champs cibles :

- `dahir_number`
- `law_number`
- `decree_number`
- `official_number`
- `bo_number`

## Regle 4 - Dates separees

Ne pas melanger :

- date de signature ;
- date de promulgation ;
- date de publication au BO ;
- date d'entree en vigueur ;
- date d'abrogation.

Champs cibles :

- `signature_date`
- `law_date`
- `bo_publication_date`
- `legal_effective_date_detected`
- `effective_from`
- `effective_to`

Le champ existant `date` peut rester la date principale affichee, mais le moteur
doit documenter pourquoi elle est choisie.

## Regle 5 - Priorite PDF officiel

Si le PDF officiel contredit une fiche HTML :

- le PDF gagne pour titre, type, numero, date et BO ;
- la fiche HTML reste en evidence secondaire ;
- le diff doit etre conserve.

Exception : si le PDF est illisible ou incomplet, la fiche peut etre retenue
avec statut `metadata_only` ou `low_confidence`.

## Regle 6 - Premiere page prioritaire

La premiere page et les premieres lignes ont un poids fort pour :

- type ;
- numero ;
- titre ;
- date ;
- BO.

Le reste du texte sert surtout a confirmer articles, TOC, resume et domaine.

## Regle 7 - Titre officiel vs titre SEO

Le titre officiel ne doit pas etre raccourci pour SEO.

Separations :

- `official_title_fr/ar` : titre officiel complet ;
- `title_fr/ar` : titre public compatible ;
- `seo_title_fr/ar` : version SEO courte ;
- `canonical_slug` : slug stable.

## Regle 8 - Publication prudente

Si un texte est `metadata_only`, sans PDF analyse, ou avec conflit critique :

- pas de correction automatique ;
- `needs_human_review = true` ;
- `canonical_validation_status` au plus `low_confidence` ;
- SEO/RAG limite ou noindex selon gravite.

## Regle 9 - Corrections humaines protegees

Tout champ modifie manuellement doit etre protege :

- ne pas ecraser sans `force`;
- afficher le diff dans la review ;
- enregistrer `reviewer_id`, date et justification.

## Regle 10 - Slug stable et redirections

Si le slug change apres canonicalisation :

- ajouter l'ancien slug a `slug_history` ;
- redirection par `fetchLawBySlug()` deja compatible ;
- regenerer sitemap seulement apres validation.


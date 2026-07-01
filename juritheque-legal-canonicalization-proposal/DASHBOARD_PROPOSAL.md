# Proposition dashboard admin

Nouvelle section : `Controle qualite juridique`.

Elle peut s'ajouter a `Admin.jsx`, qui possede deja `Qualite`, `Pipeline`,
`Veille & Import` et `Signalements`.

## Navigation proposee

Onglets :

- `A verifier`
- `Conflits critiques`
- `Metadata only`
- `Corrections sures`
- `Historique audits`
- `Sources manquantes`

## Cartes statistiques

- textes verifies ;
- textes non verifies ;
- conflits critiques ;
- metadata_only publics ;
- corrections auto possibles ;
- textes bloques SEO/RAG ;
- slugs a regenerer ;
- PDF manquants.

## Table principale

Colonnes :

- priorite ;
- loi ;
- source ;
- score canonique ;
- flags ;
- champ critique ;
- statut review ;
- derniere analyse ;
- actions.

Filtres :

- source (`SGG`, `Adala`, `BO`, `Storage`) ;
- statut validation ;
- score ;
- flag ;
- type ;
- domaine ;
- public/indexable ;
- avec/sans PDF.

## Vue detail review

Sections :

1. Resume du probleme.
2. Metadonnees actuelles.
3. Metadonnees proposees.
4. Preuves PDF/source.
5. Diff champ par champ.
6. Impact SEO/RAG.
7. Actions.

## Actions rapides

- approuver proposition ;
- approuver partiellement ;
- garder existant ;
- marquer source manquante ;
- ouvrir page publique ;
- ouvrir PDF ;
- copier reference officielle ;
- regenerer slug apres validation ;
- envoyer au pipeline enrichissement.

## Integration avec vues existantes

- `Qualite` reste une vue de completude technique.
- `Pipeline` reste une vue d'execution et scores.
- `Controle qualite juridique` devient la vue d'autorite juridique.
- `Signalements` peut creer automatiquement un item de review si un utilisateur
  signale "texte obselete", "PDF casse", "erreur de titre" ou "traduction".

## Regles UX

- Ne jamais cacher la preuve.
- Mettre les differences critiques en haut.
- Afficher les dates avec labels explicites : signature, BO, entree en vigueur.
- Ne pas utiliser "verified" si seule une inference IA existe.
- Permettre une decision en moins de deux minutes pour les cas simples.


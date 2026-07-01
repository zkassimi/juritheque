# File de revue humaine juridique

La file de revue humaine doit transformer un probleme technique en decision
editoriale simple : accepter, rejeter, demander une source, ou garder l'existant.

## Objectifs

- Montrer les metadonnees actuelles.
- Montrer les metadonnees proposees.
- Montrer les preuves : PDF page 1, fiche source, URL, extrait.
- Expliquer les flags.
- Permettre une decision rapide et auditable.

## Champs d'un item

| Champ | Description |
| --- | --- |
| `id` | identifiant review |
| `law_id` | texte concerne |
| `audit_id` | audit source |
| `priority` | 1 urgent, 5 bas |
| `status` | `pending`, `in_review`, `approved`, `rejected`, `needs_source` |
| `reason` | phrase courte expliquant le probleme |
| `flags` | liste des flags |
| `current_metadata` | valeurs DB actuelles |
| `proposed_metadata` | valeurs proposees |
| `evidence` | preuves par champ |
| `assigned_to` | reviewer affecte |
| `reviewed_by` | validateur |
| `reviewed_at` | date validation |
| `resolution_notes` | justification humaine |

## Priorites

Priorite 1 :

- page publique indexee avec numero ou type faux ;
- texte tres consulte ;
- conflit critique PDF vs DB ;
- doublon de numero avec titres differents.

Priorite 2 :

- metadata_only publie ;
- PDF absent mais source officielle disponible ;
- slug public trompeur.

Priorite 3 :

- date incertaine ;
- BO absent ;
- titre trop long ou peu propre.

Priorite 4-5 :

- ameliorations SEO ;
- champs non critiques.

## Actions disponibles

- `approve_patch` : appliquer les champs proposes.
- `approve_partial` : choisir seulement certains champs.
- `keep_current` : garder l'existant, marquer comme justifie.
- `reject_patch` : rejeter la proposition.
- `needs_source` : demander PDF/source officielle.
- `merge_duplicate` : envoyer vers un futur workflow de fusion.
- `mark_verified` : mettre `verification_status=verified` apres controle.
- `mark_low_confidence` : conserver mais limiter SEO/RAG.

## Affichage recommande

Pour chaque item :

- en-tete : type, numero, titre actuel, source ;
- score canonique ;
- badges flags ;
- comparaison en colonnes :
  - champ ;
  - actuel ;
  - propose ;
  - preuve ;
  - action ;
- visualisation PDF page 1 ;
- lien source officielle ;
- historique des changements.

## Protections

- Une action appliquee doit creer un audit.
- Les anciens slugs doivent etre conserves.
- Les champs manuels ne sont jamais ecrases sans confirmation explicite.
- Les actions destructives doivent etre absentes de cette interface.


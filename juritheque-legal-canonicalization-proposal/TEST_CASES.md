# Cas de test

Les tests ci-dessous sont des cas metier. Ils doivent etre implementes plus tard
en unit tests et integration tests autour du moteur canonique.

## Test 1 - Dahir promulguant une loi

Entree :

- record DB : `type = "Loi"`, `number = "59-24"`;
- PDF page 1 : mentionne un dahir de promulgation et une loi n 59-24.

Attendu :

- `formal_instrument_type = "Dahir"`;
- `subject_text_type = "Loi"`;
- `law_number = "59-24"`;
- `dahir_number` renseigne si detecte ;
- pas de confusion numero dahir / numero loi ;
- review si le champ public `type` doit changer.

## Test 2 - Fiche Adala metadata_only avec PDF disponible

Entree :

- record Adala avec `extraction_status = "metadata_only"`;
- `source_url` pointe vers un PDF officiel ;
- `title_ar` existe, `title_fr` est generique.

Attendu :

- tentative extraction PDF ;
- titre officiel recupere depuis PDF si possible ;
- `metadata_only` leve seulement si texte PDF suffisant ;
- sinon `canonical_validation_status = "metadata_only"` ;
- `needs_human_review = true`.

## Test 3 - Titre fiche different du titre PDF

Entree :

- `title_fr` DB parle du texte A ;
- PDF page 1 parle du texte B ;
- numero identique ou ambigu.

Attendu :

- flag `title_mismatch_pdf_vs_record` ;
- severite `critical` ;
- aucune correction auto ;
- item review priorite 1 ou 2.

## Test 4 - Code comme titre, pas comme instrument

Entree :

- `title_fr = "Code du travail"` ;
- PDF mentionne `Loi n 65-99` promulguee par dahir.

Attendu :

- `subject_text_type = "Code"` ou `Loi` selon convention validee ;
- `formal_instrument_type = "Dahir"` si le PDF est le dahir ;
- `law_number = "65-99"` ;
- `official_title_fr` conserve le titre officiel complet ;
- `seo_title_fr` peut rester court, mais derive apres validation.

## Test 5 - Date BO vs date signature

Entree :

- `date` DB = date de publication BO ;
- PDF page 1 indique une date de signature differente ;
- `bo_date` existe.

Attendu :

- `signature_date` et `bo_publication_date` separes ;
- flag `bo_date_confused_with_signature_date` si `date` est ambigu ;
- pas de changement auto du champ public sans validation.

## Test 6 - PDF scanne

Entree :

- PyMuPDF extrait moins de 200 caracteres ;
- PDF officiel disponible.

Attendu :

- OCR page 1 declenche ;
- si OCR reussit, parser premiere page ;
- sinon `ocr_needed`, `low_extraction_text`, review.

## Test 7 - Slug hash ou generique

Entree :

- `canonical_slug = "adala-1efb9bc5"` ou equivalent ;
- identite canonique verifiee.

Attendu :

- nouveau slug propose base sur type, numero et mots significatifs ;
- ancien slug ajoute a `slug_history` ;
- sitemap regenere seulement apres validation.

## Test 8 - Champ manuel protege

Entree :

- `summary_updated_manually = true` ou futur champ manuel equivalent ;
- patch propose touche une valeur modifiee manuellement.

Attendu :

- flag `manual_field_conflict` ;
- pas d'auto-update ;
- review obligatoire.

## Test 9 - SEO genere avant validation

Entree :

- `seo_title_fr` existe ;
- `canonical_validation_status` absent ou faible ;
- le moteur detecte un titre officiel different.

Attendu :

- flag `seo_generated_before_validation` ;
- SEO marque stale ;
- recalcul seulement apres validation.

## Test 10 - Doublon numero officiel

Entree :

- deux records avec meme `law_number` mais titres differents ;
- sources officielles differentes ou incoherentes.

Attendu :

- flag `duplicate_official_number` ;
- review et eventuel workflow de fusion ;
- aucune suppression automatique.


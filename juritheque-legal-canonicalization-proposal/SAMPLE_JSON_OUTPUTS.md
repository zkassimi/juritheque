# Exemples de sorties JSON

Les fichiers JSON valides correspondants sont dans `examples/`.

## `canonical_legal_record`

```json
{
  "law_id": 123,
  "canonical_validation_status": "high_confidence",
  "canonical_confidence_score": 92,
  "official_title_fr": "Loi n 59-24 relative a un dispositif de soutien",
  "official_title_ar": "[titre arabe officiel extrait du PDF]",
  "formal_instrument_type": "Dahir",
  "subject_text_type": "Loi",
  "official_number": "59-24",
  "dahir_number": "1-24-00",
  "law_number": "59-24",
  "signature_date": "2024-12-01",
  "bo_number": "7350",
  "bo_publication_date": "2024-12-12",
  "source_priority": "pdf_page_1",
  "evidence": [
    {
      "field": "law_number",
      "value": "59-24",
      "source": "pdf_page_1",
      "page": 1,
      "quote": "Loi n 59-24"
    }
  ]
}
```

## `metadata_diff_report`

```json
{
  "law_id": 123,
  "diffs": [
    {
      "field": "type",
      "current_value": "Loi",
      "proposed_value": "Dahir",
      "severity": "critical",
      "action": "review",
      "reason": "Le PDF officiel identifie l'instrument formel comme Dahir."
    }
  ],
  "safe_to_auto_update": false
}
```

## `human_review_item`

```json
{
  "law_id": 123,
  "priority": 1,
  "reason": "Type formel et numero potentiellement confondus",
  "flags": ["type_mismatch_pdf_vs_record", "law_number_dahir_number_confused"],
  "status": "pending"
}
```

## `consistency_audit_result`

```json
{
  "law_id": 123,
  "score": 68,
  "decision": "review",
  "flags": [
    {
      "code": "type_mismatch_pdf_vs_record",
      "severity": "critical",
      "message": "Le type DB ne correspond pas au type detecte dans le PDF."
    }
  ],
  "blocking": false,
  "auto_update_allowed": false
}
```


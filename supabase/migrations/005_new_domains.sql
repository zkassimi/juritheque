-- ============================================================
-- Migration 005 — Nouveaux domaines : Finances publiques & Bancaire
-- ============================================================
-- Ajoute deux nouveaux domaines juridiques :
--   • finances_publiques  → LOF, CGI, lois de finances, marchés publics
--   • bancaire            → Loi bancaire, circulaires BAM, banque participative

insert into public.domains (id, name_fr, name_ar, icon, law_count, sub_domains)
values
  (
    'finances_publiques',
    'Finances Publiques',
    'المالية العامة',
    'BarChart2',
    0,
    '{"Loi de finances","Budget de l''État","Marchés publics","Comptabilité publique","Fiscalité"}'
  ),
  (
    'bancaire',
    'Droit Bancaire & Financier',
    'القانون البنكي والمالي',
    'CreditCard',
    0,
    '{"Loi bancaire","Banque participative","Microfinance","Systèmes de paiement","Réglementation BAM"}'
  )
on conflict (id) do update
  set
    name_fr     = excluded.name_fr,
    name_ar     = excluded.name_ar,
    icon        = excluded.icon,
    sub_domains = excluded.sub_domains;

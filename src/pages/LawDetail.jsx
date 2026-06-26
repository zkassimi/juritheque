import { useEffect, useState } from 'react'
import { useParams, Link, useNavigate, useLocation } from 'react-router-dom'
import {
  ChevronRight, Download, Share2, Heart, Bot, FileText, Calendar, Tag, Eye,
  ExternalLink, AlertTriangle, CheckCircle, ChevronDown, ChevronUp, BookOpen,
  Award, Sparkles, Hash, Bell, Flag, ArrowRight, RotateCcw
} from 'lucide-react'
import ReportModal from '../components/ReportModal'
import { LAW_TYPES } from '../data/mockData'
import { useLang } from '../contexts/LangContext'
import { useAuth } from '../contexts/AuthContext'
import { fetchLawBySlug, fetchRelatedLaws, fetchDomainById, fetchLawRelations } from '../lib/api'
import { lawPath, lawCanonical, getSourceSiteUrl, getSourceLabel } from '../lib/lawUtils'
import StatusBadge from '../components/ui/StatusBadge'
import TypeBadge from '../components/ui/TypeBadge'
import RTLWrapper from '../components/ui/RTLWrapper'
import LawCard from '../components/LawCard'
import { SkeletonText } from '../components/ui/SkeletonLoader'
import { useSEO } from '../hooks/useSEO'
import JsonLD, { legalDocumentSchema, breadcrumbSchema, faqSchema } from '../components/JsonLD'
import { getGuidesForDomain } from '../data/seoIntentPages'

// ── Quality badge helper ──────────────────────────────────────────────────────
function QualityBadge({ score, status }) {
  if (score == null) return null
  const { lang } = useLang()
  const s = Number(score)
  const cfg = s >= 75
    ? { bg: 'bg-emerald-50 border-emerald-200 text-emerald-700', dot: 'bg-emerald-400', label: lang === 'ar' ? 'جودة جيدة' : 'Qualité bonne' }
    : s >= 45
      ? { bg: 'bg-amber-50 border-amber-200 text-amber-700', dot: 'bg-amber-400', label: lang === 'ar' ? 'جودة جزئية' : 'Qualité partielle' }
      : { bg: 'bg-red-50 border-red-200 text-red-700', dot: 'bg-red-400', label: lang === 'ar' ? 'للتحقق' : 'À vérifier' }
  return (
    <span className={`inline-flex items-center gap-1.5 text-xs font-medium px-2.5 py-1 rounded-full border ${cfg.bg}`}>
      <span className={`w-1.5 h-1.5 rounded-full flex-shrink-0 ${cfg.dot}`} />
      {cfg.label} — {Math.round(s)}/100
    </span>
  )
}

// ── TOC section parser ────────────────────────────────────────────────────────
function parseTOC(raw) {
  if (!raw) return null
  if (typeof raw === 'string') {
    try { return JSON.parse(raw) } catch { return null }
  }
  return raw
}

export default function LawDetail() {
  const { slug } = useParams()
  const navigate = useNavigate()
  const { pathname } = useLocation()
  const { t, lang, setLang } = useLang()

  // Synchroniser la langue depuis l'URL (/ar/loi/… → AR, /fr/loi/… → FR)
  useEffect(() => {
    const urlLang = pathname.startsWith('/ar/') ? 'ar' : 'fr'
    if (urlLang !== lang) setLang(urlLang)
  }, [pathname]) // eslint-disable-line react-hooks/exhaustive-deps
  const { user, toggleFavorite, isFavorite, addToHistory } = useAuth()
  const [loading, setLoading]         = useState(true)
  const [law, setLaw]                 = useState(null)
  const [domain, setDomain]           = useState(null)
  const [related, setRelated]         = useState([])
  const [notFound, setNotFound]       = useState(false)
  const [copied, setCopied]           = useState(false)
  const [showPdf, setShowPdf]         = useState(false)
  const [viewerError, setViewerError] = useState(false)
  const [showFullText, setShowFullText] = useState(false)
  const [reportOpen, setReportOpen]   = useState(false)
  const [relations, setRelations]     = useState({ replacedLaw: null, successorLaws: [] })

  const fav = user && law && isFavorite(law.id)

  // ── SEO dynamique — priorité aux champs enrichis ──────────────────────────

  // Title : [Type] n°[Numéro] — [sujet court] | JuriThèque
  // Priorité : champ seo_title enrichi → format structuré auto → fallback
  const seoTitle = (() => {
    if (!law) return 'Texte juridique marocain'
    if (lang === 'ar' && law.seo_title_ar) return law.seo_title_ar
    if (law.seo_title_fr) return law.seo_title_fr
    const type  = law.type  || ''
    const num   = law.number ? `n°${law.number}` : ''
    const sujet = (lang === 'ar' && law.title_ar ? law.title_ar : law.title_fr || law.title_ar || '').slice(0, 65).trim()
    const parts = [type, num].filter(Boolean).join(' ')
    return sujet ? `${parts} — ${sujet}` : parts || `Texte juridique n°${slug}`
  })()

  // Meta description : format structuré avec type, numéro, domaine, date
  // Priorité : champ seo_description enrichi → format auto → fallback
  const seoDesc = (() => {
    if (!law) return 'Consultez ce texte juridique marocain sur JuriThèque.'
    if (lang === 'ar' && law.seo_description_ar) return law.seo_description_ar
    if (law.seo_description_fr) return law.seo_description_fr
    // Format structuré depuis les données disponibles
    const type    = law.type || 'Texte juridique'
    const num     = law.number ? `n°${law.number}` : ''
    const dateStr = law.date ? `, publié le ${law.date}` : ''
    const domPart = domain?.name_fr ? ` en ${domain.name_fr}` : ' marocain'
    const resume  = law.simple_summary_fr ? ` ${String(law.simple_summary_fr).slice(0, 80)}...` : ''
    const desc    = resume
      ? `${type} ${num}${domPart}${dateStr}.${resume} Source officielle sur JuriThèque.`
      : `Consultez ${type} ${num}${domPart}${dateStr}. Résumé, source officielle et informations juridiques sur JuriThèque.`
    return desc.slice(0, 155)
  })()

  // ── Indexabilité SEO ──────────────────────────────────────────────────────
  // Une page est indexable si :
  //   1. Elle n'est pas explicitement bloquée (is_publicly_indexable !== false)
  //   2. Elle a du contenu minimal : un numéro OU un titre
  // Cas noindex légitimes : page vide, doublon explicite, test/admin
  const isPageIndexable = law
    ? (law.is_publicly_indexable !== false &&
       (law.number || law.title_fr || law.title_ar))
    : false

  const shouldNoIndex = law ? !isPageIndexable : false
  // Pendant le chargement → false (pas de noindex prématuré)

  useSEO({
    title:       seoTitle,
    description: seoDesc,
    canonical:   law ? lawPath(law) : `/loi/${slug}`,
    type:        'article',
    noindex:     shouldNoIndex,
    hreflang:    law ? [
      { lang: 'fr', url: lawPath(law, 'fr') },
      { lang: 'ar', url: lawPath(law, 'ar') },
    ] : undefined,
    article: law ? {
      publishedTime: law.date || undefined,
      section:       domain?.name_fr || undefined,
    } : undefined,
  })

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setNotFound(false)
    fetchLawBySlug(slug)
      .then(async data => {
        if (cancelled) return
        setLaw(data)
        if (data) {
          addToHistory(data)
          // Redirection 301 si l'URL utilise encore l'ancien ID numérique
          if (data.canonical_slug && slug !== data.canonical_slug) {
            navigate(`/loi/${data.canonical_slug}`, { replace: true })
            return
          }
          const [dom, rel, rels] = await Promise.all([
            data.domain_id ? fetchDomainById(data.domain_id).catch(() => null) : Promise.resolve(null),
            data.domain_id ? fetchRelatedLaws(data.domain_id, data.id, 3).catch(() => []) : Promise.resolve([]),
            fetchLawRelations(data.id, data.replaces_id).catch(() => ({ replacedLaw: null, successorLaws: [] })),
          ])
          if (!cancelled) { setDomain(dom); setRelated(rel); setRelations(rels) }
        }
        if (!cancelled) setLoading(false)
      })
      .catch(() => {
        if (!cancelled) { setNotFound(true); setLoading(false) }
      })
    return () => { cancelled = true }
  }, [slug])

  const handleShare = () => {
    navigator.clipboard.writeText(window.location.href)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  if (loading) return (
    <div className="min-h-screen bg-[#f8fafc] pt-24 px-4">
      <div className="max-w-3xl mx-auto bg-white rounded-2xl p-8 border border-gray-100">
        <SkeletonText lines={10} />
      </div>
    </div>
  )

  if (notFound || !law) return (
    <div className="min-h-screen flex items-center justify-center pt-16">
      <div className="text-center">
        <FileText size={48} className="text-gray-300 mx-auto mb-4" />
        <h2 className="font-playfair text-xl text-navy mb-2">Texte introuvable</h2>
        <button onClick={() => navigate(-1)} className="text-sm text-gold hover:underline">{t('common.back')}</button>
      </div>
    </div>
  )

  const title = lang === 'ar' && law.title_ar ? law.title_ar : law.title_fr

  // ── Détection résumés auto-générés par le pipeline ────────────────────────
  // Le pipeline génère une phrase générique pour les textes sans contenu extrait.
  // On la détecte et on la masque pour éviter d'afficher du contenu inutile.
  const isGenericSummary = (text) =>
    !text ||
    text.includes('fait partie de la base de données juridique JuriThèque') ||
    text.includes('base de données juridique JuriThèque') ||
    text.includes('base de données JuriThèque')

  const realSummaryFr = !isGenericSummary(law.simple_summary_fr) ? law.simple_summary_fr : null
  const realSummaryAr = law.simple_summary_ar?.trim().length > 30 ? law.simple_summary_ar : null

  // ── Identifiant propre — masquer les hash IDs du pipeline (ex: adala-1efb9bc5) ──
  const isHashId = (n) => Boolean(n && /^[a-z]+-[a-f0-9]{6,}$/.test(n))
  const displayNumber = law.number && !isHashId(law.number) ? law.number : null

  // Split content into logical blocks (articles / paragraphs)
  const splitContent = (text) => {
    if (!text) return []
    const articleSplit = text.split(/(?=\n(?:Article|الفصل|المادة)\s+\w)/i).filter(Boolean)
    if (articleSplit.length > 1) return articleSplit
    return text.split('\n\n').filter(s => s.trim().length > 0)
  }
  const articles_fr = splitContent(law.content_fr)
  const articles_ar = splitContent(law.content_ar)

  const hasSummary = !!(realSummaryFr || realSummaryAr)
  const hasTOC     = law.table_of_contents_fr || law.table_of_contents_ar
  const hasContent = articles_fr.length > 0 || articles_ar.length > 0

  // URL du document : notre Supabase Storage en priorité, sinon source_url (Adala / R2)
  const docUrl = law.pdf_url || law.source_url || null

  const PROXY_BASE = '/api/pdf-proxy'
  const isExternal   = docUrl && !docUrl.includes('supabase')
  // Adala direct PDF URLs: Access-Control-Allow-Origin:* + no X-Frame-Options → browser can embed directly
  // No need to route through Vercel proxy (AWS IPs can be blocked by Adala)
  const isDirectPdf  = docUrl && /\.pdf(\?|$)/i.test(docUrl)
  const viewerUrl = docUrl
    ? (isDirectPdf && isExternal ? docUrl : `${PROXY_BASE}?url=${encodeURIComponent(docUrl)}`)
    : null

  const toc = parseTOC(lang === 'ar' && law.table_of_contents_ar
    ? law.table_of_contents_ar
    : law.table_of_contents_fr)

  const importantArticles = (() => {
    if (!law.important_articles) return []
    if (Array.isArray(law.important_articles)) return law.important_articles
    if (typeof law.important_articles === 'string') {
      try { return JSON.parse(law.important_articles) } catch { return [] }
    }
    return []
  })()

  const keywords = Array.isArray(law.legal_keywords) ? law.legal_keywords : []

  // Quality signal
  const score = law.extraction_confidence_score != null ? Number(law.extraction_confidence_score) : null
  // Bannière "vérification" : uniquement si score très bas (< 30) OU marqué sans résumé
  // Évite d'afficher un signal E-E-A-T négatif sur 6 896 lois Adala correctement enrichies
  const needsReview = (score != null && score < 30) ||
                      (law.needs_human_review === true && !law.simple_summary_fr)

  // JSON-LD
  const breadcrumbs = [
    { name: t('law.breadcrumb_home'), url: '/' },
    { name: t('law.breadcrumb_base'), url: '/base' },
    ...(domain ? [{ name: (lang === 'ar' && domain.name_ar) ? domain.name_ar : domain.name_fr, url: `/domaine/${domain.id}` }] : []),
    { name: (displayNumber || (lang === 'ar' ? (law.title_ar || law.title_fr) : (law.title_fr || law.title_ar)) || 'Texte juridique').slice(0, 50), url: lawPath(law, lang) },
  ]

  // FAQ générée depuis les données disponibles (FAQPage JSON-LD + affichage visible)
  // Utilise { question, answer } pour compatibilité avec faqSchema() de JsonLD.jsx
  // Ne contient que des réponses factuelles tirées de la base — aucune invention
  const domainNameLoc = lang === 'ar' ? (domain?.name_ar || domain?.name_fr) : domain?.name_fr
  const lawTypeLoc    = lang === 'ar'
    ? (LAW_TYPES[law.type]?.label_ar || law.type || 'نص قانوني')
    : (law.type || 'texte juridique')
  const statusInVigueur = law.status === 'En vigueur' || law.status === 'ساري المفعول'

  const faqItems = [
    {
      question: `${t('law.faq_q1_prefix')} ${lawTypeLoc}${displayNumber ? ` n°${displayNumber}` : ''} ?`,
      answer: (lang === 'ar' ? realSummaryAr : realSummaryFr)
        || (lang === 'ar'
          ? `هذا ${lawTypeLoc}${law.date ? ` صادر بتاريخ ${law.date}` : ''}${domainNameLoc ? ` يندرج ضمن ${domainNameLoc}` : ''} بالمغرب. راجع المصدر الرسمي للاطلاع على التفاصيل الكاملة.`
          : `Ce texte est un ${lawTypeLoc} publié le ${law.date || 'date non précisée'}${domainNameLoc ? ` relevant du ${domainNameLoc}` : ''} au Maroc. Consultez la source officielle pour le détail complet.`),
    },
    ...(domainNameLoc ? [{
      question: t('law.faq_q2'),
      answer: `${t('law.faq_a2_prefix')} ${domainNameLoc}.`,
    }] : []),
    {
      question: t('law.faq_q3'),
      answer: statusInVigueur
        ? t('law.faq_a3_yes')
        : `${t('law.faq_a3_status')} ${law.status || (lang === 'ar' ? 'غير محدد' : 'non précisé')}.`,
    },
    {
      question: t('law.faq_q4'),
      answer: `${t('law.faq_a4_prefix')} ${getSourceLabel(law) || t('law.faq_a4_default')}.`,
    },
  ]

  return (
    <div className="min-h-screen bg-[#f8fafc] pt-16">
      <JsonLD data={[legalDocumentSchema(law, domain), breadcrumbSchema(breadcrumbs), faqSchema(faqItems)]} />

      {/* Header bar */}
      <div className="bg-white border-b border-gray-100 sticky top-16 z-30">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 h-12 flex items-center gap-2 text-xs text-navy-500">
          <Link to="/" className="hover:text-gold transition-colors">{t('law.breadcrumb_home')}</Link>
          <ChevronRight size={12} />
          <Link to="/base" className="hover:text-gold transition-colors">{t('law.breadcrumb_base')}</Link>
          <ChevronRight size={12} />
          {domain && (
            <>
              <Link to={`/domaine/${domain.id}`} className="hover:text-gold transition-colors">
                {lang === 'ar' ? domain.name_ar : domain.name_fr}
              </Link>
              <ChevronRight size={12} />
            </>
          )}
          <span className="text-navy-700 truncate max-w-[200px]">
            {displayNumber || (law.title_fr || law.title_ar || `Texte n°${slug}`)?.slice(0, 45)}
          </span>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-8">
        <div className="flex gap-8">

          {/* TOC Sidebar — affiché uniquement si un sommaire structuré existe */}
          {toc?.sections?.length > 0 && (
            <aside className="hidden xl:block w-56 flex-shrink-0">
              <div className="sticky top-28 bg-white rounded-xl border border-gray-100 p-4">
                <h4 className="text-xs font-semibold uppercase tracking-widest text-gold mb-3">{t('law.toc')}</h4>
                <div className="space-y-1 max-h-[60vh] overflow-y-auto pr-1">
                  {toc.sections.slice(0, 30).map((sec, i) => (
                    <a
                      key={i}
                      href={`#toc-${i}`}
                      className="block text-xs text-navy-600 hover:text-gold transition-colors py-1 border-l-2 border-transparent hover:border-gold pl-2 truncate"
                    >
                      {sec.titre || sec.title || `Section ${i + 1}`}
                    </a>
                  ))}
                  {toc.sections.length > 30 && (
                    <p className="text-xs text-navy-400 pl-2 pt-1">+{toc.sections.length - 30} sections…</p>
                  )}
                </div>
              </div>
            </aside>
          )}

          {/* Main */}
          <div className="flex-1 min-w-0">

            {/* ── Law header card ─────────────────────────────────────────── */}
            <div className="bg-white rounded-2xl border border-gray-100 p-6 sm:p-8 mb-4 shadow-sm">
              <div className="flex flex-wrap items-start gap-3 mb-4">
                <TypeBadge type={law.type} size="lg" />
                <StatusBadge status={law.status} size="lg" />
                {law.verification_status === 'verified' && (
                  <span className="inline-flex items-center gap-1.5 text-xs font-medium px-2.5 py-1 rounded-full border bg-emerald-50 border-emerald-200 text-emerald-700">
                    <CheckCircle size={11} />
                    Texte consolidé
                  </span>
                )}
              </div>

              <h1 className={`font-playfair font-bold text-navy text-xl sm:text-2xl leading-tight mb-2 ${lang === 'ar' ? 'font-arabic text-2xl' : ''}`}>
                {title}
              </h1>

              {/* Bilingual subtitle */}
              {lang === 'fr' && law.title_ar && (
                <p className="font-arabic text-navy-600 text-base mb-4">{law.title_ar}</p>
              )}
              {lang === 'ar' && law.title_fr && (
                <p className="font-playfair text-navy-600 text-sm italic mb-4">{law.title_fr}</p>
              )}

              {/* Meta */}
              <div className="flex flex-wrap gap-4 text-sm text-navy-500 mb-5 pt-4 border-t border-gray-50">
                {displayNumber && (
                  <span className="flex items-center gap-1.5"><FileText size={14} /> {displayNumber}</span>
                )}
                <span className="flex items-center gap-1.5"><Calendar size={14} /> {law.date}</span>
                {domain && (
                  <span className="flex items-center gap-1.5">
                    <Tag size={14} />
                    <Link to={`/domaine/${domain.id}`} className="hover:text-gold transition-colors">
                      {lang === 'ar' ? domain.name_ar : domain.name_fr}
                    </Link>
                  </span>
                )}
                {(law.detected_article_count || law.public_article_count) && (
                  <span className="flex items-center gap-1.5">
                    <Hash size={14} />
                    {law.public_article_count ?? law.detected_article_count} articles
                  </span>
                )}
              </div>

              {/* Legal keywords */}
              {keywords.length > 0 && (
                <div className="flex flex-wrap gap-1.5 mb-5">
                  {keywords.map(kw => (
                    <span key={kw} className="text-xs bg-navy/5 text-navy-700 border border-navy/10 px-2.5 py-1 rounded-full">
                      {kw}
                    </span>
                  ))}
                </div>
              )}

              {/* Legacy tags */}
              {!keywords.length && law.tags?.length > 0 && (
                <div className="flex flex-wrap gap-1.5 mb-5">
                  {law.tags.map(tag => (
                    <span key={tag} className="text-xs bg-gray-50 text-navy-600 border border-gray-100 px-2.5 py-1 rounded-full">
                      {tag}
                    </span>
                  ))}
                </div>
              )}

              {/* Référence officielle */}
              {(law.source_name || law.bo_number) && (() => {
                const siteUrl   = getSourceSiteUrl(law)
                const siteLabel = getSourceLabel(law)
                return (
                  <div className="flex flex-wrap items-center gap-3 mb-5 px-3 py-2.5 bg-blue-50/60 border border-blue-100 rounded-xl text-xs">
                    <span className="flex items-center gap-1.5 font-medium text-blue-700">
                      <ExternalLink size={12} />
                      {lang === 'ar' ? 'المصدر الرسمي :' : 'Référence :'}
                      {siteLabel && <span className="font-semibold">{siteLabel}</span>}
                    </span>
                    {law.bo_number && (
                      <span className="text-blue-600">
                        {lang === 'ar' ? 'الجريدة الرسمية عدد' : 'Bulletin Officiel n°'}&nbsp;
                        <strong>{law.bo_number}</strong>
                        {law.bo_date && <span className="text-blue-400 ml-1">({law.bo_date})</span>}
                      </span>
                    )}
                    {siteUrl && (
                      <a
                        href={siteUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="ml-auto flex items-center gap-1 text-blue-600 hover:text-blue-800 font-medium hover:underline"
                      >
                        {lang === 'ar' ? 'زيارة المصدر' : 'Visiter la source'} <ExternalLink size={10} />
                      </a>
                    )}
                  </div>
                )
              })()}

              {/* Actions */}
              <div className="flex flex-wrap gap-2 pt-4 border-t border-gray-50">
                {/* Bouton principal : Consulter le texte */}
                {docUrl ? (
                  <button
                    onClick={() => setShowPdf(v => !v)}
                    className={`flex items-center gap-1.5 px-4 py-2 rounded-xl text-sm font-medium transition-colors ${
                      showPdf
                        ? 'bg-gold text-navy'
                        : 'bg-navy text-white hover:bg-gold hover:text-navy'
                    }`}
                  >
                    <Eye size={14} />
                    {showPdf ? t('law.hide_text') : t('law.view_text')}
                  </button>
                ) : (
                  <button disabled className="flex items-center gap-1.5 px-4 py-2 bg-gray-100 text-gray-400 rounded-xl text-sm font-medium cursor-not-allowed">
                    <FileText size={14} />{t('law.text_unavailable')}
                  </button>
                )}

                {/* Télécharger — seulement si PDF hébergé chez nous */}
                {law.pdf_url && (
                  <a
                    href={law.pdf_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    download
                    className="flex items-center gap-1.5 px-4 py-2 border border-gray-200 text-navy-700 rounded-xl text-sm font-medium hover:border-gold hover:text-gold transition-colors"
                  >
                    <Download size={14} />{t('law.download')}
                  </a>
                )}

                {/* Ouvrir dans un nouvel onglet */}
                {docUrl && (
                  <a
                    href={docUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-1.5 px-4 py-2 border border-gray-200 text-navy-700 rounded-xl text-sm font-medium hover:border-gold hover:text-gold transition-colors"
                  >
                    <ExternalLink size={14} />{t('law.open_newtab')}
                  </a>
                )}

                <button
                  onClick={handleShare}
                  className="flex items-center gap-1.5 px-4 py-2 border border-gray-200 text-navy-700 rounded-xl text-sm font-medium hover:border-gold hover:text-gold transition-colors"
                >
                  <Share2 size={14} />{copied ? t('law.copied') : t('law.share')}
                </button>

                {user && (
                  <button
                    onClick={() => toggleFavorite(law)}
                    className={`flex items-center gap-1.5 px-4 py-2 border rounded-xl text-sm font-medium transition-colors ${
                      fav ? 'border-gold bg-gold/10 text-gold' : 'border-gray-200 text-navy-700 hover:border-gold hover:text-gold'
                    }`}
                  >
                    <Heart size={14} fill={fav ? 'currentColor' : 'none'} />
                    {fav ? t('common.rem_fav') : t('common.add_fav')}
                  </button>
                )}

                {/* Signaler une erreur */}
                <button
                  onClick={() => setReportOpen(true)}
                  className="flex items-center gap-1.5 px-3 py-2 border border-gray-200 text-navy-400 hover:border-orange-300 hover:text-orange-500 hover:bg-orange-50 rounded-xl text-xs font-medium transition-colors ml-auto"
                  title={t('law.report')}
                >
                  <Flag size={13} />
                  <span className="hidden sm:inline">{t('law.report')}</span>
                </button>
              </div>

              {/* Inline document viewer */}
              {showPdf && viewerUrl && !viewerError && (
                <div className="mt-5 rounded-xl overflow-hidden border border-gray-200">
                  <div className="bg-gray-50 px-4 py-2 flex items-center justify-between border-b border-gray-200">
                    <span className="text-xs font-medium text-navy-600 flex items-center gap-2">
                      📄 {lang === 'ar' ? (law.title_ar || law.title_fr) : (law.title_fr || law.title_ar)}
                      {isExternal && (
                        <span className="inline-flex items-center gap-1 text-[10px] font-semibold px-1.5 py-0.5 rounded-full bg-orange-100 text-orange-700 border border-orange-200">
                          <ExternalLink size={8} /> {t('law.official_src')}
                        </span>
                      )}
                    </span>
                    <a href={docUrl} target="_blank" rel="noopener noreferrer" className="text-xs text-gold hover:underline flex items-center gap-1">
                      <ExternalLink size={11} /> {t('law.fullscreen')}
                    </a>
                  </div>
                  <div className="relative">
                    {/* Spinner visible pendant le chargement */}
                    <div className="absolute inset-0 flex flex-col items-center justify-center bg-gray-50 pointer-events-none z-10"
                         id="viewer-loading-overlay"
                         style={{ transition: 'opacity 0.3s' }}>
                      <div className="w-8 h-8 border-2 border-gold border-t-transparent rounded-full animate-spin mb-3" />
                      <p className="text-xs text-navy-400">{lang === 'ar' ? 'جارٍ تحميل الوثيقة...' : 'Chargement du document...'}</p>
                    </div>
                    <iframe
                      src={viewerUrl}
                      className="w-full"
                      style={{ height: '700px' }}
                      title={law.title_fr || law.title_ar}
                      onLoad={(e) => {
                        const overlay = e.target.parentElement?.querySelector('#viewer-loading-overlay')
                        if (overlay) overlay.style.opacity = '0'
                      }}
                      onError={() => setViewerError(true)}
                    />
                  </div>
                  {/* Bouton toujours visible — Google Docs peut afficher "No preview available" sans déclencher onError */}
                  <div className="bg-gray-50 border-t border-gray-200 px-4 py-3 flex items-center justify-between gap-3">
                    <p className="text-xs text-navy-400">
                      {lang === 'ar'
                        ? 'إذا لم تظهر المعاينة، افتح الوثيقة مباشرة'
                        : 'Si la prévisualisation ne s\'affiche pas, ouvrez le document directement.'}
                    </p>
                    <a
                      href={docUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex-shrink-0 inline-flex items-center gap-1.5 px-3 py-1.5 bg-gold text-navy rounded-lg text-xs font-semibold hover:bg-amber-400 transition-colors"
                    >
                      <ExternalLink size={12} />
                      {lang === 'ar' ? 'فتح الوثيقة' : 'Ouvrir le document'}
                    </a>
                  </div>
                </div>
              )}

              {/* Fallback si le viewer échoue (ex: PDF bloqué côté serveur) */}
              {showPdf && viewerError && docUrl && (
                <div className="mt-5 rounded-xl border border-gray-200 bg-gray-50 p-6 text-center">
                  <p className="text-sm text-navy-500 mb-3">{t('law.viewer_error')}</p>
                  <a
                    href={docUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-2 px-4 py-2 bg-gold text-navy rounded-xl text-xs font-semibold hover:bg-gold-light transition-colors"
                  >
                    <ExternalLink size={13} />
                    {t('law.open_official_pdf')}
                  </a>
                </div>
              )}
            </div>

            {/* ── Relations entre textes ──────────────────────────────────── */}
            {relations.successorLaws.length > 0 && (
              <div className="flex items-start gap-3 bg-blue-50 border border-blue-200 rounded-xl px-4 py-3 mb-4">
                <ArrowRight size={15} className="text-blue-500 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="text-xs font-semibold text-blue-800 mb-1.5">
                    {lang === 'ar' ? 'تم استبدال هذا النص' : 'Ce texte a été mis à jour ou remplacé'}
                  </p>
                  {relations.successorLaws.map(s => (
                    <Link
                      key={s.id}
                      to={lawPath(s)}
                      className="flex items-center gap-1.5 text-xs text-blue-700 hover:text-blue-900 hover:underline"
                    >
                      <ChevronRight size={10} className="flex-shrink-0" />
                      <span className="font-medium">
                        {[s.type, s.number ? `n°${s.number}` : ''].filter(Boolean).join(' ')}
                      </span>
                      {(s.title_fr || s.title_ar) && (
                        <span className="text-blue-500">
                          — {(s.title_fr || s.title_ar).slice(0, 55)}{(s.title_fr || s.title_ar).length > 55 ? '…' : ''}
                        </span>
                      )}
                      {s.date && <span className="text-blue-400 ml-1">({s.date})</span>}
                    </Link>
                  ))}
                </div>
              </div>
            )}

            {relations.replacedLaw && (
              <div className="flex items-center gap-2 text-xs text-navy-400 mb-3 px-1">
                <RotateCcw size={11} className="text-navy-300 flex-shrink-0" />
                <span>{lang === 'ar' ? 'يُلغي :' : 'Abroge :'}</span>
                <Link
                  to={lawPath(relations.replacedLaw)}
                  className="text-navy-600 hover:text-gold hover:underline"
                >
                  {[relations.replacedLaw.type, relations.replacedLaw.number ? `n°${relations.replacedLaw.number}` : ''].filter(Boolean).join(' ')}
                  {relations.replacedLaw.date && ` (${relations.replacedLaw.date})`}
                </Link>
              </div>
            )}

            {/* ── Introduction SEO — phrase contextuelle visible (aide Google + utilisateur) */}
            <p className="text-xs text-navy-400 mb-3 px-1 leading-relaxed">
              {lang === 'ar'
                ? `${t('law.seo_intro_prefix')} ${lawTypeLoc}${displayNumber ? ` رقم ${displayNumber}` : ''}${domainNameLoc ? ` ${t('law.seo_intro_rel')} ${domainNameLoc}` : ` ${t('law.seo_intro_moroccan')}`}${law.date ? `، بتاريخ ${law.date}` : ''}. ${t('law.seo_intro_suffix')}`
                : `${t('law.seo_intro_prefix')} ${law.type || 'le texte'}${displayNumber ? ` n°${displayNumber}` : ''}${domain?.name_fr ? ` ${t('law.seo_intro_rel')} ${domain.name_fr}` : ` ${t('law.seo_intro_moroccan')}`}${law.date ? `, daté du ${law.date}` : ''}. ${t('law.seo_intro_suffix')}`
              }
            </p>

            {/* ── Warning banner — uniquement pour contenu très dégradé ────── */}
            {needsReview && (
              <div className="flex items-start gap-3 bg-amber-50 border border-amber-200 rounded-xl px-4 py-3 mb-4">
                <AlertTriangle size={16} className="text-amber-600 flex-shrink-0 mt-0.5" />
                <p className="text-xs text-amber-800">{t('law.needs_review')}</p>
              </div>
            )}

            {/* ── Synthèse ─────────────────────────────────────────────────── */}
            {hasSummary && (
              <div className="bg-white rounded-2xl border border-gray-100 mb-4 shadow-sm overflow-hidden">
                <div className="flex items-center gap-2 px-6 py-4 border-b border-gray-50 bg-gradient-to-r from-navy/5 to-transparent">
                  <Sparkles size={15} className="text-gold flex-shrink-0" />
                  <h2 className="font-semibold text-navy text-sm">{t('law.summary')}</h2>
                </div>
                <div className="p-6">
                  {/* Version française */}
                  {lang !== 'ar' && realSummaryFr && (
                    <div className="text-sm text-navy-700 leading-relaxed whitespace-pre-line">
                      {realSummaryFr}
                    </div>
                  )}
                  {/* Version arabe — avec fallback sur le FR si manquante */}
                  {lang === 'ar' && (
                    realSummaryAr ? (
                      <RTLWrapper>
                        <div className="text-sm text-navy-700 leading-loose font-arabic whitespace-pre-line">
                          {realSummaryAr}
                        </div>
                      </RTLWrapper>
                    ) : realSummaryFr ? (
                      <div>
                        <div className="text-sm text-navy-700 leading-relaxed whitespace-pre-line mb-3">
                          {realSummaryFr}
                        </div>
                        <p className="text-xs text-navy-400 italic border-t border-gray-50 pt-2">
                          الملخص العربي قيد الإعداد — النص أعلاه بالفرنسية
                        </p>
                      </div>
                    ) : null
                  )}
                  {/* Affichage bilingue en mode FR : ajouter l'arabe en dessous si disponible */}
                  {lang === 'fr' && realSummaryAr && (
                    <RTLWrapper>
                      <div className="text-sm text-navy-700 leading-loose font-arabic border-t border-gray-50 pt-4 mt-4 whitespace-pre-line">
                        {realSummaryAr}
                      </div>
                    </RTLWrapper>
                  )}
                </div>
              </div>
            )}

            {/* ── FAQ visible — 4 questions factuelles générées depuis la base ── */}
            <div className="bg-white rounded-2xl border border-gray-100 mb-4 shadow-sm overflow-hidden">
              <div className="flex items-center gap-2 px-6 py-4 border-b border-gray-50 bg-gradient-to-r from-navy/5 to-transparent">
                <Bot size={15} className="text-gold flex-shrink-0" />
                <h2 className="font-semibold text-navy text-sm">{t('law.faq')}</h2>
              </div>
              <div className="divide-y divide-gray-50">
                {faqItems.map((item, i) => (
                  <div key={i} className="px-6 py-4">
                    <p className="text-sm font-medium text-navy mb-1">{item.question}</p>
                    <p className="text-sm text-navy-500 leading-relaxed">{item.answer}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* ── Sommaire structuré (TOC) ─────────────────────────────────── */}
            {toc?.sections?.length > 0 && (
              <div className="bg-white rounded-2xl border border-gray-100 mb-4 shadow-sm overflow-hidden">
                <div className="flex items-center gap-2 px-6 py-4 border-b border-gray-50">
                  <BookOpen size={15} className="text-gold flex-shrink-0" />
                  <h2 className="font-semibold text-navy text-sm">{t('law.toc_sections')}</h2>
                  <span className="ml-auto text-xs text-navy-400">{toc.sections.length} {t('law.section_count')}</span>
                </div>
                <div className="p-6 space-y-3">
                  {toc.sections.map((sec, i) => (
                    <div key={i} id={`toc-${i}`} className="border-l-2 border-gold/30 pl-4">
                      <p className="text-sm font-medium text-navy">
                        {sec.titre || sec.title || `Section ${i + 1}`}
                        {sec.articles && <span className="ml-2 text-xs text-navy-400 font-normal">{sec.articles}</span>}
                      </p>
                      {sec.resume && (
                        <p className="text-xs text-navy-500 mt-0.5 leading-relaxed">{sec.resume}</p>
                      )}
                    </div>
                  ))}
                  {toc.notes && (
                    <p className="text-xs text-navy-400 italic border-t border-gray-50 pt-3 mt-3">{toc.notes}</p>
                  )}
                </div>
              </div>
            )}

            {/* ── Articles importants ──────────────────────────────────────── */}
            {importantArticles.length > 0 && (
              <div className="bg-white rounded-2xl border border-gray-100 mb-4 shadow-sm overflow-hidden">
                <div className="flex items-center gap-2 px-6 py-4 border-b border-gray-50">
                  <Award size={15} className="text-gold flex-shrink-0" />
                  <h2 className="font-semibold text-navy text-sm">{t('law.key_articles')}</h2>
                </div>
                <div className="divide-y divide-gray-50">
                  {importantArticles.map((art, i) => (
                    <div key={i} className="px-6 py-4">
                      <div className="flex items-baseline gap-2 mb-1">
                        <span className="text-xs font-bold text-gold uppercase tracking-wide">
                          {art.number ? `Article ${art.number}` : `Article ${i + 1}`}
                        </span>
                        {art.title && (
                          <span className="text-sm font-medium text-navy">{art.title}</span>
                        )}
                      </div>
                      {art.text && (
                        <p className="text-xs text-navy-600 leading-relaxed">{String(art.text).slice(0, 400)}{String(art.text).length > 400 ? '…' : ''}</p>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* ── Toggle texte brut (discret) — visible dès qu'il y a du contenu ── */}
            {hasContent && (
              <div className="mb-4">
                {/* Badge qualité — proche du texte extrait */}
                {score != null && (
                  <div className="flex items-center gap-2 mb-2">
                    <QualityBadge score={score} />
                    <span className="text-[11px] text-navy-400 italic">
                      {t('law.raw_text_quality')}
                    </span>
                  </div>
                )}
                <button
                  onClick={() => setShowFullText(v => !v)}
                  className="w-full flex items-center gap-2 px-4 py-2.5 bg-amber-50/60 border border-amber-100 rounded-xl text-xs font-medium text-amber-700 hover:border-amber-300 hover:bg-amber-50 transition-colors"
                >
                  <AlertTriangle size={13} className="flex-shrink-0 text-amber-500" />
                  <span className="flex-1 text-left">
                    {t('law.raw_text_toggle')}
                    {!showFullText && <span className="ml-1 text-amber-500">({articles_fr.length || articles_ar.length} blocs)</span>}
                  </span>
                  {showFullText
                    ? <ChevronUp size={13} className="flex-shrink-0" />
                    : <ChevronDown size={13} className="flex-shrink-0" />
                  }
                </button>
              </div>
            )}

            {/* ── Contenu bilingue (conditionnel) ─────────────────────────── */}
            {showFullText && (
              loading ? (
                <div className="bg-white rounded-2xl p-6 border border-gray-100">
                  <SkeletonText lines={8} />
                </div>
              ) : (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                  {/* French column */}
                  {articles_fr.length > 0 && (
                    <div className="bg-white rounded-2xl border border-gray-100 overflow-hidden">
                      <div className="px-5 py-3 border-b border-gray-50 bg-blue-50/50">
                        <span className="text-xs font-semibold text-blue-700 uppercase tracking-wide">{t('law.fr_col')}</span>
                      </div>
                      <div className="p-5 space-y-4">
                        {articles_fr.map((art, i) => (
                          <div key={i} id={`art-${i}`} className="text-sm text-navy-800 leading-relaxed border-l-2 border-blue-100 pl-3">
                            {art.split('\n').map((line, j) => (
                              <p key={j} className={line.startsWith('Article') ? 'font-semibold text-navy mb-1' : 'text-navy-700'}>
                                {line}
                              </p>
                            ))}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Arabic column */}
                  {articles_ar.length > 0 && (
                    <div className="bg-white rounded-2xl border border-gray-100 overflow-hidden">
                      <div className="px-5 py-3 border-b border-gray-50 bg-gold/5">
                        <span className="text-xs font-semibold text-gold-dark uppercase tracking-wide font-arabic">{t('law.ar_col')}</span>
                      </div>
                      <RTLWrapper className="p-5 space-y-4">
                        {articles_ar.map((art, i) => (
                          <div key={i} className="text-sm text-navy-800 leading-loose border-r-2 border-gold/30 pr-3">
                            {art.split('\n').map((line, j) => (
                              <p key={j} className={line.startsWith('المادة') || line.startsWith('الفصل') ? 'font-semibold text-navy mb-1' : 'text-navy-700'}>
                                {line}
                              </p>
                            ))}
                          </div>
                        ))}
                      </RTLWrapper>
                    </div>
                  )}

                  {/* No content at all */}
                  {articles_fr.length === 0 && articles_ar.length === 0 && (
                    <div className="col-span-2 flex flex-col items-center justify-center py-12 text-center">
                      <FileText size={36} className="text-gray-200 mb-3" />
                      <p className="text-sm text-navy-500">Texte intégral non disponible — téléchargez le PDF ci-dessus.</p>
                    </div>
                  )}
                </div>
              )
            )}

            {/* ── Message si pas de texte extrait localement ─────────────── */}
            {!hasContent && (
              <div className="bg-white rounded-2xl border border-gray-100 overflow-hidden mb-4">
                <div className="flex flex-col items-center justify-center py-8 text-center px-6">
                  <div className="w-12 h-12 rounded-2xl bg-gray-50 border border-gray-100 flex items-center justify-center mb-3">
                    <FileText size={22} className="text-gray-300" />
                  </div>
                  {docUrl ? (
                    /* ── PDF disponible : bouton direct vers le document ── */
                    <a
                      href={docUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-2 px-4 py-2 bg-gold text-navy rounded-xl text-xs font-semibold hover:bg-gold-light transition-colors"
                    >
                      <ExternalLink size={13} />
                      {t('law.open_official_pdf')}
                      {law.source_name && <span className="opacity-70">— {law.source_name.toUpperCase()}</span>}
                    </a>
                  ) : (
                    /* ── Aucun PDF : message metadata_only ou en cours d'intégration ── */
                    <>
                      <p className="text-sm font-medium text-navy-700 mb-1">
                        {law.extraction_status === 'metadata_only'
                          ? t('law.metadata_card')
                          : t('law.text_unavailable')}
                      </p>
                      <p className="text-xs text-navy-400 max-w-xs leading-relaxed mb-3">
                        {law.extraction_status === 'metadata_only'
                          ? t('law.metadata_desc')
                          : t('law.text_integrating')}
                      </p>
                      {law.source_url && (
                        <a
                          href={law.source_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center gap-2 px-4 py-2 bg-gold text-navy rounded-xl text-xs font-semibold hover:bg-gold-light transition-colors"
                        >
                          <ExternalLink size={13} />
                          {t('law.view_official_src')}
                          {law.source_name && <span className="opacity-70">— {law.source_name.toUpperCase()}</span>}
                        </a>
                      )}
                    </>
                  )}
                </div>
              </div>
            )}

            {/* ── Textes liés mentionnés dans le TOC ──────────────────────── */}
            {toc?.textes_lies?.length > 0 && (
              <div className="bg-blue-50/60 border border-blue-100 rounded-xl px-5 py-4 mb-6">
                <p className="text-xs font-semibold text-navy mb-2">{t('law.linked_texts')}</p>
                <ul className="space-y-1">
                  {toc.textes_lies.map((ref, i) => (
                    <li key={i} className="text-xs text-navy-600 flex items-center gap-1.5">
                      <ChevronRight size={10} className="text-gold flex-shrink-0" />
                      {ref}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* ── Guides thématiques liés ──────────────────────────────────── */}
            {law.domain_id && (() => {
              const guides = getGuidesForDomain(law.domain_id)
              if (!guides.length) return null
              return (
                <div className="mt-6 bg-white rounded-2xl border border-gray-100 p-5 shadow-sm">
                  <h3 className="font-semibold text-navy text-sm mb-3 flex items-center gap-2">
                    <BookOpen size={14} className="text-gold" />
                    {t('law.related_guides')}
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {guides.map(guide => (
                      <Link
                        key={guide.slug}
                        to={`/${lang}/guides/${guide.slug}`}
                        className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-gray-50 border border-gray-100 rounded-lg text-xs text-navy-700 hover:border-gold hover:text-gold transition-colors"
                      >
                        {(lang === 'ar' && guide.h1_ar) ? guide.h1_ar : guide.h1}
                        <ChevronRight size={10} className="text-gray-400" />
                      </Link>
                    ))}
                  </div>
                </div>
              )
            })()}

            {/* ── Related laws ─────────────────────────────────────────────── */}
            {related.length > 0 && (
              <div className="mt-8">
                <h3 className="font-playfair font-semibold text-navy text-lg mb-4">{t('law.related')}</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {related.map(l => <LawCard key={l.id} law={l} />)}
                </div>
              </div>
            )}

            {/* ── Maillage interne — navigation ────────────────────────────── */}
            <div className="mt-8 pt-6 border-t border-gray-100 flex flex-wrap gap-3">
              {domain && (
                <Link
                  to={`/domaine/${domain.id}`}
                  className="inline-flex items-center gap-1.5 px-4 py-2 bg-white border border-gray-200 rounded-xl text-xs font-medium text-navy-700 hover:border-gold hover:text-gold transition-colors"
                >
                  <BookOpen size={12} className="text-gold" />
                  {t('law.all_texts_domain')} — {lang === 'ar' ? domain.name_ar : domain.name_fr}
                </Link>
              )}
              {law.domain_id && (
                <Link
                  to={`/fr/veille-juridique?domain=${law.domain_id}`}
                  className="inline-flex items-center gap-1.5 px-4 py-2 bg-white border border-gray-200 rounded-xl text-xs font-medium text-navy-700 hover:border-gold hover:text-gold transition-colors"
                >
                  <Bell size={12} className="text-gold" />
                  {t('law.legal_watch_link')} — {domain ? (lang === 'ar' ? domain.name_ar : domain.name_fr) : law.domain_id}
                </Link>
              )}
              <Link
                to="/base"
                className="inline-flex items-center gap-1.5 px-4 py-2 bg-white border border-gray-200 rounded-xl text-xs font-medium text-navy-700 hover:border-gold hover:text-gold transition-colors"
              >
                <FileText size={12} className="text-gold" />
                {t('law.database_link')}
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Floating AI button */}
      <button
        onClick={() => {
          const typeNum = [law.type, law.number ? `n° ${law.number}` : ''].filter(Boolean).join(' ')
          const titlePart = law.title_fr || law.title_ar || ''
          const summaryPart = law.simple_summary_fr || ''
          const question = [
            lang === 'ar'
              ? `هل يمكنك شرح هذا النص القانوني لي؟`
              : `Pouvez-vous m'expliquer ce texte juridique ?`,
            typeNum && titlePart ? `${typeNum} : ${titlePart}` : (typeNum || titlePart),
            summaryPart,
          ].filter(Boolean).join('\n\n')
          navigate('/assistant', { state: { prefill: question.trim() } })
        }}
        className="fixed bottom-20 right-6 flex items-center gap-2 px-5 py-3 bg-navy text-white rounded-full shadow-2xl hover:bg-gold hover:text-navy transition-all duration-200 hover:-translate-y-0.5 text-sm font-semibold z-40"
      >
        <Bot size={16} className="animate-pulse" />
        {t('law.ask_ai')}
      </button>

      {/* ── Modal signalement ─────────────────────────────────────────────── */}
      <ReportModal
        isOpen={reportOpen}
        onClose={() => setReportOpen(false)}
        contentType="law"
        subject={law.title_fr || law.title_ar || law.number}
        subjectUrl={typeof window !== 'undefined' ? window.location.href : ''}
        lawId={law.id}
      />
    </div>
  )
}

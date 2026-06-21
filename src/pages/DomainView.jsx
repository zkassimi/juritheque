import { useParams, Link } from 'react-router-dom'
import { useEffect, useState } from 'react'
import { ArrowLeft, BookOpen, ChevronRight, Bell, FileText, ChevronLeft, ChevronDown, ChevronUp, HelpCircle } from 'lucide-react'
import { getGuidesForDomain } from '../data/seoIntentPages'
import { useLang } from '../contexts/LangContext'
import { fetchDomainById, fetchLawsByDomain } from '../lib/api'
import LawCard from '../components/LawCard'
import { SkeletonGrid } from '../components/ui/SkeletonLoader'
import { useSEO } from '../hooks/useSEO'
import JsonLD, { collectionPageSchema, breadcrumbSchema, faqSchema } from '../components/JsonLD'

const PAGE_SIZE = 18

export default function DomainView() {
  const { slug } = useParams()
  const { lang, t } = useLang()
  const [domain,  setDomain]  = useState(null)
  const [laws,    setLaws]    = useState([])
  const [total,   setTotal]   = useState(0)
  const [page,    setPage]    = useState(1)
  const [loading, setLoading] = useState(true)
  const [lawsLoading, setLawsLoading] = useState(false)

  // Chargement initial du domaine
  useEffect(() => {
    let cancelled = false
    setLoading(true)
    fetchDomainById(slug)
      .then(dom => { if (!cancelled) setDomain(dom) })
      .catch(() => {})
      .finally(() => { if (!cancelled) setLoading(false) })
    return () => { cancelled = true }
  }, [slug])

  // Chargement des lois (réagit aux changements de page)
  useEffect(() => {
    let cancelled = false
    setLawsLoading(true)
    fetchLawsByDomain(slug, { page, pageSize: PAGE_SIZE })
      .then(({ data, count }) => {
        if (!cancelled) { setLaws(data); setTotal(count) }
      })
      .catch(() => { if (!cancelled) setLaws([]) })
      .finally(() => { if (!cancelled) setLawsLoading(false) })
    return () => { cancelled = true }
  }, [slug, page])

  // Réinitialise la page quand on change de domaine
  useEffect(() => { setPage(1) }, [slug])

  useSEO({
    title: domain
      ? `${domain.name_fr} — Textes juridiques marocains`
      : 'Domaine juridique — JuriThèque',
    description: domain
      ? `Consultez les ${total ? total + ' ' : ''}textes juridiques marocains en matière de ${domain.name_fr.toLowerCase()} : lois, dahirs, décrets et arrêtés. ${domain.sub_domains?.slice(0,4).join(', ') || ''}. Bilingue français-arabe.`
      : 'Textes juridiques marocains par domaine juridique.',
    canonical: `/domaine/${slug}`,
    type: 'website',
  })

  if (loading) return (
    <div className="min-h-screen bg-[#f8fafc] pt-24 px-4">
      <div className="max-w-7xl mx-auto"><SkeletonGrid count={6} /></div>
    </div>
  )

  if (!domain) return (
    <div className="min-h-screen flex items-center justify-center pt-16">
      <p className="text-navy-600">Domaine introuvable.</p>
    </div>
  )

  const totalPages = Math.ceil(total / PAGE_SIZE)

  const breadcrumbs = [
    { name: 'Accueil',  url: '/' },
    { name: 'Domaines', url: '/domaines' },
    { name: domain.name_fr, url: `/domaine/${slug}` },
  ]

  // ── FAQ générée pour le domaine ──────────────────────────────────────────
  const domainFaq = [
    {
      question: `Combien de textes juridiques couvrent le domaine ${domain.name_fr} au Maroc ?`,
      answer: `JuriThèque recense ${total ? total + ' textes officiels' : 'des textes officiels'} en ${domain.name_fr.toLowerCase()}, incluant lois, décrets, dahirs et arrêtés publiés par les institutions marocaines compétentes.`,
    },
    {
      question: `Quels sont les principaux sous-domaines du ${domain.name_fr} ?`,
      answer: domain.sub_domains?.length
        ? `Les principaux sous-domaines du ${domain.name_fr.toLowerCase()} sont : ${domain.sub_domains.slice(0, 5).join(', ')}.`
        : `Ce domaine couvre l'ensemble des textes réglementaires marocains liés au ${domain.name_fr.toLowerCase()}.`,
    },
    {
      question: `Comment consulter un texte en ${domain.name_fr} sur JuriThèque ?`,
      answer: `Utilisez la barre de recherche ou naviguez par domaine dans la base de données. Chaque texte indique sa source officielle, son type (loi, décret, dahir…) et, lorsque disponible, son PDF original.`,
    },
  ]

  return (
    <div className="min-h-screen bg-[#f8fafc] pt-16">
      <JsonLD data={[collectionPageSchema(domain, total), breadcrumbSchema(breadcrumbs), faqSchema(domainFaq)].filter(Boolean)} />

      {/* ── Header ── */}
      <div className="bg-navy text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6">
          <Link to="/domaines" className="flex items-center gap-1.5 text-white/60 text-xs mb-4 hover:text-gold">
            <ArrowLeft size={12} /> {t('common.back')}
          </Link>
          <h1 className="font-playfair font-bold text-3xl">{domain.name_fr}</h1>
          <p className="font-arabic text-white/60 text-lg mt-1">{domain.name_ar}</p>
          <div className="flex flex-wrap items-center gap-3 mt-3">
            <p className="text-gold text-sm">{total} {t('domains.laws')}</p>
            <Link
              to={`/fr/veille-juridique?domain=${slug}`}
              className="inline-flex items-center gap-1.5 text-xs text-white/70 hover:text-gold transition-colors border border-white/20 px-3 py-1 rounded-full hover:border-gold"
            >
              <Bell size={11} /> Veille juridique
            </Link>
            <Link
              to={`/base?domain=${slug}`}
              className="inline-flex items-center gap-1.5 text-xs text-white/70 hover:text-gold transition-colors border border-white/20 px-3 py-1 rounded-full hover:border-gold"
            >
              <FileText size={11} /> Filtrer dans la base
            </Link>
          </div>
        </div>
      </div>

      {/* ── Contenu ── */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-10">

        {/* Grille de lois */}
        {lawsLoading ? (
          <SkeletonGrid count={PAGE_SIZE} />
        ) : laws.length === 0 ? (
          <p className="text-navy-500 text-center py-16">{t('db.empty_title')}</p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
            {laws.map(law => <LawCard key={law.id} law={law} />)}
          </div>
        )}

        {/* ── Pagination ── */}
        {totalPages > 1 && !lawsLoading && (
          <div className="flex items-center justify-center gap-2 mt-8 flex-wrap">
            <button
              onClick={() => setPage(p => Math.max(1, p - 1))}
              disabled={page === 1}
              className="p-2 rounded-lg border border-gray-200 bg-white text-navy-600 hover:border-gold disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
            >
              <ChevronLeft size={16} />
            </button>

            {(() => {
              const WINDOW = 5
              let start = Math.max(1, page - Math.floor(WINDOW / 2))
              let end   = Math.min(totalPages, start + WINDOW - 1)
              if (end - start < WINDOW - 1) start = Math.max(1, end - WINDOW + 1)
              const pages = Array.from({ length: end - start + 1 }, (_, i) => start + i)
              return (
                <>
                  {start > 1 && (
                    <>
                      <button onClick={() => setPage(1)} className="w-9 h-9 rounded-lg text-sm bg-white border border-gray-200 text-navy-600 hover:border-gold transition-colors">1</button>
                      {start > 2 && <span className="text-navy-400 text-sm">…</span>}
                    </>
                  )}
                  {pages.map(p => (
                    <button
                      key={p}
                      onClick={() => setPage(p)}
                      className={`w-9 h-9 rounded-lg text-sm font-medium transition-colors ${p === page ? 'bg-navy text-white' : 'bg-white border border-gray-200 text-navy-600 hover:border-gold'}`}
                    >
                      {p}
                    </button>
                  ))}
                  {end < totalPages && (
                    <>
                      {end < totalPages - 1 && <span className="text-navy-400 text-sm">…</span>}
                      <button onClick={() => setPage(totalPages)} className="w-9 h-9 rounded-lg text-sm bg-white border border-gray-200 text-navy-600 hover:border-gold transition-colors">{totalPages}</button>
                    </>
                  )}
                </>
              )
            })()}

            <button
              onClick={() => setPage(p => Math.min(totalPages, p + 1))}
              disabled={page === totalPages}
              className="p-2 rounded-lg border border-gray-200 bg-white text-navy-600 hover:border-gold disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
            >
              <ChevronRight size={16} />
            </button>

            <span className="text-xs text-navy-500 ml-1">
              Page {page} / {totalPages}
            </span>
          </div>
        )}

        {/* ── Guides thématiques liés ── */}
        {(() => {
          const guides = getGuidesForDomain(slug)
          if (!guides.length) return null
          return (
            <div className="mt-12 pt-8 border-t border-gray-100">
              <h3 className="font-playfair font-semibold text-navy text-lg mb-4 flex items-center gap-2">
                <BookOpen size={16} className="text-gold" />
                Guides liés à ce domaine
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                {guides.map(guide => (
                  <Link
                    key={guide.slug}
                    to={`/fr/guides/${guide.slug}`}
                    className="flex items-start gap-3 p-4 bg-white rounded-xl border border-gray-100 hover:border-gold hover:shadow-sm transition-all group"
                  >
                    <BookOpen size={14} className="text-gold flex-shrink-0 mt-0.5" />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-navy group-hover:text-gold transition-colors truncate">{guide.h1}</p>
                      <p className="text-xs text-navy-400 mt-0.5 line-clamp-2">{guide.metaDescription}</p>
                    </div>
                    <ChevronRight size={13} className="text-gray-300 group-hover:text-gold flex-shrink-0 mt-0.5 transition-colors" />
                  </Link>
                ))}
              </div>
            </div>
          )
        })()}
        {/* ── FAQ domaine ── */}
        <div className="mt-12 pt-8 border-t border-gray-100">
          <h3 className="font-playfair font-semibold text-navy text-lg mb-4 flex items-center gap-2">
            <HelpCircle size={16} className="text-gold" />
            Questions fréquentes — {domain.name_fr}
          </h3>
          <div className="space-y-2">
            {domainFaq.map((item, i) => (
              <DomainFAQItem key={i} question={item.question} answer={item.answer} />
            ))}
          </div>
        </div>

      </div>
    </div>
  )
}

// ── Mini accordéon FAQ pour la page domaine ───────────────────────────────────
function DomainFAQItem({ question, answer }) {
  const [open, setOpen] = useState(false)
  return (
    <div className="border border-gray-100 rounded-xl overflow-hidden">
      <button
        className="w-full flex items-center justify-between px-5 py-4 text-left bg-white hover:bg-gray-50 transition-colors"
        onClick={() => setOpen(v => !v)}
        aria-expanded={open}
      >
        <span className="text-sm font-medium text-navy pr-4">{question}</span>
        {open
          ? <ChevronUp   size={16} className="text-gold flex-shrink-0" />
          : <ChevronDown size={16} className="text-gold flex-shrink-0" />
        }
      </button>
      {open && (
        <div className="px-5 pb-4 pt-1 bg-gray-50/80">
          <p className="text-sm text-navy-600 leading-relaxed">{answer}</p>
        </div>
      )}
    </div>
  )
}

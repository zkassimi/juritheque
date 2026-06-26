/**
 * FeedbackButton — Bouton flottant global de suggestion/signalement
 * Affiché en bas à droite sur toutes les pages (sauf /admin)
 */
import { useState } from 'react'
import { useLocation } from 'react-router-dom'
import { MessageSquarePlus } from 'lucide-react'
import ReportModal from './ReportModal'
import { useLang } from '../contexts/LangContext'

export default function FeedbackButton() {
  const [open, setOpen] = useState(false)
  const { pathname } = useLocation()
  const { t } = useLang()

  // Masquer sur /admin et /connexion
  if (pathname.startsWith('/admin') || pathname.startsWith('/connexion')) return null

  return (
    <>
      {/* ── Bouton flottant ────────────────────────────────────────────── */}
      <div className="fixed bottom-6 right-5 z-[998] flex flex-col items-end gap-2">
        {/* Tooltip label — visible au hover */}
        <div className="
          opacity-0 translate-x-2 pointer-events-none
          group-hover:opacity-100 group-hover:translate-x-0
          transition-all duration-200
          bg-navy text-white text-xs font-medium px-3 py-1.5 rounded-lg shadow-lg
          whitespace-nowrap
          mr-1
        ">
          Donner un retour
        </div>

        <button
          onClick={() => setOpen(true)}
          className="group relative flex items-center gap-2 pl-3 pr-4 py-2.5 bg-navy text-white rounded-full shadow-lg hover:bg-gold hover:text-navy transition-all duration-200 hover:shadow-xl hover:-translate-y-0.5 active:translate-y-0"
          aria-label="Donner un retour ou signaler une erreur"
        >
          {/* Pulse dot */}
          <span className="absolute -top-1 -right-1 w-3 h-3">
            <span className="absolute inline-flex w-full h-full rounded-full bg-gold opacity-60 animate-ping" />
            <span className="relative inline-flex w-3 h-3 rounded-full bg-gold" />
          </span>

          <MessageSquarePlus size={15} className="flex-shrink-0" />
          <span className="text-xs font-semibold hidden sm:inline whitespace-nowrap">
            {t('feedback.label')}
          </span>
        </button>
      </div>

      {/* ── Modal ──────────────────────────────────────────────────────── */}
      <ReportModal
        isOpen={open}
        onClose={() => setOpen(false)}
        contentType="suggestion"
        subject="Retour global JuriThèque"
        subjectUrl={typeof window !== 'undefined' ? window.location.href : ''}
      />
    </>
  )
}

/**
 * ReportModal — Modal de signalement d'erreur / suggestion
 * Utilisé sur : LawDetail, SEOIntentPage (guides), FeedbackButton (global)
 *
 * Props:
 *   isOpen        boolean
 *   onClose       () => void
 *   contentType   'law' | 'guide' | 'suggestion' | 'other'
 *   subject       string  — titre du texte/guide
 *   subjectUrl    string  — URL de la page
 *   lawId         number  — id de la loi (optionnel)
 *   guideSlug     string  — slug du guide (optionnel)
 */

import { useState, useEffect, useRef } from 'react'
import { X, Flag, CheckCircle, AlertCircle, Loader2 } from 'lucide-react'
import { submitReport } from '../lib/api'

// ── Config des types de signalement ──────────────────────────────────────────
const REPORT_TYPES = {
  law: [
    { value: 'text_error',   label: '📄 Texte incorrect ou incomplet',      placeholder: 'Ex: L\'article 12 est manquant, le titre est erroné…' },
    { value: 'outdated',     label: '⚠️ Texte abrogé non signalé',          placeholder: 'Ex: Ce texte a été abrogé par la loi n°… en 2023…' },
    { value: 'pdf_broken',   label: '🔗 Lien PDF cassé / introuvable',      placeholder: 'Le bouton télécharger ne fonctionne pas…' },
    { value: 'translation',  label: '🌐 Erreur de traduction (FR ↔ AR)',    placeholder: 'Ex: La traduction arabe ne correspond pas…' },
    { value: 'suggestion',   label: '💡 Suggestion d\'amélioration',        placeholder: 'Votre suggestion…' },
  ],
  guide: [
    { value: 'text_error',   label: '📄 Information incorrecte',            placeholder: 'Précisez l\'erreur que vous avez trouvée…' },
    { value: 'outdated',     label: '⚠️ Contenu obsolète',                  placeholder: 'Ex: La loi a changé en 2024…' },
    { value: 'missing_text', label: '➕ Texte juridique manquant',          placeholder: 'Quel texte devrait être cité dans ce guide ?' },
    { value: 'suggestion',   label: '💡 Suggestion d\'amélioration',        placeholder: 'Votre suggestion…' },
  ],
  suggestion: [
    { value: 'missing_text', label: '➕ Ajouter un texte juridique',        placeholder: 'Quel texte souhaitez-vous voir sur JuriThèque ?' },
    { value: 'suggestion',   label: '💡 Suggestion générale',               placeholder: 'Décrivez votre suggestion…' },
    { value: 'text_error',   label: '🐛 Signaler un bug ou une erreur',     placeholder: 'Décrivez le problème rencontré…' },
  ],
  other: [
    { value: 'suggestion',   label: '💡 Suggestion',                        placeholder: 'Votre message…' },
    { value: 'text_error',   label: '🐛 Signaler un problème',              placeholder: 'Décrivez le problème…' },
  ],
}

const CONTENT_TYPE_LABELS = {
  law:        'un texte juridique',
  guide:      'un guide thématique',
  suggestion: 'une suggestion',
  other:      'quelque chose',
}

// ── Modal ─────────────────────────────────────────────────────────────────────
export default function ReportModal({
  isOpen,
  onClose,
  contentType = 'law',
  subject     = '',
  subjectUrl  = '',
  lawId       = null,
  guideSlug   = null,
}) {
  const [reportType,     setReportType]     = useState('')
  const [comment,        setComment]        = useState('')
  const [reporterEmail,  setReporterEmail]  = useState('')
  const [status,         setStatus]         = useState('idle') // idle | loading | success | error
  const overlayRef = useRef(null)

  const types = REPORT_TYPES[contentType] || REPORT_TYPES.other
  const selectedType = types.find(t => t.value === reportType)

  // Reset form when modal opens
  useEffect(() => {
    if (isOpen) {
      setReportType('')
      setComment('')
      setReporterEmail('')
      setStatus('idle')
    }
  }, [isOpen])

  // Close on Escape
  useEffect(() => {
    if (!isOpen) return
    const handler = (e) => { if (e.key === 'Escape') onClose() }
    document.addEventListener('keydown', handler)
    return () => document.removeEventListener('keydown', handler)
  }, [isOpen, onClose])

  // Block body scroll
  useEffect(() => {
    if (isOpen) document.body.style.overflow = 'hidden'
    else        document.body.style.overflow = ''
    return () => { document.body.style.overflow = '' }
  }, [isOpen])

  if (!isOpen) return null

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!reportType) return
    setStatus('loading')
    try {
      await submitReport({
        content_type:   contentType,
        report_type:    reportType,
        subject:        subject || undefined,
        subject_url:    subjectUrl || window.location.href,
        law_id:         lawId    || undefined,
        guide_slug:     guideSlug|| undefined,
        comment:        comment  || undefined,
        reporter_email: reporterEmail || undefined,
      })
      setStatus('success')
    } catch (err) {
      console.error(err)
      setStatus('error')
    }
  }

  // Click on overlay → close
  const handleOverlayClick = (e) => {
    if (e.target === overlayRef.current) onClose()
  }

  return (
    <div
      ref={overlayRef}
      onClick={handleOverlayClick}
      className="fixed inset-0 z-[9999] flex items-center justify-center p-4"
      style={{ background: 'rgba(10,20,40,0.65)', backdropFilter: 'blur(4px)' }}
    >
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md overflow-hidden animate-fade-in">

        {/* ── Header ─────────────────────────────────────────────────── */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-gray-100">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-gold/10 flex items-center justify-center">
              <Flag size={15} className="text-gold" />
            </div>
            <div>
              <h2 className="text-sm font-semibold text-navy">
                {contentType === 'suggestion' ? 'Envoyer une suggestion' : 'Signaler une erreur'}
              </h2>
              {subject && (
                <p className="text-xs text-navy-500 line-clamp-1 max-w-[280px]">{subject}</p>
              )}
            </div>
          </div>
          <button
            onClick={onClose}
            className="w-7 h-7 rounded-lg bg-gray-100 hover:bg-gray-200 flex items-center justify-center transition-colors"
          >
            <X size={13} className="text-navy" />
          </button>
        </div>

        {/* ── Success state ───────────────────────────────────────────── */}
        {status === 'success' ? (
          <div className="px-5 py-10 flex flex-col items-center gap-3 text-center">
            <div className="w-14 h-14 rounded-full bg-emerald-50 flex items-center justify-center">
              <CheckCircle size={28} className="text-emerald-500" />
            </div>
            <h3 className="font-semibold text-navy">Merci pour votre signalement !</h3>
            <p className="text-sm text-navy-500 max-w-xs">
              Votre retour a bien été enregistré. Notre équipe le traitera dans les meilleurs délais.
            </p>
            <button
              onClick={onClose}
              className="mt-2 px-5 py-2 bg-navy text-white rounded-lg text-sm font-medium hover:bg-gold hover:text-navy transition-colors"
            >
              Fermer
            </button>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="px-5 py-5 space-y-4">

            {/* ── Error state ──────────────────────────────────────────── */}
            {status === 'error' && (
              <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-lg">
                <AlertCircle size={14} className="text-red-500 flex-shrink-0" />
                <p className="text-xs text-red-700">Une erreur est survenue. Réessayez ou écrivez-nous à contact@juritheque.com</p>
              </div>
            )}

            {/* ── Type de signalement ──────────────────────────────────── */}
            <div>
              <label className="block text-xs font-semibold text-navy mb-2">
                Type de signalement <span className="text-red-500">*</span>
              </label>
              <div className="space-y-2">
                {types.map(type => (
                  <label
                    key={type.value}
                    className={`flex items-center gap-3 px-3 py-2.5 rounded-lg border cursor-pointer transition-all ${
                      reportType === type.value
                        ? 'border-gold bg-gold/5'
                        : 'border-gray-200 bg-white hover:border-gray-300 hover:bg-gray-50'
                    }`}
                  >
                    <input
                      type="radio"
                      name="reportType"
                      value={type.value}
                      checked={reportType === type.value}
                      onChange={() => setReportType(type.value)}
                      className="sr-only"
                    />
                    <div className={`w-4 h-4 rounded-full border-2 flex items-center justify-center flex-shrink-0 transition-colors ${
                      reportType === type.value ? 'border-gold' : 'border-gray-300'
                    }`}>
                      {reportType === type.value && (
                        <div className="w-2 h-2 rounded-full bg-gold" />
                      )}
                    </div>
                    <span className="text-sm text-navy">{type.label}</span>
                  </label>
                ))}
              </div>
            </div>

            {/* ── Commentaire ──────────────────────────────────────────── */}
            {reportType && (
              <div>
                <label className="block text-xs font-semibold text-navy mb-1.5">
                  Détails <span className="text-navy-400 font-normal">(optionnel)</span>
                </label>
                <textarea
                  value={comment}
                  onChange={e => setComment(e.target.value)}
                  placeholder={selectedType?.placeholder || 'Précisez votre signalement…'}
                  rows={3}
                  className="w-full px-3 py-2.5 text-sm border border-gray-200 rounded-lg text-navy placeholder-gray-400 focus:outline-none focus:border-gold focus:ring-1 focus:ring-gold/20 resize-none"
                />
              </div>
            )}

            {/* ── Email ────────────────────────────────────────────────── */}
            {reportType && (
              <div>
                <label className="block text-xs font-semibold text-navy mb-1.5">
                  Votre email <span className="text-navy-400 font-normal">(pour recevoir une réponse)</span>
                </label>
                <input
                  type="email"
                  value={reporterEmail}
                  onChange={e => setReporterEmail(e.target.value)}
                  placeholder="votre@email.com"
                  className="w-full px-3 py-2.5 text-sm border border-gray-200 rounded-lg text-navy placeholder-gray-400 focus:outline-none focus:border-gold focus:ring-1 focus:ring-gold/20"
                />
              </div>
            )}

            {/* ── Submit ───────────────────────────────────────────────── */}
            <div className="flex gap-2 pt-1">
              <button
                type="button"
                onClick={onClose}
                className="flex-1 py-2.5 border border-gray-200 text-navy text-sm font-medium rounded-lg hover:bg-gray-50 transition-colors"
              >
                Annuler
              </button>
              <button
                type="submit"
                disabled={!reportType || status === 'loading'}
                className="flex-1 py-2.5 bg-navy text-white text-sm font-semibold rounded-lg hover:bg-gold hover:text-navy transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {status === 'loading' ? (
                  <><Loader2 size={14} className="animate-spin" /> Envoi…</>
                ) : (
                  <>Envoyer le signalement</>
                )}
              </button>
            </div>

            <p className="text-[10px] text-navy-400 text-center">
              Vos signalements sont traités par l'équipe JuriThèque. Merci pour votre contribution.
            </p>
          </form>
        )}
      </div>
    </div>
  )
}

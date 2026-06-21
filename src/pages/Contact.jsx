import { useState } from 'react'
import { Link } from 'react-router-dom'
import { ArrowLeft, Mail, MessageSquare, Send, CheckCircle2, MapPin, Clock, User, Briefcase } from 'lucide-react'
import { supabase } from '../lib/supabase'
import { useSEO } from '../hooks/useSEO'

const SUBJECTS = [
  'Question sur un texte juridique',
  'Signaler une erreur',
  'Demande de partenariat',
  'Problème technique',
  'Autre',
]

export default function Contact() {
  useSEO({
    title: 'Contact — JuriThèque',
    description: 'Contactez l\'équipe JuriThèque pour toute question sur un texte juridique, signalement d\'erreur, demande de partenariat ou problème technique.',
    canonical: '/contact',
    type: 'website',
  })

  const [form, setForm]       = useState({ name: '', email: '', subject: '', message: '' })
  const [loading, setLoading] = useState(false)
  const [sent, setSent]       = useState(false)
  const [error, setError]     = useState('')

  const set = (k, v) => setForm(f => ({ ...f, [k]: v }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      const { error: sbError } = await supabase.from('reports').insert({
        content_type:   'contact',
        report_type:    'suggestion',
        subject:        form.subject,
        comment:        `[${form.name}]\n\n${form.message}`,
        reporter_email: form.email,
      })
      if (sbError) throw sbError
      setSent(true)
    } catch {
      setError('Une erreur est survenue. Réessayez ou écrivez-nous directement à contact@juritheque.com')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-[#f8fafc] pt-16">
      {/* Header */}
      <div className="bg-navy text-white py-12">
        <div className="max-w-5xl mx-auto px-4 sm:px-6">
          <Link to="/" className="flex items-center gap-1.5 text-white/60 text-xs mb-4 hover:text-gold transition-colors">
            <ArrowLeft size={12} /> Retour à l'accueil
          </Link>
          <div className="flex items-center gap-3 mb-2">
            <div className="w-10 h-10 bg-gold/20 rounded-xl flex items-center justify-center">
              <MessageSquare size={20} className="text-gold" />
            </div>
            <h1 className="font-playfair font-bold text-3xl">Contactez-nous</h1>
          </div>
          <p className="text-white/60 text-sm mt-1">Nous répondons généralement sous 24–48h</p>
        </div>
      </div>

      <div className="max-w-5xl mx-auto px-4 sm:px-6 py-12">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">

          {/* Info cards */}
          <div className="space-y-4">
            <div className="bg-white rounded-2xl border border-gray-100 p-5">
              <div className="w-9 h-9 bg-gold/10 rounded-xl flex items-center justify-center mb-3">
                <Mail size={16} className="text-gold" />
              </div>
              <h3 className="font-semibold text-navy text-sm mb-1">Email</h3>
              <a href="mailto:contact@juritheque.com" className="text-sm text-navy-600 hover:text-gold transition-colors">
                contact@juritheque.com
              </a>
            </div>

            <div className="bg-white rounded-2xl border border-gray-100 p-5">
              <div className="w-9 h-9 bg-gold/10 rounded-xl flex items-center justify-center mb-3">
                <Clock size={16} className="text-gold" />
              </div>
              <h3 className="font-semibold text-navy text-sm mb-1">Temps de réponse</h3>
              <p className="text-sm text-navy-600">24 à 48 heures ouvrables</p>
            </div>

            <div className="bg-white rounded-2xl border border-gray-100 p-5">
              <div className="w-9 h-9 bg-gold/10 rounded-xl flex items-center justify-center mb-3">
                <MapPin size={16} className="text-gold" />
              </div>
              <h3 className="font-semibold text-navy text-sm mb-1">Localisation</h3>
              <p className="text-sm text-navy-600">Maroc 🇲🇦</p>
              <p className="text-xs text-navy-400 mt-1">Service disponible en français et arabe</p>
            </div>

            {/* Arabic note */}
            <div className="bg-navy/5 rounded-2xl border border-navy/10 p-5">
              <p className="font-arabic text-right text-sm text-navy-700 leading-loose">
                يمكنكم التواصل معنا باللغة العربية أو الفرنسية.<br/>
                نرحب بجميع استفساراتكم القانونية.
              </p>
            </div>
          </div>

          {/* Form */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-2xl border border-gray-100 p-6 sm:p-8">
              {sent ? (
                <div className="flex flex-col items-center justify-center py-12 text-center">
                  <div className="w-16 h-16 bg-emerald-50 rounded-full flex items-center justify-center mb-4">
                    <CheckCircle2 size={32} className="text-emerald-500" />
                  </div>
                  <h3 className="font-playfair font-bold text-navy text-xl mb-2">Message envoyé !</h3>
                  <p className="text-navy-600 text-sm mb-6">Nous vous répondrons dans les plus brefs délais à <strong>{form.email}</strong></p>
                  <button
                    onClick={() => { setSent(false); setForm({ name: '', email: '', subject: '', message: '' }) }}
                    className="px-5 py-2.5 bg-navy text-white rounded-xl text-sm font-medium hover:bg-gold hover:text-navy transition-colors"
                  >
                    Envoyer un autre message
                  </button>
                </div>
              ) : (
                <>
                  <h2 className="font-playfair font-bold text-navy text-xl mb-6">Envoyer un message</h2>

                  {error && (
                    <div className="p-3.5 bg-red-50 border border-red-200 rounded-xl mb-4 text-sm text-red-600">
                      {error}
                    </div>
                  )}

                  <form onSubmit={handleSubmit} className="space-y-4">
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-xs font-medium text-navy-700 mb-1">Nom complet *</label>
                        <div className="relative">
                          <User size={13} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                          <input
                            type="text"
                            required
                            value={form.name}
                            onChange={e => set('name', e.target.value)}
                            placeholder="Votre nom"
                            className="w-full pl-8 pr-3 py-2.5 text-sm border border-gray-200 rounded-xl focus:outline-none focus:border-gold focus:ring-2 focus:ring-gold/20"
                          />
                        </div>
                      </div>
                      <div>
                        <label className="block text-xs font-medium text-navy-700 mb-1">Email *</label>
                        <div className="relative">
                          <Mail size={13} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                          <input
                            type="email"
                            required
                            value={form.email}
                            onChange={e => set('email', e.target.value)}
                            placeholder="votre@email.com"
                            className="w-full pl-8 pr-3 py-2.5 text-sm border border-gray-200 rounded-xl focus:outline-none focus:border-gold focus:ring-2 focus:ring-gold/20"
                          />
                        </div>
                      </div>
                    </div>

                    <div>
                      <label className="block text-xs font-medium text-navy-700 mb-1">Sujet *</label>
                      <div className="relative">
                        <Briefcase size={13} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                        <select
                          required
                          value={form.subject}
                          onChange={e => set('subject', e.target.value)}
                          className="w-full pl-8 pr-3 py-2.5 text-sm border border-gray-200 rounded-xl focus:outline-none focus:border-gold appearance-none bg-white"
                        >
                          <option value="" disabled>Sélectionner un sujet...</option>
                          {SUBJECTS.map(s => <option key={s}>{s}</option>)}
                        </select>
                      </div>
                    </div>

                    <div>
                      <label className="block text-xs font-medium text-navy-700 mb-1">Message *</label>
                      <textarea
                        required
                        rows={6}
                        value={form.message}
                        onChange={e => set('message', e.target.value)}
                        placeholder="Décrivez votre question ou demande..."
                        className="w-full px-3 py-2.5 text-sm border border-gray-200 rounded-xl focus:outline-none focus:border-gold focus:ring-2 focus:ring-gold/20 resize-none"
                      />
                    </div>

                    <button
                      type="submit"
                      disabled={loading}
                      className="w-full py-3 bg-navy text-white rounded-xl text-sm font-bold hover:bg-gold hover:text-navy transition-all duration-200 disabled:opacity-50 flex items-center justify-center gap-2"
                    >
                      {loading ? (
                        <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
                        </svg>
                      ) : <Send size={15} />}
                      {loading ? 'Envoi en cours...' : 'Envoyer le message'}
                    </button>
                  </form>
                </>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

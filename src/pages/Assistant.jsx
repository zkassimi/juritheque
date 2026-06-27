import { useState, useRef, useEffect } from 'react'
import {
  Send, Plus, Bot, User, Sparkles, MessageSquare, Lock,
  Menu, X as XIcon, ExternalLink, BookOpen, Bell, Scale,
  Building2, AlertTriangle, Search, ChevronRight,
} from 'lucide-react'
import { Link, useLocation } from 'react-router-dom'
import { useLang } from '../contexts/LangContext'
import { useAuth } from '../contexts/AuthContext'
import { useSEO } from '../hooks/useSEO'
import { retrieveRelevantSitePages } from '../lib/api'

// ── Config ────────────────────────────────────────────────────────────────────
const OPENROUTER_KEY = import.meta.env.VITE_OPENROUTER_KEY || ''

// Modèles disponibles (via VITE_AI_MODEL dans .env) :
//   - 'deepseek/deepseek-chat'         → DeepSeek V3, ~$0.14/1M tokens — défaut
//   - 'qwen/qwen-2.5-72b-instruct'     → Qwen 2.5, ~$0.13/1M tokens
//   - 'google/gemini-2.5-flash'        → Gemini Flash, ~$0.15/1M tokens
//   - 'anthropic/claude-3-5-haiku'     → meilleur arabe, ~$0.80/1M tokens
const AI_MODEL = import.meta.env.VITE_AI_MODEL || 'deepseek/deepseek-chat'

const BASE_URL = 'https://juritheque.com'

// ── Messages d'erreur professionnels (sans mention d'OpenRouter) ──────────────
function friendlyError(rawMessage = '') {
  const msg = rawMessage.toLowerCase()
  if (msg.includes('credit') || msg.includes('quota') || msg.includes('billing'))
    return 'Notre assistant connaît une forte demande en ce moment. Veuillez réessayer dans quelques instants.'
  if (msg.includes('rate limit') || msg.includes('too many'))
    return 'Trop de requêtes simultanées. Veuillez patienter quelques secondes avant de réessayer.'
  if (msg.includes('timeout') || msg.includes('network') || msg.includes('fetch'))
    return 'La connexion a été interrompue. Vérifiez votre connexion internet et réessayez.'
  if (msg.includes('model') || msg.includes('unavailable'))
    return 'Le service est temporairement indisponible. Réessayez dans quelques instants.'
  if (msg.includes('401') || msg.includes('unauthorized') || msg.includes('auth') || msg.includes('key'))
    return 'Clé API invalide ou manquante. Veuillez contacter l\'administrateur du site.'
  if (msg.includes('403') || msg.includes('forbidden'))
    return 'Accès refusé. Veuillez contacter l\'administrateur du site.'
  return 'Une erreur est survenue. Veuillez réessayer dans quelques instants.'
}

// ── System prompt ─────────────────────────────────────────────────────────────
const buildSystemPrompt = (contextBlock) => `Tu es JuriThèque Assistant, expert en droit marocain bilingue (français/arabe).

RÈGLES :
1. Si des textes JuriThèque sont fournis dans le contexte, utilise-les en priorité. Cite les textes par leur **titre uniquement** (ex: "selon le Code de la Famille").
2. Si le contexte est vide ou insuffisant, réponds QUAND MÊME avec une réponse complète et détaillée basée sur tes connaissances générales du droit marocain. Ajoute une note courte "ℹ️ À vérifier avec les textes officiels." Ne dis jamais "je ne peux pas répondre sans contexte".
3. Ne JAMAIS inventer un numéro de loi, un article précis ou une sanction spécifique que tu ne connais pas avec certitude.
4. Réponds dans la même langue que la question (français → français, arabe → arabe).
5. Tu ne remplaces pas un avocat — mentionne-le brièvement si la situation est complexe.
6. Utilise **gras** et listes à puces pour structurer les réponses. Sois concis et pratique.
7. NE JAMAIS reproduire les URLs, métadonnées (URL, Résumé, Type, Domaine) ou la structure brute du contexte. L'interface affiche automatiquement les liens cliquables sous ta réponse.
8. NE JAMAIS écrire "URL :", "Résumé :", "Type :", "Domaine :" dans ta réponse — ces données sont affichées séparément.

${contextBlock ? `━━━ TEXTES JURITHEQUE PERTINENTS ━━━\n${contextBlock}\n━━━ FIN ━━━\n` : ''}

Domaines couverts : droit civil (DOC, Moudawwana), droit du travail (Loi 65-99), droit pénal (Code pénal), droit commercial (Code de Commerce), droit administratif, droit fiscal (CGI), droit de la famille, procédure civile et pénale, droit des sociétés, droit immobilier, droit constitutionnel (Constitution 2011).`

// ── Données ───────────────────────────────────────────────────────────────────
const QUICK_PROMPTS = [
  { fr: "Je cherche la loi sur la SARL au Maroc",           ar: "أبحث عن قانون شركة م.م.م في المغرب" },
  { fr: "Quels textes concernent le licenciement ?",        ar: "ما هي النصوص المتعلقة بالفصل من العمل؟" },
  { fr: "Je veux comprendre le bail commercial",            ar: "أريد فهم عقد الإيجار التجاري" },
  { fr: "Y a-t-il des textes récents en droit du travail ?",ar: "هل هناك نصوص حديثة في قانون الشغل؟" },
  { fr: "Montre-moi les textes liés au divorce",            ar: "ما هي النصوص المتعلقة بالطلاق؟" },
  { fr: "ما هي النصوص المتعلقة بمدونة الأسرة؟",            ar: "ما هي النصوص المتعلقة بمدونة الأسرة؟" },
]

// ── Helpers ───────────────────────────────────────────────────────────────────
const SOURCE_META = {
  law:         { icon: Scale,     label: 'Texte de loi',    color: 'text-blue-600 bg-blue-50 border-blue-100' },
  guide:       { icon: BookOpen,  label: 'Guide thématique', color: 'text-amber-600 bg-amber-50 border-amber-100' },
  domain:      { icon: Building2, label: 'Domaine',          color: 'text-emerald-600 bg-emerald-50 border-emerald-100' },
  static_page: { icon: Search,    label: 'Page',             color: 'text-purple-600 bg-purple-50 border-purple-100' },
  watch:       { icon: Bell,      label: 'Veille juridique', color: 'text-rose-600 bg-rose-50 border-rose-100' },
}

function buildContextBlock(pages) {
  if (!pages || pages.length === 0) return ''
  return pages.map((p, i) => {
    const lines = [
      `${i + 1}. ${p.title}`,
      `   Type : ${p.document_type || p.source_type}`,
      `   URL  : ${BASE_URL}${p.url}`,
    ]
    if (p.legal_domain) lines.push(`   Domaine : ${p.legal_domain}`)
    if (p.summary)      lines.push(`   Résumé : ${p.summary.slice(0, 200)}`)
    else if (p.description) lines.push(`   Description : ${p.description.slice(0, 150)}`)
    if (p.keywords?.length) lines.push(`   Mots-clés : ${p.keywords.slice(0, 5).join(', ')}`)
    return lines.join('\n')
  }).join('\n\n')
}

// ── Markdown renderer léger (sans dépendance externe) ────────────────────────
function MarkdownLine({ line, isUser }) {
  const textColor = isUser ? 'text-white' : 'text-white/90'
  const boldColor  = isUser ? 'text-white font-semibold' : 'text-gold font-semibold'

  // Rendre le texte inline (gras, italique, code inline, URLs)
  const renderInline = (text) => {
    const parts = text.split(/(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`|https?:\/\/\S+)/g)
    return parts.map((part, i) => {
      if (part.startsWith('**') && part.endsWith('**'))
        return <strong key={i} className={boldColor}>{part.slice(2,-2)}</strong>
      if (part.startsWith('*') && part.endsWith('*'))
        return <em key={i} className="italic opacity-90">{part.slice(1,-1)}</em>
      if (part.startsWith('`') && part.endsWith('`'))
        return <code key={i} className="bg-white/10 px-1 py-0.5 rounded text-xs font-mono">{part.slice(1,-1)}</code>
      if (part.startsWith('http://') || part.startsWith('https://')) {
        // Extraire le titre lisible depuis l'URL (dernier segment sans tirets)
        const slug = part.replace(/\/$/, '').split('/').pop() || part
        const label = slug.replace(/-/g, ' ').replace(/\b\w/g, c => c.toUpperCase())
        return (
          <a key={i} href={part} target="_blank" rel="noopener noreferrer"
            className="underline decoration-gold/50 hover:decoration-gold text-gold/90 hover:text-gold transition-colors"
          >
            {label || part}
          </a>
        )
      }
      return part
    })
  }

  // Heading ##
  if (line.startsWith('## '))
    return <p className={`font-bold text-sm mt-3 mb-1 ${boldColor}`}>{renderInline(line.slice(3))}</p>
  // Heading #
  if (line.startsWith('# '))
    return <p className={`font-bold text-base mt-3 mb-1 ${boldColor}`}>{renderInline(line.slice(2))}</p>
  // Séparateur ━ ou ---
  if (/^[━─—-]{3,}$/.test(line.trim()))
    return <hr className="border-white/10 my-2" />
  // Liste à puces
  if (line.startsWith('- ') || line.startsWith('• ') || line.startsWith('* '))
    return (
      <div className={`flex items-start gap-2 ${textColor}`}>
        <span className="text-gold mt-0.5 flex-shrink-0 text-xs">▸</span>
        <span>{renderInline(line.replace(/^[-•*] /, ''))}</span>
      </div>
    )
  // Liste numérotée
  const numMatch = line.match(/^(\d+)\.\s(.+)/)
  if (numMatch)
    return (
      <div className={`flex items-start gap-2 ${textColor}`}>
        <span className="text-gold flex-shrink-0 font-bold text-xs min-w-[16px]">{numMatch[1]}.</span>
        <span>{renderInline(numMatch[2])}</span>
      </div>
    )
  // Masquer les marqueurs de contexte et métadonnées brutes
  if (line.startsWith('━━━')) return null
  if (/^\s*(URL|Résumé|Type|Domaine|Mots-clés)\s*[:.]\*?\s*https?:\/\//.test(line)) return null
  if (/^\s*(URL|Type|Domaine)\s*[:.]\*?\s/.test(line) && line.length < 120) return null
  // Ligne vide
  if (!line.trim()) return <div className="h-2" />
  // Texte normal
  return <p className={textColor}>{renderInline(line)}</p>
}

function MessageContent({ content, isUser }) {
  return (
    <div className="text-sm leading-relaxed space-y-0.5">
      {content.split('\n').map((line, i) => (
        <MarkdownLine key={i} line={line} isUser={isUser} />
      ))}
    </div>
  )
}

// ── Composants UI ─────────────────────────────────────────────────────────────
function SourcePageCard({ page }) {
  const meta = SOURCE_META[page.source_type] || SOURCE_META.static_page
  const Icon = meta.icon
  return (
    <a
      href={`${BASE_URL}${page.url}`}
      target="_blank"
      rel="noopener noreferrer"
      className="flex items-start gap-3 p-3 bg-white rounded-xl border border-gray-100 hover:border-gold hover:shadow-sm transition-all group"
    >
      <div className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 border ${meta.color}`}>
        <Icon size={13} />
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-1.5 mb-0.5">
          <span className={`text-[10px] font-semibold px-1.5 py-0.5 rounded-full border ${meta.color}`}>
            {meta.label}
          </span>
          {page.legal_domain && (
            <span className="text-[10px] text-navy-400">{page.legal_domain}</span>
          )}
        </div>
        <p className="text-xs font-semibold text-navy group-hover:text-gold transition-colors truncate leading-snug">
          {page.title}
        </p>
        {(page.summary || page.description) && (
          <p className="text-[11px] text-navy-500 mt-0.5 line-clamp-2 leading-relaxed">
            {(page.summary || page.description || '').slice(0, 100)}
          </p>
        )}
      </div>
      <ExternalLink size={11} className="text-gray-300 group-hover:text-gold flex-shrink-0 mt-1 transition-colors" />
    </a>
  )
}

function SourcePagesSection({ pages }) {
  if (!pages || pages.length === 0) return (
    <div className="mt-3 flex items-center gap-1.5 text-xs text-navy-400 italic">
      <AlertTriangle size={11} />
      Aucune page JuriThèque directement liée à cette question.
    </div>
  )
  return (
    <div className="mt-3">
      <p className="text-[10px] font-semibold uppercase tracking-widest text-navy-400 mb-2 flex items-center gap-1">
        <ChevronRight size={10} /> Pages utiles sur JuriThèque
      </p>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
        {pages.map((p, i) => <SourcePageCard key={i} page={p} />)}
      </div>
    </div>
  )
}

function ChatMessage({ msg, lang, onFollowUp }) {
  const isUser = msg.role === 'user'
  return (
    <div className={`flex gap-3 ${isUser ? 'flex-row-reverse' : ''}`}>
      <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${isUser ? 'bg-gold' : 'bg-navy-800'}`}>
        {isUser ? <User size={14} className="text-navy" /> : <Bot size={14} className="text-gold" />}
      </div>
      <div className={`max-w-[82%] ${isUser ? '' : 'flex-1'}`}>
        {/* Bulle */}
        <div className={`rounded-2xl px-4 py-3 ${isUser ? 'bubble-user rounded-tr-sm' : 'bubble-ai rounded-tl-sm'}`}>
          <MessageContent content={msg.content} isUser={isUser} />
          {/* Curseur clignotant pendant le streaming */}
          {msg.streaming && (
            <span className="inline-block w-2 h-4 bg-gold/80 ml-0.5 animate-pulse rounded-sm align-middle" />
          )}
        </div>

        {/* Pages utiles + follow-up — seulement pour les messages IA terminés */}
        {!isUser && !msg.streaming && (
          <div className="mt-1 px-1 space-y-3">
            {msg.sourcePages !== undefined && (
              <SourcePagesSection pages={msg.sourcePages} />
            )}
            {msg.followUps?.length > 0 && (
              <div className="flex flex-wrap gap-2 mt-2">
                {msg.followUps.map((q, i) => (
                  <button
                    key={i}
                    onClick={() => onFollowUp(q)}
                    className="text-xs px-3 py-1.5 bg-white border border-gray-100 rounded-full text-navy-600 hover:border-gold hover:text-gold transition-colors shadow-sm"
                  >
                    {q}
                  </button>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

function TypingIndicator({ searching }) {
  return (
    <div className="flex gap-3">
      <div className="w-8 h-8 rounded-full bg-navy-800 flex items-center justify-center flex-shrink-0">
        <Bot size={14} className="text-gold" />
      </div>
      <div className="bubble-ai rounded-2xl rounded-tl-sm px-4 py-3">
        {searching ? (
          <p className="text-xs text-white/60 flex items-center gap-1.5">
            <Search size={11} className="animate-pulse text-gold" />
            Recherche dans JuriThèque…
          </p>
        ) : (
          <div className="flex gap-1.5 items-center h-4">
            <span className="typing-dot" />
            <span className="typing-dot" />
            <span className="typing-dot" />
          </div>
        )}
      </div>
    </div>
  )
}

// ── LocalStorage ──────────────────────────────────────────────────────────────
const STORAGE_KEY    = 'juritheque_conversations'
const STORAGE_ACTIVE = 'juritheque_active_conv'

function loadConversations() {
  try {
    const saved = localStorage.getItem(STORAGE_KEY)
    if (saved) {
      const parsed = JSON.parse(saved)
      if (Array.isArray(parsed) && parsed.length > 0) return parsed
    }
  } catch {}
  return [{ id: 1, title: 'Nouvelle conversation', messages: [] }]
}

function loadActiveId(conversations) {
  try {
    const saved = localStorage.getItem(STORAGE_ACTIVE)
    if (saved) {
      const id = JSON.parse(saved)
      if (conversations.find(c => c.id === id)) return id
    }
  } catch {}
  return conversations[0].id
}

// ── Composant principal ───────────────────────────────────────────────────────
export default function Assistant() {
  const { t, lang } = useLang()
  const { user }    = useAuth()

  useSEO({
    title:       'Assistant Juridique IA — Droit marocain en français et arabe',
    description: 'Posez vos questions juridiques à notre assistant IA spécialisé en droit marocain. Réponses basées sur les textes officiels disponibles dans JuriThèque.',
    canonical:   '/assistant',
    type:        'website',
  })

  const [conversations, setConversations] = useState(loadConversations)
  const [activeId, setActiveId]           = useState(() => loadActiveId(loadConversations()))
  const [input, setInput]                 = useState('')
  const [typing, setTyping]               = useState(false)
  const [searching, setSearching]         = useState(false)
  const [msgLang, setMsgLang]             = useState(lang)
  const [mobileSidebar, setMobileSidebar] = useState(false)
  const messagesContainerRef = useRef(null)
  const textareaRef          = useRef(null)
  const location             = useLocation()

  const activeConv = conversations.find(c => c.id === activeId)

  // Pré-remplir depuis une fiche loi ("Demander à l'IA")
  useEffect(() => {
    if (location.state?.prefill) {
      setInput(location.state.prefill)
      setTimeout(() => {
        textareaRef.current?.focus()
        // Ajuster la hauteur du textarea au contenu pré-rempli
        if (textareaRef.current) {
          textareaRef.current.style.height = 'auto'
          textareaRef.current.style.height = Math.min(textareaRef.current.scrollHeight, 160) + 'px'
        }
      }, 100)
      // Nettoyer l'état pour éviter le re-remplissage si l'utilisateur navigue en arrière
      window.history.replaceState({}, document.title)
    }
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(conversations)) } catch {}
  }, [conversations])

  useEffect(() => {
    try { localStorage.setItem(STORAGE_ACTIVE, JSON.stringify(activeId)) } catch {}
  }, [activeId])

  useEffect(() => {
    const el = messagesContainerRef.current
    if (el) el.scrollTop = el.scrollHeight
  }, [activeConv?.messages, typing, searching])

  // ── Génère des questions de suivi à partir de la réponse IA ─────────────────
  const extractFollowUps = (text, question) => {
    // Quelques suggestions contextuelles simples basées sur les mots-clés
    const q = (question + ' ' + text).toLowerCase()
    const suggestions = []
    if (q.includes('licenci') || q.includes('travail') || q.includes('contrat'))
      suggestions.push('Quels sont les délais de préavis au Maroc ?', 'Quelle indemnité en cas de licenciement abusif ?')
    if (q.includes('sarl') || q.includes('société') || q.includes('commercial'))
      suggestions.push('Quel est le capital minimum pour une SARL ?', 'Comment dissoudre une SARL ?')
    if (q.includes('divorce') || q.includes('famille') || q.includes('moudawwana'))
      suggestions.push('Quelles sont les conditions du divorce par consentement mutuel ?', 'Comment fonctionne la garde des enfants ?')
    if (q.includes('bail') || q.includes('loyer') || q.includes('locataire'))
      suggestions.push('Quelle est la procédure d\'expulsion ?', 'Comment calculer la révision du loyer ?')
    if (q.includes('chèque') || q.includes('recouvrement') || q.includes('dette'))
      suggestions.push('Quels recours pour un chèque sans provision ?', 'Quelle est la prescription des dettes commerciales ?')
    return suggestions.slice(0, 3)
  }

  // ── Envoi d'un message avec streaming ──────────────────────────────────────
  const sendMessage = async (overrideText) => {
    const userText = (overrideText || input).trim()
    if (!userText || typing) return
    const userMsg  = { role: 'user', content: userText }
    setInput('')

    const currentMessages = activeConv?.messages || []
    setConversations(prev => prev.map(c =>
      c.id === activeId
        ? { ...c, title: userText.slice(0, 45), messages: [...c.messages, userMsg] }
        : c
    ))

    // ── Étape 1 : Recherche interne JuriThèque ───────────────────────────────
    setSearching(true)
    let sourcePages = []
    try {
      sourcePages = await retrieveRelevantSitePages(userText, { limit: 6 })
    } catch (_) {}
    setSearching(false)
    setTyping(true)

    // ── Étape 2 : Construire le contexte ────────────────────────────────────
    const contextBlock = buildContextBlock(sourcePages)
    const systemPrompt = buildSystemPrompt(contextBlock)

    // ── Étape 3 : Appel OpenRouter avec streaming SSE ────────────────────────
    try {
      const history = [...currentMessages, userMsg].map(m => ({
        role:    m.role === 'assistant' ? 'assistant' : 'user',
        content: m.content,
      }))

      const response = await fetch('https://openrouter.ai/api/v1/chat/completions', {
        method:  'POST',
        headers: {
          'Authorization': `Bearer ${OPENROUTER_KEY}`,
          'Content-Type':  'application/json',
          'HTTP-Referer':  'https://juritheque.com',
          'X-Title':       'JuriTheque Assistant',
        },
        body: JSON.stringify({
          model:       AI_MODEL,
          messages:    [{ role: 'system', content: systemPrompt }, ...history],
          max_tokens:  1500,
          temperature: 0.25,
          stream:      true,   // ← Streaming activé
        }),
      })

      if (!response.ok) {
        const err = await response.json().catch(() => ({}))
        throw new Error(err?.error?.message || `Erreur API (${response.status})`)
      }

      // Insérer un message vide "en cours de streaming"
      const streamingMsg = { role: 'assistant', content: '', sourcePages, streaming: true }
      setConversations(prev => prev.map(c =>
        c.id === activeId ? { ...c, messages: [...c.messages, streamingMsg] } : c
      ))

      // Lire le stream SSE
      const reader  = response.body.getReader()
      const decoder = new TextDecoder()
      let fullText  = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const chunk = decoder.decode(value, { stream: true })
        const lines = chunk.split('\n').filter(l => l.startsWith('data: '))

        for (const line of lines) {
          const data = line.slice(6).trim()
          if (data === '[DONE]') break
          try {
            const parsed = JSON.parse(data)
            const delta  = parsed.choices?.[0]?.delta?.content || ''
            if (!delta) continue
            fullText += delta
            // Mise à jour en temps réel du dernier message
            setConversations(prev => prev.map(c => {
              if (c.id !== activeId) return c
              const msgs = [...c.messages]
              msgs[msgs.length - 1] = { ...msgs[msgs.length - 1], content: fullText }
              return { ...c, messages: msgs }
            }))
          } catch { /* ligne SSE non-JSON (commentaire, vide) */ }
        }
      }

      // Finaliser : retirer le flag streaming, ajouter les follow-ups
      const followUps = extractFollowUps(fullText, userText)
      setConversations(prev => prev.map(c => {
        if (c.id !== activeId) return c
        const msgs = [...c.messages]
        msgs[msgs.length - 1] = {
          ...msgs[msgs.length - 1],
          content:  fullText || 'Désolé, je n\'ai pas pu générer une réponse.',
          streaming: false,
          followUps,
        }
        return { ...c, messages: msgs }
      }))

    } catch (err) {
      const errorText = `⚠️ **Service momentanément indisponible**\n\n${friendlyError(err.message)}`

      setConversations(prev => prev.map(c => {
        if (c.id !== activeId) return c
        const msgs = [...c.messages]
        // Remplacer le message en streaming s'il existe, sinon en ajouter un nouveau
        if (msgs[msgs.length - 1]?.streaming) {
          msgs[msgs.length - 1] = { role: 'assistant', content: errorText, sourcePages: [], streaming: false }
        } else {
          msgs.push({ role: 'assistant', content: errorText, sourcePages: [], streaming: false })
        }
        return { ...c, messages: msgs }
      }))
    } finally {
      setTyping(false)
      setSearching(false)
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage() }
  }

  const handleFollowUp = (question) => {
    setInput(question)
    sendMessage(question)
  }

  const newConversation = () => {
    const id = Date.now()
    setConversations(prev => [...prev, { id, title: 'Nouvelle conversation', messages: [] }])
    setActiveId(id)
  }

  const deleteConversation = (e, id) => {
    e.stopPropagation()
    setConversations(prev => {
      const updated = prev.filter(c => c.id !== id)
      if (updated.length === 0) {
        const newId = Date.now()
        setActiveId(newId)
        return [{ id: newId, title: 'Nouvelle conversation', messages: [] }]
      }
      if (id === activeId) setActiveId(updated[updated.length - 1].id)
      return updated
    })
  }

  // ── Garde : non connecté ────────────────────────────────────────────────────
  if (!user) {
    return (
      <div className="min-h-screen bg-[#f8fafc] pt-16 flex items-center justify-center">
        <div className="text-center max-w-sm mx-auto p-8 bg-white rounded-2xl border border-gray-100 shadow-sm">
          <div className="w-16 h-16 bg-navy rounded-2xl flex items-center justify-center mx-auto mb-4">
            <Lock size={24} className="text-gold" />
          </div>
          <h2 className="font-playfair font-bold text-navy text-xl mb-2">{t('assistant.login_required')}</h2>
          <p className="text-navy-600 text-sm mb-5">{t('assistant.login_msg')}</p>
          <Link to="/connexion" className="inline-flex px-6 py-2.5 bg-navy text-white rounded-xl text-sm font-semibold hover:bg-gold hover:text-navy transition-colors">
            {t('nav.login')}
          </Link>
        </div>
      </div>
    )
  }

  // ── Sidebar interne (desktop + mobile drawer) ───────────────────────────────
  const SidebarInner = ({ onClose }) => (
    <>
      <div className="flex items-center justify-between mb-4">
        <button
          onClick={() => { newConversation(); onClose?.() }}
          className="flex items-center gap-2 flex-1 px-4 py-2.5 bg-navy text-white rounded-xl text-sm font-medium hover:bg-gold hover:text-navy transition-colors"
        >
          <Plus size={15} /> {t('assistant.new_chat')}
        </button>
        {onClose && (
          <button onClick={onClose} className="ml-2 p-2 rounded-lg hover:bg-gray-100 text-navy-500">
            <XIcon size={16} />
          </button>
        )}
      </div>
      <p className="text-[10px] font-semibold uppercase tracking-widest text-navy-500 mb-2 px-1">{t('assistant.history')}</p>
      <div className="flex-1 overflow-y-auto space-y-1">
        {conversations.map(c => (
          <div
            key={c.id}
            className={`group/item w-full flex items-center gap-2 px-3 py-2.5 rounded-lg text-sm transition-colors ${
              c.id === activeId ? 'bg-navy text-white' : 'text-navy-700 hover:bg-gray-50'
            }`}
          >
            <button onClick={() => { setActiveId(c.id); onClose?.() }} className="flex items-center gap-2 flex-1 text-start truncate min-w-0">
              <MessageSquare size={13} className="flex-shrink-0" />
              <span className="truncate">{c.title}</span>
            </button>
            <button
              onClick={(e) => deleteConversation(e, c.id)}
              className={`flex-shrink-0 opacity-0 group-hover/item:opacity-100 transition-opacity p-0.5 rounded hover:bg-red-500/20 ${c.id === activeId ? 'text-white/60 hover:text-white' : 'text-navy-400 hover:text-red-500'}`}
            >×</button>
          </div>
        ))}
      </div>
      <div className="pt-3 border-t border-gray-100">
        <p className="text-[10px] font-semibold uppercase tracking-widest text-navy-500 mb-2 px-1">{t('assistant.suggestions')}</p>
        {QUICK_PROMPTS.slice(0, 3).map((p, i) => (
          <button
            key={i}
            onClick={() => { onClose?.(); sendMessage(lang === 'ar' ? p.ar : p.fr) }}
            className="w-full text-start px-3 py-2 text-xs text-navy-600 hover:text-gold hover:bg-gold/5 rounded-lg transition-colors"
          >
            <span className={lang === 'ar' ? 'font-arabic' : ''}>{lang === 'ar' ? p.ar : p.fr}</span>
          </button>
        ))}
      </div>
    </>
  )

  // ── Rendu principal ─────────────────────────────────────────────────────────
  return (
    <div className="h-screen bg-[#f8fafc] pt-16 flex">

      {/* Mobile sidebar overlay */}
      {mobileSidebar && (
        <div className="md:hidden fixed inset-0 z-50 flex">
          <div className="absolute inset-0 bg-black/40" onClick={() => setMobileSidebar(false)} />
          <aside className="relative z-10 w-72 bg-white h-full flex flex-col p-4 shadow-xl overflow-y-auto">
            <SidebarInner onClose={() => setMobileSidebar(false)} />
          </aside>
        </div>
      )}

      {/* Desktop Sidebar */}
      <aside className="hidden md:flex flex-col w-64 bg-white border-r border-gray-100 p-4">
        <SidebarInner />
      </aside>

      {/* Zone de chat */}
      <div className="flex-1 flex flex-col min-w-0">

        {/* Header du chat */}
        <div className="bg-white border-b border-gray-100 px-4 sm:px-6 py-3 flex items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <button
              onClick={() => setMobileSidebar(true)}
              className="md:hidden p-1.5 rounded-lg hover:bg-gray-100 text-navy-600 mr-1"
            >
              <Menu size={18} />
            </button>
            <div className="w-8 h-8 bg-navy rounded-lg flex items-center justify-center flex-shrink-0">
              <Bot size={15} className="text-gold" />
            </div>
            <div>
              <p className="font-semibold text-navy text-sm">{t('assistant.title')}</p>
              <p className="text-[10px] text-navy-500 hidden sm:flex items-center gap-1">
                <Sparkles size={9} className="text-gold" />
                {t('assistant.powered')} · Alimenté par JuriThèque
              </p>
            </div>
          </div>
          <div className="flex bg-gray-100 rounded-lg p-0.5">
            {['fr', 'ar'].map(l => (
              <button
                key={l}
                onClick={() => setMsgLang(l)}
                className={`px-3 py-1 rounded text-xs font-medium transition-colors ${msgLang === l ? 'bg-white text-navy shadow-sm' : 'text-navy-600'}`}
              >
                {l === 'fr' ? 'FR' : 'عربي'}
              </button>
            ))}
          </div>
        </div>

        {/* Messages */}
        <div ref={messagesContainerRef} className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-5">
          {activeConv?.messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-center py-8">
              <div className="w-16 h-16 bg-navy rounded-2xl flex items-center justify-center mb-4">
                <Bot size={28} className="text-gold" />
              </div>
              <h3 className="font-playfair font-semibold text-navy text-lg mb-2">{t('assistant.title')}</h3>
              <p className="text-navy-600 text-sm max-w-xs mb-2">{t('assistant.subtitle')}</p>
              <p className="text-navy-400 text-xs max-w-xs mb-8 flex items-center gap-1 justify-center">
                <Search size={10} className="text-gold" />
                Recherche automatiquement dans les textes JuriThèque
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 max-w-lg w-full">
                {QUICK_PROMPTS.map((p, i) => (
                  <button
                    key={i}
                    onClick={() => sendMessage(lang === 'ar' ? p.ar : p.fr)}
                    className="px-4 py-3 bg-white border border-gray-100 rounded-xl text-sm text-navy-700 hover:border-gold hover:text-gold text-start transition-colors shadow-sm"
                  >
                    <span className={lang === 'ar' ? 'font-arabic' : ''}>{lang === 'ar' ? p.ar : p.fr}</span>
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <>
              {activeConv.messages.map((msg, i) => (
                <ChatMessage key={i} msg={msg} lang={msgLang} onFollowUp={handleFollowUp} />
              ))}
              {(typing || searching) && <TypingIndicator searching={searching} />}
            </>
          )}
        </div>

        {/* Zone de saisie */}
        <div className="bg-white border-t border-gray-100 p-4 sticky bottom-0" style={{ paddingBottom: 'max(16px, env(safe-area-inset-bottom))' }}>
          <div className="max-w-4xl mx-auto flex gap-3 items-end">
            <textarea
              ref={textareaRef}
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={t('assistant.placeholder')}
              rows={1}
              className={`flex-1 px-4 py-3 bg-[#f8fafc] border border-gray-200 rounded-xl text-sm text-navy resize-none focus:outline-none focus:border-gold focus:ring-2 focus:ring-gold/20 ${lang === 'ar' ? 'font-arabic text-right' : ''}`}
              style={{ minHeight: 48, maxHeight: 160 }}
              onInput={e => {
                e.target.style.height = 'auto'
                e.target.style.height = Math.min(e.target.scrollHeight, 160) + 'px'
              }}
            />
            <button
              onClick={sendMessage}
              disabled={!input.trim() || typing}
              className="p-3 bg-navy text-white rounded-xl hover:bg-gold hover:text-navy transition-colors disabled:opacity-40 disabled:cursor-not-allowed flex-shrink-0"
            >
              <Send size={16} />
            </button>
          </div>
          <p className="text-[10px] text-center text-navy-400 mt-2">
            {t('assistant.powered')} · Les réponses sont informatives et ne remplacent pas un conseil juridique professionnel.
          </p>
        </div>
      </div>
    </div>
  )
}

import { useState, useEffect, useCallback } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { lawPath } from '../lib/lawUtils'
import {
  LayoutDashboard, FileText, Users, Plus, Edit2, Trash2,
  Search, TrendingUp, BarChart2, Eye, Shield, RefreshCw,
  CheckCircle2, XCircle, Save, X, Database, UserPlus, Mail, Lock, User, Briefcase,
  Video, Play, ExternalLink, Menu, AlertTriangle, Flag, CheckCheck, Clock, Inbox, Download,
  Bell, FileInput, Link2, RotateCcw
} from 'lucide-react'
import { useLang } from '../contexts/LangContext'
import { useAuth } from '../contexts/AuthContext'
import { supabase } from '../lib/supabase'
import { LAW_TYPES } from '../data/mockData'
import TypeBadge from '../components/ui/TypeBadge'
import StatusBadge from '../components/ui/StatusBadge'

// ── Helpers ──────────────────────────────────────────────────────────────────
function StatCard({ icon: Icon, label, value, sub, color }) {
  return (
    <div className="bg-white rounded-2xl border border-gray-100 p-5">
      <div className={`w-10 h-10 rounded-xl flex items-center justify-center mb-3 ${color}`}>
        <Icon size={18} />
      </div>
      <p className="font-playfair font-bold text-2xl text-navy">{value ?? '—'}</p>
      <p className="text-sm text-navy-600 mt-0.5">{label}</p>
      {sub && <p className="text-xs text-navy-400 mt-1">{sub}</p>}
    </div>
  )
}

function Toast({ msg, ok }) {
  return (
    <div className={`fixed bottom-6 right-6 z-50 flex items-center gap-2 px-4 py-3 rounded-xl shadow-lg text-sm font-medium ${ok ? 'bg-emerald-600 text-white' : 'bg-red-600 text-white'}`}>
      {ok ? <CheckCircle2 size={16} /> : <XCircle size={16} />}
      {msg}
    </div>
  )
}

// ── Main ──────────────────────────────────────────────────────────────────────
export default function Admin() {
  const { t } = useLang()
  const { user, isAdmin, isEditor } = useAuth()
  const navigate = useNavigate()

  const [section, setSection]     = useState(isAdmin ? 'dashboard' : 'texts')
  const [toast, setToast]         = useState(null)
  const [mobileSidebar, setMobileSidebar] = useState(false)

  // Laws state
  const [laws, setLaws]               = useState([])
  const [lawsTotal, setLawsTotal]     = useState(0)
  const [lawSearch, setLawSearch]     = useState('')
  const [lawsLoading, setLawsLoading] = useState(false)
  const [lawsFilterReview, setLawsFilterReview] = useState(false)
  const [reviewCount, setReviewCount] = useState(0)
  const [lawPage, setLawPage]         = useState(1)
  const LAW_PAGE_SIZE = 25
  const [editLaw, setEditLaw]         = useState(null)
  const [showAddLaw, setShowAddLaw]   = useState(false)
  const [newLaw, setNewLaw] = useState({ number: '', title_fr: '', title_ar: '', type: 'Loi', status: 'En vigueur', date: '', domain_id: '', language: 'Bilingue', content_fr: '', content_ar: '' })
  const [addLawLoading, setAddLawLoading] = useState(false)
  const [addLawError, setAddLawError]     = useState('')

  // Videos state
  const [videos, setVideos]           = useState([])
  const [videosLoading, setVideosLoading] = useState(false)
  const [videoSearch, setVideoSearch]   = useState('')
  const [editVideo, setEditVideo]       = useState(null)
  const [showAddVideo, setShowAddVideo] = useState(false)
  const [videoForm, setVideoForm]       = useState({ title_fr: '', title_ar: '', youtube_id: '', duration: '', author: '', domain_id: '', level: 'Débutant', date: '' })
  const [videoLoading, setVideoLoading] = useState(false)
  const [videoError, setVideoError]     = useState('')

  // Users state
  const [users, setUsers]           = useState([])
  const [usersTotal, setUsersTotal]   = useState(0)
  const [userSearch, setUserSearch]   = useState('')
  const [usersLoading, setUsersLoading] = useState(false)
  const [showAddUser, setShowAddUser] = useState(false)
  const [newUser, setNewUser]         = useState({ name: '', email: '', password: '', profession: '', role: 'user' })
  const [addUserLoading, setAddUserLoading] = useState(false)
  const [addUserError, setAddUserError]     = useState('')

  // Reports state
  const [reports, setReports]             = useState([])
  const [reportsLoading, setReportsLoading] = useState(false)
  const [reportsFilter, setReportsFilter]   = useState('pending') // pending | all

  // Subscribers state
  const [subscribers, setSubscribers]         = useState([])
  const [subscribersLoading, setSubscribersLoading] = useState(false)
  const [subscribersSearch, setSubscribersSearch]   = useState('')

  // Veille & Import queue
  const [queue, setQueue]               = useState([])
  const [queueLoading, setQueueLoading] = useState(false)
  const [queueCount, setQueueCount]     = useState(0)
  const [needsUpdate, setNeedsUpdate]   = useState([])
  const [needsUpdateLoading, setNeedsUpdateLoading] = useState(false)
  const [needsUpdateCount, setNeedsUpdateCount]     = useState(0)
  const [veilleTab, setVeilleTab]       = useState('queue') // 'queue' | 'updates'

  // Stats
  const [stats, setStats]       = useState({ laws: 0, users: 0, thisMonth: 0 })

  // Domaines dynamiques depuis Supabase (avec fallback complet)
  const [adminDomains, setAdminDomains] = useState([
    { id: 'civil',              name_fr: 'Droit Civil' },
    { id: 'penal',              name_fr: 'Droit Pénal' },
    { id: 'commercial',         name_fr: 'Droit Commercial' },
    { id: 'administratif',      name_fr: 'Droit Administratif' },
    { id: 'travail',            name_fr: 'Droit du Travail' },
    { id: 'fiscal',             name_fr: 'Droit Fiscal' },
    { id: 'international',      name_fr: 'Droit International' },
    { id: 'numerique',          name_fr: 'Droit Numérique' },
    { id: 'constitutionnel',    name_fr: 'Droit Constitutionnel' },
    { id: 'bancaire',           name_fr: 'Droit Bancaire & Financier' },
    { id: 'finances_publiques', name_fr: 'Finances Publiques' },
  ])

  const notify = (msg, ok = true) => {
    setToast({ msg, ok })
    setTimeout(() => setToast(null), 3000)
  }

  // ── Fetch stats ──
  const loadStats = useCallback(async () => {
    const [{ count: lawCount }, { count: userCount }, { count: monthCount }, { count: revCount }, { count: qCount }, { count: nuCount }] = await Promise.all([
      supabase.from('laws').select('*', { count: 'exact', head: true }),
      supabase.from('profiles').select('*', { count: 'exact', head: true }),
      supabase.from('laws').select('*', { count: 'exact', head: true })
        .gte('created_at', new Date(new Date().getFullYear(), new Date().getMonth(), 1).toISOString()),
      supabase.from('laws').select('*', { count: 'exact', head: true })
        .eq('needs_human_review', true),
      supabase.from('import_queue').select('*', { count: 'exact', head: true })
        .eq('status', 'pending'),
      supabase.from('laws').select('*', { count: 'exact', head: true })
        .eq('needs_update', true),
    ])
    setStats({ laws: lawCount || 0, users: userCount || 0, thisMonth: monthCount || 0 })
    setLawsTotal(lawCount || 0)
    setUsersTotal(userCount || 0)
    setReviewCount(revCount || 0)
    setQueueCount(qCount || 0)
    setNeedsUpdateCount(nuCount || 0)
  }, [])

  // ── Fetch import_queue ──
  const loadQueue = useCallback(async () => {
    setQueueLoading(true)
    const { data, count } = await supabase
      .from('import_queue')
      .select('*', { count: 'exact' })
      .eq('status', 'pending')
      .order('detected_at', { ascending: false })
      .limit(100)
    setQueue(data || [])
    setQueueCount(count || 0)
    setQueueLoading(false)
  }, [])

  // ── Fetch laws à mettre à jour ──
  const loadNeedsUpdate = useCallback(async () => {
    setNeedsUpdateLoading(true)
    const { data, count } = await supabase
      .from('laws')
      .select('id,number,title_fr,title_ar,type,status,domain_id,needs_update,pending_bo,last_checked', { count: 'exact' })
      .eq('needs_update', true)
      .order('last_checked', { ascending: true })
      .limit(100)
    setNeedsUpdate(data || [])
    setNeedsUpdateCount(count || 0)
    setNeedsUpdateLoading(false)
  }, [])

  const rejectQueueItem = async (id) => {
    await supabase.from('import_queue').update({ status: 'rejected' }).eq('id', id)
    setQueue(prev => prev.filter(q => q.id !== id))
    setQueueCount(c => Math.max(0, c - 1))
    notify('Entrée rejetée')
  }

  const doneQueueItem = async (id) => {
    await supabase.from('import_queue').update({ status: 'done' }).eq('id', id)
    setQueue(prev => prev.filter(q => q.id !== id))
    setQueueCount(c => Math.max(0, c - 1))
    notify('Marqué comme traité ✓')
  }

  const clearNeedsUpdate = async (id) => {
    await supabase.from('laws').update({ needs_update: false, pending_bo: null }).eq('id', id)
    setNeedsUpdate(prev => prev.filter(l => l.id !== id))
    setNeedsUpdateCount(c => Math.max(0, c - 1))
    notify('Marqué comme traité ✓')
  }

  // ── Fetch laws ──
  const loadLaws = useCallback(async (q = '', reviewOnly = false, page = 1) => {
    setLawsLoading(true)
    const from = (page - 1) * 25
    let query = supabase
      .from('laws')
      .select('id,number,title_fr,title_ar,type,status,date,domain_id,language,tags,pdf_url,simple_summary_fr,simple_summary_ar,public_article_count,detected_article_count,extraction_confidence_score,extraction_status,needs_human_review,is_publicly_indexable,summary_updated_manually', { count: 'exact' })
      .order(reviewOnly ? 'extraction_confidence_score' : 'created_at', { ascending: reviewOnly })
      .range(from, from + 24)
    if (q) query = query.or(`title_fr.ilike.%${q}%,number.ilike.%${q}%`)
    if (reviewOnly) query = query.eq('needs_human_review', true)
    const { data, count } = await query
    setLaws(data || [])
    if (count != null) setLawsTotal(count)
    setLawsLoading(false)
  }, [])

  // ── Fetch users/profiles ──
  const loadUsers = useCallback(async (q = '') => {
    setUsersLoading(true)
    let query = supabase.from('profiles').select('*').order('created_at', { ascending: false }).limit(100)
    if (q) query = query.or(`name.ilike.%${q}%,email.ilike.%${q}%`)
    const { data } = await query
    setUsers(data || [])
    setUsersLoading(false)
  }, [])

  // ── Fetch reports ──
  const loadReports = useCallback(async (filter = 'pending') => {
    setReportsLoading(true)
    let query = supabase.from('reports').select('*').order('created_at', { ascending: false }).limit(100)
    if (filter !== 'all') query = query.eq('status', filter)
    const { data } = await query
    setReports(data || [])
    setReportsLoading(false)
  }, [])

  const updateReportStatus = async (id, newStatus) => {
    await supabase.from('reports').update({ status: newStatus, updated_at: new Date().toISOString() }).eq('id', id)
    setReports(prev => prev.map(r => r.id === id ? { ...r, status: newStatus } : r))
  }

  // ── Fetch videos ──
  const loadVideos = useCallback(async (q = '') => {
    setVideosLoading(true)
    let query = supabase.from('videos').select('*').order('created_at', { ascending: false }).limit(100)
    if (q) query = query.or(`title_fr.ilike.%${q}%,author.ilike.%${q}%`)
    const { data } = await query
    setVideos(data || [])
    setVideosLoading(false)
  }, [])

  const handleAddVideo = async () => {
    if (!videoForm.title_fr || !videoForm.youtube_id) {
      setVideoError('Titre français et ID YouTube sont obligatoires.')
      return
    }
    setVideoLoading(true); setVideoError('')
    try {
      const { error } = await supabase.from('videos').insert({
        title_fr:   videoForm.title_fr,
        title_ar:   videoForm.title_ar || null,
        youtube_id: videoForm.youtube_id.trim(),
        duration:   videoForm.duration || null,
        author:     videoForm.author || null,
        domain_id:  videoForm.domain_id || null,
        level:      videoForm.level,
        date:       videoForm.date || null,
        thumbnail:  videoForm.youtube_id ? `https://img.youtube.com/vi/${videoForm.youtube_id.trim()}/mqdefault.jpg` : null,
        views:      0,
      })
      if (error) throw error
      notify('Vidéo ajoutée !')
      setShowAddVideo(false)
      setVideoForm({ title_fr: '', title_ar: '', youtube_id: '', duration: '', author: '', domain_id: '', level: 'Débutant', date: '' })
      loadVideos('')
    } catch (err) {
      setVideoError(err?.message || 'Erreur lors de la création.')
    } finally { setVideoLoading(false) }
  }

  const saveVideo = async () => {
    const { id, ...fields } = editVideo
    const { error } = await supabase.from('videos').update({
      title_fr:   fields.title_fr,
      title_ar:   fields.title_ar || null,
      youtube_id: fields.youtube_id,
      duration:   fields.duration || null,
      author:     fields.author || null,
      domain_id:  fields.domain_id || null,
      level:      fields.level,
      date:       fields.date || null,
      thumbnail:  fields.youtube_id ? `https://img.youtube.com/vi/${fields.youtube_id}/mqdefault.jpg` : null,
    }).eq('id', id)
    if (error) return notify('Erreur lors de la mise à jour', false)
    setVideos(prev => prev.map(v => v.id === id ? { ...v, ...fields } : v))
    setEditVideo(null)
    notify('Vidéo mise à jour !')
  }

  const deleteVideo = async (id) => {
    if (!confirm('Supprimer cette vidéo définitivement ?')) return
    const { error } = await supabase.from('videos').delete().eq('id', id)
    if (error) return notify('Erreur lors de la suppression', false)
    setVideos(prev => prev.filter(v => v.id !== id))
    notify('Vidéo supprimée')
  }

  // Charger les domaines depuis Supabase au montage
  useEffect(() => {
    supabase
      .from('domains')
      .select('id,name_fr,name_ar')
      .order('name_fr')
      .then(({ data }) => {
        if (data && data.length > 0) setAdminDomains(data)
      })
      .catch(() => {}) // garder le fallback en cas d'erreur
  }, [])

  useEffect(() => { loadStats() }, [])
  useEffect(() => { if (section === 'texts')   { setLawPage(1); loadLaws(lawSearch, lawsFilterReview, 1) } },   [section]) // eslint-disable-line react-hooks/exhaustive-deps
  useEffect(() => { if (section === 'texts')   loadLaws(lawSearch, lawsFilterReview, lawPage) }, [lawPage])     // eslint-disable-line react-hooks/exhaustive-deps
  useEffect(() => { if (section === 'videos')  loadVideos(videoSearch) }, [section])
  useEffect(() => { if (section === 'users')   loadUsers(userSearch) },  [section])
  useEffect(() => { if (section === 'reports')     loadReports(reportsFilter) }, [section]) // eslint-disable-line react-hooks/exhaustive-deps
  useEffect(() => { if (section === 'subscribers') loadSubscribers(subscribersSearch) }, [section]) // eslint-disable-line react-hooks/exhaustive-deps
  useEffect(() => { if (section === 'veille') { loadQueue(); loadNeedsUpdate() } }, [section]) // eslint-disable-line react-hooks/exhaustive-deps

  // ── Subscribers ──
  const loadSubscribers = useCallback(async (q = '') => {
    setSubscribersLoading(true)
    let query = supabase
      .from('subscribers')
      .select('*')
      .order('created_at', { ascending: false })
      .limit(200)
    if (q) query = query.ilike('email', `%${q}%`)
    const { data } = await query
    setSubscribers(data || [])
    setSubscribersLoading(false)
  }, [])

  // ── Actions ──
  const deleteLaw = async (id) => {
    if (!confirm('Supprimer ce texte définitivement ?')) return
    const { error } = await supabase.from('laws').delete().eq('id', id)
    if (error) return notify('Erreur lors de la suppression', false)
    setLaws(prev => prev.filter(l => l.id !== id))
    setStats(s => ({ ...s, laws: s.laws - 1 }))
    notify('Texte supprimé')
  }

  const saveLaw = async () => {
    const { id, ...fields } = editLaw
    const { error } = await supabase.from('laws').update({
      title_fr:              fields.title_fr,
      status:                fields.status,
      type:                  fields.type,
      domain_id:             fields.domain_id,
      // Enrichment fields
      simple_summary_fr:     fields.simple_summary_fr     ?? null,
      simple_summary_ar:     fields.simple_summary_ar     ?? null,
      public_article_count:  fields.public_article_count  ?? null,
      needs_human_review:    fields.needs_human_review     ?? false,
      is_publicly_indexable: fields.is_publicly_indexable ?? true,
      // Set manual flags when summaries are present (already set in onChange)
      summary_updated_manually: fields.summary_updated_manually ?? false,
    }).eq('id', id)
    if (error) return notify('Erreur lors de la mise à jour', false)
    setLaws(prev => prev.map(l => l.id === id ? { ...l, ...fields } : l))
    setEditLaw(null)
    notify('Texte mis à jour')
  }

  const updateUserRole = async (userId, role) => {
    const { error } = await supabase.from('profiles').update({ role }).eq('id', userId)
    if (error) return notify('Erreur lors de la mise à jour du rôle', false)
    setUsers(prev => prev.map(u => u.id === userId ? { ...u, role } : u))
    notify(`Rôle mis à jour → ${role}`)
  }

  const handleAddUser = async () => {
    setAddUserLoading(true)
    setAddUserError('')
    try {
      // 1. Create auth user via signUp
      const { data, error } = await supabase.auth.signUp({
        email: newUser.email,
        password: newUser.password,
        options: { data: { name: newUser.name, profession: newUser.profession } },
      })
      if (error) throw error

      // 2. Update profile role if not default 'user'
      if (newUser.role !== 'user' && data.user?.id) {
        await supabase.from('profiles').update({
          role: newUser.role,
          name: newUser.name,
          profession: newUser.profession,
        }).eq('id', data.user.id)
      }

      notify(`Utilisateur ${newUser.email} créé avec succès !`)
      setShowAddUser(false)
      setNewUser({ name: '', email: '', password: '', profession: '', role: 'user' })
      loadUsers('')
      loadStats()
    } catch (err) {
      const msg = err?.message || ''
      if (msg.includes('already registered')) setAddUserError('Cet email est déjà utilisé.')
      else if (msg.includes('Password')) setAddUserError('Mot de passe trop court (min 6 caractères).')
      else setAddUserError(msg || 'Erreur lors de la création.')
    } finally {
      setAddUserLoading(false)
    }
  }

  const handleAddLaw = async () => {
    if (!newLaw.number || !newLaw.title_fr || !newLaw.type) {
      setAddLawError('Référence, titre français et type sont obligatoires.')
      return
    }
    setAddLawLoading(true)
    setAddLawError('')
    try {
      const { error } = await supabase.from('laws').insert({
        number:     newLaw.number,
        title_fr:   newLaw.title_fr,
        title_ar:   newLaw.title_ar || null,
        type:       newLaw.type,
        status:     newLaw.status,
        date:       newLaw.date || null,
        domain_id:  newLaw.domain_id || null,
        language:   newLaw.language,
        content_fr: newLaw.content_fr || null,
        content_ar: newLaw.content_ar || null,
      })
      if (error) throw error
      notify('Texte ajouté avec succès !')
      setShowAddLaw(false)
      setNewLaw({ number: '', title_fr: '', title_ar: '', type: 'Loi', status: 'En vigueur', date: '', domain_id: '', language: 'Bilingue', content_fr: '', content_ar: '' })
      loadLaws('')
      loadStats()
    } catch (err) {
      setAddLawError(err?.message || 'Erreur lors de la création.')
    } finally {
      setAddLawLoading(false)
    }
  }

  // Editors see only texts + videos; admins see everything
  const MENU = [
    ...(isAdmin ? [{ key: 'dashboard', icon: LayoutDashboard, label: 'Dashboard' }] : []),
    { key: 'texts',   icon: FileText, label: 'Textes juridiques' },
    { key: 'veille',  icon: Bell,     label: 'Veille & Import', badge: (queueCount + needsUpdateCount) || null },
    { key: 'videos',  icon: Video,    label: 'Vidéos' },
    { key: 'reports',     icon: Flag,     label: 'Signalements' },
    { key: 'subscribers', icon: Inbox,    label: 'Abonnés' },
    ...(isAdmin ? [{ key: 'users', icon: Users, label: 'Utilisateurs' }] : []),
  ]

  const STATUSES = ['En vigueur','Abrogé','Modifié']
  const TYPES = Object.keys(LAW_TYPES)

  // ── Access guard — editors AND admins allowed ──
  if (!user || !isEditor) {
    return (
      <div className="min-h-screen flex items-center justify-center pt-16">
        <div className="text-center">
          <Shield size={48} className="text-gray-200 mx-auto mb-4" />
          <h2 className="font-playfair text-xl text-navy mb-2">Accès restreint</h2>
          <p className="text-navy-500 text-sm mb-4">Vous n'avez pas les droits nécessaires pour accéder à cette page.</p>
          <button onClick={() => navigate('/')} className="text-sm text-gold hover:underline">← Retour</button>
        </div>
      </div>
    )
  }

  const SidebarContent = ({ onSelect }) => (
    <div className="p-4">
      <div className="flex items-center gap-2 px-2 mb-4 pt-1">
        <div className="w-7 h-7 rounded-lg bg-navy flex items-center justify-center">
          <Shield size={13} className="text-gold" />
        </div>
        <span className="text-xs font-bold text-navy uppercase tracking-wide">{isAdmin ? 'Admin' : 'Éditeur'}</span>
      </div>
      <nav className="space-y-1">
        {MENU.map(({ key, icon: Icon, label, badge }) => (
          <button
            key={key}
            onClick={() => { setSection(key); onSelect?.() }}
            className={`w-full flex items-center gap-2.5 px-3 py-2.5 rounded-xl text-sm font-medium transition-colors ${
              section === key ? 'bg-navy text-white' : 'text-navy-700 hover:bg-gray-50'
            }`}
          >
            <Icon size={15} />
            <span className="flex-1 text-left">{label}</span>
            {badge > 0 && (
              <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded-full ${section === key ? 'bg-white/20 text-white' : 'bg-amber-100 text-amber-700'}`}>
                {badge}
              </span>
            )}
          </button>
        ))}
      </nav>
      <div className="mt-6 pt-4 border-t border-gray-100 space-y-1">
        <Link to="/base" onClick={() => onSelect?.()} className="flex items-center gap-2.5 px-3 py-2 rounded-xl text-xs text-navy-500 hover:bg-gray-50">
          <Database size={13} />Voir la base
        </Link>
      </div>
    </div>
  )

  return (
    <div className="min-h-screen bg-[#f8fafc] pt-16 flex">
      {toast && <Toast {...toast} />}

      {/* Mobile sidebar overlay */}
      {mobileSidebar && (
        <div className="lg:hidden fixed inset-0 z-50 flex">
          <div className="absolute inset-0 bg-black/40" onClick={() => setMobileSidebar(false)} />
          <aside className="relative z-10 w-64 bg-white h-full overflow-y-auto shadow-xl">
            <SidebarContent onSelect={() => setMobileSidebar(false)} />
          </aside>
        </div>
      )}

      {/* Desktop sidebar */}
      <aside className="hidden lg:block w-56 bg-white border-r border-gray-100 flex-shrink-0 sticky top-16 h-[calc(100vh-4rem)] overflow-y-auto">
        <SidebarContent />
      </aside>

      {/* Content */}
      <div className="flex-1 p-4 sm:p-6 min-w-0 overflow-auto">
        {/* Mobile top bar */}
        <div className="lg:hidden flex items-center gap-3 mb-4 bg-white rounded-xl border border-gray-100 px-4 py-3">
          <button onClick={() => setMobileSidebar(true)} className="p-1.5 rounded-lg hover:bg-gray-100 text-navy">
            <Menu size={18} />
          </button>
          <span className="text-sm font-semibold text-navy capitalize">{MENU.find(m => m.key === section)?.label || 'Admin'}</span>
        </div>

        {/* ══ DASHBOARD ══ */}
        {section === 'dashboard' && (
          <div>
            <div className="flex items-center justify-between mb-6">
              <h1 className="font-playfair font-bold text-navy text-2xl">Dashboard</h1>
              <button onClick={loadStats} className="flex items-center gap-1.5 px-3 py-2 rounded-lg border border-gray-200 text-xs text-navy-600 hover:border-gold hover:text-gold">
                <RefreshCw size={12} />Actualiser
              </button>
            </div>

            <div className="grid grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
              <StatCard icon={FileText}   label="Textes juridiques" value={stats.laws}      sub="dans la base"    color="bg-blue-50 text-blue-600" />
              <StatCard icon={TrendingUp} label="Ajoutés ce mois"   value={stats.thisMonth} sub="nouveaux textes" color="bg-emerald-50 text-emerald-600" />
              <StatCard icon={Users}      label="Utilisateurs"      value={stats.users}     sub="inscrits"        color="bg-gold/20 text-yellow-700" />
            </div>

            {/* Quick actions */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
              <div className="bg-white rounded-2xl border border-gray-100 p-6">
                <h3 className="font-semibold text-navy mb-3 flex items-center gap-2">
                  <FileText size={16} className="text-gold" />Textes récents
                </h3>
                <button
                  onClick={() => setSection('texts')}
                  className="w-full text-left text-sm text-navy-600 hover:text-gold transition-colors py-1"
                >
                  → Gérer les {stats.laws} textes
                </button>
              </div>
              <div className="bg-white rounded-2xl border border-gray-100 p-6">
                <h3 className="font-semibold text-navy mb-3 flex items-center gap-2">
                  <Users size={16} className="text-gold" />Gestion utilisateurs
                </h3>
                <button
                  onClick={() => setSection('users')}
                  className="w-full text-left text-sm text-navy-600 hover:text-gold transition-colors py-1"
                >
                  → Voir les {stats.users} utilisateurs
                </button>
                <p className="text-xs text-navy-400 mt-2">Modifiez les rôles : user / editor / admin</p>
              </div>
            </div>

          </div>
        )}

        {/* ══ TEXTES ══ */}
        {section === 'texts' && (
          <div>
            <div className="flex flex-wrap items-center justify-between gap-3 mb-5">
              <div className="flex items-center gap-3">
                <h1 className="font-playfair font-bold text-navy text-2xl">Textes juridiques</h1>
                {/* Badge "À vérifier" */}
                {reviewCount > 0 && (
                  <button
                    onClick={() => {
                      const next = !lawsFilterReview
                      setLawsFilterReview(next)
                      setLawPage(1)
                      loadLaws(lawSearch, next, 1)
                    }}
                    className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold border transition-colors ${
                      lawsFilterReview
                        ? 'bg-amber-500 border-amber-500 text-white'
                        : 'bg-amber-50 border-amber-300 text-amber-700 hover:bg-amber-100'
                    }`}
                  >
                    <AlertTriangle size={12} />
                    À vérifier
                    <span className={`px-1.5 py-0.5 rounded-full text-[10px] font-bold ${lawsFilterReview ? 'bg-white/30 text-white' : 'bg-amber-200 text-amber-800'}`}>
                      {reviewCount}
                    </span>
                  </button>
                )}
              </div>
              <div className="flex gap-2">
                <button onClick={() => loadLaws(lawSearch, lawsFilterReview)} className="p-2 rounded-lg border border-gray-200 text-navy-600 hover:border-gold">
                  <RefreshCw size={14} />
                </button>
                <button
                  onClick={() => { setShowAddLaw(true); setAddLawError('') }}
                  className="flex items-center gap-1.5 px-4 py-2 bg-navy text-white rounded-xl text-sm font-medium hover:bg-gold hover:text-navy transition-colors"
                >
                  <Plus size={14} /> Ajouter
                </button>
              </div>
            </div>

            {/* ── Modal Ajouter texte ── */}
            {showAddLaw && (
              <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm p-4">
                <div className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
                  <div className="flex items-center justify-between p-6 border-b border-gray-100">
                    <h2 className="font-playfair font-bold text-navy text-xl">Ajouter un texte juridique</h2>
                    <button onClick={() => setShowAddLaw(false)} className="p-2 rounded-lg hover:bg-gray-100"><X size={16} /></button>
                  </div>
                  <div className="p-6 space-y-4">
                    {addLawError && <p className="text-sm text-red-600 bg-red-50 px-4 py-2 rounded-lg">{addLawError}</p>}
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="text-xs font-semibold text-navy-600 uppercase tracking-wide mb-1 block">Référence *</label>
                        <input className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:border-gold" placeholder="Ex: Loi n°65-99" value={newLaw.number} onChange={e => setNewLaw(p => ({ ...p, number: e.target.value }))} />
                      </div>
                      <div>
                        <label className="text-xs font-semibold text-navy-600 uppercase tracking-wide mb-1 block">Date</label>
                        <input type="date" className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:border-gold" value={newLaw.date} onChange={e => setNewLaw(p => ({ ...p, date: e.target.value }))} />
                      </div>
                    </div>
                    <div>
                      <label className="text-xs font-semibold text-navy-600 uppercase tracking-wide mb-1 block">Titre français *</label>
                      <input className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:border-gold" placeholder="Titre en français" value={newLaw.title_fr} onChange={e => setNewLaw(p => ({ ...p, title_fr: e.target.value }))} />
                    </div>
                    <div>
                      <label className="text-xs font-semibold text-navy-600 uppercase tracking-wide mb-1 block">Titre arabe</label>
                      <input className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:border-gold font-arabic text-right" placeholder="العنوان بالعربية" value={newLaw.title_ar} onChange={e => setNewLaw(p => ({ ...p, title_ar: e.target.value }))} />
                    </div>
                    <div className="grid grid-cols-3 gap-4">
                      <div>
                        <label className="text-xs font-semibold text-navy-600 uppercase tracking-wide mb-1 block">Type *</label>
                        <select className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:border-gold" value={newLaw.type} onChange={e => setNewLaw(p => ({ ...p, type: e.target.value }))}>
                          {TYPES.map(t => <option key={t}>{t}</option>)}
                        </select>
                      </div>
                      <div>
                        <label className="text-xs font-semibold text-navy-600 uppercase tracking-wide mb-1 block">Statut</label>
                        <select className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:border-gold" value={newLaw.status} onChange={e => setNewLaw(p => ({ ...p, status: e.target.value }))}>
                          {STATUSES.map(s => <option key={s}>{s}</option>)}
                        </select>
                      </div>
                      <div>
                        <label className="text-xs font-semibold text-navy-600 uppercase tracking-wide mb-1 block">Domaine</label>
                        <select className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:border-gold" value={newLaw.domain_id} onChange={e => setNewLaw(p => ({ ...p, domain_id: e.target.value }))}>
                          <option value="">— Sélectionner —</option>
                          {adminDomains.map(d => <option key={d.id} value={d.id}>{d.name_fr || d.id}</option>)}
                        </select>
                      </div>
                    </div>
                    <div>
                      <label className="text-xs font-semibold text-navy-600 uppercase tracking-wide mb-1 block">Contenu français</label>
                      <textarea rows={4} className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:border-gold resize-none" placeholder="Texte du contenu en français..." value={newLaw.content_fr} onChange={e => setNewLaw(p => ({ ...p, content_fr: e.target.value }))} />
                    </div>
                    <div>
                      <label className="text-xs font-semibold text-navy-600 uppercase tracking-wide mb-1 block">Contenu arabe</label>
                      <textarea rows={4} className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:border-gold resize-none font-arabic text-right" placeholder="نص المحتوى بالعربية..." value={newLaw.content_ar} onChange={e => setNewLaw(p => ({ ...p, content_ar: e.target.value }))} />
                    </div>
                  </div>
                  <div className="flex justify-end gap-3 px-6 pb-6">
                    <button onClick={() => setShowAddLaw(false)} className="px-4 py-2 rounded-xl border border-gray-200 text-sm text-navy-600 hover:bg-gray-50">Annuler</button>
                    <button onClick={handleAddLaw} disabled={addLawLoading} className="flex items-center gap-2 px-5 py-2 bg-navy text-white rounded-xl text-sm font-semibold hover:bg-gold hover:text-navy transition-colors disabled:opacity-50">
                      {addLawLoading ? 'Enregistrement...' : <><Save size={14} /> Enregistrer</>}
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* Search */}
            <div className="bg-white rounded-2xl border border-gray-100 mb-4 p-4">
              <div className="relative">
                <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                <input
                  type="text"
                  placeholder="Rechercher par titre ou référence..."
                  value={lawSearch}
                  onChange={e => { setLawSearch(e.target.value); setLawPage(1); loadLaws(e.target.value, lawsFilterReview, 1) }}
                  className="w-full pl-8 pr-4 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:border-gold"
                />
              </div>
            </div>

            {/* Table */}
            <div className="bg-white rounded-2xl border border-gray-100 overflow-hidden">
              {lawsLoading ? (
                <div className="flex items-center justify-center py-16 text-navy-400 text-sm">Chargement…</div>
              ) : laws.length === 0 ? (
                <p className="text-center text-navy-500 py-10 text-sm">Aucun texte trouvé.</p>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-sm" style={{ tableLayout: 'fixed', minWidth: '860px' }}>
                    {/* Largeurs fixes des colonnes */}
                    <colgroup>
                      <col style={{ width: '64px' }}  />   {/* ID */}
                      <col style={{ width: '110px' }} />   {/* Référence */}
                      <col />                              {/* Titre — prend le reste */}
                      <col style={{ width: '90px' }}  />   {/* Type */}
                      <col style={{ width: '110px' }} />   {/* Statut */}
                      <col style={{ width: '68px' }}  />   {/* Score */}
                      <col style={{ width: '100px' }} />   {/* Date */}
                      <col style={{ width: '90px' }}  />   {/* Actions */}
                    </colgroup>

                    <thead className="bg-gray-50 text-xs text-navy-500 uppercase tracking-wide">
                      <tr>
                        <th className="px-3 py-3 text-start">ID</th>
                        <th className="px-3 py-3 text-start">Réf.</th>
                        <th className="px-3 py-3 text-start">Titre</th>
                        <th className="px-3 py-3 text-start">Type</th>
                        <th className="px-3 py-3 text-start">Statut</th>
                        <th className="px-3 py-3 text-start">Score</th>
                        <th className="px-3 py-3 text-start">Date</th>
                        <th className="px-3 py-3 text-end">Actions</th>
                      </tr>
                    </thead>

                    <tbody className="divide-y divide-gray-50">
                      {laws.map(law => {
                        const score      = law.extraction_confidence_score != null ? Number(law.extraction_confidence_score) : null
                        const scoreColor = score == null        ? 'text-gray-300'
                          : score >= 75  ? 'text-emerald-600 bg-emerald-50'
                          : score >= 45  ? 'text-amber-600 bg-amber-50'
                          : 'text-red-600 bg-red-50'
                        return (
                          <tr key={law.id} className={`hover:bg-gray-50 transition-colors ${law.needs_human_review ? 'border-l-2 border-amber-400' : ''}`}>

                            {/* ID */}
                            <td className="px-3 py-2.5 text-xs text-navy-400">#{law.id}</td>

                            {/* Référence */}
                            <td className="px-3 py-2.5 text-xs text-navy-600 overflow-hidden">
                              <span className="block truncate">{law.number || '—'}</span>
                            </td>

                            {/* Titre */}
                            <td className="px-3 py-2.5 overflow-hidden">
                              <div className="flex items-start gap-1.5 min-w-0">
                                {law.needs_human_review && (
                                  <AlertTriangle size={11} className="text-amber-500 flex-shrink-0 mt-0.5" />
                                )}
                                <div className="min-w-0 flex-1">
                                  <p className="text-navy font-medium text-xs truncate" title={law.title_fr}>
                                    {law.title_fr || '—'}
                                  </p>
                                  {law.title_ar && (
                                    <p className="text-[11px] text-navy-400 font-arabic truncate">{law.title_ar}</p>
                                  )}
                                  {!law.simple_summary_fr && (
                                    <p className="text-[10px] text-navy-300 italic">Sans résumé</p>
                                  )}
                                </div>
                              </div>
                            </td>

                            {/* Type */}
                            <td className="px-3 py-2.5"><TypeBadge type={law.type} /></td>

                            {/* Statut */}
                            <td className="px-3 py-2.5"><StatusBadge status={law.status} /></td>

                            {/* Score */}
                            <td className="px-3 py-2.5">
                              {score != null
                                ? <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${scoreColor}`}>{Math.round(score)}</span>
                                : <span className="text-xs text-gray-300">—</span>
                              }
                            </td>

                            {/* Date */}
                            <td className="px-3 py-2.5 text-xs text-navy-500">{law.date ?? '—'}</td>

                            {/* Actions */}
                            <td className="px-3 py-2.5">
                              <div className="flex items-center justify-end gap-0.5">
                                <Link
                                  to={lawPath(law)}
                                  target="_blank"
                                  className="p-1.5 rounded-lg hover:bg-blue-50 text-blue-500 transition-colors"
                                  title="Voir"
                                >
                                  <Eye size={13} />
                                </Link>
                                <button
                                  onClick={() => setEditLaw({ ...law })}
                                  className="p-1.5 rounded-lg hover:bg-gold/10 text-amber-600 transition-colors"
                                  title="Modifier"
                                >
                                  <Edit2 size={13} />
                                </button>
                                <button
                                  onClick={() => deleteLaw(law.id)}
                                  className="p-1.5 rounded-lg hover:bg-red-50 text-red-500 transition-colors"
                                  title="Supprimer"
                                >
                                  <Trash2 size={13} />
                                </button>
                              </div>
                            </td>
                          </tr>
                        )
                      })}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
            {/* ── Pagination ── */}
            {Math.ceil(lawsTotal / 25) > 1 && (
              <div className="flex items-center justify-between gap-2 mt-4 flex-wrap">
                <p className="text-xs text-navy-400">
                  {(lawPage - 1) * 25 + 1}–{Math.min(lawPage * 25, lawsTotal)} sur {lawsTotal} textes
                </p>
                <div className="flex items-center gap-1">
                  <button
                    onClick={() => setLawPage(p => Math.max(1, p - 1))}
                    disabled={lawPage === 1}
                    className="px-3 py-1.5 rounded-lg border border-gray-200 bg-white text-xs text-navy-600 hover:border-gold disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
                  >
                    ← Préc.
                  </button>

                  {(() => {
                    const totalPages = Math.ceil(lawsTotal / 25)
                    const WINDOW = 5
                    let start = Math.max(1, lawPage - Math.floor(WINDOW / 2))
                    let end   = Math.min(totalPages, start + WINDOW - 1)
                    if (end - start < WINDOW - 1) start = Math.max(1, end - WINDOW + 1)
                    return Array.from({ length: end - start + 1 }, (_, i) => start + i).map(p => (
                      <button
                        key={p}
                        onClick={() => setLawPage(p)}
                        className={`w-8 h-8 rounded-lg text-xs font-medium transition-colors ${
                          p === lawPage ? 'bg-navy text-white' : 'bg-white border border-gray-200 text-navy-600 hover:border-gold'
                        }`}
                      >
                        {p}
                      </button>
                    ))
                  })()}

                  <button
                    onClick={() => setLawPage(p => Math.min(Math.ceil(lawsTotal / 25), p + 1))}
                    disabled={lawPage === Math.ceil(lawsTotal / 25)}
                    className="px-3 py-1.5 rounded-lg border border-gray-200 bg-white text-xs text-navy-600 hover:border-gold disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
                  >
                    Suiv. →
                  </button>
                </div>
              </div>
            )}
          </div>
        )}

        {/* ══ VIDÉOS ══ */}
        {section === 'videos' && (
          <div>
            <div className="flex items-center justify-between mb-5">
              <h1 className="font-playfair font-bold text-navy text-2xl">Vidéos</h1>
              <div className="flex gap-2">
                <button onClick={() => loadVideos(videoSearch)} className="p-2 rounded-lg border border-gray-200 text-navy-600 hover:border-gold">
                  <RefreshCw size={14} />
                </button>
                <button
                  onClick={() => { setShowAddVideo(true); setVideoError('') }}
                  className="flex items-center gap-1.5 px-4 py-2 bg-navy text-white rounded-xl text-sm font-medium hover:bg-gold hover:text-navy transition-colors"
                >
                  <Plus size={14} /> Ajouter
                </button>
              </div>
            </div>

            {/* Search */}
            <div className="bg-white rounded-2xl border border-gray-100 mb-4 p-4">
              <div className="relative">
                <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                <input
                  type="text"
                  placeholder="Rechercher par titre ou auteur..."
                  value={videoSearch}
                  onChange={e => { setVideoSearch(e.target.value); loadVideos(e.target.value) }}
                  className="w-full pl-8 pr-4 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:border-gold"
                />
              </div>
            </div>

            {/* Table */}
            <div className="bg-white rounded-2xl border border-gray-100 overflow-hidden">
              {videosLoading ? (
                <div className="flex items-center justify-center py-16 text-navy-400 text-sm">Chargement...</div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead className="bg-gray-50 text-xs text-navy-500 uppercase tracking-wide">
                      <tr>
                        <th className="px-4 py-3 text-start">Miniature</th>
                        <th className="px-4 py-3 text-start">Titre</th>
                        <th className="px-4 py-3 text-start">Auteur</th>
                        <th className="px-4 py-3 text-start">Niveau</th>
                        <th className="px-4 py-3 text-start">Durée</th>
                        <th className="px-4 py-3 text-start">Domaine</th>
                        <th className="px-4 py-3 text-end">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-50">
                      {videos.map(vid => {
                        const ytId = vid.youtube_id ?? vid.youtubeId
                        const thumb = vid.thumbnail || `https://img.youtube.com/vi/${ytId}/default.jpg`
                        return (
                          <tr key={vid.id} className="hover:bg-gray-50 transition-colors">
                            <td className="px-4 py-3">
                              <div className="relative w-20 h-12 rounded-lg overflow-hidden bg-gray-100 flex-shrink-0">
                                <img src={thumb} alt="" className="w-full h-full object-cover" />
                                <div className="absolute inset-0 flex items-center justify-center">
                                  <Play size={14} className="text-white drop-shadow" fill="white" />
                                </div>
                              </div>
                            </td>
                            <td className="px-4 py-3 max-w-[220px]">
                              <p className="text-navy font-medium text-xs truncate">{vid.title_fr}</p>
                              {vid.title_ar && <p className="text-[11px] text-navy-400 font-arabic truncate">{vid.title_ar}</p>}
                            </td>
                            <td className="px-4 py-3 text-xs text-navy-600 whitespace-nowrap">{vid.author || '—'}</td>
                            <td className="px-4 py-3">
                              <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                                vid.level === 'Expert'        ? 'bg-purple-50 text-purple-700' :
                                vid.level === 'Intermédiaire' ? 'bg-blue-50 text-blue-700' :
                                'bg-emerald-50 text-emerald-700'
                              }`}>{vid.level || 'Débutant'}</span>
                            </td>
                            <td className="px-4 py-3 text-xs text-navy-500 whitespace-nowrap">{vid.duration || '—'}</td>
                            <td className="px-4 py-3 text-xs text-navy-500">{vid.domain_id || '—'}</td>
                            <td className="px-4 py-3">
                              <div className="flex items-center justify-end gap-1">
                                <a
                                  href={`https://youtube.com/watch?v=${ytId}`}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="p-1.5 rounded-lg hover:bg-blue-50 text-blue-600 transition-colors"
                                  title="Voir sur YouTube"
                                >
                                  <ExternalLink size={13} />
                                </a>
                                <button
                                  onClick={() => setEditVideo({ ...vid })}
                                  className="p-1.5 rounded-lg hover:bg-gold/10 text-yellow-700 transition-colors"
                                >
                                  <Edit2 size={13} />
                                </button>
                                <button
                                  onClick={() => deleteVideo(vid.id)}
                                  className="p-1.5 rounded-lg hover:bg-red-50 text-red-500 transition-colors"
                                >
                                  <Trash2 size={13} />
                                </button>
                              </div>
                            </td>
                          </tr>
                        )
                      })}
                    </tbody>
                  </table>
                  {videos.length === 0 && (
                    <p className="text-center text-navy-500 py-10 text-sm">Aucune vidéo. Cliquez sur "+ Ajouter" pour commencer.</p>
                  )}
                </div>
              )}
            </div>
          </div>
        )}

        {/* ══ SIGNALEMENTS ══ */}
        {section === 'reports' && (
          <div>
            <div className="flex flex-wrap items-center justify-between gap-3 mb-5">
              <h1 className="font-playfair font-bold text-navy text-2xl">Signalements & Feedback</h1>
              <div className="flex gap-2">
                <select
                  value={reportsFilter}
                  onChange={e => { setReportsFilter(e.target.value); loadReports(e.target.value) }}
                  className="text-sm border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:border-gold"
                >
                  <option value="pending">En attente</option>
                  <option value="reviewed">Examinés</option>
                  <option value="fixed">Corrigés</option>
                  <option value="dismissed">Ignorés</option>
                  <option value="all">Tous</option>
                </select>
                <button onClick={() => loadReports(reportsFilter)} className="p-2 rounded-lg border border-gray-200 text-navy-600 hover:border-gold">
                  <RefreshCw size={14} />
                </button>
              </div>
            </div>

            {reportsLoading ? (
              <div className="flex items-center justify-center py-16 text-navy-400 text-sm">Chargement...</div>
            ) : reports.length === 0 ? (
              <div className="bg-white rounded-2xl border border-gray-100 py-16 text-center">
                <Flag size={32} className="text-gray-200 mx-auto mb-3" />
                <p className="text-sm text-navy-400">Aucun signalement {reportsFilter !== 'all' ? `"${reportsFilter}"` : ''}.</p>
              </div>
            ) : (
              <div className="space-y-3">
                {reports.map(r => (
                  <div key={r.id} className="bg-white rounded-xl border border-gray-100 p-4 hover:border-gray-200 transition-all">
                    <div className="flex items-start justify-between gap-3 mb-2">
                      <div className="flex items-center gap-2 flex-wrap">
                        {/* Badge type */}
                        <span className={`inline-flex items-center gap-1 text-[10px] font-semibold px-2 py-0.5 rounded-full border ${
                          r.report_type === 'text_error'   ? 'bg-red-50 text-red-700 border-red-200' :
                          r.report_type === 'outdated'     ? 'bg-orange-50 text-orange-700 border-orange-200' :
                          r.report_type === 'pdf_broken'   ? 'bg-yellow-50 text-yellow-700 border-yellow-200' :
                          r.report_type === 'translation'  ? 'bg-blue-50 text-blue-700 border-blue-200' :
                          r.report_type === 'suggestion'   ? 'bg-purple-50 text-purple-700 border-purple-200' :
                          'bg-gray-50 text-gray-700 border-gray-200'
                        }`}>
                          {r.report_type === 'text_error'  ? '📄 Texte incorrect' :
                           r.report_type === 'outdated'    ? '⚠️ Abrogé non signalé' :
                           r.report_type === 'pdf_broken'  ? '🔗 PDF cassé' :
                           r.report_type === 'translation' ? '🌐 Traduction' :
                           r.report_type === 'missing_text'? '➕ Manquant' :
                           r.report_type === 'suggestion'  ? '💡 Suggestion' : r.report_type}
                        </span>
                        {/* Badge contenu */}
                        <span className="text-[10px] text-navy-400 bg-gray-50 border border-gray-200 px-2 py-0.5 rounded-full">
                          {r.content_type}
                        </span>
                        {/* Badge status */}
                        <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full ${
                          r.status === 'pending'  ? 'bg-amber-50 text-amber-700' :
                          r.status === 'reviewed' ? 'bg-blue-50 text-blue-700'  :
                          r.status === 'fixed'    ? 'bg-green-50 text-green-700' :
                          'bg-gray-50 text-gray-500'
                        }`}>
                          {r.status === 'pending' ? '⏳ En attente' : r.status === 'reviewed' ? '👁 Examiné' : r.status === 'fixed' ? '✅ Corrigé' : '🚫 Ignoré'}
                        </span>
                      </div>
                      <span className="text-[10px] text-navy-400 flex-shrink-0">
                        {new Date(r.created_at).toLocaleDateString('fr-FR', { day: '2-digit', month: 'short', year: 'numeric' })}
                      </span>
                    </div>

                    {r.subject && (
                      <p className="text-xs font-medium text-navy mb-1 line-clamp-1">{r.subject}</p>
                    )}
                    {r.subject_url && (
                      <a href={r.subject_url} target="_blank" rel="noopener noreferrer"
                         className="text-[10px] text-gold hover:underline truncate block mb-2">
                        {r.subject_url}
                      </a>
                    )}
                    {r.comment && (
                      <p className="text-sm text-navy-600 leading-relaxed bg-gray-50 rounded-lg px-3 py-2 mb-3">
                        "{r.comment}"
                      </p>
                    )}
                    {r.reporter_email && (
                      <p className="text-[10px] text-navy-400 mb-3">
                        📧 <a href={`mailto:${r.reporter_email}`} className="hover:text-gold transition-colors">{r.reporter_email}</a>
                      </p>
                    )}

                    {/* Actions */}
                    <div className="flex gap-2 flex-wrap">
                      {r.status !== 'reviewed' && (
                        <button
                          onClick={() => updateReportStatus(r.id, 'reviewed')}
                          className="flex items-center gap-1 text-[10px] font-medium px-2.5 py-1 rounded-lg bg-blue-50 text-blue-700 hover:bg-blue-100 transition-colors"
                        >
                          <Eye size={10} /> Marquer examiné
                        </button>
                      )}
                      {r.status !== 'fixed' && (
                        <button
                          onClick={() => updateReportStatus(r.id, 'fixed')}
                          className="flex items-center gap-1 text-[10px] font-medium px-2.5 py-1 rounded-lg bg-green-50 text-green-700 hover:bg-green-100 transition-colors"
                        >
                          <CheckCheck size={10} /> Marquer corrigé
                        </button>
                      )}
                      {r.status !== 'dismissed' && (
                        <button
                          onClick={() => updateReportStatus(r.id, 'dismissed')}
                          className="flex items-center gap-1 text-[10px] font-medium px-2.5 py-1 rounded-lg bg-gray-50 text-gray-600 hover:bg-gray-100 transition-colors"
                        >
                          <XCircle size={10} /> Ignorer
                        </button>
                      )}
                      {r.status !== 'pending' && (
                        <button
                          onClick={() => updateReportStatus(r.id, 'pending')}
                          className="flex items-center gap-1 text-[10px] font-medium px-2.5 py-1 rounded-lg bg-amber-50 text-amber-700 hover:bg-amber-100 transition-colors"
                        >
                          <Clock size={10} /> Remettre en attente
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* ══ VEILLE & IMPORT ══ */}
        {section === 'veille' && (
          <div>
            <div className="flex flex-wrap items-center justify-between gap-3 mb-5">
              <div>
                <h1 className="font-playfair font-bold text-navy text-2xl">Veille & Import</h1>
                <p className="text-sm text-navy-500 mt-1">Textes détectés par la veille automatique — à valider avant import</p>
              </div>
              <button
                onClick={() => { loadQueue(); loadNeedsUpdate() }}
                className="flex items-center gap-1.5 px-3 py-2 rounded-lg border border-gray-200 text-xs text-navy-600 hover:border-gold"
              >
                <RefreshCw size={13} /> Actualiser
              </button>
            </div>

            {/* Onglets */}
            <div className="flex gap-2 mb-5">
              <button
                onClick={() => setVeilleTab('queue')}
                className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium border transition-colors ${
                  veilleTab === 'queue'
                    ? 'bg-navy text-white border-navy'
                    : 'bg-white text-navy-600 border-gray-200 hover:border-gold'
                }`}
              >
                <FileInput size={14} />
                À importer
                {queueCount > 0 && (
                  <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded-full ${veilleTab === 'queue' ? 'bg-white/20' : 'bg-amber-100 text-amber-700'}`}>
                    {queueCount}
                  </span>
                )}
              </button>
              <button
                onClick={() => setVeilleTab('updates')}
                className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium border transition-colors ${
                  veilleTab === 'updates'
                    ? 'bg-amber-500 text-white border-amber-500'
                    : 'bg-white text-navy-600 border-gray-200 hover:border-gold'
                }`}
              >
                <AlertTriangle size={14} />
                À mettre à jour
                {needsUpdateCount > 0 && (
                  <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded-full ${veilleTab === 'updates' ? 'bg-white/20' : 'bg-red-100 text-red-700'}`}>
                    {needsUpdateCount}
                  </span>
                )}
              </button>
            </div>

            {/* ── Onglet : File d'import (import_queue) ── */}
            {veilleTab === 'queue' && (
              <div>
                {queueLoading ? (
                  <div className="flex items-center justify-center py-16 text-navy-400 text-sm">Chargement…</div>
                ) : queue.length === 0 ? (
                  <div className="bg-white rounded-2xl border border-gray-100 py-16 text-center">
                    <CheckCircle2 size={36} className="text-emerald-300 mx-auto mb-3" />
                    <p className="text-sm text-navy-500 font-medium">File d'import vide</p>
                    <p className="text-xs text-navy-400 mt-1">Lancez la veille depuis le dashboard pipeline pour détecter de nouveaux textes.</p>
                  </div>
                ) : (
                  <div className="space-y-2">
                    {queue.map(item => {
                      const actionColor = item.action === 'new' ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                        : item.action === 'update' ? 'bg-amber-50 text-amber-700 border-amber-200'
                        : 'bg-red-50 text-red-700 border-red-200'
                      const actionLabel = item.action === 'new' ? '🆕 Nouveau' : item.action === 'update' ? '✏️ Modification' : '🗑 Abrogation'
                      return (
                        <div key={item.id} className="bg-white rounded-xl border border-gray-100 p-4 hover:border-gray-200 transition-all">
                          <div className="flex items-start gap-3 flex-wrap">
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center gap-2 flex-wrap mb-1">
                                <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full border ${actionColor}`}>
                                  {actionLabel}
                                </span>
                                <span className="text-[10px] text-navy-400 bg-gray-50 border border-gray-200 px-2 py-0.5 rounded-full">
                                  {item.source}
                                </span>
                                {item.law_type && (
                                  <span className="text-[10px] text-navy-500 bg-blue-50 border border-blue-100 px-2 py-0.5 rounded-full">
                                    {item.law_type}
                                  </span>
                                )}
                                {item.domain_guess && (
                                  <span className="text-[10px] text-gold bg-gold/10 border border-gold/20 px-2 py-0.5 rounded-full">
                                    {item.domain_guess}
                                  </span>
                                )}
                              </div>
                              <p className="text-sm font-medium text-navy leading-snug line-clamp-2">
                                {item.title_fr || item.law_number || item.pdf_url?.split('/').pop() || '—'}
                              </p>
                              {item.law_number && (
                                <p className="text-xs text-navy-500 mt-0.5">Réf. : <span className="font-mono">{item.law_number}</span></p>
                              )}
                              <p className="text-[10px] text-navy-400 mt-1">
                                Détecté le {new Date(item.detected_at).toLocaleDateString('fr-FR', { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' })}
                              </p>
                            </div>

                            {/* Actions */}
                            <div className="flex items-center gap-1.5 flex-shrink-0">
                              {item.pdf_url && (
                                <a
                                  href={item.pdf_url}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="flex items-center gap-1 text-[10px] font-medium px-2.5 py-1.5 rounded-lg bg-blue-50 text-blue-700 hover:bg-blue-100 transition-colors"
                                  title="Voir le PDF"
                                >
                                  <Link2 size={10} /> PDF
                                </a>
                              )}
                              <button
                                onClick={() => doneQueueItem(item.id)}
                                className="flex items-center gap-1 text-[10px] font-medium px-2.5 py-1.5 rounded-lg bg-emerald-50 text-emerald-700 hover:bg-emerald-100 transition-colors"
                                title="Marquer traité"
                              >
                                <CheckCircle2 size={10} /> Traité
                              </button>
                              <button
                                onClick={() => rejectQueueItem(item.id)}
                                className="flex items-center gap-1 text-[10px] font-medium px-2.5 py-1.5 rounded-lg bg-red-50 text-red-600 hover:bg-red-100 transition-colors"
                                title="Rejeter"
                              >
                                <XCircle size={10} /> Rejeter
                              </button>
                            </div>
                          </div>
                        </div>
                      )
                    })}
                  </div>
                )}
              </div>
            )}

            {/* ── Onglet : Textes à mettre à jour ── */}
            {veilleTab === 'updates' && (
              <div>
                {needsUpdateLoading ? (
                  <div className="flex items-center justify-center py-16 text-navy-400 text-sm">Chargement…</div>
                ) : needsUpdate.length === 0 ? (
                  <div className="bg-white rounded-2xl border border-gray-100 py-16 text-center">
                    <CheckCircle2 size={36} className="text-emerald-300 mx-auto mb-3" />
                    <p className="text-sm text-navy-500 font-medium">Aucun texte à mettre à jour</p>
                    <p className="text-xs text-navy-400 mt-1">La veille signale ici les textes existants qui ont été modifiés ou abrogés.</p>
                  </div>
                ) : (
                  <div className="bg-white rounded-2xl border border-gray-100 overflow-hidden">
                    <table className="w-full text-sm">
                      <thead className="bg-gray-50 text-xs text-navy-500 uppercase tracking-wide">
                        <tr>
                          <th className="px-4 py-3 text-start">Référence</th>
                          <th className="px-4 py-3 text-start">Titre</th>
                          <th className="px-4 py-3 text-start">Domaine</th>
                          <th className="px-4 py-3 text-start">BO signalé</th>
                          <th className="px-4 py-3 text-start">Vérifié le</th>
                          <th className="px-4 py-3 text-end">Actions</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-50">
                        {needsUpdate.map(law => (
                          <tr key={law.id} className="hover:bg-amber-50/30 transition-colors border-l-2 border-amber-400">
                            <td className="px-4 py-3 text-xs font-mono text-navy-700">{law.number || '—'}</td>
                            <td className="px-4 py-3 max-w-[280px]">
                              <p className="text-navy font-medium text-xs truncate">{law.title_fr || '—'}</p>
                              {law.title_ar && <p className="text-[11px] text-navy-400 font-arabic truncate">{law.title_ar}</p>}
                            </td>
                            <td className="px-4 py-3 text-xs text-gold font-medium">{law.domain_id || '—'}</td>
                            <td className="px-4 py-3 text-xs text-navy-600">
                              {law.pending_bo ? (
                                <span className="font-mono text-amber-700 bg-amber-50 px-2 py-0.5 rounded">{law.pending_bo}</span>
                              ) : '—'}
                            </td>
                            <td className="px-4 py-3 text-xs text-navy-500">
                              {law.last_checked ? new Date(law.last_checked).toLocaleDateString('fr-FR') : '—'}
                            </td>
                            <td className="px-4 py-3">
                              <div className="flex items-center justify-end gap-1">
                                <Link
                                  to={lawPath(law)}
                                  target="_blank"
                                  className="p-1.5 rounded-lg hover:bg-blue-50 text-blue-500 transition-colors"
                                  title="Voir le texte"
                                >
                                  <Eye size={13} />
                                </Link>
                                <button
                                  onClick={() => { setEditLaw({ ...law }); setSection('texts') }}
                                  className="p-1.5 rounded-lg hover:bg-gold/10 text-amber-600 transition-colors"
                                  title="Modifier"
                                >
                                  <Edit2 size={13} />
                                </button>
                                <button
                                  onClick={() => clearNeedsUpdate(law.id)}
                                  className="p-1.5 rounded-lg hover:bg-emerald-50 text-emerald-600 transition-colors"
                                  title="Marquer traité"
                                >
                                  <CheckCheck size={13} />
                                </button>
                              </div>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* ══ SUBSCRIBERS ══ */}
        {section === 'subscribers' && (
          <div>
            <div className="flex flex-wrap items-center justify-between gap-3 mb-5">
              <div>
                <h1 className="font-playfair font-bold text-navy text-2xl">Abonnés newsletter</h1>
                <p className="text-sm text-navy-500 mt-1">{subscribers.length} abonné{subscribers.length > 1 ? 's' : ''} enregistré{subscribers.length > 1 ? 's' : ''}</p>
              </div>
              <div className="flex gap-2">
                {/* Export CSV simple */}
                <button
                  onClick={() => {
                    const csv = ['Email,Source,Langue,Domaine,Date']
                      .concat(subscribers.map(s =>
                        `${s.email},${s.source || ''},${s.lang || ''},${s.domain_id || ''},${new Date(s.created_at).toLocaleDateString('fr-FR')}`
                      )).join('\n')
                    const blob = new Blob([csv], { type: 'text/csv' })
                    const url = URL.createObjectURL(blob)
                    const a = document.createElement('a')
                    a.href = url; a.download = 'abonnes_juritheque.csv'; a.click()
                    URL.revokeObjectURL(url)
                  }}
                  className="flex items-center gap-1.5 px-3 py-2 rounded-lg border border-gray-200 text-xs text-navy-700 hover:border-gold hover:text-gold transition-colors"
                >
                  <Download size={13} /> Exporter CSV
                </button>
                <button onClick={() => loadSubscribers(subscribersSearch)} className="p-2 rounded-lg border border-gray-200 text-navy-600 hover:border-gold">
                  <RefreshCw size={14} />
                </button>
              </div>
            </div>

            {/* Recherche */}
            <div className="relative mb-4">
              <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
              <input
                type="text"
                value={subscribersSearch}
                onChange={e => { setSubscribersSearch(e.target.value); loadSubscribers(e.target.value) }}
                placeholder="Filtrer par email..."
                className="w-full max-w-sm pl-9 pr-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:border-gold"
              />
            </div>

            {subscribersLoading ? (
              <div className="flex items-center justify-center py-16 text-navy-400 text-sm">Chargement...</div>
            ) : subscribers.length === 0 ? (
              <div className="bg-white rounded-2xl border border-gray-100 py-16 text-center">
                <Inbox size={32} className="text-gray-200 mx-auto mb-3" />
                <p className="text-sm text-navy-400">Aucun abonné pour l'instant.</p>
                <p className="text-xs text-navy-300 mt-1">Les inscriptions via le footer et les popups apparaissent ici.</p>
              </div>
            ) : (
              <div className="bg-white rounded-2xl border border-gray-100 overflow-hidden">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-gray-100 bg-gray-50/60">
                      <th className="text-left px-4 py-3 text-xs font-semibold text-navy-500 uppercase tracking-wide">Email</th>
                      <th className="text-left px-4 py-3 text-xs font-semibold text-navy-500 uppercase tracking-wide">Source</th>
                      <th className="text-left px-4 py-3 text-xs font-semibold text-navy-500 uppercase tracking-wide hidden sm:table-cell">Domaine</th>
                      <th className="text-left px-4 py-3 text-xs font-semibold text-navy-500 uppercase tracking-wide hidden md:table-cell">Langue</th>
                      <th className="text-left px-4 py-3 text-xs font-semibold text-navy-500 uppercase tracking-wide">Date</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-50">
                    {subscribers.map(s => (
                      <tr key={s.id} className="hover:bg-gray-50/50 transition-colors">
                        <td className="px-4 py-3 font-medium text-navy">
                          <a href={`mailto:${s.email}`} className="hover:text-gold transition-colors">{s.email}</a>
                        </td>
                        <td className="px-4 py-3">
                          <span className={`inline-flex items-center text-[10px] font-semibold px-2 py-0.5 rounded-full ${
                            s.source === 'footer'  ? 'bg-blue-50 text-blue-700' :
                            s.source === 'domain'  ? 'bg-purple-50 text-purple-700' :
                            s.source === 'popup'   ? 'bg-green-50 text-green-700' :
                            'bg-gray-50 text-gray-700'
                          }`}>
                            {s.source || 'footer'}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-navy-500 hidden sm:table-cell">
                          {s.domain_id ? (
                            <span className="text-xs text-gold font-medium">{s.domain_id}</span>
                          ) : (
                            <span className="text-xs text-gray-300">—</span>
                          )}
                        </td>
                        <td className="px-4 py-3 text-navy-500 text-xs hidden md:table-cell">{s.lang || 'fr'}</td>
                        <td className="px-4 py-3 text-navy-400 text-xs">
                          {new Date(s.created_at).toLocaleDateString('fr-FR', { day: '2-digit', month: 'short', year: 'numeric' })}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {/* ══ USERS ══ */}
        {section === 'users' && (
          <div>
            <div className="flex items-center justify-between mb-5">
              <h1 className="font-playfair font-bold text-navy text-2xl">Utilisateurs</h1>
              <div className="flex gap-2">
                <button
                  onClick={() => { setShowAddUser(true); setAddUserError('') }}
                  className="flex items-center gap-1.5 px-4 py-2 bg-navy text-white rounded-xl text-sm font-medium hover:bg-gold hover:text-navy transition-colors"
                >
                  <UserPlus size={14} />Ajouter un utilisateur
                </button>
                <button onClick={() => loadUsers(userSearch)} className="p-2 rounded-lg border border-gray-200 text-navy-600 hover:border-gold">
                  <RefreshCw size={14} />
                </button>
              </div>
            </div>

            <div className="bg-white rounded-2xl border border-gray-100 mb-4 p-4">
              <div className="relative">
                <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                <input
                  type="text"
                  placeholder="Rechercher par nom ou email..."
                  value={userSearch}
                  onChange={e => { setUserSearch(e.target.value); loadUsers(e.target.value) }}
                  className="w-full pl-8 pr-4 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:border-gold"
                />
              </div>
            </div>

            <div className="bg-white rounded-2xl border border-gray-100 overflow-hidden">
              {usersLoading ? (
                <div className="flex items-center justify-center py-16 text-navy-400 text-sm">Chargement...</div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead className="bg-gray-50 text-xs text-navy-500 uppercase tracking-wide">
                      <tr>
                        <th className="px-4 py-3 text-start">Utilisateur</th>
                        <th className="px-4 py-3 text-start">Profession</th>
                        <th className="px-4 py-3 text-start">Rôle</th>
                        <th className="px-4 py-3 text-start">Inscrit le</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-50">
                      {users.map(u => (
                        <tr key={u.id} className="hover:bg-gray-50">
                          <td className="px-4 py-3">
                            <div className="flex items-center gap-2.5">
                              <div className="w-8 h-8 rounded-full bg-navy flex items-center justify-center text-white font-bold text-xs flex-shrink-0">
                                {(u.name || u.email || '?')[0].toUpperCase()}
                              </div>
                              <div>
                                <p className="font-medium text-navy text-xs">{u.name || '—'}</p>
                                <p className="text-[11px] text-navy-400">{u.email}</p>
                              </div>
                            </div>
                          </td>
                          <td className="px-4 py-3 text-xs text-navy-600">{u.profession || '—'}</td>
                          <td className="px-4 py-3">
                            <select
                              value={u.role || 'user'}
                              onChange={e => updateUserRole(u.id, e.target.value)}
                              className={`text-xs border rounded-lg px-2 py-1 focus:outline-none focus:border-gold font-medium ${
                                u.role === 'admin'  ? 'border-red-300 bg-red-50 text-red-700' :
                                u.role === 'editor' ? 'border-blue-300 bg-blue-50 text-blue-700' :
                                'border-gray-200 bg-gray-50 text-navy-600'
                              }`}
                            >
                              <option value="user">user</option>
                              <option value="editor">editor</option>
                              <option value="admin">admin</option>
                            </select>
                          </td>
                          <td className="px-4 py-3 text-xs text-navy-500">
                            {u.created_at ? new Date(u.created_at).toLocaleDateString('fr-FR') : '—'}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                  {users.length === 0 && (
                    <p className="text-center text-navy-500 py-10 text-sm">Aucun utilisateur trouvé.</p>
                  )}
                </div>
              )}
            </div>
          </div>
        )}

      </div>

      {/* ── Add User Modal ── */}
      {showAddUser && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md p-6">
            <div className="flex items-center justify-between mb-5">
              <div>
                <h3 className="font-playfair font-bold text-navy text-lg">Créer un utilisateur</h3>
                <p className="text-xs text-navy-500 mt-0.5">L'utilisateur recevra un email de confirmation</p>
              </div>
              <button onClick={() => { setShowAddUser(false); setAddUserError('') }} className="p-1.5 rounded-lg hover:bg-gray-100 text-navy-500">
                <X size={16} />
              </button>
            </div>

            {addUserError && (
              <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-xl mb-4">
                <XCircle size={14} className="text-red-500 flex-shrink-0" />
                <p className="text-xs text-red-600">{addUserError}</p>
              </div>
            )}

            <div className="space-y-3">
              {/* Name */}
              <div>
                <label className="block text-xs font-medium text-navy-700 mb-1">Nom complet</label>
                <div className="relative">
                  <User size={13} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                  <input type="text" value={newUser.name}
                    onChange={e => setNewUser(p => ({ ...p, name: e.target.value }))}
                    placeholder="Nom complet"
                    className="w-full pl-8 pr-3 py-2.5 text-sm border border-gray-200 rounded-lg focus:outline-none focus:border-gold"
                  />
                </div>
              </div>

              {/* Email */}
              <div>
                <label className="block text-xs font-medium text-navy-700 mb-1">Email</label>
                <div className="relative">
                  <Mail size={13} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                  <input type="email" value={newUser.email}
                    onChange={e => setNewUser(p => ({ ...p, email: e.target.value }))}
                    placeholder="email@exemple.com"
                    className="w-full pl-8 pr-3 py-2.5 text-sm border border-gray-200 rounded-lg focus:outline-none focus:border-gold"
                  />
                </div>
              </div>

              {/* Password */}
              <div>
                <label className="block text-xs font-medium text-navy-700 mb-1">Mot de passe</label>
                <div className="relative">
                  <Lock size={13} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                  <input type="password" value={newUser.password}
                    onChange={e => setNewUser(p => ({ ...p, password: e.target.value }))}
                    placeholder="Min. 6 caractères"
                    minLength={6}
                    className="w-full pl-8 pr-3 py-2.5 text-sm border border-gray-200 rounded-lg focus:outline-none focus:border-gold"
                  />
                </div>
              </div>

              {/* Profession */}
              <div>
                <label className="block text-xs font-medium text-navy-700 mb-1">Profession</label>
                <div className="relative">
                  <Briefcase size={13} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                  <input type="text" value={newUser.profession}
                    onChange={e => setNewUser(p => ({ ...p, profession: e.target.value }))}
                    placeholder="Avocat, Magistrat, Étudiant..."
                    className="w-full pl-8 pr-3 py-2.5 text-sm border border-gray-200 rounded-lg focus:outline-none focus:border-gold"
                  />
                </div>
              </div>

              {/* Role */}
              <div>
                <label className="block text-xs font-medium text-navy-700 mb-1">Rôle</label>
                <select
                  value={newUser.role}
                  onChange={e => setNewUser(p => ({ ...p, role: e.target.value }))}
                  className="w-full px-3 py-2.5 text-sm border border-gray-200 rounded-lg focus:outline-none focus:border-gold"
                >
                  <option value="user">user — accès standard</option>
                  <option value="editor">editor — peut ajouter des textes</option>
                  <option value="admin">admin — accès complet</option>
                </select>
              </div>
            </div>

            <div className="flex gap-2 mt-5 pt-4 border-t border-gray-100">
              <button
                onClick={handleAddUser}
                disabled={addUserLoading || !newUser.email || !newUser.password}
                className="flex items-center gap-1.5 px-4 py-2.5 bg-navy text-white rounded-xl text-sm font-medium hover:bg-gold hover:text-navy transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex-1 justify-center"
              >
                {addUserLoading ? (
                  <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
                  </svg>
                ) : <><UserPlus size={14} />Créer l'utilisateur</>}
              </button>
              <button
                onClick={() => { setShowAddUser(false); setAddUserError('') }}
                className="px-4 py-2.5 border border-gray-200 rounded-xl text-sm text-navy-600 hover:bg-gray-50"
              >
                Annuler
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ── Add Video Modal ── */}
      {showAddVideo && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm p-4">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-xl max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between p-6 border-b border-gray-100">
              <h2 className="font-playfair font-bold text-navy text-xl">Ajouter une vidéo</h2>
              <button onClick={() => setShowAddVideo(false)} className="p-2 rounded-lg hover:bg-gray-100"><X size={16} /></button>
            </div>
            <div className="p-6 space-y-4">
              {videoError && <p className="text-sm text-red-600 bg-red-50 px-4 py-2 rounded-lg">{videoError}</p>}

              <div>
                <label className="text-xs font-semibold text-navy-600 uppercase tracking-wide mb-1 block">Titre français *</label>
                <input className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:border-gold" placeholder="Titre en français" value={videoForm.title_fr} onChange={e => setVideoForm(p => ({ ...p, title_fr: e.target.value }))} />
              </div>
              <div>
                <label className="text-xs font-semibold text-navy-600 uppercase tracking-wide mb-1 block">Titre arabe</label>
                <input className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:border-gold font-arabic text-right" placeholder="العنوان بالعربية" value={videoForm.title_ar} onChange={e => setVideoForm(p => ({ ...p, title_ar: e.target.value }))} />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-xs font-semibold text-navy-600 uppercase tracking-wide mb-1 block">ID YouTube *</label>
                  <input className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:border-gold font-mono" placeholder="ex: dQw4w9WgXcQ" value={videoForm.youtube_id} onChange={e => setVideoForm(p => ({ ...p, youtube_id: e.target.value.trim() }))} />
                  <p className="text-[10px] text-navy-400 mt-1">L'ID après ?v= dans l'URL YouTube</p>
                </div>
                <div>
                  <label className="text-xs font-semibold text-navy-600 uppercase tracking-wide mb-1 block">Durée</label>
                  <input className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:border-gold" placeholder="ex: 42:15" value={videoForm.duration} onChange={e => setVideoForm(p => ({ ...p, duration: e.target.value }))} />
                </div>
              </div>

              {/* YouTube preview */}
              {videoForm.youtube_id && (
                <div className="rounded-xl overflow-hidden border border-gray-200">
                  <img
                    src={`https://img.youtube.com/vi/${videoForm.youtube_id}/mqdefault.jpg`}
                    alt="Aperçu miniature"
                    className="w-full h-32 object-cover"
                    onError={e => { e.target.style.display = 'none' }}
                  />
                  <p className="text-xs text-center text-navy-400 py-1 bg-gray-50">Aperçu miniature YouTube</p>
                </div>
              )}

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-xs font-semibold text-navy-600 uppercase tracking-wide mb-1 block">Auteur</label>
                  <input className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:border-gold" placeholder="Prof. Nom Prénom" value={videoForm.author} onChange={e => setVideoForm(p => ({ ...p, author: e.target.value }))} />
                </div>
                <div>
                  <label className="text-xs font-semibold text-navy-600 uppercase tracking-wide mb-1 block">Date</label>
                  <input type="date" className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:border-gold" value={videoForm.date} onChange={e => setVideoForm(p => ({ ...p, date: e.target.value }))} />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-xs font-semibold text-navy-600 uppercase tracking-wide mb-1 block">Niveau</label>
                  <select className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:border-gold" value={videoForm.level} onChange={e => setVideoForm(p => ({ ...p, level: e.target.value }))}>
                    <option>Débutant</option>
                    <option>Intermédiaire</option>
                    <option>Expert</option>
                  </select>
                </div>
                <div>
                  <label className="text-xs font-semibold text-navy-600 uppercase tracking-wide mb-1 block">Domaine</label>
                  <select className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:border-gold" value={videoForm.domain_id} onChange={e => setVideoForm(p => ({ ...p, domain_id: e.target.value }))}>
                    <option value="">— Sélectionner —</option>
                    {adminDomains.map(d => <option key={d.id} value={d.id}>{d.name_fr || d.id}</option>)}
                  </select>
                </div>
              </div>
            </div>
            <div className="flex justify-end gap-3 px-6 pb-6">
              <button onClick={() => setShowAddVideo(false)} className="px-4 py-2 rounded-xl border border-gray-200 text-sm text-navy-600 hover:bg-gray-50">Annuler</button>
              <button onClick={handleAddVideo} disabled={videoLoading} className="flex items-center gap-2 px-5 py-2 bg-navy text-white rounded-xl text-sm font-semibold hover:bg-gold hover:text-navy transition-colors disabled:opacity-50">
                {videoLoading ? 'Enregistrement...' : <><Save size={14} /> Enregistrer</>}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ── Edit Video Modal ── */}
      {editVideo && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-xl max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between p-6 border-b border-gray-100">
              <h3 className="font-playfair font-bold text-navy text-lg">Modifier la vidéo #{editVideo.id}</h3>
              <button onClick={() => setEditVideo(null)} className="p-1.5 rounded-lg hover:bg-gray-100 text-navy-500"><X size={16} /></button>
            </div>
            <div className="p-6 space-y-4">
              <div>
                <label className="block text-xs font-medium text-navy-700 mb-1">Titre français *</label>
                <input className="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:border-gold" value={editVideo.title_fr} onChange={e => setEditVideo(p => ({ ...p, title_fr: e.target.value }))} />
              </div>
              <div>
                <label className="block text-xs font-medium text-navy-700 mb-1">Titre arabe</label>
                <input className="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:border-gold font-arabic text-right" value={editVideo.title_ar || ''} onChange={e => setEditVideo(p => ({ ...p, title_ar: e.target.value }))} />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-medium text-navy-700 mb-1">ID YouTube *</label>
                  <input className="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:border-gold font-mono" value={editVideo.youtube_id || ''} onChange={e => setEditVideo(p => ({ ...p, youtube_id: e.target.value.trim() }))} />
                </div>
                <div>
                  <label className="block text-xs font-medium text-navy-700 mb-1">Durée</label>
                  <input className="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:border-gold" placeholder="42:15" value={editVideo.duration || ''} onChange={e => setEditVideo(p => ({ ...p, duration: e.target.value }))} />
                </div>
              </div>
              {editVideo.youtube_id && (
                <div className="rounded-xl overflow-hidden border border-gray-200">
                  <img src={`https://img.youtube.com/vi/${editVideo.youtube_id}/mqdefault.jpg`} alt="" className="w-full h-28 object-cover" />
                </div>
              )}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-medium text-navy-700 mb-1">Auteur</label>
                  <input className="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:border-gold" value={editVideo.author || ''} onChange={e => setEditVideo(p => ({ ...p, author: e.target.value }))} />
                </div>
                <div>
                  <label className="block text-xs font-medium text-navy-700 mb-1">Date</label>
                  <input type="date" className="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:border-gold" value={editVideo.date || ''} onChange={e => setEditVideo(p => ({ ...p, date: e.target.value }))} />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-medium text-navy-700 mb-1">Niveau</label>
                  <select className="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:border-gold" value={editVideo.level || 'Débutant'} onChange={e => setEditVideo(p => ({ ...p, level: e.target.value }))}>
                    <option>Débutant</option><option>Intermédiaire</option><option>Expert</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-medium text-navy-700 mb-1">Domaine</label>
                  <select className="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:border-gold" value={editVideo.domain_id || ''} onChange={e => setEditVideo(p => ({ ...p, domain_id: e.target.value }))}>
                    <option value="">— Sélectionner —</option>
                    {adminDomains.map(d => <option key={d.id} value={d.id}>{d.name_fr || d.id}</option>)}
                  </select>
                </div>
              </div>
            </div>
            <div className="flex gap-2 px-6 pb-6">
              <button onClick={saveVideo} className="flex items-center gap-1.5 px-4 py-2.5 bg-navy text-white rounded-xl text-sm font-medium hover:bg-gold hover:text-navy transition-colors">
                <Save size={14} />Enregistrer
              </button>
              <button onClick={() => setEditVideo(null)} className="px-4 py-2.5 border border-gray-200 rounded-xl text-sm text-navy-600 hover:bg-gray-50">Annuler</button>
            </div>
          </div>
        </div>
      )}

      {/* ── Edit Law Modal ── */}
      {editLaw && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-playfair font-bold text-navy text-lg">Modifier le texte #{editLaw.id}</h3>
              <button onClick={() => setEditLaw(null)} className="p-1.5 rounded-lg hover:bg-gray-100 text-navy-500">
                <X size={16} />
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-navy-700 mb-1">Titre FR</label>
                <input
                  type="text"
                  value={editLaw.title_fr}
                  onChange={e => setEditLaw(p => ({ ...p, title_fr: e.target.value }))}
                  className="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:border-gold"
                />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-navy-700 mb-1">Type</label>
                  <select
                    value={editLaw.type}
                    onChange={e => setEditLaw(p => ({ ...p, type: e.target.value }))}
                    className="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:border-gold"
                  >
                    {TYPES.map(tp => <option key={tp}>{tp}</option>)}
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-medium text-navy-700 mb-1">Statut</label>
                  <select
                    value={editLaw.status}
                    onChange={e => setEditLaw(p => ({ ...p, status: e.target.value }))}
                    className="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:border-gold"
                  >
                    {STATUSES.map(s => <option key={s}>{s}</option>)}
                  </select>
                </div>
              </div>
              <div>
                <label className="block text-xs font-medium text-navy-700 mb-1">Domaine</label>
                <select
                  value={editLaw.domain_id || ''}
                  onChange={e => setEditLaw(p => ({ ...p, domain_id: e.target.value }))}
                  className="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:border-gold"
                >
                  <option value="">— Sélectionner —</option>
                  {adminDomains.map(d => <option key={d.id} value={d.id}>{d.name_fr || d.id}</option>)}
                </select>
              </div>
            </div>

            {/* ── Qualité & Enrichissement ── */}
            <details className="group border border-gray-200 rounded-xl overflow-hidden">
              <summary className="flex items-center gap-2 px-4 py-3 cursor-pointer bg-gray-50 hover:bg-gray-100 transition-colors text-xs font-semibold text-navy-700 uppercase tracking-wide list-none">
                <span className="flex-1">Qualité &amp; Enrichissement</span>
                {editLaw.extraction_confidence_score != null && (
                  <span className={`px-2 py-0.5 rounded-full font-medium ${
                    Number(editLaw.extraction_confidence_score) >= 75 ? 'bg-emerald-100 text-emerald-700'
                    : Number(editLaw.extraction_confidence_score) >= 45 ? 'bg-amber-100 text-amber-700'
                    : 'bg-red-100 text-red-700'
                  }`}>
                    {Math.round(Number(editLaw.extraction_confidence_score))}/100
                  </span>
                )}
                <svg className="w-4 h-4 group-open:rotate-180 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </summary>
              <div className="p-4 space-y-4">
                {/* Read-only scores */}
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs font-medium text-navy-500 mb-1">Score d'extraction (auto)</label>
                    <div className="px-3 py-2 bg-gray-50 rounded-lg text-sm text-navy-600 border border-gray-100">
                      {editLaw.extraction_confidence_score != null ? `${Math.round(Number(editLaw.extraction_confidence_score))}/100` : '—'}
                    </div>
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-navy-500 mb-1">Articles détectés (auto)</label>
                    <div className="px-3 py-2 bg-gray-50 rounded-lg text-sm text-navy-600 border border-gray-100">
                      {editLaw.detected_article_count ?? '—'}
                    </div>
                  </div>
                </div>

                {/* Editable: public article count */}
                <div>
                  <label className="block text-xs font-medium text-navy-700 mb-1">Articles publiés (ajustable)</label>
                  <input
                    type="number"
                    min="0"
                    value={editLaw.public_article_count ?? ''}
                    onChange={e => setEditLaw(p => ({ ...p, public_article_count: e.target.value ? parseInt(e.target.value) : null }))}
                    className="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:border-gold"
                    placeholder="Nombre d'articles"
                  />
                </div>

                {/* Summary FR */}
                <div>
                  <label className="block text-xs font-medium text-navy-700 mb-1">Résumé simplifié (Français)</label>
                  <textarea
                    rows={4}
                    value={editLaw.simple_summary_fr || ''}
                    onChange={e => setEditLaw(p => ({ ...p, simple_summary_fr: e.target.value, summary_updated_manually: true }))}
                    className="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:border-gold resize-none"
                    placeholder="Résumé en français pour le grand public…"
                  />
                </div>

                {/* Summary AR */}
                <div>
                  <label className="block text-xs font-medium text-navy-700 mb-1">Résumé simplifié (Arabe)</label>
                  <textarea
                    rows={4}
                    value={editLaw.simple_summary_ar || ''}
                    onChange={e => setEditLaw(p => ({ ...p, simple_summary_ar: e.target.value, summary_updated_manually: true }))}
                    className="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:border-gold resize-none font-arabic text-right"
                    placeholder="ملخص بالعربية للعموم…"
                  />
                </div>

                {/* Checkboxes */}
                <div className="flex flex-col gap-2 pt-1">
                  <label className="flex items-center gap-2.5 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={!!editLaw.needs_human_review}
                      onChange={e => setEditLaw(p => ({ ...p, needs_human_review: e.target.checked }))}
                      className="w-4 h-4 accent-gold"
                    />
                    <span className="text-xs text-navy-700">Nécessite une revue humaine</span>
                  </label>
                  <label className="flex items-center gap-2.5 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={editLaw.is_publicly_indexable !== false}
                      onChange={e => setEditLaw(p => ({ ...p, is_publicly_indexable: e.target.checked }))}
                      className="w-4 h-4 accent-gold"
                    />
                    <span className="text-xs text-navy-700">Indexable publiquement (SEO)</span>
                  </label>
                </div>
              </div>
            </details>

            <div className="flex gap-2 mt-5 pt-4 border-t border-gray-100">
              <button
                onClick={saveLaw}
                className="flex items-center gap-1.5 px-4 py-2.5 bg-navy text-white rounded-xl text-sm font-medium hover:bg-gold hover:text-navy transition-colors"
              >
                <Save size={14} />Enregistrer
              </button>
              <button
                onClick={() => setEditLaw(null)}
                className="px-4 py-2.5 border border-gray-200 rounded-xl text-sm text-navy-600 hover:bg-gray-50"
              >
                Annuler
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

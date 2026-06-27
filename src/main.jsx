import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App'
import { AuthProvider } from './contexts/AuthContext'
import { LangProvider } from './contexts/LangContext'
import { SpeedInsights } from '@vercel/speed-insights/react'
import './index.css'

// ── Error Boundary — affiche un message utile au lieu d'une page blanche ──────
class ErrorBoundary extends React.Component {
  constructor(props) { super(props); this.state = { hasError: false, error: null } }
  static getDerivedStateFromError(error) {
    // Chunk hash mismatch après déploiement : recharger une fois pour récupérer les nouveaux assets
    const msg = error?.message || ''
    if (msg.includes('Failed to fetch dynamically imported module') ||
        msg.includes('Loading chunk') ||
        msg.includes('Loading CSS chunk') ||
        msg.includes('Importing a module script failed')) {
      const RELOAD_KEY = 'chunk_reload_at'
      const last = Number(sessionStorage.getItem(RELOAD_KEY) || 0)
      if (Date.now() - last > 10000) {
        sessionStorage.setItem(RELOAD_KEY, String(Date.now()))
        window.location.reload()
        return { hasError: false, error: null }
      }
    }
    return { hasError: true, error }
  }
  componentDidCatch(error, info) { console.error('[ErrorBoundary]', error, info) }
  render() {
    if (!this.state.hasError) return this.props.children
    return (
      <div style={{
        minHeight: '100vh', display: 'flex', flexDirection: 'column',
        alignItems: 'center', justifyContent: 'center',
        fontFamily: 'sans-serif', background: '#f8fafc', padding: 24,
      }}>
        <div style={{ maxWidth: 480, textAlign: 'center' }}>
          <div style={{ fontSize: 48, marginBottom: 16 }}>⚖️</div>
          <h1 style={{ color: '#1a2744', marginBottom: 8 }}>JuriThèque</h1>
          <p style={{ color: '#64748b', marginBottom: 24 }}>
            Une erreur inattendue s'est produite. Veuillez recharger la page.
          </p>
          <button
            onClick={() => window.location.reload()}
            style={{
              background: '#1a2744', color: 'white', border: 'none',
              borderRadius: 12, padding: '10px 24px', cursor: 'pointer',
              fontSize: 14, fontWeight: 600,
            }}
          >
            Recharger la page
          </button>
          {import.meta.env.DEV && (
            <pre style={{ marginTop: 24, textAlign: 'left', fontSize: 11, color: '#ef4444', background: '#fef2f2', padding: 12, borderRadius: 8, overflow: 'auto' }}>
              {this.state.error?.toString()}
            </pre>
          )}
        </div>
      </div>
    )
  }
}

const app = (
  <React.StrictMode>
    <ErrorBoundary>
      <BrowserRouter>
        <LangProvider>
          <AuthProvider>
            <App />
            <SpeedInsights />
          </AuthProvider>
        </LangProvider>
      </BrowserRouter>
    </ErrorBoundary>
  </React.StrictMode>
)

// Hydrater le HTML pré-rendu si disponible, sinon rendu classique SPA
const rootEl = document.getElementById('root')
if (rootEl.hasChildNodes()) {
  ReactDOM.hydrateRoot(rootEl, app)
} else {
  ReactDOM.createRoot(rootEl).render(app)
}

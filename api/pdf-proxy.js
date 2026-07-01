// Vercel Serverless Function — PDF Proxy
// Route: /api/pdf-proxy?url=<encoded_url>
// Fetches PDFs from official Moroccan legal sources server-side,
// bypassing X-Frame-Options restrictions so the iframe works within the site.

const ALLOWED_ORIGINS = [
  'supabase.co',
  'pdfs.juritheque.com',      // Cloudflare R2 (PDFs migrés — egress gratuit)
  'r2.dev',                   // R2 domaine par défaut (fallback si pas de domaine custom)
  'adala.justice.gov.ma',
  'sgg.gov.ma',
  'bkam.ma',
  'anrt.ma',
  'mem.gov.ma',
  'environnement.gov.ma',
  'finances.gov.ma',
  'emploi.gov.ma',
  'sante.gov.ma',
  'interieur.gov.ma',
  'agriculture.gov.ma',
  'mcinet.gov.ma',
  'chambredesrepresentants.ma',
  'sgcm.gov.ma',
  'legalcases.ma',
  'bulletinofficiel.net',
]

function isAllowed(hostname) {
  const h = hostname.toLowerCase()
  return ALLOWED_ORIGINS.some(origin => h === origin || h.endsWith('.' + origin))
}

export default async function handler(req, res) {
  const rawUrl = req.query?.url || ''

  if (!rawUrl) {
    res.status(400).send('URL manquante.')
    return
  }

  let parsed
  try {
    parsed = new URL(rawUrl)
  } catch {
    res.status(400).send('URL invalide.')
    return
  }

  if (!isAllowed(parsed.hostname)) {
    res.status(403).send('Source non autorisée.')
    return
  }

  // ── Fetch le document depuis la source officielle ──────────────────
  let response
  try {
    response = await fetch(rawUrl, {
      headers: {
        'User-Agent':      'Mozilla/5.0 (compatible; JuriTheque-Proxy/1.0)',
        'Accept':          'application/pdf,text/html,*/*',
        'Accept-Language': 'fr-FR,fr;q=0.9,ar;q=0.8',
        'Referer':         'https://juritheque.com/',
      },
      redirect: 'follow',
      signal: AbortSignal.timeout(10000),
    })
  } catch (e) {
    // Serveur inaccessible depuis Vercel → fallback Google Docs Viewer
    const gdocs = `https://docs.google.com/viewer?url=${encodeURIComponent(rawUrl)}&embedded=true`
    res.redirect(302, gdocs)
    return
  }

  if (!response.ok) {
    // Erreur HTTP → fallback Google Docs Viewer
    const gdocs = `https://docs.google.com/viewer?url=${encodeURIComponent(rawUrl)}&embedded=true`
    res.redirect(302, gdocs)
    return
  }

  const contentType = response.headers.get('content-type') || ''
  const buffer      = await response.arrayBuffer()
  const bytes       = new Uint8Array(buffer)

  // ── Détecter si c'est un PDF ────────────────────────────────────────
  const isPdf = contentType.includes('pdf') ||
    (bytes[0] === 0x25 && bytes[1] === 0x50 && bytes[2] === 0x44 && bytes[3] === 0x46) // %PDF

  if (isPdf) {
    res.setHeader('Content-Type', 'application/pdf')
    res.setHeader('Content-Disposition', 'inline; filename="document.pdf"')
    res.setHeader('X-Frame-Options', 'SAMEORIGIN')
    res.setHeader('Cache-Control', 'public, max-age=3600')
    res.status(200).send(Buffer.from(buffer))
    return
  }

  // ── C'est du HTML → chercher le lien PDF dans la page ──────────────
  const html = new TextDecoder('utf-8', { fatal: false }).decode(bytes)
  let pdfUrl = null

  // Pattern 1 : href direct vers .pdf
  const m1 = html.match(/href=["']([^"']*\.pdf[^"']*)['"]/i)
  if (m1) pdfUrl = m1[1]

  // Pattern 2 : Adala — lien direct dans le body
  if (!pdfUrl) {
    const m2 = html.match(/(https?:\/\/adala[^"'<>\s]+\.pdf[^"'<>\s]*)/i)
    if (m2) pdfUrl = m2[1]
  }

  // Pattern 3 : iframe embed PDF
  if (!pdfUrl) {
    const m3 = html.match(/src=["']([^"']*\.pdf[^"']*)['"]/i)
    if (m3) pdfUrl = m3[1]
  }

  if (pdfUrl) {
    // Résoudre les URLs relatives
    if (!pdfUrl.startsWith('http')) {
      try {
        pdfUrl = new URL(pdfUrl, rawUrl).href
      } catch {
        pdfUrl = null
      }
    }

    if (pdfUrl) {
      let pdfParsed
      try { pdfParsed = new URL(pdfUrl) } catch { pdfParsed = null }

      if (pdfParsed && isAllowed(pdfParsed.hostname)) {
        // Essayer de récupérer le PDF directement et le servir inline
        try {
          const pdfResp = await fetch(pdfUrl, {
            headers: {
              'User-Agent':      'Mozilla/5.0 (compatible; JuriTheque-Proxy/1.0)',
              'Accept':          'application/pdf,*/*',
              'Accept-Language': 'fr-FR,fr;q=0.9,ar;q=0.8',
              'Referer':         'https://juritheque.com/',
            },
            redirect: 'follow',
            signal: AbortSignal.timeout(12000),
          })
          if (pdfResp.ok) {
            const pdfBuf = await pdfResp.arrayBuffer()
            const pdfBytes = new Uint8Array(pdfBuf)
            const isPdfFile = pdfBytes[0] === 0x25 && pdfBytes[1] === 0x50 &&
                              pdfBytes[2] === 0x44 && pdfBytes[3] === 0x46
            if (isPdfFile) {
              res.setHeader('Content-Type', 'application/pdf')
              res.setHeader('Content-Disposition', 'inline; filename="document.pdf"')
              res.setHeader('X-Frame-Options', 'SAMEORIGIN')
              res.setHeader('Cache-Control', 'public, max-age=3600')
              res.status(200).send(Buffer.from(pdfBuf))
              return
            }
          }
        } catch {
          // fetch du PDF échoue → fallback Google Docs
        }
        // Fallback Google Docs avec l'URL du vrai PDF (meilleure chance que l'URL HTML)
        const gdocs = `https://docs.google.com/viewer?url=${encodeURIComponent(pdfUrl)}&embedded=true`
        res.redirect(302, gdocs)
        return
      }
    }
  }

  // ── Fallback : Google Docs Viewer sur l'URL originale ──────────────
  const gdocs = `https://docs.google.com/viewer?url=${encodeURIComponent(rawUrl)}&embedded=true`
  res.redirect(302, gdocs)
}

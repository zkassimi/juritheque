/**
 * prerender.mjs — Génère du HTML statique pour les guides et pages statiques.
 * Lance après `vite build` via : npm run prerender
 *
 * Résultat : dist/<route>/index.html pour chaque route prérendue.
 * Le .htaccess sert ces fichiers directement (LCP instantané + aperçus sociaux).
 */
import puppeteer from 'puppeteer'
import { preview } from 'vite'
import { writeFileSync, mkdirSync } from 'fs'
import { resolve, join } from 'path'
import { fileURLToPath } from 'url'

const __dirname = fileURLToPath(new URL('.', import.meta.url))
const ROOT = resolve(__dirname, '..')
const DIST = join(ROOT, 'dist')

// ── Slugs des guides (FR + AR générés automatiquement) ───────────────────────
const GUIDE_SLUGS = [
  'code-du-travail-maroc',
  'licenciement-maroc',
  'code-de-commerce-maroc',
  'sarl-maroc',
  'bail-commercial-maroc',
  'recouvrement-maroc',
  'cheque-sans-provision-maroc',
  'creation-societe-maroc',
  'code-de-la-famille-maroc',
  'divorce-maroc',
  'delai-de-prescription-maroc',
  'procedure-civile-maroc',
  'collectivites-territoriales-maroc',
  'revocation-elu-maroc',
  'mre-droits-juridiques-maroc',
  'heritage-succession-mre-maroc',
  'investir-maroc-mre',
  'achat-immobilier-maroc-mre',
  'double-nationalite-droit-maroc',
  'investissement-etranger-maroc',
  'marches-publics-maroc',
  'urbanisme-maroc',
  'etat-civil-maroc',
  'depenses-personnel-maroc',
  'recouvrement-creances-publiques-maroc',
  'droit-sport-football-maroc',
  'droit-numerique-ia-maroc',
  'droit-influenceurs-maroc',
  'code-route-maroc',
  'protection-consommateur-maroc',
  // Spokes — Marchés Publics
  'passation-marches-publics-maroc',
  'execution-marche-public-maroc',
  'controle-marches-publics-maroc',
  // Spokes — Droit Numérique
  'protection-donnees-personnelles-maroc',
  'ecommerce-maroc',
  // Spokes — Urbanisme
  'permis-construire-maroc',
  'infractions-urbanistiques-maroc',
]

const STATIC_ROUTES = [
  // '/' exclue : home SPA avec CSS render-blocking = FCP pire qu'en SPA pure
  '/fr/guides',
  '/domaines',
  '/glossaire',
  '/a-propos',
  '/methodologie',
  '/mentions-legales',
  '/politique-confidentialite',
  '/contact',
]

const ALL_ROUTES = [
  ...STATIC_ROUTES,
  ...GUIDE_SLUGS.map(s => `/fr/guides/${s}`),
  ...GUIDE_SLUGS.map(s => `/ar/guides/${s}`),
]

// ── Render une route et écrit son HTML dans dist/ ─────────────────────────────
async function renderRoute(page, route, baseUrl) {
  try {
    await page.goto(`${baseUrl}${route}`, { waitUntil: 'networkidle2', timeout: 20000 })

    // Attendre que React ait rendu le contenu initial
    await page.waitForSelector('#root > *', { timeout: 8000 }).catch(() => {})


    const html = await page.content()

    if (route === '/') {
      writeFileSync(join(DIST, 'index.html'), html, 'utf8')
    } else {
      const dir = join(DIST, route)
      mkdirSync(dir, { recursive: true })
      writeFileSync(join(dir, 'index.html'), html, 'utf8')
    }
    process.stdout.write(`  ✓ ${route}\n`)
    return true
  } catch (err) {
    process.stdout.write(`  ✗ ${route} — ${err.message.slice(0, 60)}\n`)
    return false
  }
}

async function run() {
  console.log('\n🚀 JuriThèque — Prerendering statique\n')

  const server = await preview({
    root: ROOT,
    preview: { port: 4173, strictPort: false },
  })

  const baseUrl = (server.resolvedUrls?.local?.[0] || 'http://localhost:4173').replace(/\/$/, '')
  console.log(`📡 Serveur: ${baseUrl}`)
  console.log(`📄 ${ALL_ROUTES.length} routes (${STATIC_ROUTES.length} statiques + ${GUIDE_SLUGS.length * 2} guides FR+AR)\n`)

  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage'],
  })

  const page = await browser.newPage()
  await page.setViewport({ width: 1280, height: 800 })

  let ok = 0, fail = 0
  for (const route of ALL_ROUTES) {
    const success = await renderRoute(page, route, baseUrl)
    success ? ok++ : fail++
  }

  await browser.close()
  server.httpServer.close()

  console.log(`\n✅ ${ok} pages générées${fail ? ` — ⚠ ${fail} timeouts ignorés` : ''}\n`)
}

run().catch(err => {
  console.error('\n❌ Erreur critique:', err.message)
  process.exit(1)
})

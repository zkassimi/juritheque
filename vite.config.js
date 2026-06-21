import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { writeFileSync, readFileSync, existsSync } from 'fs'
import compression from 'vite-plugin-compression'

const htaccess = () => ({
  name: 'htaccess',
  closeBundle() {
    // ── Copier seo-preview.php vers dist/ ─────────────────────────────────────
    const phpSrc = 'public/seo-preview.php'
    if (existsSync(phpSrc)) {
      writeFileSync('dist/seo-preview.php', readFileSync(phpSrc))
    }

    writeFileSync('dist/.htaccess', `Options -MultiViews
RewriteEngine On

# ── 0. Fichiers statiques réels : priorité absolue ───────────────────────────
RewriteCond %{REQUEST_FILENAME} -f
RewriteRule ^ - [L]

RewriteCond %{REQUEST_FILENAME} -d
RewriteRule ^ - [L]

# ── 0b. Pages pré-rendues : index.html dans sous-répertoire (sans redirect) ──
RewriteCond %{DOCUMENT_ROOT}%{REQUEST_URI}/index.html -f
RewriteRule ^ %{REQUEST_URI}/index.html [L]

# ── 1. Bots sociaux sur /loi/[slug] → seo-preview.php ───────────────────────
RewriteCond %{HTTP_USER_AGENT} (facebookexternalhit|facebot|WhatsApp|Twitterbot|LinkedInBot|TelegramBot|Slackbot|Discordbot|Googlebot|bingbot|applebot) [NC]
RewriteCond %{REQUEST_URI} ^/loi/(.+)$ [NC]
RewriteRule ^loi/(.+)$ /seo-preview.php?slug=$1 [L,QSA]

# ── 2. SPA fallback : tout le reste → index.html ────────────────────────────
RewriteRule ^ index.html [QSA,L]

# MIME types explicites pour les ES modules (obligatoire sur Hostinger)
AddType application/javascript .js .mjs
AddType text/css .css
AddType image/svg+xml .svg
AddType font/woff2 .woff2
AddType font/woff .woff

# ── Compression GZIP (réduit les tailles de 60-80%) ──────────────────────────
<IfModule mod_deflate.c>
    AddOutputFilterByType DEFLATE text/html
    AddOutputFilterByType DEFLATE text/css
    AddOutputFilterByType DEFLATE application/javascript
    AddOutputFilterByType DEFLATE application/json
    AddOutputFilterByType DEFLATE image/svg+xml
    AddOutputFilterByType DEFLATE text/plain
    AddOutputFilterByType DEFLATE text/xml
</IfModule>

# ── Compression Brotli si disponible (encore plus efficace) ──────────────────
<IfModule mod_brotli.c>
    AddOutputFilterByType BROTLI_COMPRESS text/html text/css application/javascript application/json
</IfModule>

# ── Servir les fichiers pré-compressés .gz si disponibles ────────────────────
<IfModule mod_rewrite.c>
    RewriteCond %{HTTP:Accept-Encoding} gzip
    RewriteCond %{REQUEST_FILENAME}.gz -f
    RewriteRule ^(.*)$ $1.gz [QSA,L]
</IfModule>

# Force le bon Content-Type sur tous les fichiers JS
<FilesMatch "\\.js$">
    Header set Content-Type "application/javascript; charset=utf-8"
</FilesMatch>

# index.html : jamais mis en cache
<FilesMatch "index\\.html$">
    Header set Cache-Control "no-cache, no-store, must-revalidate"
</FilesMatch>

# Assets avec hash : cache 1 an
<FilesMatch "\\.(js|css|svg|ico|png|jpg|webp|woff2?)$">
    Header set Cache-Control "public, max-age=31536000, immutable"
</FilesMatch>

# ── Expires headers (fallback si Cache-Control ignoré) ───────────────────────
<IfModule mod_expires.c>
    ExpiresActive On
    ExpiresByType text/html                  "access plus 0 seconds"
    ExpiresByType text/css                   "access plus 1 year"
    ExpiresByType application/javascript     "access plus 1 year"
    ExpiresByType image/svg+xml              "access plus 1 year"
    ExpiresByType image/png                  "access plus 1 year"
    ExpiresByType image/webp                 "access plus 1 year"
    ExpiresByType font/woff2                 "access plus 1 year"
</IfModule>

# ── Keep-Alive pour réduire les connexions TCP ────────────────────────────────
<IfModule mod_headers.c>
    Header set Connection keep-alive
</IfModule>
`)
  },
})

export default defineConfig({
  plugins: [
    react(),
    htaccess(),
    compression({ algorithm: 'gzip',          ext: '.gz', deleteOriginFile: false }),
    compression({ algorithm: 'brotliCompress', ext: '.br', deleteOriginFile: false }),
  ],
  server: { port: 5173 },
  build: {
    // Minification avancée avec esbuild (par défaut, rapide et efficace)
    minify: 'esbuild',
    // CSS minification
    cssMinify: true,
    // Cible moderne — réduit le polyfill inutile
    target: 'es2020',
    rollupOptions: {
      output: {
        manualChunks: {
          // React core — chargé une fois, mis en cache longtemps
          'vendor-react': ['react', 'react-dom', 'react-router-dom'],
          // Supabase — lazy, chargé seulement quand DB nécessaire
          'vendor-supabase': ['@supabase/supabase-js'],
          // Icônes Lucide — tree-shaken
          'vendor-icons': ['lucide-react'],
        },
      },
    },
    // Désactive l'avertissement de taille
    chunkSizeWarningLimit: 600,
    // Activer le rapport de taille pour détecter les régressions
    reportCompressedSize: true,
  },
})

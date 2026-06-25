<?php
/**
 * seo-preview.php — JuriThèque SEO Prerenderer
 * ─────────────────────────────────────────────
 * Sert aux bots (Google, Facebook, WhatsApp...) une page HTML complète
 * avec contenu indexable, Open Graph, et Schema.org JSON-LD.
 *
 * Pour les visiteurs humains → redirige vers la SPA React.
 */

// ── Configuration ─────────────────────────────────────────────────────────────
define('SUPABASE_URL',  'https://bmargdbbcnhkrjeidmvh.supabase.co');
define('SUPABASE_KEY',  'sb_publishable_QmGOC1wxyEHXpbAN4p6NaA_85FoIih5');
define('SITE_URL',      'https://juritheque.com');
define('SITE_NAME',     'JuriThèque');
define('OG_IMAGE',      'https://juritheque.com/og-image.png');

// ── Noms lisibles des domaines ─────────────────────────────────────────────────
$DOMAIN_NAMES = [
    'civil'                  => 'Droit Civil',
    'penal'                  => 'Droit Pénal',
    'commercial'             => 'Droit Commercial',
    'administratif'          => 'Droit Administratif',
    'travail'                => 'Droit du Travail',
    'fiscal'                 => 'Droit Fiscal',
    'international'          => 'Droit International',
    'numerique'              => 'Droit Numérique',
    'constitutionnel'        => 'Droit Constitutionnel',
    'bancaire'               => 'Droit Bancaire',
    'finances_publiques'     => 'Finances Publiques',
    'collectivites'          => 'Collectivités Territoriales',
    'environnement'          => 'Droit de l\'Environnement',
    'sante'                  => 'Droit de la Santé',
    'foncier'                => 'Droit Foncier',
    'famille'                => 'Droit de la Famille',
];

// ── Détection bot ──────────────────────────────────────────────────────────────
function isSocialBot() {
    $ua = strtolower($_SERVER['HTTP_USER_AGENT'] ?? '');
    $bots = [
        'facebookexternalhit', 'facebot',
        'whatsapp',
        'twitterbot',
        'linkedinbot',
        'telegrambot',
        'slackbot', 'slack-imgproxy',
        'discordbot',
        'skypeuripreview',
        'googlebot',
        'bingbot', 'msnbot',
        'applebot',
        'ia_archiver',
        'ahrefsbot', 'semrushbot', 'mj12bot',
    ];
    foreach ($bots as $bot) {
        if (str_contains($ua, $bot)) return true;
    }
    return false;
}

// ── Slug ──────────────────────────────────────────────────────────────────────
$requestUri = $_SERVER['REQUEST_URI'] ?? '';
$slug       = trim($_GET['slug'] ?? '');

if (empty($slug)) {
    if (preg_match('#/loi/([^/?#]+)#', $requestUri, $m)) {
        $slug = urldecode($m[1]);
    }
}

// ── Pas un bot OU pas de slug → SPA normale ───────────────────────────────────
if (!isSocialBot() || empty($slug)) {
    header('Location: ' . SITE_URL . $requestUri, true, 302);
    exit;
}

// ── Fetch loi depuis Supabase ─────────────────────────────────────────────────
function fetchLaw($slug) {
    $url = SUPABASE_URL . '/rest/v1/laws'
         . '?canonical_slug=eq.' . urlencode($slug)
         . '&select=number,title_fr,title_ar,type,date,simple_summary_fr,simple_summary_ar,domain_id,status,source_name'
         . '&limit=1';

    $ctx = stream_context_create([
        'http' => [
            'method'  => 'GET',
            'header'  => implode("\r\n", [
                'apikey: '        . SUPABASE_KEY,
                'Authorization: Bearer ' . SUPABASE_KEY,
                'Accept: application/json',
            ]),
            'timeout' => 5,
        ],
    ]);

    $body = @file_get_contents($url, false, $ctx);
    if (!$body) return null;
    $data = json_decode($body, true);
    return !empty($data[0]) ? $data[0] : null;
}

$law = fetchLaw($slug);

// ── Fallback : ancien slug dans slug_history → 301 permanent ─────────────────
if (!$law) {
    $url = SUPABASE_URL . '/rest/v1/laws'
         . '?slug_history=cs.%7B%22' . urlencode($slug) . '%22%7D'
         . '&select=canonical_slug'
         . '&limit=1';
    $ctx = stream_context_create([
        'http' => [
            'method'  => 'GET',
            'header'  => implode("\r\n", [
                'apikey: ' . SUPABASE_KEY,
                'Authorization: Bearer ' . SUPABASE_KEY,
                'Accept: application/json',
            ]),
            'timeout' => 5,
        ],
    ]);
    $body = @file_get_contents($url, false, $ctx);
    if ($body) {
        $data = json_decode($body, true);
        if (!empty($data[0]['canonical_slug'])) {
            header('HTTP/1.1 301 Moved Permanently');
            header('Location: ' . SITE_URL . '/loi/' . $data[0]['canonical_slug']);
            exit;
        }
    }
}

// ── Métadonnées ───────────────────────────────────────────────────────────────
$esc = fn($s) => htmlspecialchars($s ?? '', ENT_QUOTES, 'UTF-8');
$json = fn($s) => json_encode($s ?? '', JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);

if ($law) {
    $number    = $law['number']           ?? '';
    $titleFr   = $law['title_fr']         ?? '';
    $titleAr   = $law['title_ar']         ?? '';
    $type      = $law['type']             ?? 'Texte juridique';
    $date      = $law['date']             ?? '';
    $summary   = $law['simple_summary_fr'] ?? '';
    $summaryAr = $law['simple_summary_ar'] ?? '';
    $domainId  = $law['domain_id']        ?? '';
    $status    = $law['status']           ?? '';
    $source    = $law['source_name']      ?? '';

    global $DOMAIN_NAMES;
    $domainLabel = $DOMAIN_NAMES[$domainId] ?? ucfirst(str_replace('_', ' ', $domainId));

    // Titre principal
    $mainTitle = $titleFr ?: $titleAr;
    $ogTitle   = $mainTitle ? $mainTitle . ' — ' . SITE_NAME : SITE_NAME . ' | مكتبة القانون';

    // Description
    if ($summary) {
        $ogDesc = mb_substr(strip_tags($summary), 0, 200);
    } elseif ($titleFr) {
        $dateFmt = $date ? ' du ' . date('d/m/Y', strtotime($date)) : '';
        $ogDesc  = $type . ($number ? ' n° ' . $number : '') . $dateFmt
                 . ' — Texte juridique marocain disponible sur JuriThèque.';
    } else {
        $ogDesc = 'Texte juridique marocain disponible sur ' . SITE_NAME . '.';
    }

    $ogUrl    = SITE_URL . '/loi/' . rawurlencode($slug);
    $dateFmt  = $date ? date('d/m/Y', strtotime($date)) : '';
    $dateISO  = $date ?: '';

    // Titre court pour breadcrumb
    $shortTitle = $number
        ? ($type . ' n° ' . $number)
        : mb_substr($mainTitle ?: 'Texte juridique', 0, 60);

} else {
    $ogTitle    = SITE_NAME . ' | مكتبة القانون';
    $ogDesc     = 'Base de données juridique marocaine bilingue. 7 400+ lois, dahirs, décrets et codes.';
    $ogUrl      = SITE_URL;
    $mainTitle  = $ogTitle;
    $titleFr    = ''; $titleAr = ''; $type = ''; $number = '';
    $date       = ''; $dateFmt = ''; $dateISO = ''; $summary = ''; $summaryAr = '';
    $domainId   = ''; $domainLabel = ''; $status = ''; $source = '';
    $shortTitle = '';
}

// ── JSON-LD par loi ───────────────────────────────────────────────────────────
$jsonLd = '';
if ($law) {
    $breadcrumbs = [
        ['@type'=>'ListItem','position'=>1,'name'=>'JuriThèque','item'=>SITE_URL],
        ['@type'=>'ListItem','position'=>2,'name'=>'Base de données','item'=>SITE_URL.'/base'],
    ];
    if ($domainId && $domainLabel) {
        $breadcrumbs[] = ['@type'=>'ListItem','position'=>3,'name'=>$domainLabel,'item'=>SITE_URL.'/domaine/'.$domainId];
        $breadcrumbs[] = ['@type'=>'ListItem','position'=>4,'name'=>$shortTitle,'item'=>$ogUrl];
    } else {
        $breadcrumbs[] = ['@type'=>'ListItem','position'=>3,'name'=>$shortTitle,'item'=>$ogUrl];
    }

    $articleSchema = [
        '@type'         => 'Article',
        'headline'      => $ogTitle,
        'description'   => $ogDesc,
        'url'           => $ogUrl,
        'publisher'     => ['@type'=>'Organization','name'=>SITE_NAME,'url'=>SITE_URL,'logo'=>['@type'=>'ImageObject','url'=>OG_IMAGE]],
        'inLanguage'    => 'fr',
        'isPartOf'      => ['@id' => SITE_URL . '/#website'],
    ];
    if ($dateISO) {
        $articleSchema['datePublished'] = $dateISO;
        $articleSchema['dateModified']  = $dateISO;
    }

    $ld = [
        '@context' => 'https://schema.org',
        '@graph'   => [
            ['@type'=>'BreadcrumbList','itemListElement'=>$breadcrumbs],
            $articleSchema,
        ],
    ];
    $jsonLd = json_encode($ld, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES | JSON_PRETTY_PRINT);
}

// ── Rendu HTML ────────────────────────────────────────────────────────────────
header('Content-Type: text/html; charset=UTF-8');
?>
<!DOCTYPE html>
<html lang="fr" dir="ltr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title><?= $esc($ogTitle) ?></title>
  <meta name="description" content="<?= $esc($ogDesc) ?>">
  <meta name="robots" content="index,follow">
  <link rel="canonical" href="<?= $esc($ogUrl) ?>">

  <!-- Open Graph -->
  <meta property="og:type"         content="article">
  <meta property="og:site_name"    content="<?= $esc(SITE_NAME) ?>">
  <meta property="og:title"        content="<?= $esc($ogTitle) ?>">
  <meta property="og:description"  content="<?= $esc($ogDesc) ?>">
  <meta property="og:url"          content="<?= $esc($ogUrl) ?>">
  <meta property="og:image"        content="<?= $esc(OG_IMAGE) ?>">
  <meta property="og:image:width"  content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:locale"       content="fr_MA">

  <!-- Twitter Card -->
  <meta name="twitter:card"        content="summary_large_image">
  <meta name="twitter:title"       content="<?= $esc($ogTitle) ?>">
  <meta name="twitter:description" content="<?= $esc($ogDesc) ?>">
  <meta name="twitter:image"       content="<?= $esc(OG_IMAGE) ?>">

  <!-- Redirect humains vers SPA -->
  <meta http-equiv="refresh" content="0; url=<?= $esc($ogUrl) ?>">

  <!-- JSON-LD -->
  <?php if ($jsonLd): ?>
  <script type="application/ld+json">
  <?= $jsonLd ?>
  </script>
  <?php endif; ?>

  <style>
    *{box-sizing:border-box;margin:0;padding:0}
    body{font-family:Georgia,serif;color:#1a2e4a;background:#f8f5f0;padding:0}
    .skip{position:absolute;left:-9999px}
    nav{background:#1a2e4a;padding:12px 24px}
    nav a{color:#c9a84c;text-decoration:none;font-family:sans-serif;font-size:13px;margin-right:16px}
    nav a:hover{text-decoration:underline}
    .breadcrumb{background:#fff;border-bottom:1px solid #e8e4df;padding:10px 24px;font-size:12px;font-family:sans-serif;color:#64748b}
    .breadcrumb a{color:#1a2e4a;text-decoration:none}
    .breadcrumb a:hover{color:#c9a84c}
    .breadcrumb span{margin:0 6px;color:#cbd5e1}
    main{max-width:860px;margin:32px auto;padding:0 24px 48px}
    .meta-badge{display:inline-block;background:#1a2e4a;color:#c9a84c;font-size:11px;font-family:sans-serif;font-weight:700;padding:3px 10px;border-radius:20px;letter-spacing:.05em;margin-bottom:12px;text-transform:uppercase}
    h1{font-size:26px;line-height:1.3;color:#1a2e4a;margin-bottom:8px}
    .title-ar{font-family:serif;font-size:20px;color:#64748b;direction:rtl;text-align:right;margin-bottom:20px;padding:12px;background:#fff;border-radius:8px;border-right:3px solid #c9a84c}
    .meta-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:12px;margin-bottom:24px}
    .meta-item{background:#fff;border-radius:8px;padding:12px 16px;border:1px solid #e8e4df}
    .meta-item dt{font-size:10px;font-family:sans-serif;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:#94a3b8;margin-bottom:4px}
    .meta-item dd{font-size:14px;font-weight:600;color:#1a2e4a}
    .summary-box{background:#fff;border-radius:10px;padding:24px;border:1px solid #e8e4df;margin-bottom:24px}
    .summary-box h2{font-size:15px;font-family:sans-serif;font-weight:700;color:#64748b;text-transform:uppercase;letter-spacing:.08em;margin-bottom:12px}
    .summary-box p{font-size:15px;line-height:1.7;color:#334155}
    .summary-ar{direction:rtl;text-align:right;font-family:serif;font-size:16px;line-height:1.8;color:#334155;margin-top:16px;padding-top:16px;border-top:1px solid #f1f5f9}
    .cta{display:inline-block;background:#c9a84c;color:#1a2e4a;padding:12px 24px;border-radius:8px;font-family:sans-serif;font-weight:700;font-size:14px;text-decoration:none;margin-top:8px}
    .cta:hover{background:#e0bc6a}
    footer{background:#1a2e4a;color:rgba(255,255,255,.5);font-family:sans-serif;font-size:12px;padding:20px 24px;text-align:center;margin-top:48px}
    footer a{color:#c9a84c;text-decoration:none}
  </style>
</head>
<body>

<?php if ($law): ?>

<!-- Navigation -->
<nav aria-label="Navigation principale">
  <a href="<?= SITE_URL ?>">⚖️ JuriThèque</a>
  <a href="<?= SITE_URL ?>/base">Base de données</a>
  <a href="<?= SITE_URL ?>/domaines">Domaines</a>
  <a href="<?= SITE_URL ?>/glossaire">Glossaire</a>
  <a href="<?= SITE_URL ?>/assistant">Assistant IA</a>
  <a href="<?= SITE_URL ?>/fr/veille-juridique">Veille juridique</a>
</nav>

<!-- Fil d'Ariane -->
<nav class="breadcrumb" aria-label="Fil d'Ariane">
  <a href="<?= SITE_URL ?>">Accueil</a>
  <span>›</span>
  <a href="<?= SITE_URL ?>/base">Base de données</a>
  <?php if ($domainId && $domainLabel): ?>
  <span>›</span>
  <a href="<?= SITE_URL ?>/domaine/<?= $esc($domainId) ?>"><?= $esc($domainLabel) ?></a>
  <?php endif; ?>
  <span>›</span>
  <span><?= $esc($shortTitle) ?></span>
</nav>

<main>

  <!-- Type badge -->
  <?php if ($type): ?>
  <div class="meta-badge"><?= $esc($type) ?><?= $number ? ' n° ' . $esc($number) : '' ?></div>
  <?php endif; ?>

  <!-- Titre principal -->
  <?php if ($titleFr): ?>
  <h1><?= $esc($titleFr) ?></h1>
  <?php elseif ($titleAr): ?>
  <h1><?= $esc($titleAr) ?></h1>
  <?php endif; ?>

  <!-- Titre arabe -->
  <?php if ($titleAr && $titleFr): ?>
  <div class="title-ar" lang="ar" dir="rtl"><?= $esc($titleAr) ?></div>
  <?php endif; ?>

  <!-- Métadonnées -->
  <dl class="meta-grid">
    <?php if ($type): ?>
    <div class="meta-item"><dt>Type</dt><dd><?= $esc($type) ?></dd></div>
    <?php endif; ?>
    <?php if ($dateFmt): ?>
    <div class="meta-item"><dt>Date</dt><dd><?= $esc($dateFmt) ?></dd></div>
    <?php endif; ?>
    <?php if ($status): ?>
    <div class="meta-item"><dt>Statut</dt><dd><?= $esc($status) ?></dd></div>
    <?php endif; ?>
    <?php if ($domainLabel): ?>
    <div class="meta-item"><dt>Domaine</dt><dd><?= $esc($domainLabel) ?></dd></div>
    <?php endif; ?>
    <?php if ($source): ?>
    <div class="meta-item"><dt>Source</dt><dd><?= $esc($source) ?></dd></div>
    <?php endif; ?>
  </dl>

  <!-- Résumé -->
  <?php if ($summary || $summaryAr): ?>
  <div class="summary-box">
    <h2>Résumé</h2>
    <?php if ($summary): ?>
    <p><?= $esc($summary) ?></p>
    <?php endif; ?>
    <?php if ($summaryAr): ?>
    <p class="summary-ar" lang="ar" dir="rtl"><?= $esc($summaryAr) ?></p>
    <?php endif; ?>
  </div>
  <?php endif; ?>

  <!-- CTA -->
  <a class="cta" href="<?= $esc($ogUrl) ?>">
    Consulter le texte intégral sur JuriThèque →
  </a>

</main>

<?php else: ?>
<!-- Loi non trouvée — fallback -->
<nav aria-label="Navigation principale">
  <a href="<?= SITE_URL ?>">⚖️ JuriThèque</a>
  <a href="<?= SITE_URL ?>/base">Base de données</a>
</nav>
<main style="padding:48px 24px;text-align:center">
  <h1>JuriThèque — Base de données juridique marocaine</h1>
  <p style="margin:16px 0;color:#64748b">7 400+ textes juridiques marocains en accès libre.</p>
  <a class="cta" href="<?= SITE_URL ?>">Accéder à JuriThèque →</a>
</main>
<?php endif; ?>

<footer>
  <p>© JuriThèque — <a href="<?= SITE_URL ?>">juritheque.com</a> · Base de données juridique marocaine bilingue (français / arabe) · 7 400+ textes officiels</p>
</footer>

</body>
</html>

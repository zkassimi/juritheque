<?php
/**
 * pdf-proxy.php — Proxy PDF pour contourner X-Frame-Options des sources officielles
 *
 * Usage : /pdf-proxy.php?url=https%3A%2F%2Fadala.justice.gov.ma%2F...
 *
 * Sources autorisées uniquement (whitelist de sécurité)
 */

$ALLOWED_ORIGINS = [
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
];

// ── Sécurité ────────────────────────────────────────────────────────
$raw_url = isset($_GET['url']) ? trim($_GET['url']) : '';

if (empty($raw_url)) {
    http_response_code(400);
    exit('URL manquante.');
}

if (!preg_match('#^https?://#i', $raw_url)) {
    http_response_code(400);
    exit('URL invalide.');
}

$parsed = parse_url($raw_url);
$host   = strtolower($parsed['host'] ?? '');

$allowed = false;
foreach ($ALLOWED_ORIGINS as $origin) {
    if ($host === $origin || str_ends_with($host, '.' . $origin)) {
        $allowed = true;
        break;
    }
}

if (!$allowed) {
    http_response_code(403);
    exit('Source non autorisée.');
}

// ── Fetch avec cURL ─────────────────────────────────────────────────
$ch = curl_init();
curl_setopt_array($ch, [
    CURLOPT_URL            => $raw_url,
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_FOLLOWLOCATION => true,
    CURLOPT_MAXREDIRS      => 5,
    CURLOPT_TIMEOUT        => 20,
    CURLOPT_USERAGENT      => 'Mozilla/5.0 (compatible; JuriTheque-Proxy/1.0)',
    CURLOPT_SSL_VERIFYPEER => false,
    CURLOPT_HTTPHEADER     => [
        'Accept: application/pdf,text/html,*/*',
        'Accept-Language: fr-FR,fr;q=0.9,ar;q=0.8',
        'Referer: https://juritheque.com/',
    ],
]);

$body        = curl_exec($ch);
$http_code   = curl_getinfo($ch, CURLINFO_HTTP_CODE);
$content_type= curl_getinfo($ch, CURLINFO_CONTENT_TYPE);
$final_url   = curl_getinfo($ch, CURLINFO_EFFECTIVE_URL);
curl_close($ch);

if (!$body || $http_code >= 400) {
    http_response_code(502);
    exit('Impossible de récupérer le document (HTTP ' . $http_code . ').');
}

// ── Détecter si c'est un PDF ou du HTML ────────────────────────────
$is_pdf = (
    str_contains(strtolower($content_type ?? ''), 'pdf') ||
    str_starts_with($body, '%PDF') ||
    str_starts_with($body, "\x25\x50\x44\x46")
);

if ($is_pdf) {
    // Servir le PDF directement (l'iframe peut l'afficher)
    header('Content-Type: application/pdf');
    header('Content-Disposition: inline; filename="document.pdf"');
    header('X-Frame-Options: SAMEORIGIN');
    header('Cache-Control: public, max-age=3600');
    header('Content-Length: ' . strlen($body));
    echo $body;
    exit;
}

// ── C'est du HTML → chercher le lien PDF direct ──────────────────
// Adala structure : liens PDF dans des <a href="...pdf">
$pdf_url = null;

// Pattern 1 : href direct vers .pdf
if (preg_match('#href=["\']([^"\']*\.pdf[^"\']*)["\']#i', $body, $m)) {
    $pdf_url = $m[1];
}

// Pattern 2 : Adala spécifique — liens de téléchargement
if (!$pdf_url && preg_match('#(https?://adala[^"\'<>\s]+\.pdf[^"\'<>\s]*)#i', $body, $m)) {
    $pdf_url = $m[1];
}

// Pattern 3 : iframe embed PDF interne
if (!$pdf_url && preg_match('#src=["\']([^"\']*\.pdf[^"\']*)["\']#i', $body, $m)) {
    $pdf_url = $m[1];
}

if ($pdf_url) {
    // URL relative → absolue
    if (!preg_match('#^https?://#i', $pdf_url)) {
        $base = $parsed['scheme'] . '://' . $parsed['host'];
        $pdf_url = str_starts_with($pdf_url, '/')
            ? $base . $pdf_url
            : $base . '/' . ltrim($pdf_url, '/');
    }

    // Vérifier que la source du PDF est aussi dans la whitelist
    $pdf_parsed = parse_url($pdf_url);
    $pdf_host   = strtolower($pdf_parsed['host'] ?? '');
    $pdf_allowed = false;
    foreach ($ALLOWED_ORIGINS as $origin) {
        if ($pdf_host === $origin || str_ends_with($pdf_host, '.' . $origin)) {
            $pdf_allowed = true;
            break;
        }
    }

    if ($pdf_allowed) {
        // Rediriger vers Google Docs Viewer avec le PDF direct trouvé
        $gdocs = 'https://docs.google.com/viewer?url=' . urlencode($pdf_url) . '&embedded=true';
        header('Location: ' . $gdocs, true, 302);
        exit;
    }
}

// ── Fallback : Google Docs Viewer sur l'URL originale ──────────────
$gdocs = 'https://docs.google.com/viewer?url=' . urlencode($raw_url) . '&embedded=true';
header('Location: ' . $gdocs, true, 302);
exit;

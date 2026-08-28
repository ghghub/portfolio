# -*- coding: utf-8 -*-
"""
Genera una pagina HTML por caso de estudio a partir de los datos que viven en index.html.

Uso:  python build.py

Lee el array CASES de index.html (fuente unica de verdad) y escribe /casos/<slug>.html
para cada caso, en espanol e ingles. Tambien reescribe sitemap.xml.
Si editas un caso en index.html, volve a correr este script.
"""
import io, os, re, json

BASE = os.path.dirname(os.path.abspath(__file__))
URL = 'https://gportfolio-web.vercel.app/'
IDX = os.path.join(BASE, 'index.html')

# ---------------------------------------------------------------- utilidades

def leer_bloque(s, nombre):
    i = s.index('var %s = [' % nombre)
    i = s.index('[', i)
    prof = 0
    for j in range(i, len(s)):
        if s[j] == '[':
            prof += 1
        elif s[j] == ']':
            prof -= 1
            if prof == 0:
                return s[i:j + 1]
    raise ValueError(nombre)


def a_json(txt):
    """Pone comillas en las claves respetando el contenido de las cadenas."""
    out, i, n, dentro = [], 0, len(txt), False
    while i < n:
        ch = txt[i]
        if dentro:
            out.append(ch)
            if ch == '\\' and i + 1 < n:
                out.append(txt[i + 1]); i += 2; continue
            if ch == '"':
                dentro = False
            i += 1; continue
        if ch == '"':
            dentro = True; out.append(ch); i += 1; continue
        m = re.match(r'([A-Za-z_][A-Za-z0-9_]*)\s*:', txt[i:])
        if m and (not out or out[-1].strip() in ('', '{', ',')):
            out.append('"%s":' % m.group(1)); i += m.end(); continue
        out.append(ch); i += 1
    return json.loads(re.sub(r',(\s*[}\]])', r'\1', ''.join(out)))


def slug(t):
    t = t.lower()
    for a, b in [('á','a'),('é','e'),('í','i'),('ó','o'),('ú','u'),('ñ','n'),('ü','u')]:
        t = t.replace(a, b)
    t = re.sub(r'[^a-z0-9]+', '-', t).strip('-')
    return '-'.join(t.split('-')[:5])


def sin_html(t):
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', t)).strip()


# ---------------------------------------------------------------- datos

src = io.open(IDX, encoding='utf-8').read()
CASES = a_json(leer_bloque(src, 'CASES'))
DIM = json.loads(re.search(r'var DIM = (\{.*?\});', src, re.S).group(1))


def dim_attr(ruta):
    d = DIM.get(ruta)
    return ' width="%d" height="%d"' % (d[0], d[1]) if d else ''

estilos = re.search(r'<style>(.*?)</style>', src, re.S).group(1)

SLUGS = [slug(c['es']['title']) for c in CASES]

# ---------------------------------------------------------------- plantilla

PAG = u'''<!DOCTYPE html>
<html lang="%(lang)s">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<meta name="color-scheme" content="dark light" />
<title>%(title)s · Gabriel González</title>
<link rel="canonical" href="%(url)scasos/%(slug)s.html" />
<link rel="alternate" hreflang="es" href="%(url)scasos/%(slug_es)s.html" />
<link rel="alternate" hreflang="en" href="%(url)scasos/%(slug_en)s.html" />
<link rel="alternate" hreflang="x-default" href="%(url)scasos/%(slug_es)s.html" />
<meta name="description" content="%(desc)s" />
<meta name="author" content="Gabriel González" />
<meta name="robots" content="index, follow, max-image-preview:large" />
<meta property="og:type" content="article" />
<meta property="og:title" content="%(title)s" />
<meta property="og:description" content="%(desc)s" />
<meta property="og:url" content="%(url)scasos/%(slug)s.html" />
<meta property="og:image" content="%(url)simg/estancco/estancco-00.jpg" />
<meta name="twitter:card" content="summary_large_image" />
<link rel="icon" href="data:image/svg+xml,%%3Csvg xmlns=%%27http://www.w3.org/2000/svg%%27 viewBox=%%270 0 100 100%%27%%3E%%3Crect width=%%27100%%27 height=%%27100%%27 fill=%%27%%230a0a0a%%27/%%3E%%3Ctext x=%%2750%%27 y=%%2772%%27 font-family=%%27Helvetica,Arial,sans-serif%%27 font-size=%%2764%%27 font-weight=%%27700%%27 fill=%%27%%23f2f2f0%%27 text-anchor=%%27middle%%27%%3EG%%3C/text%%3E%%3C/svg%%3E" />
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600;700&family=Archivo+Black&display=swap" rel="stylesheet">
<style>%(estilos)s
  body{background:#ececec;color:#16171a}
  .caso{max-width:68ch;margin:0 auto;padding:0 24px}
  .caso-top{padding:34px 0;font-size:14px}
  .caso-top a{color:#6b6b6b;text-decoration:none;margin-right:24px}
  .caso-top a:hover{color:#16171a}
  .caso h1{font-family:"Archivo Black",Archivo,sans-serif;font-size:clamp(30px,6vw,54px);
    font-weight:400;letter-spacing:-.03em;text-transform:uppercase;line-height:.98;
    max-width:none;margin:40px 0 18px}
  .caso .meta{color:#6b6b6b;font-size:15px;margin-bottom:8px}
  .caso h2{font-size:13px;letter-spacing:.16em;text-transform:uppercase;color:#6b6b6b;
    margin:48px 0 14px;padding-bottom:8px;border-bottom:1px solid #dcdcdc;font-weight:400}
  .caso p{margin-bottom:16px;color:#3a3a3c;font-size:17px}
  .caso ul{list-style:none;margin:0 0 16px}
  .caso li{position:relative;padding-left:20px;margin-bottom:12px;color:#3a3a3c;font-size:17px}
  .caso li:before{content:"·";position:absolute;left:0;color:#a8a8a8}
  .caso strong{color:#16171a;font-weight:600}
  .otros{border-top:1px solid #dcdcdc;margin-top:70px;padding:40px 0 90px}
  .otros h2{border:0;padding:0;margin-bottom:20px}
  .otros a{display:block;color:#16171a;text-decoration:none;padding:16px 0;
    border-bottom:1px solid #dcdcdc;font-size:19px;font-weight:600}
  .otros a:hover{color:#6b6b6b}
  .cierre{margin-top:56px;padding-top:28px;border-top:1px solid #dcdcdc;
    font-size:19px;color:#16171a;max-width:46ch}
  .caso figure{margin:34px 0}
  .caso figure img{width:100%%;height:auto;display:block;background:#dcdcdc}
  .caso .piezas{margin:48px 0 0;display:flex;flex-direction:column;gap:14px}
  .caso .piezas img{width:100%%;height:auto;display:block;background:#dcdcdc}
</style>
<script type="application/ld+json">%(jsonld)s</script>
</head>
<body>
<article class="caso">
  <div class="caso-top">
    <a href="../index.html">%(volver)s</a>
    <a href="https://www.linkedin.com/in/dg-gabriel-gonzalez" target="_blank" rel="noopener">LinkedIn</a>
    <a href="https://www.behance.net/Gabriel_HG" target="_blank" rel="noopener">Behance</a>
  </div>
  <h1>%(title)s</h1>
  <p class="meta">%(client)s</p>
  <p class="meta">%(meta)s</p>
%(portada)s
%(cuerpo)s
%(piezas)s
  <p class="cierre">%(cierre)s</p>
  <nav class="otros">
    <h2>%(otros_titulo)s</h2>
%(otros)s
  </nav>
</article>
</body>
</html>
'''

CIERRE = {
 'es': u'Ayudo a empresas de complejidad técnica a alinear su percepción con su capacidad. '
       u'<a href="../index.html#contacto" style="color:#16171a">Hablemos</a>.',
 'en': u'I help technically complex companies to align perception with capability. '
       u'<a href="../index.html#contacto" style="color:#16171a">Let’s talk</a>.',
}
VOLVER = {'es': u'← Volver al portfolio', 'en': u'← Back to portfolio'}
OTROS = {'es': u'Más casos de estudio', 'en': u'More case studies'}

# ---------------------------------------------------------------- generacion

os.makedirs(os.path.join(BASE, 'casos'), exist_ok=True)
generadas = []

for i, c in enumerate(CASES):
    for lang in ('es', 'en'):
        d = c[lang]
        sl = SLUGS[i] if lang == 'es' else SLUGS[i] + '-en'

        cuerpo = []
        for bl in d['blocks']:
            cuerpo.append('  <h2>%s</h2>' % bl[0])
            if len(bl) > 1:
                for par in bl[1]:
                    cuerpo.append('  <p>%s</p>' % par)
            if len(bl) > 2 and bl[2]:
                cuerpo.append('  <ul>')
                for li in bl[2]:
                    cuerpo.append('    <li>%s</li>' % li)
                cuerpo.append('  </ul>')
            if len(bl) > 3 and bl[3]:
                for par in bl[3]:
                    cuerpo.append('  <p>%s</p>' % par)

        portada = ''
        if c.get('cover'):
            portada = (u'  <figure><img src="../%s" alt="%s"%s '
                       u'decoding="async" /></figure>'
                       % (c['cover'], d['title'].replace('"', '&quot;'),
                          dim_attr(c['cover'])))

        piezas = ''
        if c.get('shots'):
            filas = [u'  <div class="piezas">']
            for k, src in enumerate(c['shots']):
                filas.append(u'    <img src="../%s" alt="%s \u00b7 %d"%s '
                             u'loading="lazy" decoding="async" />'
                             % (src, d['title'].replace('"', '&quot;'), k + 1,
                                dim_attr(src)))
            filas.append(u'  </div>')
            piezas = '\n'.join(filas)

        primer_parrafo = sin_html(d['blocks'][0][1][0])
        desc = (primer_parrafo[:180] + '…') if len(primer_parrafo) > 180 else primer_parrafo
        desc = desc.replace('"', '&quot;')

        otros = []
        for k, otro in enumerate(CASES):
            if k == i:
                continue
            osl = SLUGS[k] if lang == 'es' else SLUGS[k] + '-en'
            otros.append('    <a href="%s.html">%s</a>' % (osl, otro[lang]['title']))

        jsonld = json.dumps({
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": d['title'],
            "description": desc,
            "inLanguage": lang,
            "url": URL + 'casos/' + sl + '.html',
            "author": {"@type": "Person", "name": "Gabriel González",
                       "url": URL, "@id": URL + "#gabriel"},
            "publisher": {"@type": "Person", "name": "Gabriel González", "@id": URL + "#gabriel"},
            "about": d['client'],
            "isPartOf": {"@type": "WebSite", "@id": URL + "#sitio"}
        }, ensure_ascii=False, indent=1)

        html = PAG % {
            'lang': lang, 'slug': sl, 'url': URL, 'estilos': estilos,
            'title': d['title'], 'client': d['client'], 'meta': d['meta'],
            'desc': desc, 'cuerpo': '\n'.join(cuerpo), 'jsonld': jsonld,
            'portada': portada, 'piezas': piezas,
            'otros': '\n'.join(otros), 'otros_titulo': OTROS[lang],
            'volver': VOLVER[lang], 'cierre': CIERRE[lang],
            'slug_es': SLUGS[i], 'slug_en': SLUGS[i] + '-en',
        }
        ruta = os.path.join(BASE, 'casos', sl + '.html')
        io.open(ruta, 'w', encoding='utf-8').write(html)
        generadas.append('casos/%s.html' % sl)


# ---------------------------------------------------------------- articulos

ART = u'''<!DOCTYPE html>
<html lang="%(lang)s">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<meta name="color-scheme" content="dark light" />
<title>%(title)s · Gabriel González</title>
<link rel="canonical" href="%(url)sarticulos/%(slug)s.html" />
<meta name="description" content="%(desc)s" />
<meta name="author" content="Gabriel González" />
<meta name="robots" content="index, follow, max-image-preview:large" />
<meta property="og:type" content="article" />
<meta property="og:title" content="%(title)s" />
<meta property="og:description" content="%(desc)s" />
<meta property="og:url" content="%(url)sarticulos/%(slug)s.html" />
<meta property="og:image" content="%(url)simg/estancco/estancco-00.jpg" />
<meta name="twitter:card" content="summary_large_image" />
<link rel="icon" href="data:image/svg+xml,%%3Csvg xmlns=%%27http://www.w3.org/2000/svg%%27 viewBox=%%270 0 100 100%%27%%3E%%3Crect width=%%27100%%27 height=%%27100%%27 fill=%%27%%230a0a0a%%27/%%3E%%3Ctext x=%%2750%%27 y=%%2772%%27 font-family=%%27Helvetica,Arial,sans-serif%%27 font-size=%%2764%%27 font-weight=%%27700%%27 fill=%%27%%23f2f2f0%%27 text-anchor=%%27middle%%27%%3EG%%3C/text%%3E%%3C/svg%%3E" />
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600;700&family=Archivo+Black&display=swap" rel="stylesheet">
<style>%(estilos)s
  body{background:#ececec;color:#16171a}
  .art{max-width:64ch;margin:0 auto;padding:0 24px}
  .art-top{padding:34px 0;font-size:14px}
  .art-top a{color:#6b6b6b;text-decoration:none;margin-right:24px}
  .art-top a:hover{color:#16171a}
  .kicker{color:#6b6b6b;font-size:14px;letter-spacing:.1em;text-transform:uppercase;margin:44px 0 14px}
  .art h1{font-size:clamp(30px,5vw,44px);font-weight:700;letter-spacing:-.02em;
    line-height:1.12;max-width:none;margin-bottom:36px}
  .art p{margin-bottom:22px;color:#3a3a3c;font-size:18px;line-height:1.62}
  .art p:first-of-type{font-size:20px;color:#16171a}
  .cierre{margin-top:52px;padding-top:28px;border-top:1px solid #dcdcdc;
    font-size:20px;color:#16171a;max-width:46ch}
  .evidencia{margin:44px 0 90px;padding:26px 0;border-top:1px solid #dcdcdc;border-bottom:1px solid #dcdcdc}
  .evidencia span{display:block;color:#6b6b6b;font-size:13px;letter-spacing:.12em;
    text-transform:uppercase;margin-bottom:8px}
  .evidencia a{color:#16171a;text-decoration:none;font-size:22px;font-weight:600}
  .evidencia a:hover{color:#6b6b6b}
</style>
<script type="application/ld+json">%(jsonld)s</script>
</head>
<body>
<article class="art">
  <div class="art-top">
    <a href="../index.html">&larr; Volver al portfolio</a>
    <a href="https://www.linkedin.com/in/dg-gabriel-gonzalez" target="_blank" rel="noopener">LinkedIn</a>
  </div>
  <p class="kicker">%(kicker)s</p>
  <h1>%(title)s</h1>
%(cuerpo)s
  <p class="cierre">%(cierre)s <a href="../index.html#contacto" style="color:#16171a">Hablemos</a>.</p>
  <div class="evidencia">
    <span>%(ev_etq)s</span>
    <a href="%(ev_url)s">%(ev_tit)s</a>
  </div>
</article>
</body>
</html>
'''

ruta_art = os.path.join(BASE, 'articulos.json')
if os.path.exists(ruta_art):
    ARTS = json.loads(io.open(ruta_art, encoding='utf-8').read())
    os.makedirs(os.path.join(BASE, 'articulos'), exist_ok=True)
    for a in ARTS:
        cuerpo = '\n'.join('  <p>%s</p>' % x for x in a['body'])
        primero = sin_html(a['body'][0])
        desc = (primero[:180] + '\u2026') if len(primero) > 180 else primero
        desc = desc.replace('"', '&quot;')
        jsonld = json.dumps({
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": a['title'],
            "description": desc,
            "inLanguage": a['lang'],
            "url": URL + 'articulos/' + a['slug'] + '.html',
            "author": {"@type": "Person", "name": "Gabriel Gonz\u00e1lez",
                       "url": URL, "@id": URL + "#gabriel"},
            "publisher": {"@type": "Person", "name": "Gabriel Gonz\u00e1lez", "@id": URL + "#gabriel"},
            "isPartOf": {"@type": "WebSite", "@id": URL + "#sitio"}
        }, ensure_ascii=False, indent=1)
        html = ART % {
            'lang': a['lang'], 'slug': a['slug'], 'url': URL, 'estilos': estilos,
            'title': a['title'], 'kicker': a['kicker'], 'desc': desc,
            'cuerpo': cuerpo, 'cierre': a['cierre'], 'jsonld': jsonld,
            'ev_etq': a['caso']['etiqueta'], 'ev_url': a['caso']['url'],
            'ev_tit': a['caso']['titulo'],
        }
        io.open(os.path.join(BASE, 'articulos', a['slug'] + '.html'), 'w', encoding='utf-8').write(html)
        generadas.append('articulos/%s.html' % a['slug'])
    print('articulos generados: %d' % len(ARTS))

# ---------------------------------------------------------------- sitemap

filas = ['  <url>\n    <loc>%s</loc>\n    <changefreq>monthly</changefreq>\n    <priority>1.0</priority>\n  </url>' % URL]
for g in generadas:
    filas.append('  <url>\n    <loc>%s%s</loc>\n    <changefreq>yearly</changefreq>\n    <priority>0.8</priority>\n  </url>' % (URL, g))

sitemap = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
           + '\n'.join(filas) + '\n</urlset>\n')
io.open(os.path.join(BASE, 'sitemap.xml'), 'w', encoding='utf-8').write(sitemap)

print('paginas generadas: %d' % len(generadas))
for g in generadas:
    print('  ' + g)
print('sitemap.xml actualizado con %d URLs' % (len(generadas) + 1))

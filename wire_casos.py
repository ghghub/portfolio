# -*- coding: utf-8 -*-
"""
Engancha una imagen de portada a cada caso de estudio.

Uso:
  1. Guarda la imagen en  img/casos/<slug>.jpg   (o .png)
  2. Corre:  python wire_casos.py

Los slugs son los nombres de archivo que ya viven en /casos:

  vender-continuidad-no-acero.jpg          -> Vender continuidad, no acero
  una-marca-que-sostiene-otras.jpg         -> Una marca que sostiene otras marcas
  tomar-un-shopping.jpg                    -> Tomar un shopping
  disenar-confianza-para-quienes-estan.jpg -> Disenar confianza para quienes estan cansados

El script lee el tamano real de cada imagen, lo agrega al mapa DIM, escribe
el campo cover del caso correspondiente y vuelve a generar las paginas.
Es idempotente: se puede correr las veces que haga falta.
"""
import io, os, re, json, subprocess, sys

from PIL import Image

BASE = os.path.dirname(os.path.abspath(__file__))
IDX = os.path.join(BASE, 'index.html')
DIR = os.path.join(BASE, 'img', 'casos')

SLUGS = [
    'vender-continuidad-no-acero',
    'una-marca-que-sostiene-otras',
    'tomar-un-shopping',
    'disenar-confianza-para-quienes-estan',
]
EXTS = ('.jpg', '.jpeg', '.png', '.webp')

if not os.path.isdir(DIR):
    os.makedirs(DIR)
    print('Cree la carpeta img/casos/. Guarda ahi las imagenes y volve a correr.')
    sys.exit(0)

# ------------------------------------------------ que imagenes hay realmente
encontradas = {}
for i, sl in enumerate(SLUGS):
    for ext in EXTS:
        ruta = os.path.join(DIR, sl + ext)
        if os.path.exists(ruta):
            with Image.open(ruta) as im:
                w, h = im.size
            encontradas[i] = ('img/casos/' + sl + ext, w, h)
            break

if not encontradas:
    print('No hay imagenes en img/casos/. Nombres esperados:')
    for sl in SLUGS:
        print('  %s.jpg' % sl)
    sys.exit(0)

src = io.open(IDX, encoding='utf-8').read()

# ------------------------------------------------------------ mapa DIM
m = re.search(r'var DIM = (\{.*?\});', src, re.S)
DIM = json.loads(m.group(1))
for ruta, w, h in encontradas.values():
    DIM[ruta] = [w, h]
nuevo_dim = 'var DIM = %s;' % json.dumps(DIM, ensure_ascii=False, sort_keys=True)
src = src[:m.start()] + nuevo_dim + src[m.end():]

# ------------------------------------------------ campo cover de cada caso
# Ubicamos donde abre cada caso: un "{" con profundidad de llaves en cero
# dentro del array. Hay que contar llaves ademas de corchetes, porque cada
# caso tiene objetos anidados (es, en, credits) que tambien abren con "{".
# Se ignoran las llaves que aparezcan dentro de cadenas.
i0 = src.index('var CASES = [')
i0 = src.index('[', i0)
corch = llaves = 0
dentro = False
arranques = []
j = i0
while j < len(src):
    ch = src[j]
    if dentro:
        if ch == chr(92):
            j += 2
            continue
        if ch == '"':
            dentro = False
        j += 1
        continue
    if ch == '"':
        dentro = True
    elif ch == '[':
        corch += 1
    elif ch == ']':
        corch -= 1
        if corch == 0:
            break
    elif ch == '{':
        if corch == 1 and llaves == 0:
            arranques.append(j)
        llaves += 1
    elif ch == '}':
        llaves -= 1
    j += 1

if len(arranques) != len(SLUGS):
    print('Esperaba %d casos y encontre %d. No toco nada.'
          % (len(SLUGS), len(arranques)))
    sys.exit(1)

cambios = 0
for idx in sorted(encontradas, reverse=True):   # de atras hacia adelante
    ruta = encontradas[idx][0]
    ini = arranques[idx]
    fin = src.index(' es:{', ini)
    cabeza = src[ini:fin]                       # solo lo previo al bloque es
    if re.search(r'\bcover\s*:', cabeza):
        nueva = re.sub(r'cover\s*:\s*"[^"]*"', 'cover:"%s"' % ruta, cabeza, count=1)
    else:
        nueva = cabeza.rstrip() + '\n cover:"%s",\n' % ruta
    src = src[:ini] + nueva + src[fin:]
    cambios += 1

io.open(IDX, 'w', encoding='utf-8').write(src)

for idx in sorted(encontradas):
    ruta, w, h = encontradas[idx]
    print('caso %d  %s  %dx%d' % (idx + 1, ruta, w, h))
print('index.html actualizado (%d portadas)' % cambios)

faltan = [SLUGS[i] for i in range(len(SLUGS)) if i not in encontradas]
if faltan:
    print('todavia sin imagen:')
    for f in faltan:
        print('  img/casos/%s.jpg' % f)

subprocess.check_call([sys.executable, os.path.join(BASE, 'build.py')], cwd=BASE)

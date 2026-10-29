#!/usr/bin/env python3
"""Añade a bloqueo.json (0.9.0) los mods de biodiversidad del hito 2 (h2sinbp + End's Phantasm).
Lee los jars reales (SHA-1, neoforge.mods.toml) y comprueba dependencias obligatorias contra el conjunto completo.
Uso: python3 -I anadir_biomas.py <dir_modpack>"""
import hashlib, io, json, shutil, sys, tomllib, zipfile
from pathlib import Path
mp = Path(sys.argv[1]); CACHE = Path.home()/'dev/modpack-cache/jars'; LAB = Path.home()/'dev/biomas-lab'
# slug, titulo, projectID, fileID, jar, pilar, porque
NUEVOS = [
 ('natures-spirit',"Nature's Spirit",1044992,9251843,LAB/'jars/natures_spirit-2.3.1-1.21.1.jar','mundo','Biomas de carácter (sabanas, chaparral, cipreses, secuoyas)'),
 ('regions-unexplored','Regions Unexplored',659110,9252522,LAB/'jars/regions-unexplored-0.6.3-neoforge-21.1.jar','mundo','Biomas grandes y variados, también en el Nether'),
 ('lets-do-bloomingnature','[Let\'s Do] BloomingNature',962885,8914292,LAB/'jars/letsdo-bloomingnature-neoforge-1.1.11.jar','mundo','Prados y bosques floridos (fijado a 1.1.11, la probada)'),
 ('biomes-o-plenty','Biomes O\' Plenty',220318,8288121,LAB/'jars_cf/BiomesOPlenty-neoforge-1.21.1-21.1.0.14.jar','mundo','Biomas de bosque, humedal y Nether'),
 ('promenade','Promenade',399648,9128732,LAB/'jars/promenade-neoforge-6.0.1.jar','mundo','Biomas de carácter (sakura, cañón, humedal)'),
 ('nyctophobia-fabric','Nyctophobia',584511,8709122,LAB/'jars/nyctophobia-neoforge-mc1.21.1-2.0.0.jar','mundo','Bosque embrujado'),
 ('ecologics','Ecologics',570463,8415537,LAB/'jars/ecologics-1.21.1-2.3.7.jar','mundo','Biomas de oasis y cocoteros (fijado a 2.3.7: la 2.3.8 exige NeoForge 21.1.264)'),
 ('oh-the-biomes-weve-gone','Oh The Biomes We\'ve Gone',1070751,9114631,LAB/'jars2/Oh-The-Biomes-Weve-Gone-NeoForge-2.6.3.jar','mundo','Biomas fantásticos y de paisaje (hito 2)'),
 ('oh-the-trees-youll-grow','Oh The Trees You\'ll Grow',962544,9113653,LAB/'jars2/Oh-The-Trees-Youll-Grow-neoforge-1.21.1-5.3.5.jar','mundo','Árboles y arbolado de Oh The Biomes We\'ve Gone'),
 ('incendium','Incendium',591388,5962249,LAB/'jars2/Incendium_1.21.x_v5.4.4.jar','mundo','Nether ampliado (hito 2)'),
 ('hybrid-aquatic','Hybrid Aquatic',834427,9063977,LAB/'jars2/hybrid_aquatic-neoforge-1.21.1-1.7.4.jar','mundo','Biodiversidad oceánica (hito 2)'),
 ('phantasm','End\'s Phantasm',565254,6367800,LAB/'jars4/phantasm-1.0.3.jar','mundo','Biomas aditivos del End; conserva Nullscape (hito 2)'),
 ('corgilib','CorgiLib',693313,9113612,LAB/'jars2/Corgilib-NeoForge-1.21.1-5.0.0.10.jar','dependencia',''),
 ('hybrid-api','Hybrid API [HAPI]',883374,9063597,LAB/'jars2/hapi-neoforge-1.21.1-1.1.3.jar','dependencia',''),
 ('kotlin-for-forge','Kotlin for Forge',351264,8335665,LAB/'jars2/kotlinforforge-5.12.0-all.jar','dependencia',''),
 ('biolith','Biolith',852512,8435635,LAB/'jars/biolith-neoforge-3.0.14.jar','dependencia',''),
 ('terrablender-neoforge','TerraBlender (NeoForge)',940057,6054947,LAB/'jars_cf/TerraBlender-neoforge-1.21.1-4.1.0.8.jar','dependencia',''),
 ('glitchcore','GlitchCore',955399,8109792,LAB/'jars_cf/GlitchCore-neoforge-1.21.1-2.1.0.2.jar','dependencia',''),
]
def mods_de(z, ruta=''):
    out = []
    n = 'META-INF/neoforge.mods.toml'
    if n in z.namelist():
        t = tomllib.loads(z.read(n).decode('utf8'))
        deps = t.get('dependencies', {})
        for m in t.get('mods', []):
            d = [{'modId': x['modId'], 'tipo': x.get('type', 'required' if x.get('mandatory') else 'optional'),
                  'rango': x.get('versionRange', ''), 'lado': x.get('side', 'BOTH')} for x in deps.get(m['modId'], [])]
            out.append({'modId': m['modId'], 'version': str(m.get('version', '')), 'deps': d, **({'incluido_en_jarjar': True} if ruta else {})})
    for j in [x for x in z.namelist() if x.startswith('META-INF/jarjar/') and x.endswith('.jar')]:
        with zipfile.ZipFile(io.BytesIO(z.read(j))) as zz: out += mods_de(zz, j)
    return out
b = json.load(open(mp/'bloqueo.json'))
ya = {e['projectID'] for e in b['entradas']}
for slug, titulo, pid, fid, jar, pilar, porque in NUEVOS:
    if pid in ya: print('ya está', slug); continue
    datos = jar.read_bytes(); sha1 = hashlib.sha1(datos).hexdigest()
    with zipfile.ZipFile(jar) as z: mods = mods_de(z)
    dest = CACHE/f'{fid}-{jar.name}'
    if not dest.exists(): shutil.copy(jar, dest)
    b['entradas'].append({'slug': slug, 'titulo': titulo, 'projectID': pid, 'fileID': fid, 'archivo': jar.name, 'tipo': 'release',
        'fecha': '', 'bytes': len(datos), 'sha1': sha1, 'licencia': '', 'autores': [], 'url': f'https://www.curseforge.com/minecraft/mc-mods/{slug}',
        'pilar': pilar, 'porque': porque, 'mods': mods, 'tamano_ok': True, 'etiquetas_cf': ['1.21.1', 'NeoForge'], 'es_neoforge': True})
    print('añadido', slug, sha1[:8], [m['modId'] for m in mods if not m.get('incluido_en_jarjar')])
# dependencias obligatorias
ids = {m['modId'] for e in b['entradas'] for m in e['mods']} | {'minecraft', 'neoforge', 'java'}
fallos = [(e['slug'], m['modId'], d['modId']) for e in b['entradas'] for m in e['mods'] for d in m['deps']
          if d['tipo'] == 'required' and d['modId'] not in ids]
print('dependencias obligatorias sin cubrir:', fallos or 'ninguna')
json.dump(b, open(mp/'bloqueo.json', 'w'), indent=1, ensure_ascii=False)
print(len(b['entradas']), 'entradas')

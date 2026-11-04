#!/usr/bin/env python3
"""Baut je Skill ein ZIP (ein Skill, ein Ordner, eine SKILL.md) für ein Sprachpaket. Entwurf 01.11.2026.
Aufruf: python3 -I tools/zip_bauen.py <paket-wurzel>      z. B. en oder de
Liest <paket-wurzel>/skeleton/skills/* und <paket-wurzel>/skills/*, schreibt <paket-wurzel>/dist/<skill>.zip.
Prüft je Skill: Frontmatter (name = Ordnername, description höchstens 1024 Zeichen), genau eine Datei SKILL.md.
Feste Zeitstempel und sortierte Einträge; die komprimierten Bytes können je zlib-Version abweichen (Hashes der Einträge vergleichen)."""
import sys, os, re, glob, zipfile

root = sys.argv[1]
fehler = []
hinweise = []
skills = {}
for basis in ('skeleton/skills', 'skills'):
    for d in sorted(glob.glob(os.path.join(root, basis, '*'))):
        if os.path.isdir(d):
            name = os.path.basename(d)
            if name in skills:
                fehler.append(f'{name}: doppelt (skeleton/skills und skills)')
            skills[name] = d

out = os.path.join(root, 'dist')
os.makedirs(out, exist_ok=True)
for name, d in skills.items():
    dateien = [p for p in glob.glob(os.path.join(d, '**', '*'), recursive=True) if os.path.isfile(p)]
    if [os.path.relpath(p, d) for p in dateien] != ['SKILL.md']:
        fehler.append(f'{name}: erwartet genau eine Datei SKILL.md, gefunden {[os.path.relpath(p, d) for p in dateien]}')
        continue
    t = open(os.path.join(d, 'SKILL.md'), encoding='utf-8').read()
    m = re.match(r'---\nname: (.+)\ndescription: (.+)\n---\n', t)
    if not m:
        fehler.append(f'{name}: Frontmatter (name, description in je einer Zeile) fehlt'); continue
    if m.group(1) != name:
        fehler.append(f'{name}: name {m.group(1)!r} passt nicht zum Ordner')
    if not re.fullmatch(r'[a-z0-9-]{1,64}', m.group(1)) or re.search(r'anthropic|claude', m.group(1)):
        fehler.append(f'{name}: name verstößt gegen die Spezifikation (höchstens 64 Zeichen, a-z, 0-9, Bindestrich, nicht anthropic oder claude)')
    if re.search(r'[<>]', m.group(1) + m.group(2)):
        fehler.append(f'{name}: spitze Klammern (XML-Tags) in name oder description nicht erlaubt')
    if not m.group(2).strip():
        fehler.append(f'{name}: description leer')
    if t.count('\n') + 1 > 500:
        fehler.append(f'{name}: SKILL.md über 500 Zeilen (Empfehlung der Spezifikation)')
    if re.search(r'\b(ich|mich|mir|I|me|my)\b', re.sub(r'„[^“]*“|“[^”]*”|"[^"]*"', '', m.group(2))):
        hinweise.append(name)
    if len(m.group(2)) > 1024:
        fehler.append(f'{name}: description über 1024 Zeichen')
    pfad = os.path.join(out, name + '.zip')
    with zipfile.ZipFile(pfad, 'w', zipfile.ZIP_DEFLATED) as z:
        zi = zipfile.ZipInfo(f'{name}/SKILL.md', date_time=(2026, 10, 31, 0, 0, 0))
        zi.compress_type = zipfile.ZIP_DEFLATED
        zi.external_attr = 0o644 << 16
        z.writestr(zi, t.encode('utf-8'))
    print(f'  gebaut {os.path.relpath(pfad, root)} ({os.path.getsize(pfad)} Bytes, SKILL.md {len(t)} Zeichen)')
if fehler:
    print(f'FEHLER: {len(fehler)}')
    for f in fehler:
        print(' -', f)
    sys.exit(1)
if hinweise:
    print(f'Hinweis: {len(hinweise)} Beschreibungen sind nicht in dritter Person (Spezifikation, Ich-Form): ' + ', '.join(hinweise))
print(f'{len(skills)} ZIPs, sauber')

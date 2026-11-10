#!/usr/bin/env python3
"""Skelett prüfen und bauen. Aufruf: python3 -I skelett.py <pruefen|bauen> <second-brain-wurzel>
pruefen: Frontmatter der Skills, Länge der Anweisungen, Fragetexte und Optionen wörtlich gegen spec/Fragen_Stufe1.yaml,
         Aktivierungsoptionen der Module, Datenschutz-Sperre (keine Spur der Muttersprache der Nutzerin).
bauen:   schreibt dist/<skill>.zip je Skill und dist/second-brain-skills-buendel.zip (alle Skills in einem ZIP).
         Inhalt und Reihenfolge der ZIP-Einträge sind deterministisch (feste Zeitstempel, sortiert). Die komprimierten Bytes
         können je zlib-Version abweichen: Vergleiche daher die Hashes der Einträge, nicht der ZIP-Dateien."""
import sys, os, re, glob, zipfile, yaml

cmd, root = sys.argv[1], sys.argv[2]
sk = os.path.join(root, 'skeleton')
fehler = []
F = fehler.append
SPUR = re.compile(r'[\u0400-\u06FF\u0E00-\u0E7F\u3040-\u9FFF]')

skills = sorted(d for d in os.listdir(os.path.join(sk, 'skills')) if os.path.isdir(os.path.join(sk, 'skills', d)))

def pruefen():
    # Datenschutz-Sperre über alles im Skelett
    for p in glob.glob(os.path.join(sk, '**', '*.*'), recursive=True):
        if os.path.basename(p) == 'skelett.py':
            continue   # enthält das Suchmuster selbst
        for n, z in enumerate(open(p, encoding='utf-8'), 1):
            if SPUR.search(z):
                F(f'{os.path.relpath(p, root)}:{n}: Sprachspur gefunden')
    # Skills: Frontmatter
    texte = {}
    for s in skills:
        t = open(os.path.join(sk, 'skills', s, 'SKILL.md'), encoding='utf-8').read()
        texte[s] = t
        m = re.match(r'---\nname: (.+)\ndescription: (.+)\n---\n', t)
        if not m:
            F(f'{s}: Frontmatter (name, description) fehlt oder ist mehrzeilig'); continue
        if m.group(1) != s:
            F(f'{s}: name {m.group(1)!r} passt nicht zum Ordner')
        if not re.fullmatch(r'[a-z][a-z0-9-]{0,63}', m.group(1)):
            F(f'{s}: name ungültig')
        if len(m.group(2)) > 1024:
            F(f'{s}: description über 1024 Zeichen ({len(m.group(2))})')
        print(f'  {s}: description {len(m.group(2))} Zeichen, SKILL.md {len(t)} Zeichen')
    # Zusatzdateien im Skill-Ordner stehen Claude im Free-Konto nicht sicher zur Verfügung (Befund D9)
    for s in skills:
        extra = [f for f in os.listdir(os.path.join(sk, 'skills', s)) if f != 'SKILL.md']
        if extra:
            F(f'{s}: Zusatzdateien {extra} im Skill-Ordner (Befund D9: Inhalt gehört in die SKILL.md)')
    # Anweisungen
    a = open(os.path.join(sk, 'anweisungen', 'Projekt-Anweisungen.txt'), encoding='utf-8').read()
    print(f'  Projekt-Anweisungen: {len(a)} Zeichen')
    if len(a) > 5000:
        F(f'Projekt-Anweisungen {len(a)} Zeichen, Ziel unter 5000')
    # Fragen wörtlich
    fr = yaml.safe_load(open(os.path.join(root, 'spec', 'Fragen_Stufe1.yaml'), encoding='utf-8'))
    iv = texte.get('onboarding-interview', '')
    fragen = [q for r in fr['runden'] for q in r['fragen']] + list(fr.get('vorsatz', []))
    for q in fragen:
        if q['frage'] not in iv:
            F(f'onboarding-interview: Frage {q["id"]} nicht wörtlich enthalten: {q["frage"]!r}')
        for o in q.get('optionen', []):
            o2 = o.replace(' (Empfohlen)', '').replace(' (Recommended)', '')
            if o2 not in iv:
                F(f'onboarding-interview: Option {o2!r} ({q["id"]}) nicht wörtlich enthalten')
        for ff in q.get('folgefragen', []):
            if ff['frage'] not in iv:
                F(f'onboarding-interview: Folgefrage {ff["id"]} nicht wörtlich enthalten')
        for k in ('hinweis_bei', 'hinweis_wenn_nur'):
            for o, text in (q.get(k) or {}).items():
                if text not in iv:
                    F(f'onboarding-interview: Hinweistext zu {o!r} ({q["id"]}) nicht wörtlich enthalten')
    # Stufe 2 und die Regeln beider Stufen wörtlich im Skill (Trockenlauf 4, Entscheid 03.11.)
    p2 = os.path.join(root, 'spec', 'Fragen_Stufe2.yaml')
    fr2 = yaml.safe_load(open(p2, encoding='utf-8')) if os.path.exists(p2) else {}
    for q in fr2.get('fragen', []):
        if q['frage'] not in iv:
            F(f'onboarding-interview: Stufe-2-Frage {q["id"]} nicht wörtlich enthalten: {q["frage"]!r}')
        for o in q.get('optionen', []):
            o2 = str(o).replace(' (Empfohlen)', '').replace(' (Recommended)', '')
            if o2 not in iv:
                F(f'onboarding-interview: Option {o2!r} ({q["id"]}) nicht wörtlich enthalten')
    for name in (fr2.get('eigene_bereiche') or {}):
        if f'- {name}: ' not in iv:
            F(f'onboarding-interview: eigener Bereich {name!r} fehlt in der Tabelle der eigenen Bereiche')
    for name, d in (('Stufe 1', fr), ('Stufe 2', fr2)):
        for k, text in (d.get('regeln') or {}).items():
            if text not in iv:
                F(f'onboarding-interview: Regel {k} ({name}) nicht wörtlich enthalten')
    # Welle 5: gemeinsame Regeln wortgleich in den drei Skills
    gp = os.path.join(root, 'spec', 'Gemeinsame_Regeln.yaml')
    gem = ((yaml.safe_load(open(gp, encoding='utf-8')) or {}).get('regeln') or {}) if os.path.exists(gp) else {}
    for k, text in gem.items():
        for s in ('onboarding-interview', 'setup-brain', 'weekly-review'):
            if text not in texte.get(s, ''):
                F(f'{s}: gemeinsame Regel {k} nicht wörtlich enthalten')
    # Aktivierungsoptionen der Module stehen in der Aktivierungstabelle
    for p in glob.glob(os.path.join(root, 'spec', 'module', '*.yaml')):
        m = yaml.safe_load(open(p, encoding='utf-8'))
        for r in m['aktivierung'].get('wenn_antwort', []):
            if r['option'] not in iv:
                F(f'onboarding-interview: Aktivierungsoption {r["option"]!r} ({m["id"]}) fehlt')
        for v in m['vorlagen']:
            sb = texte.get('setup-brain', '')
            if m['id'] not in ('person', 'werkzeuge') and v['name'] not in sb:
                F(f'setup-brain: Dokument {v["name"]!r} ({m["id"]}) fehlt')
    # Kern-Dokumente stehen in setup-brain und in den Vorlagen
    vorl = texte['setup-brain']
    kern = yaml.safe_load(open(os.path.join(root, 'spec', 'module', 'kern.yaml'), encoding='utf-8'))
    for v in kern['vorlagen']:
        if v['name'] not in texte['setup-brain']:
            F(f'setup-brain: Kern-Eintrag {v["name"]!r} fehlt')
        if v['art'] == 'doc' and f'## {v["name"]}' not in vorl:
            F(f'setup-brain: Vorlage für {v["name"]!r} fehlt')
    # Feste Wertelisten (Befunde D7/D8) wörtlich in Anweisungen und Interview-Skill
    sc = yaml.safe_load(open(os.path.join(root, 'spec', 'Profilschema.yaml'), encoding='utf-8'))
    for w in sc['werte']['status'] + sc['werte']['quelle']:
        for name, txt in (('onboarding-interview', iv), ('Projekt-Anweisungen', a)):
            if w not in txt:
                F(f'{name}: Wert {w!r} aus Profilschema.werte fehlt')

    # Konto-Text wörtlich aus spec/Konto_Text.md in setup-brain
    kt = open(os.path.join(root, 'spec', 'Konto_Text.md'), encoding='utf-8').read()
    km = re.search(r'```\n(.*?)```', kt, re.S)
    if not km or km.group(1) not in vorl:
        F('setup-brain: Konto-Text aus spec/Konto_Text.md nicht wörtlich enthalten')

    # Bausteine der Module stehen wörtlich in setup-brain; die Anweisungen verweisen auf die Bereichsregeln
    for p in sorted(glob.glob(os.path.join(root, 'spec', 'module', '*.yaml'))):
        m = yaml.safe_load(open(p, encoding='utf-8'))
        if m['id'] == 'kern':
            continue
        b = (m.get('anweisungsbaustein') or '').strip('\n')
        if not b:
            F(f'Modul {m["id"]}: kein Anweisungsbaustein')
        elif b not in vorl:
            F(f'setup-brain: Anweisungsbaustein von {m["id"]} nicht wörtlich enthalten')
    if '## Bereichsregeln' not in vorl and '## Area rules' not in vorl:
        F('setup-brain: Abschnitt Bereichsregeln in der Vorlage von 00_Status fehlt')
    if 'Bereichsregeln' not in a and 'Area rules' not in a:
        F('Projekt-Anweisungen: Verweis auf die Bereichsregeln fehlt')

    # Skills je Bereich (Befund F14, 10.11.2026): die Tabelle in setup-brain nennt die Skills jedes Moduls wie die Spec
    tm = re.search(r'## (?:Skills je Bereich|Skills per area)\n(.*?)(?=\n## )', vorl, re.S)
    if not tm:
        F('setup-brain: Abschnitt "Skills je Bereich" fehlt')
    else:
        zeilen = {}
        for z in tm.group(1).splitlines():
            zellen = [c.strip() for c in z.strip().strip('|').split('|')]
            if z.strip().startswith('|') and len(zellen) >= 2:
                zeilen[zellen[0]] = zellen[1]
        for p in sorted(glob.glob(os.path.join(root, 'spec', 'module', '*.yaml'))):
            m = yaml.safe_load(open(p, encoding='utf-8'))
            if m['id'] == 'kern' or not m['skills']:
                continue
            for s in m['skills']:
                if s not in zeilen.get(m['id'], ''):
                    F(f'setup-brain: Tabelle "Skills je Bereich": Skill {s} von {m["id"]} fehlt')

    # Skill area-manager (nachrüstbar, liegt in skills/): Verzeichnis und Bausteine gegen die Module
    am = os.path.join(root, 'skills', 'area-manager', 'SKILL.md')
    if os.path.exists(am):
        amt = open(am, encoding='utf-8').read()
        for p in sorted(glob.glob(os.path.join(root, 'spec', 'module', '*.yaml'))):
            m = yaml.safe_load(open(p, encoding='utf-8'))
            if m['id'] == 'kern':
                continue
            b = (m.get('anweisungsbaustein') or '').strip('\n')
            if b not in amt:
                F(f'area-manager: Baustein von {m["id"]} nicht wörtlich enthalten')
            if f'| {m["id"]} | {m["version"]} |' not in amt:
                F(f'area-manager: Verzeichniszeile mit Version für {m["id"]} fehlt oder weicht ab')
            for s in m['skills']:
                if s not in amt:
                    F(f'area-manager: Skill {s} von {m["id"]} fehlt im Verzeichnis')

def bauen():
    out = os.path.join(root, 'dist')
    os.makedirs(out, exist_ok=True)
    def zip_(pfad, ordner):
        with zipfile.ZipFile(pfad, 'w', zipfile.ZIP_DEFLATED) as z:
            for s in ordner:
                for p in sorted(glob.glob(os.path.join(sk, 'skills', s, '**', '*'), recursive=True)):
                    if os.path.isfile(p):
                        arc = os.path.relpath(p, os.path.join(sk, 'skills'))
                        zi = zipfile.ZipInfo(arc, date_time=(2026, 10, 31, 0, 0, 0))
                        zi.compress_type = zipfile.ZIP_DEFLATED
                        zi.external_attr = 0o644 << 16
                        z.writestr(zi, open(p, 'rb').read())
        print('  gebaut', os.path.relpath(pfad, root))
    for s in skills:
        zip_(os.path.join(out, s + '.zip'), [s])
    zip_(os.path.join(out, 'second-brain-skills-buendel.zip'), skills)

if cmd == 'pruefen':
    pruefen()
elif cmd == 'bauen':
    pruefen()
    if not fehler:
        bauen()
else:
    sys.exit('pruefen oder bauen')
if fehler:
    print(f'FEHLER: {len(fehler)}')
    for f in fehler:
        print(' -', f)
    sys.exit(1)
print('Skelett sauber')

#!/usr/bin/env python3
"""Parität der Sprachpakete prüfen (de und en). Entwurf 01.11.2026.
Aufruf: python3 -I tools/lang_parity.py pruefen <wurzel-de> <wurzel-en>
        python3 -I tools/lang_parity.py selbsttest <wurzel-de> <wurzel-en>
Prüft, dass beide Pakete dieselbe Struktur haben, ohne die Sprache zu verstehen:
  - gleiche Dateien (spec/*.yaml|md, spec/module, skills/*/SKILL.md, skeleton/skills/*/SKILL.md, skeleton/anweisungen/*.txt)
  - YAML: gleiche Schlüssel, gleiche Listenlängen, gleiche IDs, Typen, Tags, Profilpfade, Fragenreferenzen
  - SKILL.md und Anweisungen: gleicher Frontmatter-Name, gleiche Zahl an Überschriften, Codeblöcken und Tabellenzeilen
  - im en-Paket keine deutschen Dokumentnamen (außer in plain-prose-de, wo deutsche Beispiele gewollt sind)
Bekannte, gewollte Abweichungen stehen in AUSNAHMEN. Prüft Struktur, nicht die Qualität der Übersetzung."""
import sys, os, re, glob, shutil, tempfile
import yaml

DATEIEN = ['spec/*.yaml', 'spec/*.md', 'spec/module/*.yaml', 'skills/*/SKILL.md', 'skeleton/skills/*/SKILL.md',
           'skeleton/anweisungen/*.txt']
# Pfade (Dateiname:Schlüsselpfad), bei denen Listenlängen bewusst abweichen dürfen
AUSNAHMEN = {'spec/Fragen_Stufe1.yaml:runden.0.fragen.0.fragen.0.optionen'}
INVARIANT = {'id', 'typ', 'pflicht', 'modul', 'art', 'version', 'profil_pfad', 'zaehlt_mit', 'tags', 'referenz', 'kanal_detail',
             'skills', 'eigener_projektkandidat', 'runde', 'reihenfolge', 'schema_version', 'abgeleitet_aus', 'wenn_modul',
             'immer', 'fiktiv', 'sperrt_tags', 'spaeter', 'modul_aktiv'}
SCHLUESSEL_UEBERSETZT = {'hinweis_bei', 'hinweis_wenn_nur', 'sperrt_tags', 'wenn_antwort', 'antwort', 'antwort_profil', 'bedeutung', 'eigene_bereiche'}
DEUTSCH_DOKUMENTE = ['Fakten-Ledger', 'Wochenplan', '01_Profil', '02_Offene_Fragen', 'State_Arbeit', 'State_Familie',
                     'State_Termine', 'State_Lernen', 'Lernprotokoll', 'Stilprofil', 'Bauprojekte', 'Briefe_Scans',
                     'Prüfzeile', 'Gelesen:', 'Abgelegt:']
SPUR = re.compile(r'[\u0400-\u06FF\u0E00-\u0E7F\u3040-\u9FFF]')
fehler = []
F = fehler.append


def dateien(root):
    s = set()
    for g in DATEIEN:
        for p in glob.glob(os.path.join(root, g)):
            s.add(os.path.relpath(p, root))
    return s


def yaml_vergleich(ort, a, b):
    if type(a) != type(b):
        F(f'{ort}: Typ {type(a).__name__} gegen {type(b).__name__}')
        return
    if isinstance(a, dict):
        schluessel = ort.rsplit('.', 1)[-1]
        if schluessel in SCHLUESSEL_UEBERSETZT:
            if len(a) != len(b):
                F(f'{ort}: {len(a)} Einträge gegen {len(b)}')
            elif schluessel == 'sperrt_tags' and sorted(a.values()) != sorted(b.values()):
                F(f'{ort}: Tags {sorted(a.values())} gegen {sorted(b.values())}')
            return
        if set(a) != set(b):
            F(f'{ort}: Schlüssel {sorted(set(a) ^ set(b))} nur in einer Sprache')
        for k in a:
            if k in b:
                yaml_vergleich(f'{ort}.{k}' if ort else k, a[k], b[k])
    elif isinstance(a, list):
        if len(a) != len(b) and ort not in AUSNAHMEN:
            F(f'{ort}: Liste mit {len(a)} gegen {len(b)} Einträgen')
            return
        if ort.rsplit('.', 1)[-1] in INVARIANT and '.ziele.' not in ort:
            if a != b:
                F(f'{ort}: {a} gegen {b}')
            return
        for i, (x, y) in enumerate(zip(a, b)):
            yaml_vergleich(f'{ort}.{i}', x, y)
    else:
        k = ort.rsplit('.', 1)[-1]
        if k in INVARIANT and a != b:
            F(f'{ort}: {a!r} gegen {b!r}')
        if k == 'frage' and isinstance(a, str) and re.match(r's\d\.', a) and a != b:
            F(f'{ort}: Verweis {a!r} gegen {b!r}')


def text_kennzahlen(t):
    t = t.replace('\r', '')
    ueb = len(re.findall(r'(?m)^#{1,6} ', re.sub(r'```.*?```', '', t, flags=re.S)))
    zaun = t.count('```')
    tab = len(re.findall(r'(?m)^\|', t))
    return ueb, zaun, tab


def pruefen(de, en):
    a, b = dateien(de), dateien(en)
    for p in sorted(a - b):
        if p.startswith('spec/personas'):
            continue
        F(f'{p}: nur im deutschen Paket')
    for p in sorted(b - a):
        F(f'{p}: nur im englischen Paket')
    for p in sorted(a & b):
        ta = open(os.path.join(de, p), encoding='utf-8').read()
        tb = open(os.path.join(en, p), encoding='utf-8').read()
        if p.endswith('.yaml'):
            yaml_vergleich(p, yaml.safe_load(ta), yaml.safe_load(tb))
        else:
            ka, kb = text_kennzahlen(ta), text_kennzahlen(tb)
            if ka != kb:
                F(f'{p}: Überschriften/Codeblöcke/Tabellenzeilen {ka} gegen {kb}')
            if p.endswith('SKILL.md'):
                na = re.search(r'(?m)^name: (.+)$', ta); nb = re.search(r'(?m)^name: (.+)$', tb)
                if not na or not nb or na.group(1) != nb.group(1):
                    F(f'{p}: Frontmatter-Name verschieden')
    # englisches Paket: keine deutschen Dokumentnamen
    for p in sorted(b):
        if p.endswith('plain-prose-de/SKILL.md'):
            continue
        tb = open(os.path.join(en, p), encoding='utf-8').read()
        for w in DEUTSCH_DOKUMENTE:
            if re.search(r'(?<![\w-])' + re.escape(w) + r'(?![\w-])', tb):
                F(f'{p}: deutscher Dokumentname {w!r} im englischen Paket')
        if SPUR.search(tb):
            F(f'{p}: Sprachspur gefunden')
    return len(a & b)


def kopie(src, ziel):
    for g in DATEIEN:
        for p in glob.glob(os.path.join(src, g)):
            r = os.path.relpath(p, src)
            os.makedirs(os.path.dirname(os.path.join(ziel, r)), exist_ok=True)
            shutil.copy(p, os.path.join(ziel, r))


def selbsttest(de, en):
    muster = [
        ('spec/Fragen_Stufe1.yaml', lambda t: t.replace('          - Prepare decisions\n', '', 1)),
        ('spec/Fragen_Stufe1.yaml', lambda t: t.replace('id: s1.zeit', 'id: s1.zeit2', 1)),
        ('spec/module/wissen.yaml', lambda t: t.replace('skills: [knowledge-note]', 'skills: []', 1)),
        ('spec/module/kern.yaml', lambda t: t.replace('  - {name: Weekly-Plan, art: doc}\n', '', 1)),
        ('skills/fact-check/SKILL.md', lambda t: t.replace('## Rules', '', 1)),
        ('skills/fact-check/SKILL.md', lambda t: t.replace('name: fact-check', 'name: fact-checker', 1)),
        ('skeleton/skills/setup-brain/SKILL.md', lambda t: t.replace('```\n', '', 1)),
        ('skills/decision-check/SKILL.md', lambda t: t + '\nSiehe Wochenplan.\n'),
        ('skeleton/anweisungen/Projekt-Anweisungen.txt', lambda t: t + '\n## Extra\n'),
    ]
    nicht_erkannt = 0
    for i, (datei, mut) in enumerate(muster):
        tmp = tempfile.mkdtemp(prefix='sbparity')
        kopie(en, tmp)
        p = os.path.join(tmp, datei)
        alt = open(p, encoding='utf-8').read()
        neu = mut(alt)
        if neu == alt:
            print(f'  Mutation {i}: ändert nichts (Test kaputt)'); nicht_erkannt += 1; continue
        open(p, 'w', encoding='utf-8').write(neu)
        fehler.clear()
        pruefen(de, tmp)
        if not fehler:
            print(f'  Mutation {i} ({datei}) NICHT erkannt'); nicht_erkannt += 1
        shutil.rmtree(tmp, ignore_errors=True)
    fehler.clear()
    pruefen(de, en)
    print(f'Selbsttest: {len(muster)} Mutationen, {nicht_erkannt} nicht erkannt; Ausgangslage {len(fehler)} Befunde')
    return nicht_erkannt == 0 and not fehler


if __name__ == '__main__':
    cmd, de, en = sys.argv[1], sys.argv[2], sys.argv[3]
    if cmd == 'selbsttest':
        ok = selbsttest(de, en)
        sys.exit(0 if ok else 1)
    n = pruefen(de, en)
    print(f'Gemeinsame Dateien: {n}')
    if fehler:
        print(f'FEHLER: {len(fehler)}')
        for f in fehler:
            print(' -', f)
        sys.exit(1)
    print('Parität sauber')

#!/usr/bin/env python3
"""SKILL.md-Kopf prüfen: Frontmatter, Schlüssel, Name, Beschreibung. Entwurf 12.11.2026.
Eigene Umsetzung der öffentlich dokumentierten Regeln des Agent-Skills-Formats (agentskills.io), kein kopierter Code.
Aufruf (Arbeitsrepo oder Export, Wurzel ist das Verzeichnis mit skills/ bzw. de/ und en/):
  python3 -I tools/frontmatter_pruefen.py pruefen <wurzel>     alle SKILL.md unter den bekannten Skill-Ordnern prüfen
  python3 -I tools/frontmatter_pruefen.py selbsttest           Mutationen auf einer Kopie müssen erkannt werden
Fehler (Exit 1): kein Frontmatter, unerlaubter Schlüssel, Name nicht kebab-case oder länger als 64 oder ungleich Ordnername,
Beschreibung fehlt, länger als 1024 Zeichen oder mit spitzen Klammern.
Warnung (Exit 0): SKILL.md länger als 500 Zeilen."""
import sys, os, re, glob, shutil, tempfile
import yaml

ERLAUBT = {'name', 'description', 'license', 'allowed-tools', 'metadata', 'compatibility'}
MAX_NAME, MAX_BESCHR, MAX_ZEILEN = 64, 1024, 500
ORDNER = ('skills', 'skeleton/skills', 'en/skills', 'en/skeleton/skills', 'de/skills', 'de/skeleton/skills')


def kopf(text):
    """Frontmatter als dict oder (None, Fehlertext)."""
    if not text.startswith('---\n'):
        return None, 'kein Frontmatter am Dateianfang'
    m = re.match(r'^---\n(.*?)\n---(\n|$)', text, re.DOTALL)
    if not m:
        return None, 'Frontmatter nicht geschlossen'
    try:
        d = yaml.safe_load(m.group(1))
    except yaml.YAMLError as e:
        return None, f'YAML im Frontmatter ungültig: {e}'
    if not isinstance(d, dict):
        return None, 'Frontmatter ist kein Verzeichnis aus Schlüsseln'
    return d, None


def pruefe_datei(pfad):
    """(fehler, warnungen) für eine SKILL.md."""
    fehler, warn = [], []
    with open(pfad, encoding='utf-8') as f:
        text = f.read()
    d, f_kopf = kopf(text)
    if f_kopf:
        return [f_kopf], warn
    for k in sorted(set(d) - ERLAUBT):
        fehler.append(f'unerlaubter Schlüssel „{k}“ (erlaubt: {", ".join(sorted(ERLAUBT))})')
    name = d.get('name')
    ordner = os.path.basename(os.path.dirname(os.path.abspath(pfad)))
    if not isinstance(name, str) or not name.strip():
        fehler.append('name fehlt oder ist kein Text')
    else:
        name = name.strip()
        if not re.match(r'^[a-z0-9-]+$', name):
            fehler.append(f'name „{name}“ nicht kebab-case (nur a–z, 0–9, Bindestrich)')
        if name.startswith('-') or name.endswith('-') or '--' in name:
            fehler.append(f'name „{name}“ mit Bindestrich am Rand oder doppeltem Bindestrich')
        if len(name) > MAX_NAME:
            fehler.append(f'name hat {len(name)} Zeichen, höchstens {MAX_NAME}')
        if name != ordner:
            fehler.append(f'name „{name}“ ungleich Ordnername „{ordner}“')
    b = d.get('description')
    if not isinstance(b, str) or not b.strip():
        fehler.append('description fehlt, ist leer oder kein Text')
    else:
        b = b.strip()
        if len(b) > MAX_BESCHR:
            fehler.append(f'description hat {len(b)} Zeichen, höchstens {MAX_BESCHR}')
        if '<' in b or '>' in b:
            fehler.append('description enthält spitze Klammern')
    c = d.get('compatibility')
    if c is not None and (not isinstance(c, str) or len(c) > 500):
        fehler.append('compatibility muss Text mit höchstens 500 Zeichen sein')
    zeilen = text.count('\n') + (0 if text.endswith('\n') else 1)
    if zeilen > MAX_ZEILEN:
        warn.append(f'{zeilen} Zeilen, empfohlen höchstens {MAX_ZEILEN}')
    return fehler, warn


def dateien(wurzel):
    out = []
    for rel in ORDNER:
        out += sorted(glob.glob(os.path.join(wurzel, rel, '*', 'SKILL.md')))
    return out


def pruefen(wurzel):
    dat = dateien(wurzel)
    if not dat:
        print(f'FEHLER: keine SKILL.md unter {wurzel} gefunden (gesucht in {", ".join(ORDNER)})')
        return 1
    n_f = 0
    for p in dat:
        fe, wa = pruefe_datei(p)
        rel = os.path.relpath(p, wurzel)
        for z in fe:
            print(f'FEHLER  {rel}: {z}')
        for z in wa:
            print(f'Warnung {rel}: {z}')
        n_f += len(fe)
    print(f'{len(dat)} SKILL.md geprüft, {n_f} Fehler')
    return 1 if n_f else 0


GUT = '---\nname: {n}\ndescription: {b}\n---\n\n# Test\n'


def selbsttest():
    """Eine gültige Datei muss bestehen, jede Mutation muss einen Fehler liefern."""
    t = tempfile.mkdtemp()
    try:
        faelle = {
            'gut': (GUT.format(n='mein-skill', b='Tut etwas. Verwenden bei „mach das“.'), 'mein-skill', False),
            'ohne-kopf': ('# nur Text\n', 'mein-skill', True),
            'nicht-geschlossen': ('---\nname: mein-skill\ndescription: x\n', 'mein-skill', True),
            'fremder-schluessel': ('---\nname: mein-skill\nversion: 1\ndescription: x\n---\nx\n', 'mein-skill', True),
            'name-gross': (GUT.format(n='Mein-Skill', b='x'), 'Mein-Skill', True),
            'name-doppelstrich': (GUT.format(n='mein--skill', b='x'), 'mein--skill', True),
            'name-ungleich-ordner': (GUT.format(n='anderer', b='x'), 'mein-skill', True),
            'beschreibung-leer': ('---\nname: mein-skill\ndescription: ""\n---\nx\n', 'mein-skill', True),
            'beschreibung-zu-lang': (GUT.format(n='mein-skill', b='a' * 1025), 'mein-skill', True),
            'beschreibung-klammer': (GUT.format(n='mein-skill', b='nimm <das>'), 'mein-skill', True),
        }
        ok = True
        for k, (inhalt, ordner, soll_fehler) in faelle.items():
            d = os.path.join(t, k, 'skills', ordner)
            os.makedirs(d)
            p = os.path.join(d, 'SKILL.md')
            with open(p, 'w', encoding='utf-8') as f:
                f.write(inhalt)
            fe, _ = pruefe_datei(p)
            gut = bool(fe) == soll_fehler
            ok &= gut
            print(('ok     ' if gut else 'FALSCH ') + f'{k}: {"Fehler erkannt" if fe else "kein Fehler"}' + (f' ({fe[0]})' if fe else ''))
        # Zeilen-Warnung
        d = os.path.join(t, 'lang', 'skills', 'mein-skill')
        os.makedirs(d)
        p = os.path.join(d, 'SKILL.md')
        with open(p, 'w', encoding='utf-8') as f:
            f.write(GUT.format(n='mein-skill', b='x') + 'zeile\n' * 600)
        fe, wa = pruefe_datei(p)
        gut = not fe and bool(wa)
        ok &= gut
        print(('ok     ' if gut else 'FALSCH ') + f'zu-lang: Warnung ohne Fehler ({wa[0] if wa else "keine Warnung"})')
        print('Selbsttest bestanden' if ok else 'Selbsttest FEHLGESCHLAGEN')
        return 0 if ok else 1
    finally:
        shutil.rmtree(t, ignore_errors=True)


if __name__ == '__main__':
    a = sys.argv[1:]
    if a[:1] == ['pruefen'] and len(a) == 2:
        sys.exit(pruefen(a[1]))
    if a == ['selbsttest']:
        sys.exit(selbsttest())
    print(__doc__)
    sys.exit(2)

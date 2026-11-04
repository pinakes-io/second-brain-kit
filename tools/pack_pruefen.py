#!/usr/bin/env python3
"""Pack prüfen und Skill bauen (Modul bauen, Skill vibe-pack). Entwurf 01.11.2026.
Aufruf: python3 -I pack_pruefen.py <befehl> <second-brain-wurzel> [datei] [--fall <id>]
  skill        SKILL.md von vibe-pack (Wurzel en: englisches Paket, Abschnitte und Wörter auf Englisch): Frontmatter, Länge, Sperrwörter, gerade Anführungszeichen, nur eine Datei,
               Abschnitte vorhanden, die Vorlage im Skill erfüllt alle Pflichtbausteine, Pflichtliste und Richtwerte
               gleich denen in docs/vibe-pack/eval/faelle.yaml.
  pack <datei> ein erzeugtes Pack (aus einem Testlauf in claude.ai eingefügt): Pflichtbausteine, Verbote (Platzhalter,
               echte Daten), Längen. Mit --fall <id> zusätzlich die Fallregeln (kundenliste, einkaufsliste,
               ki_zusammenfassung). Echte Daten werden nur als Art gemeldet, nie ausgegeben.
  selbsttest   das gute Beispiel muss sauber sein, jede Mutation muss erkannt werden.
  bauen        skill und selbsttest, danach dist/vibe-pack.zip (ein ZIP, ein Skill).
Prüft Muster, keine Bedeutung. Für die Fälle bestandsskript und ablauf_mail_tabelle (Rücklauf, Routing) gibt es keine
Mustersuche: die prüft man im Testlauf von Hand."""
import sys, os, re, glob, zipfile
import yaml
HIER = os.path.dirname(os.path.abspath(__file__))

MAX_SKILL = 8000
MAX_AGENTS = 2000
MAX_REGELN = 8
MAX_BLATT = 5
SPUR = re.compile(r'[\u0400-\u06FF\u0E00-\u0E7F\u3040-\u9FFF]')
SPERR_HASH = {'08bb42a30ca57f34', '0e687aaa28b03552', '10e9f239e3523081', '1fb64a3038eeafe3', '2fb41c42cec5d64a', '40682117405d613a', '4756fd517ec88676', '5aaaa9680bbe0c27', '69db31976ead37b8', 'a9070f7731fa04c9', 'cd5b21ee2453ac37', 'cd81fa9aeafb6a12', 'da075a7cb2f313f3', 'dad17e1c456be506', 'f3f2184b56f946c6', 'fe432cb211dac676'}
import hashlib


def sperrwort(text):
    """Sperrwörter als Prüfsummen (Einzelwörter und Wortpaare), damit die Namen nirgends im Klartext stehen."""
    toks = re.findall(r'[\wäöüß]+', text.lower())
    for i, t in enumerate(toks):
        if hashlib.sha256(t.encode()).hexdigest()[:16] in SPERR_HASH:
            return True
        if i + 1 < len(toks) and hashlib.sha256((t + ' ' + toks[i + 1]).encode()).hexdigest()[:16] in SPERR_HASH:
            return True
    return False

ABSCHNITTE = {
    'de': ('## Rolle', '## Vibe Check', '## Pre-Mortem', '## Das Pack', '## Quellenleiter', '## Rücklauf',
           '## Ausgabe', '## Grenzen', '## Beispiel', '## Selbstprüfung'),
    'en': ('## Role', '## Vibe check', '## Pre-mortem', '## The pack', '## Source ladder', '## Feedback loop',
           '## Output', '## Limits', '## Example', '## Self-check'),
}
WOERTER = {
    'de': ('Es geht nicht', 'Nächste Sitzung', '🔎 Pack:', 'Doc Bauprojekte'),
    'en': ('It does not work', 'Next session', '🔎 Pack:', 'doc Build_Projects'),
}

HTML = {'a', 'p', 'br', 'hr', 'div', 'span', 'html', 'head', 'body', 'script', 'style', 'ul', 'ol', 'li', 'h1', 'h2', 'h3', 'h4',
        'input', 'button', 'form', 'table', 'tr', 'td', 'th', 'img', 'label', 'title', 'meta', 'link', 'section', 'nav',
        'header', 'footer', 'main', 'canvas', 'select', 'option', 'textarea', 'b', 'i', 'em', 'strong', 'code', 'pre'}

# Pflichtbausteine; die Schlüssel entsprechen docs/vibe-pack/eval/faelle.yaml (gemeinsam.pflicht)
PFLICHT = {
    'verbote_test_loeschen': [r'Never delete, skip or weaken tests'],
    'verbote_fake': [r'No fake implementations'],
    'verbote_secrets': [r'Secrets only from environment variables'],
    'verbote_rm': [r'Nothing destructive'],
    'schnittstellen_erhalten': [r'Do not change existing interfaces'],
    'doku_vor_code': [r'Docs before code'],
    'abnahme_laiensprache': [r'(?m)^Done means: \S'],
    'nicht_ziele': [r'(?m)^Not now: \S'],
    'tracer_mit_erwarteter_ausgabe': [r'(?m)^1 Tracer:.*Expected:'],
    'verification_vor_fertig': [r'(?m)^2 Verification:', r'only after showing the command and its output'],
    'stopp_nach_versuchen': [r'three failed attempts'],
    'uebergabe_am_ende': [r'(?m)^At the end of every session write HANDOVER\.md', r'(?m)^Last: write HANDOVER\.md'],
}
# Weitere Bausteine des Skills (Echtdaten-Regel, Pre-Mortem), nicht in der Pflichtliste der Fälle
EXTRA = {
    'echtdaten_regel': [r'Use invented sample data only'],
    'risks': [r'(?m)^Risks: \S'],
    'setup_knoten': [r'(?m)^0 Setup:'],
}
ECHT = {
    'E-Mail-Muster': r'[\w.+-]+@[\w-]+\.[\w.-]+',
    'Telefon-Muster': r'(?<!\d)(?:\+49|0049|0)\d{2,4}[ /-]?\d{5,}(?!\d)',
    'IBAN-Muster': r'\b[A-Z]{2}\d{2}(?: ?\d{4}){3,}\b',
}
KI_BLOCK = ('AI feature rules:\n- Fixed workflow first, an agent loop only where it is really needed.\n'
            '- Set a cost cap and count tokens per call.\n- Never run model-generated code unprotected.\n'
            '- Use structured output with a schema, do not parse free text.\n- Log every model call.\n')
FAELLE = {
    'kundenliste': dict(
        muss=[r'Use invented sample data only', r'(?im)^Not now:.*\blogin\b', r'(?im)^Not now:.*\bhosting\b'],
        verboten=[r'(?im)^Stack:.*\b(cloud|aws|azure|firebase|vercel|heroku|supabase)\b']),
    'einkaufsliste': dict(
        muss=[r'(?m)^1 Tracer:.*Expected:'],
        verboten=[r'(?i)\bdocker\b', r'(?i)\b(postgres|mysql|database server)\b', r'(?im)^\d+ .*\blogin\b']),
    'ki_zusammenfassung': dict(
        muss=[r'(?i)fixed workflow', r'(?i)cost cap', r'(?i)never run model-generated code unprotected',
              r'(?i)structured output', r'(?i)log every model call'],
        verboten=[r'(?i)\b(langchain|llamaindex)\b']),
}


def sprache(root):
    """en, wenn die Wurzel das en-Paket ist (en/ im Arbeitsrepo und im Export), sonst de."""
    return 'en' if os.path.basename(os.path.normpath(root)) == 'en' else 'de'


def teile(text):
    t = '\n'.join(z for z in text.splitlines() if not z.startswith('```'))
    p = re.split(r'(?m)^=== (\S+) ===[ \t]*$', t)
    return t, {p[i]: p[i + 1] for i in range(1, len(p) - 1, 2)}


def platzhalter(t):
    funde = []
    for m in re.finditer(r'<([^<>\n]{1,80})>', t):
        erst = m.group(1).strip().lstrip('/').split()[0].lower() if m.group(1).strip() else ''
        if erst not in HTML:
            funde.append(m.group(0))
    funde += re.findall(r'\b(?:TODO|XXX|FIXME|TBD)\b', t)
    funde += re.findall(r'\[(?:\.\.\.|…|\?)\]', t)
    return funde


def pruefe_pack(text, fall=None, vorlage=False):
    f = []
    t, d = teile(text)
    for n in ('AGENTS.md', 'PLAN.md'):
        if n not in d:
            f.append(f'Datei {n} fehlt (Markerzeile === {n} ===)')
    if f:
        return f
    agents, plan = d['AGENTS.md'], d['PLAN.md']
    for tok, muster in {**PFLICHT, **EXTRA}.items():
        for m in muster:
            if not re.search(m, t):
                f.append(f'Pflichtbaustein {tok} fehlt (Muster {m!r})')
    regeln = re.findall(r'(?m)^\d+\. ', agents)
    if len(regeln) > MAX_REGELN:
        f.append(f'{len(regeln)} Regeln in AGENTS.md, höchstens {MAX_REGELN}')
    if len(agents.strip()) > MAX_AGENTS:
        f.append(f'AGENTS.md {len(agents.strip())} Zeichen, höchstens {MAX_AGENTS}')
    for nr, name in ((0, 'Setup'), (1, 'Tracer'), (2, 'Verification')):
        if not re.search(rf'(?m)^{nr} {name}:', plan):
            f.append(f'PLAN.md: Pflichtknoten {nr} {name} fehlt')
    blatt = [z for z in plan.splitlines() if re.match(r'^[3-9] \S', z)]
    if len(blatt) > MAX_BLATT:
        f.append(f'{len(blatt)} Blattknoten, höchstens {MAX_BLATT}')
    for z in blatt:
        if 'Expected:' not in z:
            f.append(f'Blattknoten ohne Expected: {z[:40]!r}')
    if not vorlage:
        for p in platzhalter(t):
            f.append(f'Platzhalter übrig: {p[:40]!r}')
        for art, muster in ECHT.items():
            if re.search(muster, t):
                f.append(f'Verdacht auf echte Daten ({art}); Treffer nicht ausgegeben')
    if fall:
        if fall not in FAELLE:
            f.append(f'Fall {fall!r} unbekannt (kundenliste, einkaufsliste, ki_zusammenfassung)')
        else:
            for m in FAELLE[fall]['muss']:
                if not re.search(m, t):
                    f.append(f'Fall {fall}: erwartet {m!r} fehlt')
            for m in FAELLE[fall]['verboten']:
                if re.search(m, t):
                    f.append(f'Fall {fall}: verboten {m!r} gefunden')
    return f


def skill_pruefen(root):
    f = []
    ordner = os.path.join(root, 'skills', 'vibe-pack')
    p = os.path.join(ordner, 'SKILL.md')
    if not os.path.isfile(p):
        return ['skills/vibe-pack/SKILL.md fehlt']
    rest = [x for x in glob.glob(os.path.join(ordner, '**', '*'), recursive=True)
            if os.path.isfile(x) and os.path.basename(x) != 'SKILL.md']
    if rest:
        f.append(f'Zusatzdateien {rest} (Befund D9: nur SKILL.md ist verlässlich)')
    t = open(p, encoding='utf-8').read()
    m = re.match(r'---\nname: (.+)\ndescription: (.+)\n---\n', t)
    if not m:
        return f + ['Frontmatter (name, description) fehlt oder ist mehrzeilig']
    if m.group(1) != 'vibe-pack':
        f.append(f'name {m.group(1)!r} passt nicht zum Ordner')
    d = m.group(2)
    if len(d) > 1024:
        f.append(f'description {len(d)} Zeichen, höchstens 1024')
    if ': ' in d or ' #' in d:
        f.append('description enthält ": " oder " #" (YAML-Risiko)')
    if '<' in d or '>' in d:
        f.append('spitze Klammern in der description')
    if len(t) > MAX_SKILL:
        f.append(f'SKILL.md {len(t)} Zeichen, höchstens {MAX_SKILL}')
    for n, z in enumerate(t.splitlines(), 1):
        if SPUR.search(z):
            f.append(f'Zeile {n}: Sprachspur')
        if sperrwort(z):
            f.append(f'Zeile {n}: Sperrwort gefunden')
    ohne = re.sub(r'```.*?```', '', t[m.end():], flags=re.S)
    ohne = re.sub(r'`[^`\n]*`', '', ohne)
    for z in ohne.splitlines():
        if '"' in z:
            f.append(f'gerades Anführungszeichen außerhalb von Code: {z.strip()[:50]!r}')
    sp = sprache(root)
    for abschnitt in ABSCHNITTE[sp]:
        if abschnitt not in t:
            f.append(f'Abschnitt {abschnitt!r} fehlt')
    for wort in WOERTER[sp]:
        if wort not in t:
            f.append(f'Skill erwähnt {wort!r} nicht')
    bloecke = [b for b in re.findall(r'```\n(.*?)```', t, re.S) if '=== AGENTS.md ===' in b]
    if len(bloecke) != 1:
        f.append(f'{len(bloecke)} Vorlagenblöcke mit AGENTS.md statt 1')
    else:
        f += ['Vorlage im Skill: ' + x for x in pruefe_pack(bloecke[0], vorlage=True)]
    ki = [b for b in re.findall(r'```\n(.*?)```', t, re.S) if b.startswith('AI feature rules:')]
    if len(ki) != 1 or ki[0] != KI_BLOCK:
        f.append('KI-Block im Skill fehlt oder weicht von KI_BLOCK ab')
    ev = os.path.join(HIER, '..', 'docs', 'vibe-pack', 'eval', 'faelle.yaml')
    if os.path.isfile(ev):
        e = yaml.safe_load(open(ev, encoding='utf-8'))['gemeinsam']
        if set(e['pflicht']) != set(PFLICHT):
            f.append(f'Pflichtliste weicht von faelle.yaml ab: nur Werkzeug {sorted(set(PFLICHT) - set(e["pflicht"]))}, nur faelle {sorted(set(e["pflicht"]) - set(PFLICHT))}')
        r = e['richtwerte']
        if (r['regeldatei_zeichen_max'], r['regeln_max'], r['blattknoten_max']) != (MAX_AGENTS, MAX_REGELN, MAX_BLATT):
            f.append('Richtwerte weichen von faelle.yaml ab')
    else:
        f.append('docs/vibe-pack/eval/faelle.yaml fehlt')
    print(f'  vibe-pack ({sp}): description {len(d)} Zeichen, SKILL.md {len(t)} Zeichen')
    return f


def selbsttest(root):
    f = []
    gut = open(os.path.join(HIER, 'fixtures', 'vibe-pack', 'pack_einkaufsliste.md'), encoding='utf-8').read()
    x = pruefe_pack(gut, fall='einkaufsliste')
    if x:
        f.append(f'Selbsttest: gutes Beispiel nicht sauber: {x}')
    alle = {**PFLICHT, **EXTRA}
    for tok, muster in alle.items():
        neu = '\n'.join(z for z in gut.splitlines() if not re.search(muster[0], z))
        if not any(tok in e for e in pruefe_pack(neu)):
            f.append(f'Selbsttest: Wegfall von {tok} nicht erkannt')

    def erkannt(name, neu, stichwort, fall=None):
        if not any(stichwort in e for e in pruefe_pack(neu, fall=fall)):
            f.append(f'Selbsttest: {name} nicht erkannt')
    erkannt('Platzhalter <name>', gut.replace('```\n', '', 1) + '\n<name>\n', 'Platzhalter')
    erkannt('TODO', gut.replace('Last: write HANDOVER.md.', 'Last: write HANDOVER.md. TODO later'), 'Platzhalter')
    erkannt('E-Mail', gut.replace('Project:', 'Contact: anna@example.org\nProject:'), 'E-Mail-Muster')
    erkannt('Telefon', gut.replace('Project:', 'Call 0171 2345678\nProject:'), 'Telefon-Muster')
    erkannt('zu lange AGENTS.md', gut.replace('Project:', 'Note: ' + 'x' * 2100 + '\nProject:'), 'AGENTS.md')
    erkannt('neunte Regel', gut.replace('\nUse invented', '\n9. One more rule.\n\nUse invented'), 'Regeln in AGENTS.md')
    erkannt('PLAN.md fehlt', gut.replace('=== PLAN.md ===', ''), 'PLAN.md fehlt')
    erkannt('sechs Blattknoten', gut.replace('Last:', '6 a. Expected: b\n7 c. Expected: d\n8 e. Expected: f\nLast:'), 'Blattknoten, höchstens')
    erkannt('Blattknoten ohne Expected', gut.replace('Last:', '6 Extra leaf\nLast:'), 'ohne Expected')
    erkannt('Docker im Einkaufsfall', gut.replace('Plain HTML', 'Docker and plain HTML'), 'Fall einkaufsliste', 'einkaufsliste')
    erkannt('Login als Knoten', gut.replace('3 Cross out', '3 Login screen. Expected: x\n4 Cross out'), 'Fall einkaufsliste', 'einkaufsliste')
    if pruefe_pack(gut, fall='kundenliste'):
        f.append(f'Selbsttest: gutes Beispiel besteht kundenliste nicht: {pruefe_pack(gut, fall="kundenliste")}')
    erkannt('kundenliste ohne Login in Not now', gut.replace('Login, ', ''), 'Fall kundenliste', 'kundenliste')
    erkannt('kundenliste mit Cloud-Stack', gut.replace('Plain HTML', 'Firebase and plain HTML'), 'Fall kundenliste', 'kundenliste')
    erkannt('KI-Fall ohne Block', gut, 'Fall ki_zusammenfassung', 'ki_zusammenfassung')
    mit_ki = gut.replace('\nUse invented', '\n' + KI_BLOCK + '\nUse invented')
    if pruefe_pack(mit_ki, fall='ki_zusammenfassung'):
        f.append(f'Selbsttest: Pack mit KI-Block besteht ki_zusammenfassung nicht: {pruefe_pack(mit_ki, fall="ki_zusammenfassung")}')
    return f


def bauen(root):
    out = os.path.join(root, 'dist')
    os.makedirs(out, exist_ok=True)
    pfad = os.path.join(out, 'vibe-pack.zip')
    with zipfile.ZipFile(pfad, 'w', zipfile.ZIP_DEFLATED) as z:
        zi = zipfile.ZipInfo('vibe-pack/SKILL.md', date_time=(2026, 11, 1, 0, 0, 0))
        zi.compress_type = zipfile.ZIP_DEFLATED
        zi.external_attr = 0o644 << 16
        z.writestr(zi, open(os.path.join(root, 'skills', 'vibe-pack', 'SKILL.md'), 'rb').read())
    print('  gebaut', os.path.relpath(pfad, root))


def main():
    a = sys.argv[1:]
    if len(a) < 2:
        sys.exit(__doc__)
    fall = None
    if '--fall' in a:
        i = a.index('--fall')
        fall = a[i + 1]
        a = a[:i] + a[i + 2:]
    cmd, root = a[0], a[1]
    if cmd == 'skill':
        fehler = skill_pruefen(root)
    elif cmd == 'pack':
        if len(a) < 3:
            sys.exit('pack braucht eine Datei')
        fehler = pruefe_pack(open(a[2], encoding='utf-8').read(), fall=fall)
    elif cmd == 'selbsttest':
        fehler = selbsttest(root)
    elif cmd == 'bauen':
        fehler = skill_pruefen(root) + selbsttest(root)
        if not fehler:
            bauen(root)
    else:
        sys.exit(__doc__)
    if fehler:
        print(f'FEHLER: {len(fehler)}')
        for x in fehler:
            print(' -', x)
        sys.exit(1)
    print('sauber')


if __name__ == '__main__':
    main()

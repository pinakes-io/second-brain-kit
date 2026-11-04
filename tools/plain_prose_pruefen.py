#!/usr/bin/env python3
"""Prüft die Skills plain-prose-de und plain-prose-en und misst Texte. Nur Standardbibliothek.

Aufruf (aus der Repo-Wurzel, mit python3 -I):
  skills    <wurzel>                 Frontmatter, Länge, gemeinsamer Kern wortgleich, Sperrwörter, gerade Anführungszeichen
  text      <de|en> <datei> [<datei2>] Zählwerte und Funde je Datei (Heuristik, keine Lesbarkeitsindizes)
  selbsttest <wurzel>                vorher/nachher-Beispiele unter tools/fixtures/plain-prose/ müssen sich verbessern, ohne Fakten zu verlieren
  eingaben  <wurzel> <ordner>        schreibt die 15 Nutzernachrichten nach <ordner>/<id>.txt (für einen Lauf in claude.ai)
  eval      <wurzel> <ordner>        prüft Skill-Ausgaben (<ordner>/<id>.txt) gegen tools/fixtures/plain-prose/eval/faelle.yaml
  bauen     <wurzel>                 erst skills, dann dist/<skill>.zip (ein Skill je ZIP, feste Zeitstempel)

Die Zählwerte sind Heuristiken (Satzgrenzen, Passiv, Nominalisierungen). Sie dienen dem Testen des Skills,
nicht als Lesbarkeitsurteil. Exit 1 bei Fehlern in skills, selbsttest und bauen."""
import sys, os, re, glob, statistics, zipfile
HIER = os.path.dirname(os.path.abspath(__file__))

SKILLS = ['plain-prose-de', 'plain-prose-en']
SPUR = re.compile(r'[\u0400-\u06FF\u0E00-\u0E7F\u3040-\u9FFF]')
# Eigennamen der Stilquellen und ihrer Kennzahlen nennt der Skill nie (Entscheid 01.11.); großgeschrieben, Wortgrenze
SPERR_HASH = {'206cc80e216c4383', '2dc7c4a9dd718bfd', '59bd2c0cf151dbfb', '5e39d14589c00013', '829af112ee3cdf7f', '84308bea454057aa', '9139fbaccae22a96', 'b7b88b0c808ffb92', 'b8d04d979a920275', 'c5f975b35c72cfe2', 'd523d77885ea1a72'}
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

KERN = re.compile(r'<!-- kern:start.*?<!-- kern:ende -->', re.S)
NB = '\u00a0'
MAX_SKILL = 8000

ABK = ['z. B.', 'd. h.', 'u. a.', 'Abs.', 'Art.', 'bzw.', 'ca.', 'Nr.', 'usw.', 'etc.', 'e.g.', 'i.e.', 'Mr.', 'Dr.', 'vs.']

FLOSKELN = {
    'de': [r'ist es wichtig zu beachten', r'in der heutigen (?:schnelllebigen )?zeit', r'tauchen wir ein',
           r'zusammenfassend lässt sich', r'im folgenden', r'spielt eine (?:entscheidende|zentrale|wichtige) rolle',
           r'auf das nächste level', r'nicht nur\b.{0,80}\bsondern auch', r'\binnovativ', r'\bganzheitlich',
           r'\bnahtlos', r'\bmaßgeschneidert', r'es kommt darauf an', r'verschiedene faktoren',
           r'könnte möglicherweise', r'\bmöglicherweise\b.{0,40}\bkönnte', r'ich hoffe, das hilft', r'\bgerne!'],
    'en': [r'it is important to note', r"in today[’']s (?:fast-paced )?world", r'in the digital landscape', r'\bdelve',
           r'\btapestry', r'\bleverag', r'\bseamless', r'\brobust\b', r'\bfoster', r'game-changer',
           r'plays a (?:crucial|vital|key) role', r'testament to', r'in conclusion', r'in order to',
           r'due to the fact that', r'not just\b.{0,60}\bbut', r'arguably', r'could potentially',
           r'\broadmap\b', r'i hope this helps', r'great question'],
}
PASSIV = {
    # Satz enthält eine Form von werden UND ein Partizip (ge-, ver-, be-, er-, zer-, ent-, -iert), Reihenfolge egal
    'de': re.compile(r'(?=.*\b(?:wird|werden|wurde|wurden|worden)\b)(?=.*\b(?:\w{0,6}ge\w{2,}(?:t|en)|(?:ver|be|er|zer|ent)\w+t|\w+iert)\b)', re.I | re.S),
    'en': re.compile(r'\b(?:am|is|are|was|were|be|been|being)\s+(?:\w+ly\s+)?\w+(?:ed|en)\b(?:\s+by\b)?', re.I),
}
NOMINAL = {
    'de': re.compile(r'\b[A-ZÄÖÜ]\w{3,}(?:ung|heit|keit|ion|nahme|ität|ismus)(?:en)?\b'),
    'en': re.compile(r'\b\w{3,}(?:tion|ment|ance|ence|ity)s?\b', re.I),
}
TYPO = {
    'de': [(r'"', 'gerades Anführungszeichen'), (r"\w'\w", 'gerader Apostroph'), (r'\d(?:%|€)', 'Zahl ohne Leerzeichen vor % oder €'),
           (r'\d (?:%|€|km|kg|°C)', 'normales statt geschütztes Leerzeichen vor Einheit (weich)'),
           (r'—', 'langer Gedankenstrich'), (r'\w - \w', 'Bindestrich als Gedankenstrich'),
           (r'(?<![\d.,])\d{5,}(?![\d.,])', 'Zahl ab fünf Stellen ungegliedert'), (r'\bz\.B\.|\bd\.h\.|\bu\.a\.', 'Abkürzung ohne Leerzeichen')],
    'en': [(r'"', 'straight double quote'), (r"\w'\w", 'straight apostrophe'), (r'--', 'double hyphen as dash'),
           (r'\w - \w', 'hyphen used as dash')],
}


def saetze(text):
    t = text
    for i, a in enumerate(ABK):
        t = t.replace(a, a.replace('.', '\x00').replace(' ', '\x01'))
    # keine Trennung nach Ziffer+Punkt (Ordnungszahl: 3. November); Trennung auch nach . ! ? plus schließendem Anführungszeichen
    teile = re.split(r'(?:(?<![0-9]\.)(?<=[.!?])|(?<=[.!?][”’"“]))\s+(?=[A-ZÄÖÜ„“"0-9])', t.strip())
    return [s.replace('\x00', '.').replace('\x01', ' ') for s in teile if s.strip()]


def woerter(s):
    return re.findall(r"[\wÄÖÜäöüß’'-]+", s)


def messen(sprache, text):
    ss = saetze(text)
    laengen = [len(woerter(s)) for s in ss]
    flach = text.replace(NB, ' ')
    floskeln = [m.group(0) for p in FLOSKELN[sprache] for m in re.finditer(p, flach, re.I)]
    typo = [(name, m.group(0)) for p, name in TYPO[sprache] for m in re.finditer(p, text)]
    return {
        'saetze': len(ss),
        'woerter': sum(laengen),
        'mittel': round(statistics.mean(laengen), 1) if laengen else 0,
        'median': statistics.median(laengen) if laengen else 0,
        'laengster': max(laengen) if laengen else 0,
        'streuung': round(statistics.pstdev(laengen), 1) if len(laengen) > 1 else 0,
        'passiv': sum(1 for s in ss if PASSIV[sprache].search(s)),
        'nominal': len(NOMINAL[sprache].findall(flach)),
        'floskeln': floskeln,
        'typo': typo,
    }


def ausgeben(name, w):
    print(f'{name}: {w["saetze"]} Sätze, {w["woerter"]} Wörter · Ø {w["mittel"]} · Median {w["median"]} · '
          f'längster {w["laengster"]} · Streuung {w["streuung"]} · Passivsätze {w["passiv"]} · '
          f'Nominalisierungen {w["nominal"]} · Floskeln {len(w["floskeln"])} · Typografie {len(w["typo"])}')
    for f in w['floskeln']:
        print(f'   Floskel: {f!r}')
    for n, f in w['typo']:
        print(f'   Typografie: {n}: {f!r}')


ZAHL = re.compile(r'\d+(?:[ \u00a0.]\d{3})*(?:,\d+)?')


def zahlen(text):
    """Zahlen normalisiert (Tausendertrenner Leerzeichen/geschützt/Punkt entfernt), z. B. 42.394 und 42 394 -> 42394."""
    return [re.sub(r'[ \u00a0.]', '', z) for z in ZAHL.findall(text)]


ZAHLWORT = {'0': ('zero', 'null'), '1': ('one', 'ein', 'eins', 'eine', 'einen', 'einem', 'einer'), '2': ('two', 'zwei'),
            '3': ('three', 'drei'), '4': ('four', 'vier'), '5': ('five', 'fünf'), '6': ('six', 'sechs'),
            '7': ('seven', 'sieben'), '8': ('eight', 'acht'), '9': ('nine', 'neun')}


def zahlwort_da(z, text):
    """Einstellige Zahl gilt als erhalten, wenn ihr Wort im Text steht (Hausregel: eins bis neun ausgeschrieben)."""
    return any(re.search(r'\b' + w + r'\b', text, re.I) for w in ZAHLWORT.get(z, ()))


def fakten_fehlen(vorher, nachher, muss=()):
    """Was aus vorher fehlt: Zahlen (automatisch) und die Zeichenketten aus muss."""
    n_flach = nachher.replace(NB, ' ')
    nz = zahlen(nachher)
    fehlt = [z for z in dict.fromkeys(zahlen(vorher)) if z not in nz and not zahlwort_da(z, n_flach)]
    fehlt += [m for m in muss if m.replace(NB, ' ') not in n_flach]
    return fehlt


def aehnlichkeit(a, b):
    import difflib
    return round(difflib.SequenceMatcher(None, woerter(a.lower()), woerter(b.lower())).ratio(), 2)


MARKER = re.compile(r'^\s*(?:✎|Gezählt|🔎|⚠|📝)', re.M)
MARKDOWN = re.compile(r'\*\*|__|^#{1,6} |^\s*[-*] ', re.M)


def ausgabe_teilen(roh):
    """Skill-Ausgabe in (Text, Rest) teilen: Text endet vor der ersten Marker-Zeile."""
    m = MARKER.search(roh)
    return (roh[:m.start()].strip(), roh[m.start():]) if m else (roh.strip(), '')


def zaehlzeile(rest):
    m1 = re.search(r'Ø[^\d]*?([\d,.]+)\s*→\s*([\d,.]+)', rest)
    m2 = re.search(r'längster Satz[^\d]*?(\d+)\s*→\s*(\d+)', rest)
    f = lambda s: float(s.replace(',', '.'))
    return (f(m1.group(1)), f(m1.group(2))) if m1 else None, (int(m2.group(1)), int(m2.group(2))) if m2 else None


def eval_lauf(root, ordner):
    import yaml
    faelle = yaml.safe_load(open(os.path.join(HIER, 'fixtures', 'plain-prose', 'eval', 'faelle.yaml'),
                                 encoding='utf-8'))['faelle']
    fehler, warn = [], []
    abw = []
    for f in faelle:
        p = os.path.join(ordner, f['id'] + '.txt')
        if not os.path.isfile(p):
            fehler.append(f'{f["id"]}: Ausgabe fehlt'); continue
        roh = open(p, encoding='utf-8').read()
        text, rest = ausgabe_teilen(roh)
        sp, v = f['sprache'], f['text']
        F = lambda s: fehler.append(f'{f["id"]}: {s}')
        W = lambda s: warn.append(f'{f["id"]}: {s}')
        for x in fakten_fehlen(v, text, f.get('muss', [])):
            F(f'Fakt fehlt: {x!r}')
        for rx in f.get('verboten', []):
            m = re.search(rx, text, re.I)
            if m: F(f'verboten gefunden: {m.group(0)!r}')
        for rx in f.get('erwartet', []):
            if not re.search(rx, text, re.I): F(f'erwartet, fehlt: /{rx}/')
        ae = aehnlichkeit(v, text)
        if 'min_aehnlichkeit' in f and ae < f['min_aehnlichkeit']:
            F(f'Übereingriff: Ähnlichkeit {ae} < {f["min_aehnlichkeit"]}')
        lv, ln = len(woerter(v)), len(woerter(text))
        if 'max_laenge' in f and ln > f['max_laenge'] * lv:
            F(f'Längenziel verfehlt: {ln}/{lv} Wörter')
        if not f.get('markdown_ok') and MARKDOWN.search(text):
            F('Markdown im Text')
        # Floskeln: nur außerhalb der Pflicht-Zeichenketten (Zitate)
        ohne = text
        for m in f.get('muss', []):
            ohne = ohne.replace(m, '')
        rest_fl = messen(sp, ohne)['floskeln']
        if rest_fl: F(f'Floskeln übrig: {rest_fl}')
        typo = messen(sp, ohne)['typo']
        harte = [x for x in typo if 'Anführungszeichen' in x[0] or 'quote' in x[0]]
        if harte: F(f'Typografie: {harte}')
        weich = [x for x in typo if x not in harte]
        if weich: W(f'Typografie (weich): {weich}')
        if '✎' not in rest: W('keine Zeile „✎ Geändert“')
        zv, zn = messen(sp, v), messen(sp, text)
        oe, ol = zaehlzeile(rest)
        if oe:
            for ang, ist, wo in ((oe[0], zv['mittel'], 'vorher'), (oe[1], zn['mittel'], 'nachher')):
                if ist:
                    d = abs(ang - ist) / ist
                    abw.append(d)
                    if d > 0.2: W(f'Zählzeile Ø {wo}: angegeben {ang}, gemessen {ist}')
        else:
            W('keine auswertbare Zählzeile')
        print(f'{f["id"]:20} Ähnlichkeit {ae:4} · Wörter {lv}->{ln} · Ø {zv["mittel"]}->{zn["mittel"]}')
    if abw:
        print(f'Zählzeile: mittlere Abweichung {round(100 * sum(abw) / len(abw))} %, '
              f'über 20 %: {sum(d > 0.2 for d in abw)} von {len(abw)}')
    for w in warn:
        print(' ~', w)
    return fehler


def skills_pruefen(root):
    fehler = []
    kerne = {}
    for s in SKILLS:
        p = os.path.join(root, 'skills', s, 'SKILL.md')
        if not os.path.isfile(p):
            fehler.append(f'{s}: SKILL.md fehlt'); continue
        t = open(p, encoding='utf-8').read()
        m = re.match(r'---\nname: (.+)\ndescription: (.+)\n---\n', t)
        if not m:
            fehler.append(f'{s}: Frontmatter (name, description) fehlt oder ist mehrzeilig'); continue
        if m.group(1) != s:
            fehler.append(f'{s}: name {m.group(1)!r} passt nicht zum Ordner')
        if not re.fullmatch(r'[a-z][a-z0-9-]{0,63}', m.group(1)):
            fehler.append(f'{s}: name ungültig')
        if len(m.group(2)) > 1024:
            fehler.append(f'{s}: description über 1024 Zeichen')
        if '<' in m.group(2) or '>' in m.group(2):
            fehler.append(f'{s}: spitze Klammern in der description')
        andere = [x for x in SKILLS if x != s][0]
        if andere not in m.group(2):
            fehler.append(f'{s}: description verweist nicht auf {andere}')
        for n, z in enumerate(t.splitlines(), 1):
            if SPUR.search(z):
                fehler.append(f'{s}:{n}: Sprachspur')
            if sperrwort(z):
                fehler.append(f'{s}:{n}: Sperrwort gefunden')
        koerper = t[m.end():]
        ohne_code = re.sub(r'`[^`\n]*`', '', koerper)
        for n, z in enumerate(ohne_code.splitlines(), 1):
            if '"' in z:
                fehler.append(f'{s}: gerades Anführungszeichen außerhalb von Code: {z.strip()[:60]!r}')
        k = KERN.findall(t)
        if len(k) != 1:
            fehler.append(f'{s}: gemeinsamer Kern fehlt oder doppelt ({len(k)})')
        else:
            kerne[s] = k[0]
        print(f'  {s}: description {len(m.group(2))} Zeichen, SKILL.md {len(t)} Zeichen')
        if len(t) > MAX_SKILL:
            fehler.append(f'{s}: SKILL.md {len(t)} Zeichen, Ziel höchstens {MAX_SKILL} (Entscheid 01.11.: straffen)')
        if 'glätten' in m.group(2):
            fehler.append(f'{s}: „glätten“ als Auslöser widerspricht der Regel gegen Glätte')
        if '## Beispiele' not in t and '## Examples' not in t:
            fehler.append(f'{s}: Abschnitt „## Beispiele“ fehlt')
        rest = [x for x in glob.glob(os.path.join(root, 'skills', s, '**', '*'), recursive=True)
                if os.path.isfile(x) and os.path.basename(x) != 'SKILL.md']
        if rest:
            fehler.append(f'{s}: Zusatzdateien {rest} (Befund D9: nur SKILL.md ist verlässlich)')
    if len(kerne) == 2 and len(set(kerne.values())) != 1:
        fehler.append('gemeinsamer Kern weicht zwischen plain-prose-de und plain-prose-en ab')
    return fehler


def selbsttest(root):
    fehler = []
    fx = os.path.join(HIER, 'fixtures', 'plain-prose')
    for sp in ('de', 'en'):
        v = messen(sp, open(os.path.join(fx, f'vorher_{sp}.txt'), encoding='utf-8').read())
        n = messen(sp, open(os.path.join(fx, f'nachher_{sp}.txt'), encoding='utf-8').read())
        ausgeben(f'vorher_{sp}', v)
        ausgeben(f'nachher_{sp}', n)
        if not n['mittel'] < v['mittel']: fehler.append(f'{sp}: Ø Satzlänge nicht gesunken')
        if n['mittel'] < 8: fehler.append(f'{sp}: Nachher zu abgehackt (Ø unter 8 Wörtern)')
        if not n['passiv'] < v['passiv']: fehler.append(f'{sp}: Passiv nicht gesunken')
        if not n['nominal'] < v['nominal']: fehler.append(f'{sp}: Nominalisierungen nicht gesunken')
        if n['floskeln']: fehler.append(f'{sp}: Floskeln im Nachher')
        fx_v = open(os.path.join(fx, f'vorher_{sp}.txt'), encoding='utf-8').read()
        fx_n = open(os.path.join(fx, f'nachher_{sp}.txt'), encoding='utf-8').read()
        for x in fakten_fehlen(fx_v, fx_n):
            fehler.append(f'{sp}: Fakt fehlt im Nachher: {x!r}')
        if n['typo']: fehler.append(f'{sp}: Typografie-Funde im Nachher')
        if not v['floskeln'] or not v['passiv']: fehler.append(f'{sp}: Vorher-Beispiel prüft nichts (keine Funde)')
        if sp == 'de' and not v['typo']: fehler.append('de: Vorher-Beispiel ohne Typografie-Funde')
    return fehler


def bauen(root):
    out = os.path.join(root, 'dist')
    os.makedirs(out, exist_ok=True)
    for s in SKILLS:
        pfad = os.path.join(out, s + '.zip')
        with zipfile.ZipFile(pfad, 'w', zipfile.ZIP_DEFLATED) as z:
            zi = zipfile.ZipInfo(f'{s}/SKILL.md', date_time=(2026, 11, 1, 0, 0, 0))
            zi.compress_type = zipfile.ZIP_DEFLATED
            zi.external_attr = 0o644 << 16
            z.writestr(zi, open(os.path.join(root, 'skills', s, 'SKILL.md'), 'rb').read())
        print('  gebaut', os.path.relpath(pfad, root))


def eingaben(root, ziel):
    """Schreibt je Fall die Nutzernachricht (Auftrag, Leerzeile, Text) nach <ziel>/<id>.txt, zum Einfügen in claude.ai."""
    import yaml
    faelle = yaml.safe_load(open(os.path.join(root, 'tools', 'fixtures', 'plain-prose', 'eval', 'faelle.yaml'),
                                 encoding='utf-8'))['faelle']
    os.makedirs(ziel, exist_ok=True)
    for f in faelle:
        open(os.path.join(ziel, f['id'] + '.txt'), 'w', encoding='utf-8').write(f"{f['auftrag']}\n\n{f['text']}\n")
    print(len(faelle), 'Nachrichten nach', ziel)
    return []


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    cmd = sys.argv[1]
    if cmd == 'text':
        sp = sys.argv[2]
        if sp not in ('de', 'en'):
            sys.exit('Sprache de oder en')
        for p in sys.argv[3:]:
            ausgeben(os.path.basename(p), messen(sp, open(p, encoding='utf-8').read()))
        return
    root = sys.argv[2]
    if cmd == 'skills':
        fehler = skills_pruefen(root)
    elif cmd == 'eval':
        fehler = eval_lauf(root, sys.argv[3])
    elif cmd == 'eingaben':
        fehler = eingaben(root, sys.argv[3])
    elif cmd == 'selbsttest':
        fehler = selbsttest(root)
    elif cmd == 'bauen':
        fehler = skills_pruefen(root) + selbsttest(root)
        if not fehler:
            bauen(root)
    else:
        sys.exit(__doc__)
    if fehler:
        print(f'FEHLER: {len(fehler)}')
        for f in fehler:
            print(' -', f)
        sys.exit(1)
    print('sauber')


if __name__ == '__main__':
    main()

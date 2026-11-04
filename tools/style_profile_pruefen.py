#!/usr/bin/env python3
"""Prüfwerkzeug für den Skill style-profile (Entwurf 03.11.2026). Nur Standardbibliothek und PyYAML.
Aufruf (aus der Repo-Wurzel, mit python3 -I):
  skills     <wurzel>              SKILL.md de (skills/) und en-Paket (en/skills/): Frontmatter, Länge, Sperrwörter, Zusatzdateien,
                                   Pflichtzeilen des Profilformats, Abstimmung mit plain-prose (gleiche Zeilenbezeichner)
  messen     <wurzel>              Satzlängen-Kennwerte der Textproben je Fall (zum Schreiben der Erwartung)
  eingaben   <wurzel> <ordner>     schreibt je Fall die Nutzernachricht nach <ordner>/<id>.txt (für einen Lauf in claude.ai)
  eval       <wurzel> <ordner>     prüft Ausgaben <ordner>/<id>.txt gegen tools/fixtures/style-profile/eval/faelle.yaml
  selbsttest <wurzel>              die guten Beispiele unter eval/gut/ müssen bestehen, jede Mutation muss erkannt werden
Geprüft werden Muster und Zahlen, keine Bedeutung. Exit 1 bei Fehlern."""
import sys, os, re, glob, statistics, tempfile, shutil
import yaml
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import plain_prose_pruefen as gemeinsam   # gemeinsame Sperrwort-Prüfung (Prüfsummen, keine Klartext-Namen)

NAME = 'style-profile'
# Strukturen: Arbeitsrepo (skills/, en/skills/) und Export (de/skills/, en/skills/)
SKILLS = {'de': ['skills/style-profile/SKILL.md', 'de/skills/style-profile/SKILL.md'], 'en': ['en/skills/style-profile/SKILL.md']}


def finde(root, kandidaten):
    return next((r for r in kandidaten if os.path.isfile(os.path.join(root, r))), kandidaten[0])
MAX_SKILL = 8000
SPUR = re.compile(r'[\u0400-\u06FF\u0E00-\u0E7F\u3040-\u9FFF]')
PFLICHTZEILEN = {'de': ['Geltung:', 'Anrede:', 'Satzlänge:', 'Ton:', 'Genderform:', 'Zeichensetzung:', 'Englisch:', 'Häufige Wörter:', 'Nie benutzt:'],
                 'en': ['Scope:', 'Address:', 'Sentence length:', 'Tone:', 'Gender form:', 'Punctuation:', 'English:', 'Frequent words:', 'Never used:']}
BEISPIELE = {'de': '## Beispiele', 'en': '## Examples'}
ABK = ['z. B.', 'd. h.', 'u. a.', 'Abs.', 'Art.', 'ca.', 'Nr.', 'usw.', 'bzw.', 'Dr.', 'Mr.', 'e.g.', 'i.e.']
SCHLUSS = re.compile(r'^(?:Mit freundlichen Grüßen|Viele Grüße|Freundliche Grüße|Liebe Grüße|Kind regards|Bis \w+!?)\b.*$', re.I | re.M)
INFERENZ = re.compile(r'\b(?:Alter|Geschlecht|männlich|weiblich|Persönlichkeit|Charakter|Herkunft|Muttersprach\w*|introvertiert|'
                      r'extravertiert|krank\w*|Operation|Fieber|Gesundheit)\b', re.I)
FREMD_HINWEIS = re.compile(r'weitergeleitet|fremd|nicht von dir|nicht von mir|nicht deine|nicht meine', re.I)


def woerter(s):
    return re.findall(r"[\wÄÖÜäöüß’'-]+", s)


def saetze(text):
    t = text
    for a in ABK:
        t = t.replace(a, a.replace('.', '\x00').replace(' ', '\x01'))
    teile = re.split(r'(?:(?<![0-9]\.)(?<=[.!?])|(?<=[.!?][”’"“]))\s+(?=[A-ZÄÖÜ„“"0-9\'])', t.strip())
    return [s.replace('\x00', '.').replace('\x01', ' ') for s in teile if s.strip()]


def statistik(texte):
    ss = [s for t in texte for s in saetze(t)]
    laengen = sorted(len(woerter(s)) for s in ss)
    n = len(laengen)
    return {'saetze': n, 'woerter': sum(laengen), 'median': statistics.median(laengen), 'p90': laengen[int(0.9 * (n - 1))],
            'max': laengen[-1]}


def fixtures(root):
    return os.path.join(root, 'tools', 'fixtures', 'style-profile', 'eval')


def lade_faelle(root):
    return yaml.safe_load(open(os.path.join(fixtures(root), 'faelle.yaml'), encoding='utf-8'))['faelle']


def texte(root, fall):
    d = os.path.join(fixtures(root), 'eingang', fall['id'])
    lies = lambda n: open(os.path.join(d, n + '.txt'), encoding='utf-8').read().strip()
    return [lies(n) for n in fall['eigene']], [lies(n) for n in fall.get('fremd', [])]


def skills_pruefen(root):
    fehler = []
    for sp, rels in SKILLS.items():
        rel = finde(root, rels)
        p = os.path.join(root, rel)
        if not os.path.isfile(p):
            fehler.append(f'{rel} fehlt'); continue
        t = open(p, encoding='utf-8').read()
        m = re.match(r'---\nname: (.+)\ndescription: (.+)\n---\n', t)
        if not m:
            fehler.append(f'{rel}: Frontmatter fehlt oder ist mehrzeilig'); continue
        if m.group(1) != NAME:
            fehler.append(f'{rel}: name {m.group(1)!r}')
        if len(m.group(2)) > 1024:
            fehler.append(f'{rel}: description über 1024 Zeichen')
        if '<' in m.group(2) or '>' in m.group(2):
            fehler.append(f'{rel}: spitze Klammern in der description')
        if len(t) > MAX_SKILL:
            fehler.append(f'{rel}: {len(t)} Zeichen, Grenze {MAX_SKILL}')
        for n, z in enumerate(t.splitlines(), 1):
            if SPUR.search(z): fehler.append(f'{rel}:{n}: Sprachspur')
            if gemeinsam.sperrwort(z): fehler.append(f'{rel}:{n}: Sperrwort (Prüfsumme)')
        for z in PFLICHTZEILEN[sp]:
            if z not in t:
                fehler.append(f'{rel}: Pflichtzeile {z!r} fehlt')
        for r in ('plain-prose-de', 'plain-prose-en'):
            if r not in t:
                fehler.append(f'{rel}: Verweis auf {r} fehlt')
        if BEISPIELE[sp] not in t:
            fehler.append(f'{rel}: Abschnitt „{BEISPIELE[sp]}“ fehlt')
        if sp == 'de':
            ohne = re.sub(r'`[^`\n]*`', '', re.sub(r'```.*?```', '', t[m.end():], flags=re.S))
            if '"' in ohne:
                fehler.append(f'{rel}: gerades Anführungszeichen außerhalb von Code')
        andere = [f for f in glob.glob(os.path.join(os.path.dirname(p), '**', '*'), recursive=True)
                  if os.path.isfile(f) and os.path.basename(f) != 'SKILL.md']
        if andere:
            fehler.append(f'{rel}: Zusatzdateien {andere} (Befund D9)')
        print(f'  {sp}: SKILL.md {len(t)} Zeichen, description {len(m.group(2))}')
    # Abstimmung mit plain-prose: Der deutsche Überarbeiten-Skill muss die Bezeichner kennen
    for pfade, label in ((['skills/plain-prose-en/SKILL.md', 'de/skills/plain-prose-en/SKILL.md'], 'Englisch:'),
                         (['en/skills/plain-prose-en/SKILL.md'], 'English:')):
        pfad = finde(root, pfade)
        pp = os.path.join(root, pfad)
        if os.path.isfile(pp) and label not in open(pp, encoding='utf-8').read():
            fehler.append(f'{pfad} nennt den Bezeichner {label!r} nicht (Abstimmung mit style-profile)')
    ppd = os.path.join(root, finde(root, ['skills/plain-prose-de/SKILL.md', 'de/skills/plain-prose-de/SKILL.md']))
    if os.path.isfile(ppd):
        t = open(ppd, encoding='utf-8').read()
        if 'Genderform' not in t:
            fehler.append('plain-prose-de nennt „Genderform“ nicht (Abstimmung mit style-profile)')
    return fehler


def messen(root):
    for f in lade_faelle(root):
        eig, fr = texte(root, f)
        s = statistik(eig)
        print(f'{f["id"]:16} eigene Texte {len(eig)}, Wörter {s["woerter"]}, Sätze {s["saetze"]}, Median {s["median"]}, '
              f'p90 {s["p90"]}, max {s["max"]}' + (f' · fremd {len(fr)}' if fr else ''))
        from collections import Counter
        c = Counter(w.lower() for t in eig for w in woerter(t) if len(w) >= 5)
        print('   mindestens dreimal:', ', '.join(f'{w} {n}' for w, n in c.most_common(10) if n >= 3))


def eingaben(root, ziel):
    os.makedirs(ziel, exist_ok=True)
    for f in lade_faelle(root):
        eig, fr = texte(root, f)
        alle = eig + fr
        teile = [f'Leite aus diesen Texten mein Stilprofil ab. Die Texte stammen von mir und stehen für: {f["geltung"]}.']
        teile += [f'Text {i}:\n{t}' for i, t in enumerate(alle, 1)]
        open(os.path.join(ziel, f['id'] + '.txt'), 'w', encoding='utf-8').write('\n\n'.join(teile) + '\n')
        print('geschrieben', f['id'])


def ngramme(text, n=5):
    w = [x.lower() for x in woerter(text)]
    return {' '.join(w[i:i + n]) for i in range(len(w) - n + 1)}


def pruefe_ausgabe(root, f, roh):
    """Liefert die Liste der Fehler für eine Ausgabe."""
    F = []
    eig, fr = texte(root, f)
    zeilen = {m.group(1): m.group(2) for m in (re.match(r'^\s*[-*]?\s*(Geltung|Anrede|Satzlänge|Ton|Genderform|Zeichensetzung|'
                                                       r'Englisch|Häufige Wörter|Nie benutzt):\s*(.*)$', z) for z in roh.splitlines()) if m}
    if f.get('zu_kurz'):
        if not re.search(r'zu wenig|mindestens', roh, re.I): F.append('zu wenig Material nicht benannt')
        if 'Satzlänge:' in roh: F.append('Satzlänge abgeleitet trotz zu wenig Material')
        if zeilen: F.append('Profilzeilen trotz zu wenig Material')
        if re.search(r'Soll ich das so ins Stilprofil', roh): F.append('Frage nach Ablage trotz zu wenig Material')
    else:
        if len(zeilen) < 6: F.append(f'nur {len(zeilen)} Profilzeilen, mindestens 6 erwartet')
        if not re.search(r'Soll ich .*Stilprofil', roh): F.append('Frage nach Zustimmung fehlt')
        sl = re.search(r'Satzlänge:\s*meist (\d+) bis (\d+) Wörter, selten über (\d+)', roh)
        if not sl:
            F.append('Zeile „Satzlänge: meist X bis Y Wörter, selten über Z“ fehlt')
        else:
            x, y, z = (int(sl.group(i)) for i in (1, 2, 3))
            st = statistik(eig)
            if not (x - 2 <= st['median'] <= y + 2): F.append(f'Satzlänge meist {x} bis {y} passt nicht zum Median {st["median"]}')
            if not (st['p90'] - 2 <= z <= st['max'] + 5): F.append(f'„selten über {z}“ passt nicht (p90 {st["p90"]}, max {st["max"]})')
            nn = re.search(r'aus (\d+) Texten', roh)
            if not nn: F.append('Zahl der Texte („aus N Texten“) fehlt')
            elif int(nn.group(1)) != len(eig): F.append(f'aus {nn.group(1)} Texten, es sind {len(eig)} eigene')
        for label, rx in (f.get('erwartet') or {}).items():
            if label not in zeilen:
                F.append(f'Zeile {label}: fehlt')
            elif not re.search(rx, zeilen[label], re.I):
                F.append(f'{label}: {zeilen[label]!r} passt nicht zu /{rx}/')
    if re.search(r'Abgelegt:|Filed:', roh): F.append('Ablage gemeldet, obwohl noch keine Zustimmung vorlag')
    for n in f.get('namen', []):
        if re.search(re.escape(n), roh, re.I): F.append(f'Name oder Angabe aus den Proben im Ergebnis: {n!r}')
    if INFERENZ.search(roh) and not f.get('inferenz_ok'): F.append(f'Rückschluss auf die Person: {INFERENZ.search(roh).group(0)!r}')
    gram = set()
    for t in eig + fr:
        gram |= ngramme(t)
    kopie = sorted(ngramme(roh) & gram)
    if kopie: F.append(f'Wortfolge aus den Proben übernommen: {kopie[0]!r}')
    if fr and not FREMD_HINWEIS.search(roh): F.append('fremder Text nicht als solcher benannt')
    return F


def eval_lauf(root, ordner):
    fehler = []
    for f in lade_faelle(root):
        p = os.path.join(ordner, f['id'] + '.txt')
        if not os.path.isfile(p):
            fehler.append(f'{f["id"]}: Ausgabe fehlt'); continue
        for e in pruefe_ausgabe(root, f, open(p, encoding='utf-8').read()):
            fehler.append(f'{f["id"]}: {e}')
        print('geprüft', f['id'])
    return fehler


def mutationen(f, roh):
    """(Name, mutierter Text) je Mutation, die für diesen Fall erkannt werden muss."""
    m = []
    m.append(('Ablage ohne Zustimmung', roh + '\n📝 Abgelegt: Stilprofil\n'))
    m.append(('Rückschluss auf die Person', roh + '\nAlter: wohl über 50\n'))
    if f.get('zu_kurz'):
        m.append(('Satzlänge trotz zu wenig Material', roh + '\nSatzlänge: meist 8 bis 12 Wörter, selten über 20 (aus 1 Texten)\n'))
        return m
    m.append(('Satzlänge falsch', re.sub(r'meist \d+ bis \d+ Wörter, selten über \d+', 'meist 2 bis 3 Wörter, selten über 4', roh)))
    m.append(('Textzahl falsch', re.sub(r'aus \d+ Texten', 'aus 9 Texten', roh)))
    m.append(('Frage nach Zustimmung fehlt', '\n'.join(z for z in roh.splitlines() if 'Soll ich' not in z)))
    for n in f.get('namen', [])[:1]:
        m.append(('Name im Ergebnis', roh + f'\nHäufige Wörter: {n}, danke\n'))
    for label in list((f.get('erwartet') or {}))[:1]:
        m.append((f'{label} fehlt', '\n'.join(z for z in roh.splitlines() if not z.lstrip('-* ').startswith(label + ':'))))
    return m


def selbsttest(root):
    fehler = []
    gut = os.path.join(fixtures(root), 'gut')
    for f in lade_faelle(root):
        roh = open(os.path.join(gut, f['id'] + '.txt'), encoding='utf-8').read()
        e = pruefe_ausgabe(root, f, roh)
        if e:
            fehler.append(f'{f["id"]}: gutes Beispiel fällt durch: {e}')
            continue
        eig, fr = texte(root, f)
        muts = mutationen(f, roh)
        # Kopie einer Wortfolge aus den Proben
        woerter_proben = woerter(' '.join(eig))
        muts.append(('Wortfolge kopiert', roh + '\n' + ' '.join(woerter_proben[10:17]) + '\n'))
        if fr:
            muts.append(('fremder Text nicht benannt', re.sub(FREMD_HINWEIS, 'Text', roh)))
        for name, mut in muts:
            if not pruefe_ausgabe(root, f, mut):
                fehler.append(f'{f["id"]}: Mutation „{name}“ wurde nicht erkannt')
        print(f'  {f["id"]}: gut besteht, {len(muts)} Mutationen erkannt')
    return fehler


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    cmd, root = sys.argv[1], sys.argv[2]
    if cmd == 'messen':
        messen(root); return
    if cmd == 'eingaben':
        eingaben(root, sys.argv[3]); return
    fehler = {'skills': lambda: skills_pruefen(root), 'eval': lambda: eval_lauf(root, sys.argv[3]),
              'selbsttest': lambda: selbsttest(root)}.get(cmd, lambda: sys.exit(__doc__))()
    if fehler:
        print(f'FEHLER: {len(fehler)}')
        for x in fehler:
            print(' -', x)
        sys.exit(1)
    print('sauber')


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Prüft den Skill transcript-minutes und seine Protokolle. Standardbibliothek plus PyYAML. Entwurf 01.11.2026.

Aufruf (aus der Repo-Wurzel, mit python3 -I):
  skill      <wurzel>                       (Wurzel en: englisches Paket) Frontmatter, Länge, Abschnitte, Sperrwörter, Anführungszeichen, nur eine Datei,
                                            Vorlage und Prüfzeile im Skill erfüllen die Form
  protokoll  <wurzel> <fall> <datei>        ein Protokoll (aus einem Testlauf eingefügt) gegen Eingang und Erwartung des Falls
  eval       <wurzel> <ordner>              <ordner>/<fall>.md für alle Fälle in tools/fixtures/transcript-minutes/eval/faelle.yaml
  selbsttest <wurzel>                       gute Beispiele müssen sauber sein, jede Mutation muss erkannt werden
  erzeugen   <wurzel>                       schreibt den langen Fall (eingang/lang.txt und gut/lang.md), deterministisch
  bauen      <wurzel>                       skill, selbsttest, dann dist/transcript-minutes.zip (ein Skill, eine Datei)

Geprüft werden Muster und Zahlen, keine Bedeutung: Kennungen am Satzende und im Eingang vorhanden, Abdeckung jeder
Eingangskennung, Tabelle mit vier Feldern je Zeile, keine doppelte oder zerteilte Aufgabe, Zahlen und Fristen aus dem
Eingang, „offen“ statt Erfundenem, Prüfzeile gegen Zählung. Exit 1 bei Fehlern."""
import sys, os, re, glob, zipfile, hashlib, difflib
import yaml
HIER = os.path.dirname(os.path.abspath(__file__))

MAX_SKILL = 8000
NB = ' '
SKILL = 'transcript-minutes'
SPUR = re.compile(r'[\u0400-\u06FF\u0E00-\u0E7F\u3040-\u9FFF]')
# Namen und Marken aus dem Auftragstext stehen nie im Repo: nur als Hash (Wort, Wortpaar), Entscheid 01.11. (Übergabe, Befund 2)
SPERR_HASH = {'4dd68e2ab3a30973', '34550715062af006', 'ceebe4612a1cd805', '760dcecfbe1ce8c3', '40d0f98f40ad3f5c',
              'a4b5394a666cfd3c', 'b11830879d740bf3'}
ZEIT = r'\d{1,2}:\d{2}(?::\d{2})?'
K1 = rf'(?:A\d+|{ZEIT})'
KENN = re.compile(rf'\[\s*({K1}(?:\s*,\s*{K1})*)\s*\]')
KTOK = re.compile(K1)
ERLAUBT = ['Beschlüsse', 'Inhalt', 'Offene Punkte', 'Aufgaben', 'Nicht aufgenommen']
KOPF_TAB = ['aufgabe', 'zuständig', 'frist', 'kategorie']
PRUEF = re.compile(r'^🔎 Protokoll: Durchgänge (\d) · ergänzt (\d+) · Abdeckung (\d+)/(\d+) · Aufgaben (\d+)'
                   r'(?: \(Zuständig offen (\d+), Frist offen (\d+)\))?(?: · Ablage: .+)?$')
PRUEF_EN = re.compile(r'^🔎 Minutes: passes (\d) · added (\d+) · coverage (\d+)/(\d+) · tasks (\d+)'
                      r'(?: \(owner open (\d+), deadline open (\d+)\))?(?: · Filing: .+)?$')
# Sprachabhängige Teile der Skill-Prüfung; Protokoll, Eval und Selbsttest bleiben deutsch (Fixtures nur de)
SK = {
    'de': dict(
        desc=('Besprechung', 'Interview', 'Telefonat', 'Workshop', 'Vortrag', 'Chat', 'Protokoll'),
        abschnitte=('## Vorbereitung', '## Kennungen', '## Durchgänge', '## Einordnung', '## Das Protokoll', '## Ausgabe',
                    '## Ablage', '## Grenzen', '## Beispiel', '## Selbstprüfung'),
        woerter=('Zeitmarke', 'Absatz', 'offen', 'Nicht aufgenommen', 'Durchgang', 'Rollen', 'Entscheidungen', 'Wochenplan',
                 'Gesprächsart', 'Grenze', 'Zeichen für Zeichen', 'erfinde nichts', 'Anweisungen'),
        vorlage=('# <Titel nach Gesprächsart>', 'Hinweis: Von einer KI', '## Beschlüsse', '## Inhalt', '### <Überschrift',
                 '## Offene Punkte', '## Aufgaben', '| Aufgabe | Zuständig | Frist | Kategorie |', '|---|---|---|---|',
                 '## Nicht aufgenommen', '🔎 Protokoll:'),
        gerade=True),
    'en': dict(
        desc=('meeting', 'interview', 'phone call', 'workshop', 'talk', 'chat', 'minutes'),
        abschnitte=('## Preparation', '## References', '## Passes', '## Classification', '## The minutes', '## Output',
                    '## Filing', '## Limits', '## Example', '## Self-check'),
        woerter=('timestamp', 'paragraph', 'open', 'Not included', 'pass', 'roles', 'Decisions', 'Weekly-Plan',
                 'kind of conversation', 'limit', 'character for character', 'invent nothing', 'instructions'),
        vorlage=('# <title by kind of conversation>', 'Note: Created by an AI', '## Decisions', '## Content', '### <heading',
                 '## Open points', '## Tasks', '| Task | Owner | Deadline | Category |', '|---|---|---|---|',
                 '## Not included', '🔎 Minutes:'),
        gerade=False),
}
ZAHL = re.compile(r'\d+(?:[  .]\d{3})*(?:,\d+)?')
WORT = {1: 'ein', 2: 'zwei', 3: 'drei', 4: 'vier', 5: 'fünf', 6: 'sechs', 7: 'sieben', 8: 'acht', 9: 'neun',
        10: 'zehn', 11: 'elf', 12: 'zwölf'}
ABK = ['z. B.', 'd. h.', 'u. a.', 'Abs.', 'Art.', 'bzw.', 'ca.', 'Nr.', 'usw.', 'etc.', 'Dr.', 'vs.']
SPLIT = re.compile(r'(?:(?<![0-9]\.)(?<=[.!?])|(?<=[.!?][”’"“]))\s+(?=[A-ZÄÖÜ„“"0-9\x02])')


def norm(s):
    return re.sub(r'\s+', ' ', s.replace(NB, ' ').lower()).strip(' .,;')


def zahlen(t):
    return [re.sub(r'[  .]', '', z) for z in ZAHL.findall(t)]


def sperrwort(text):
    toks = re.findall(r'[\wäöüß]+', text.lower())
    for i, t in enumerate(toks):
        if hashlib.sha256(t.encode()).hexdigest()[:16] in SPERR_HASH:
            return t[:1] + '…'
        if i + 1 < len(toks) and hashlib.sha256((t + ' ' + toks[i + 1]).encode()).hexdigest()[:16] in SPERR_HASH:
            return t[:1] + '…'
    return None


# ---------------------------------------------------------------- Eingang
def kennungen_eingang(text):
    """(modus, Liste): Zeitmarken am Zeilenanfang, sonst Absätze (Leerzeilen, ohne Leerzeilen jede Zeile)."""
    zeit = []
    for z in text.splitlines():
        m = re.match(r'\s*\[?(' + ZEIT + r')\]?(?=\s)', z)
        if m:
            zeit.append(m.group(1))
    if len(zeit) >= 2:
        return 'zeit', list(dict.fromkeys(zeit))
    if re.search(r'\n\s*\n', text.strip()):
        bloecke = [b for b in re.split(r'\n\s*\n', text.strip()) if b.strip()]
    else:
        bloecke = [z for z in text.splitlines() if z.strip()]
    return 'absatz', [f'A{i}' for i in range(1, len(bloecke) + 1)]


# ---------------------------------------------------------------- Protokoll zerlegen
def zerlegen(text):
    d = {'titel': '', 'kopf': [], 'abschnitte': {}, 'reihenfolge': [], 'themen': [], 'pruef': None}
    aktuell = None
    for z in text.splitlines():
        s = z.rstrip()
        if s.startswith('🔎'):
            d['pruef'] = s
            continue
        if s.startswith('# ') and not d['titel']:
            d['titel'] = s[2:].strip()
            continue
        m = re.match(r'^## (.+)$', s)
        if m:
            aktuell = m.group(1).strip()
            d['abschnitte'].setdefault(aktuell, [])
            d['reihenfolge'].append(aktuell)
            continue
        if aktuell is None:
            if s.strip():
                d['kopf'].append(s.strip())
            continue
        m3 = re.match(r'^### (.+)$', s)
        if m3 and aktuell == 'Inhalt':
            d['themen'].append(m3.group(1).strip())
        d['abschnitte'][aktuell].append(s)
    return d


def satz_einheiten(t):
    """Sätze eines Absatzes als (Text ohne Kennung, [Kennungen]). Die Kennung darf vor oder nach dem Satzpunkt stehen."""
    marker = {}

    def ers(m):
        i = len(marker)
        marker[i] = KTOK.findall(m.group(1))
        return f' \x02{i}\x03'
    t = KENN.sub(ers, t)
    t = re.sub(r'([.!?])\s+(\x02\d+\x03)', r' \2\1', t)
    for a in ABK:
        t = t.replace(a, a.replace('.', '\x00').replace(' ', '\x01'))
    res = []
    for s in SPLIT.split(t.strip()):
        s = s.replace('\x00', '.').replace('\x01', ' ')
        ks = []
        for m in re.finditer(r'\x02(\d+)\x03', s):
            ks += marker[int(m.group(1))]
        klar = re.sub(r'\s*\x02\d+\x03', '', s).strip()
        if klar:
            res.append((klar, ks))
    return res


def einheiten(zeilen):
    out, par = [], []

    def flush():
        if par:
            out.extend(satz_einheiten(' '.join(par)))
            par.clear()
    for z in zeilen:
        s = z.strip()
        if not s or s.startswith('###') or s.startswith('|'):
            flush()
            continue
        if re.match(r'^[-*] ', s):
            flush()
            out.extend(satz_einheiten(s[2:]))
            continue
        par.append(s)
    flush()
    return out


def tabelle(zeilen):
    """(Kopf, Zeilen, Fehler). Jede Zeile: Liste der Zellen."""
    f = []
    rows = [z.strip() for z in zeilen if z.strip().startswith('|')]
    if len(rows) < 2:
        return [], [], ['Aufgaben: keine Tabelle (Kopfzeile und Trennzeile fehlen)']
    zellen = lambda z: [c.strip() for c in z.strip().strip('|').split('|')]
    kopf = zellen(rows[0])
    if [c.lower() for c in kopf] != KOPF_TAB:
        f.append(f'Tabellenkopf {kopf} statt Aufgabe | Zuständig | Frist | Kategorie')
    if not re.match(r'^\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)*\|?$', rows[1]):
        f.append('Tabelle: Trennzeile unter dem Kopf fehlt')
    daten = []
    for r in rows[2:]:
        c = zellen(r)
        if len(c) != 4:
            f.append(f'Tabelle: {len(c)} statt vier Felder in Zeile {r[:50]!r}')
            continue
        if any(not x for x in c):
            f.append(f'Tabelle: leeres Feld (zerteilte Aufgabe?) in Zeile {r[:50]!r}; fehlende Angabe heißt „offen“')
            continue
        if re.search(r'<br\s*/?>', r, re.I):
            f.append(f'Tabelle: Zeilenumbruch in Zeile {r[:50]!r}')
        daten.append(c)
    return kopf, daten, f


def tokens_na(zeilen):
    t = ' '.join(zeilen)
    out = set()
    for m in re.finditer(r'\bA(\d+)\s*[–-]\s*A?(\d+)\b', t):
        a, b = int(m.group(1)), int(m.group(2))
        if a <= b <= 100000:
            out.update(f'A{i}' for i in range(a, b + 1))
    t2 = re.sub(r'\bA\d+\s*[–-]\s*A?\d+\b', ' ', t)
    out.update(re.findall(r'\bA\d+\b', t2))
    out.update(re.findall(r'\b' + ZEIT + r'\b', t2))
    return out


def zahlen_fehlen(eingang, text):
    e = re.sub(r'(?m)^\s*\[?' + ZEIT + r'\]?', ' ', eingang)
    ez = set(zahlen(e))
    low = e.lower()
    fehlt = []
    for z in dict.fromkeys(zahlen(text)):
        if z in ez:
            continue
        if z.isdigit() and 1 <= int(z) <= 12 and re.search(r'\b' + WORT[int(z)] + r'(?:e|er|en|es|em)?\b', low):
            continue
        fehlt.append(z)
    return fehlt


def passt(wert, erwartet):
    """erwartet: Text oder Liste; 'offen' verlangt genau offen, sonst Teilstring (ohne Groß-/Kleinschreibung)."""
    for e in ([erwartet] if isinstance(erwartet, str) else erwartet):
        if e == 'offen':
            if norm(wert) == 'offen':
                return True
        elif norm(e) in norm(wert):
            return True
    return False


# ---------------------------------------------------------------- Prüfung eines Protokolls
def pruefe(eingang, prot, fall=None):
    """-> (Fehler, Warnungen). fall None: nur Form."""
    f, w = [], []
    fall = fall or {}
    modus, ek = kennungen_eingang(eingang)
    eset = set(ek)
    d = zerlegen(prot)
    ab = d['abschnitte']
    if not d['titel']:
        f.append('Titelzeile (# …) fehlt')
    elif fall.get('titel') and not re.search(fall['titel'], d['titel']):
        f.append(f'Titel {d["titel"]!r} passt nicht zur Gesprächsart (erwartet /{fall["titel"]}/)')
    if not any(z.startswith('Hinweis:') and 'KI' in z for z in d['kopf']):
        f.append('Hinweis-Zeile („Hinweis: Von einer KI …“) fehlt')
    kopf_zeile = next((z for z in d['kopf'] if z.startswith('Datum:')), None)
    if not kopf_zeile:
        f.append('Kopfzeile „Datum: … · Beteiligte: … · Kennungen: …“ fehlt')
    elif fall.get('kennung') and ('Zeitmarken' if fall['kennung'] == 'zeit' else 'Absatznummern') not in kopf_zeile:
        f.append('Kopfzeile nennt die Zählweise nicht (Zeitmarken oder Absatznummern)')
    for n in ab:
        if n not in ERLAUBT:
            f.append(f'Unbekannter Abschnitt {n!r}')
    reihe = [n for n in d['reihenfolge'] if n in ERLAUBT]
    if reihe != sorted(reihe, key=ERLAUBT.index):
        f.append(f'Reihenfolge der Abschnitte falsch: {reihe}')
    if 'Inhalt' not in ab:
        f.append('Abschnitt Inhalt fehlt')
    nth = len(d['themen'])
    if nth < 1 or nth > 5:
        f.append(f'{nth} Themenblöcke, erlaubt sind 1 bis 5')
    if nth < fall.get('themen_min', 1):
        f.append(f'{nth} Themenblöcke, mindestens {fall["themen_min"]} erwartet')

    # Aussagen: Kennung je Satz, Kennungen im Eingang
    gesamt, aussagen = set(), []
    for name in ('Beschlüsse', 'Inhalt', 'Offene Punkte'):
        for satz, ks in einheiten(ab.get(name, [])):
            aussagen.append((name, satz, ks))
            if not ks:
                f.append(f'{name}: Satz ohne Kennung: {satz[:60]!r}')
            gesamt.update(ks)
    kopf, rows, tf = tabelle(ab['Aufgaben']) if 'Aufgaben' in ab else ([], [], [])
    f += tf
    for r in rows:
        ks = KTOK.findall(' '.join(KENN.findall(r[0])))
        if not ks:
            f.append(f'Aufgabe ohne Kennung: {r[0][:50]!r}')
        gesamt.update(ks)
    unbekannt = sorted(k for k in gesamt if k not in eset)
    if unbekannt:
        f.append(f'Kennung nicht im Eingang: {unbekannt[:6]}')
    na = tokens_na(ab.get('Nicht aufgenommen', []))
    na_unbekannt = sorted(k for k in na if k not in eset)
    if na_unbekannt:
        f.append(f'Nicht aufgenommen: Kennung nicht im Eingang: {na_unbekannt[:6]}')
    benutzt = (gesamt | na) & eset
    fehlt = [k for k in ek if k not in benutzt]
    if fehlt:
        f.append(f'Abdeckung: {len(fehlt)} Kennungen weder im Protokoll noch unter Nicht aufgenommen, z. B. {fehlt[:6]}')

    # Beschlüsse, Offene Punkte, Muss, Einmaligkeit, Zusammenführung
    inhalt_text = ' '.join(s for n, s, k in aussagen)
    if 'beschluesse' in fall:
        bl = [s for n, s, k in aussagen if n == 'Beschlüsse']
        if not fall['beschluesse'] and 'Beschlüsse' in ab:
            f.append('Abschnitt Beschlüsse ohne Grundlage (im Gespräch wurde nichts beschlossen)')
        for rx in fall['beschluesse']:
            if not any(re.search(rx, s, re.I) for s in bl):
                f.append(f'Beschluss fehlt: /{rx}/')
        if len(bl) > fall.get('beschluesse_max', len(fall['beschluesse'])):
            f.append(f'{len(bl)} Beschlüsse, höchstens {fall.get("beschluesse_max", len(fall["beschluesse"]))} erwartet (erfunden?)')
        for rx in fall.get('beschluesse_verboten', []):
            if any(re.search(rx, s, re.I) for s in bl):
                f.append(f'Beschluss überholt, steht aber noch als Beschluss: /{rx}/')
    if 'offen' in fall:
        ol = [s for n, s, k in aussagen if n == 'Offene Punkte']
        for rx in fall['offen']:
            if not any(re.search(rx, s, re.I) for s in ol):
                f.append(f'Offener Punkt fehlt: /{rx}/')
    flach = prot.replace(NB, ' ')
    for m in fall.get('muss', []):
        if m.replace(NB, ' ') not in flach:
            f.append(f'Pflichtangabe fehlt: {m!r}')
    for rx in fall.get('hoechstens_einmal', []):
        n = len(re.findall(rx, inhalt_text.replace(NB, ' ')))
        if n > 1:
            f.append(f'mehrfach genannt statt zusammengeführt ({n}×): /{rx}/')
    for gruppe in fall.get('gemeinsam', []):
        if not any(set(gruppe) <= set(k) for n, s, k in aussagen):
            f.append(f'Doppelt Genanntes nicht in einer Aussage zusammengeführt: {gruppe}')
    for rx in fall.get('verbotene_namen', []):
        if re.search(rx, flach):
            f.append(f'verbotener Name im Protokoll: /{rx}/')

    # Zahlen: nichts erfunden
    ohne = '\n'.join(z for z in prot.splitlines() if not z.startswith('🔎'))
    ohne = re.sub(r'(?ms)^## Nicht aufgenommen.*?(?=^## |\Z)', '', ohne)
    ohne = KENN.sub('', ohne)
    for z in zahlen_fehlen(eingang, ohne):
        f.append(f'Zahl nicht im Eingang (erfunden?): {z}')

    # Aufgaben
    if 'aufgaben' in fall:
        erw = fall['aufgaben']
        if not erw and 'Aufgaben' in ab:
            f.append('Abschnitt Aufgaben ohne Grundlage')
        if erw and 'Aufgaben' not in ab:
            f.append('Abschnitt Aufgaben fehlt')
        if rows and len(rows) != len(erw):
            f.append(f'Aufgaben: {len(rows)} Zeilen, erwartet {len(erw)} (zerteilt, doppelt oder erfunden?)')
        for e in erw:
            zeile = next((r for r in rows if e['stichwort'].lower() in r[0].lower()), None)
            if not zeile:
                f.append(f'Aufgabe fehlt: {e["stichwort"]!r}')
                continue
            if not passt(zeile[1], e['zustaendig']):
                f.append(f'Aufgabe {e["stichwort"]!r}: Zuständig {zeile[1]!r}, erwartet {e["zustaendig"]!r}')
            if not passt(zeile[2], e['frist']):
                f.append(f'Aufgabe {e["stichwort"]!r}: Frist {zeile[2]!r}, erwartet {e["frist"]!r}')
    names = [norm(re.sub(KENN, '', r[0])) for r in rows]
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            if difflib.SequenceMatcher(None, names[i], names[j]).ratio() >= 0.9:
                f.append(f'Aufgabe doppelt: {rows[i][0][:40]!r} und {rows[j][0][:40]!r}')
    e_norm = norm(eingang)
    for r in rows:
        for spalte, name in ((1, 'Zuständig'), (2, 'Frist')):
            wert = r[spalte]
            if norm(wert) == 'offen':
                continue
            teile = [t for t in re.split(r'\s*(?:,|/|;|\bund\b)\s*', wert) if t.strip()] if spalte == 1 else [wert]
            for t in teile:
                if norm(t) in e_norm:
                    continue
                if spalte == 1 and fall.get('rollen_ok') and re.search(fall['rollen_ok'], t):
                    continue
                if spalte == 2 and not zahlen_fehlen(eingang, t):
                    w.append(f'Frist nicht wörtlich aus dem Eingang: {t!r}')
                    continue
                f.append(f'{name} nicht im Eingang (erfunden?): {t!r}')
        ueberschr = [norm(x) for x in d['themen']]
        kat = norm(r[3])
        if ueberschr and not any(kat in u or u in kat or set(kat.split()) & set(u.split()) for u in ueberschr):
            w.append(f'Kategorie {r[3]!r} gehört zu keinem Themenblock')

    # Prüfzeile
    p = PRUEF.match(d['pruef'] or '')
    if not d['pruef']:
        f.append('Prüfzeile (🔎 Protokoll: …) fehlt')
    elif not p:
        f.append(f'Prüfzeile hat nicht die vorgeschriebene Form: {d["pruef"][:80]!r}')
    else:
        dg, erg, cov, tot, na_, zo, fo = p.groups()
        if int(dg) < 2 or int(dg) > 3:
            f.append(f'Prüfzeile: Durchgänge {dg}, die Abdeckungsprüfung (Durchgang 2) fehlt oder es sind mehr als drei')
        if (int(cov), int(tot)) != (len(set(ek) & benutzt), len(ek)):
            f.append(f'Prüfzeile: Abdeckung {cov}/{tot}, gezählt {len(set(ek) & benutzt)}/{len(ek)}')
        if int(na_) != len(rows):
            f.append(f'Prüfzeile: Aufgaben {na_}, gezählt {len(rows)}')
        if rows and zo is None:
            f.append('Prüfzeile: Angabe (Zuständig offen …, Frist offen …) fehlt')
        if zo is not None:
            z_ist = sum(1 for r in rows if norm(r[1]) == 'offen')
            f_ist = sum(1 for r in rows if norm(r[2]) == 'offen')
            if (int(zo), int(fo)) != (z_ist, f_ist):
                f.append(f'Prüfzeile: offen {zo}/{fo}, gezählt {z_ist}/{f_ist}')
    return f, w


# ---------------------------------------------------------------- langer Fall
ROLLEN = ['Leitung', 'Technik', 'Lager', 'Verwaltung', 'Personal', 'Kommunikation']
FUELL = ['Ich sehe das ähnlich, aber lasst uns beim Thema bleiben.', 'Kurze Pause, die Kaffeemaschine ist wieder leer.',
         'Kann jemand die Folie noch einmal zeigen?', 'Das hatten wir vorhin schon, ich wollte es nur noch einmal sagen.',
         'Die Verbindung ist schlecht, ich bin kurz weg.', 'Gutes Beispiel, das merke ich mir.',
         'Ich höre euch nicht richtig, bitte etwas lauter.', 'Danke für den Hinweis, das war hilfreich.',
         'Wir schweifen etwas ab, aber das ist spannend.', 'Ich schreibe mit, falls etwas fehlt.',
         'Das Wetter war heute Morgen schlimm.', 'Entschuldigung, ich war kurz stumm geschaltet.',
         'Stimmt, so habe ich das noch nicht gesehen.', 'Das lassen wir erst einmal so stehen.',
         'Ich bin gespannt, wie es sich entwickelt.', 'Bitte alle kurz auf Mute, es hallt.']
N_LANG = 160
GEPLANT = {
    18: ('Leitung', 'Wir ziehen an den Standort Halle Nord um. Das ist beschlossen.'),
    22: ('Technik', 'Ich kümmere mich um die Elektroplanung und liefere sie bis zum 14. Dezember.'),
    37: ('Lager', 'Wir erstellen die Lagerliste für den Umzug. Einen Termin nenne ich noch nicht.'),
    45: ('Leitung', 'Das Budget für den Umzug beträgt 48.000 €. Das ist freigegeben.'),
    58: ('Verwaltung', 'Ich kläre die Versicherung bis Ende November.'),
    65: ('Leitung', 'Offen ist, wie viele Parkplätze an der Halle Nord verfügbar sind.'),
    77: ('Personal', 'Ich übernehme den Schulungsplan.'),
    91: ('Leitung', 'Wir starten am 3. März 2027. Das ist verbindlich.'),
    99: ('Leitung', 'Zur Erinnerung: Das Budget bleibt bei 48.000 €.'),
    112: ('Verwaltung', 'Offen ist, wer künftig die Reinigung der Halle übernimmt.'),
    134: ('Kommunikation', 'Ich schreibe den Pressetext bis zum 20. Januar.'),
}


def lang_erzeugen():
    absaetze = []
    for i in range(1, N_LANG + 1):
        r, t = GEPLANT.get(i, (ROLLEN[i % len(ROLLEN)], FUELL[i % len(FUELL)]))
        absaetze.append(f'{r}: {t}')
    eingang = '\n\n'.join(absaetze) + '\n'
    fuell = [i for i in range(1, N_LANG + 1) if i not in GEPLANT]
    bereiche, start = [], fuell[0]
    for a, b in zip(fuell, fuell[1:] + [None]):
        if b != a + 1:
            bereiche.append(f'A{start}' if start == a else f'A{start}–A{a}')
            start = b
    gut = f"""# Workshop-Protokoll
Datum: offen · Beteiligte: Leitung, Technik, Lager, Verwaltung, Personal, Kommunikation · Kennungen: Absatznummern
Hinweis: Von einer KI aus dem Transkript erstellt. Vor dem Weitergeben prüfen.

## Beschlüsse
- Die Organisation zieht an den Standort Halle Nord um. [A18]
- Das Budget für den Umzug beträgt 48.000 € und ist freigegeben; es bleibt unverändert. [A45, A99]
- Der Start ist am 3. März 2027 und verbindlich. [A91]

## Inhalt
### Standort und Zeitplan
Die Leitung beschließt den Umzug an den Standort Halle Nord [A18]. Der Start ist für den 3. März 2027 festgelegt [A91].

### Vorbereitung des Umzugs
Die Technik liefert die Elektroplanung [A22]. Das Lager erstellt die Lagerliste für den Umzug [A37]. Die Verwaltung klärt die Versicherung [A58].

### Personal und Kommunikation
Das Personal übernimmt den Schulungsplan [A77]. Die Kommunikation schreibt den Pressetext [A134].

## Offene Punkte
- Offen ist, wie viele Parkplätze an der Halle Nord verfügbar sind. [A65]
- Offen ist, wer künftig die Reinigung der Halle übernimmt. [A112]

## Aufgaben
| Aufgabe | Zuständig | Frist | Kategorie |
|---|---|---|---|
| Elektroplanung liefern [A22] | Technik | bis zum 14. Dezember | Vorbereitung |
| Lagerliste für den Umzug erstellen [A37] | Lager | offen | Vorbereitung |
| Versicherung klären [A58] | Verwaltung | bis Ende November | Vorbereitung |
| Schulungsplan übernehmen [A77] | Personal | offen | Personal |
| Pressetext schreiben [A134] | Kommunikation | bis zum 20. Januar | Kommunikation |

## Nicht aufgenommen
{', '.join(bereiche)} (Zwischenrufe, Technik und Pausen, kein Sachinhalt)

🔎 Protokoll: Durchgänge 2 · ergänzt 2 · Abdeckung {N_LANG}/{N_LANG} · Aufgaben 5 (Zuständig offen 0, Frist offen 2)
"""
    return eingang, gut


# ---------------------------------------------------------------- Fälle laden
def pfade(root):
    return os.path.join(HIER, 'fixtures', SKILL)


def sprache(root):
    """en, wenn die Wurzel das en-Paket ist (en/ im Arbeitsrepo und im Export), sonst de."""
    return 'en' if os.path.basename(os.path.normpath(root)) == 'en' else 'de'


def laden(root):
    fx = pfade(root)
    faelle = yaml.safe_load(open(os.path.join(fx, 'eval', 'faelle.yaml'), encoding='utf-8'))['faelle']
    return {x['id']: x for x in faelle}, fx


def lies(fx, rel):
    return open(os.path.join(fx, rel), encoding='utf-8').read()


# ---------------------------------------------------------------- Skill prüfen
def skill_pruefen(root):
    f = []
    ordner = os.path.join(root, 'skills', SKILL)
    p = os.path.join(ordner, 'SKILL.md')
    if not os.path.isfile(p):
        return [f'skills/{SKILL}/SKILL.md fehlt']
    rest = [x for x in glob.glob(os.path.join(ordner, '**', '*'), recursive=True)
            if os.path.isfile(x) and os.path.basename(x) != 'SKILL.md']
    if rest:
        f.append(f'Zusatzdateien {rest} (Befund D9: nur SKILL.md ist verlässlich)')
    t = open(p, encoding='utf-8').read()
    m = re.match(r'---\nname: (.+)\ndescription: (.+)\n---\n', t)
    if not m:
        return f + ['Frontmatter (name, description) fehlt oder ist mehrzeilig']
    if m.group(1) != SKILL:
        f.append(f'name {m.group(1)!r} passt nicht zum Ordner')
    d = m.group(2)
    if len(d) > 1024:
        f.append(f'description {len(d)} Zeichen, höchstens 1024')
    if ': ' in d or ' #' in d:
        f.append('description enthält ": " oder " #" (YAML-Risiko)')
    if '<' in d or '>' in d:
        f.append('spitze Klammern in der description')
    sp = sprache(root)
    k = SK[sp]
    if k['gerade'] and '"' in d:
        f.append('gerades Anführungszeichen in der description')
    for wort in k['desc']:
        if wort not in d:
            f.append(f'description nennt {wort!r} nicht (alle Gesprächsarten und Protokoll sollen auslösen)')
    if len(t) > MAX_SKILL:
        f.append(f'SKILL.md {len(t)} Zeichen, höchstens {MAX_SKILL}')
    for n, z in enumerate(t.splitlines(), 1):
        if SPUR.search(z):
            f.append(f'Zeile {n}: Sprachspur')
    s = sperrwort(t)
    if s:
        f.append(f'Sperrwort aus dem Auftragstext im Skill ({s})')
    ohne = re.sub(r'```.*?```', '', t[m.end():], flags=re.S)
    ohne = re.sub(r'`[^`\n]*`', '', ohne)
    for z in ohne.splitlines():
        if k['gerade'] and '"' in z:
            f.append(f'gerades Anführungszeichen außerhalb von Code: {z.strip()[:50]!r}')
    for abschnitt in k['abschnitte']:
        if abschnitt not in t:
            f.append(f'Abschnitt {abschnitt!r} fehlt')
    for wort in k['woerter']:
        if wort.lower() not in t.lower():
            f.append(f'Skill erwähnt {wort!r} nicht')
    bloecke = re.findall(r'```\n(.*?)```', t, re.S)
    if len(bloecke) != 1:
        f.append(f'{len(bloecke)} Vorlagenblöcke statt 1')
    else:
        b = bloecke[0]
        for muss in k['vorlage']:
            if muss not in b:
                f.append(f'Vorlage enthält {muss!r} nicht')
        pz = [z for z in b.splitlines() if z.startswith('🔎')]
        if len(pz) != 1 or not (PRUEF_EN if sp == 'en' else PRUEF).match(pz[0]):
            f.append('Prüfzeile in der Vorlage passt nicht zur Form, die das Werkzeug prüft')
    print(f'  {SKILL} ({sp}): description {len(d)} Zeichen, SKILL.md {len(t)} Zeichen')
    # Fixtures und Dokumente dürfen die gesperrten Namen ebenfalls nicht enthalten
    for dateien in (glob.glob(os.path.join(pfade(root), '**', '*'), recursive=True),
                    glob.glob(os.path.join(root, 'docs', SKILL, '**', '*'), recursive=True)):
        for x in dateien:
            if os.path.isfile(x):
                s = sperrwort(open(x, encoding='utf-8').read())
                if s:
                    f.append(f'Sperrwort aus dem Auftragstext in {os.path.relpath(x, root)} ({s})')
    return f


# ---------------------------------------------------------------- Selbsttest
def selbsttest(root):
    f = []
    faelle, fx = laden(root)
    eingang = {k: lies(fx, v['datei']) for k, v in faelle.items() if k != 'lang'}
    gut = {k: lies(fx, v['gut']) for k, v in faelle.items() if k != 'lang'}
    le, lg = lang_erzeugen()
    eingang['lang'], gut['lang'] = le, lg
    for k in ('lang',):  # erzeugte Dateien müssen zum Generator passen, sofern vorhanden
        for rel, soll in ((faelle[k]['datei'], le), (faelle[k]['gut'], lg)):
            pfad = os.path.join(fx, rel)
            if os.path.isfile(pfad) and open(pfad, encoding='utf-8').read() != soll:
                f.append(f'{rel} weicht vom Generator ab (protokoll_pruefen.py erzeugen)')
    for k in faelle:
        fe, we = pruefe(eingang[k], gut[k], faelle[k])
        for x in fe:
            f.append(f'Selbsttest: gutes Beispiel {k} nicht sauber: {x}')
    # Eingangszählung
    for k, (modus, anzahl) in {'kurz_zeitmarken': ('zeit', 10), 'kurz_ohne': ('absatz', 11), 'doppelt': ('absatz', 11),
                               'fehlende_fristen': ('zeit', 11), 'lang': ('absatz', N_LANG)}.items():
        m, ks = kennungen_eingang(eingang[k])
        if (m, len(ks)) != (modus, anzahl):
            f.append(f'Selbsttest: Eingang {k} zählt {m}/{len(ks)} statt {modus}/{anzahl}')

    def erkannt(name, k, fn, stichwort):
        neu = fn(gut[k])
        if neu == gut[k]:
            f.append(f'Selbsttest: Mutation {name} änderte nichts')
            return
        fe, _ = pruefe(eingang[k], neu, faelle[k])
        if not any(stichwort in x for x in fe):
            f.append(f'Selbsttest: {name} nicht erkannt (Stichwort {stichwort!r}, Funde {fe[:3]})')
    R = lambda a, b, n=1: (lambda t: t.replace(a, b, n))
    z = 'kurz_zeitmarken'
    erkannt('Kennung entfernt', z, R(' [02:05]', ''), 'ohne Kennung')
    erkannt('Kennung erfunden', z, R('[02:05]', '[09:59]'), 'nicht im Eingang')
    erkannt('Eingangskennung nicht abgedeckt', z, R('05:10 (Verabschiedung, kein Sachinhalt)', 'kein Eintrag'), 'Abdeckung')
    erkannt('fünftes Feld', z, R('| Einkauf | bis Freitag | Vertrag |', '| Einkauf | bis Freitag | Vertrag | extra |'), 'statt vier Felder')
    erkannt('Aufgabe zerteilt', z, R('\n\n## Nicht aufgenommen', '\n| | Technik | offen | Vertrag |\n\n## Nicht aufgenommen'), 'leeres Feld')
    erkannt('Aufgabe doppelt', z, R('| Vertrag technisch prüfen [02:30] | Technik | bis zum 15. Januar | Vertrag |',
                                    '| Vertrag technisch prüfen [02:30] | Technik | bis zum 15. Januar | Vertrag |\n| Vertrag technisch prüfen [02:30] | Technik | bis zum 15. Januar | Vertrag |'), 'doppelt')
    erkannt('Frist erfunden', z, R('bis Freitag', 'bis zum 3. Mai'), 'Frist')
    erkannt('Zuständiger erfunden', z, R('| Einkauf | bis Freitag', '| Beschaffung | bis Freitag'), 'Zuständig')
    erkannt('Zahl erfunden', z, R('12.400', '14.200', 2), 'Zahl nicht im Eingang')
    erkannt('Durchgang 2 fehlt', z, R('Durchgänge 2', 'Durchgänge 1'), 'Durchgang')
    erkannt('Abdeckung falsch gezählt', z, R('Abdeckung 10/10', 'Abdeckung 9/10'), 'Abdeckung 9/10')
    erkannt('Aufgabenzahl falsch', z, R('Aufgaben 3 (', 'Aufgaben 4 ('), 'Aufgaben 4')
    erkannt('Hinweis fehlt', z, R('Hinweis: Von einer KI aus dem Transkript erstellt. Vor dem Weitergeben prüfen.\n', ''), 'Hinweis')
    erkannt('sechs Themenblöcke', z, R('## Offene Punkte', ''.join(f'### Block {i}\nText {i} [00:35].\n\n' for i in range(4)) + '## Offene Punkte'), 'Themenblöcke')
    erkannt('Beschluss erfunden', z, R('- Der Start ist Ende Februar 2027. [03:40]', '- Der Start ist Ende Februar 2027. [03:40]\n- Das Budget wird um 10 % erhöht. [01:20]'), 'Beschlüsse')
    erkannt('Beschluss fehlt', z, R('- Der Start ist Ende Februar 2027. [03:40]\n', ''), 'Beschluss fehlt')
    erkannt('Aufgabenabschnitt fehlt', z, lambda t: re.sub(r'(?ms)^## Aufgaben.*?(?=^## Nicht)', '', t), 'Aufgabe')
    erkannt('Kopf der Tabelle verändert', z, R('| Aufgabe | Zuständig | Frist | Kategorie |', '| Aufgabe | Wer | Frist | Kategorie |'), 'Tabellenkopf')
    erkannt('Satz ohne Kennung mitten im Absatz', z, R('Anbieter A kostet 9.800 € im Jahr [00:35]', 'Anbieter A kostet 9.800 € im Jahr'), 'ohne Kennung')
    erkannt('Offener Punkt entfernt', z, R('## Offene Punkte\n- Offen ist, ob die alten Tickets übernommen werden. [04:45]\n\n', ''), 'Offener Punkt fehlt')
    d = 'doppelt'
    erkannt('Zusammenführung getrennt', d, R('[A2, A7]', '[A2]'), 'zusammengeführt')
    erkannt('Betrag mehrfach', d, R('Tamsorn klärt', 'Das Budget beträgt 8.500 € [A7]. Tamsorn klärt'), 'mehrfach')
    erkannt('überholter Beschluss', d, R('## Inhalt', '- Die Eröffnung findet am 1. Juni statt. [A4]\n\n## Inhalt'), 'überholt')
    erkannt('Aufgabe aus zwei Absätzen doppelt', d, R('| Plakate bestellen [A5, A8] | Quillen | bis zum 10. Mai | Marketing |',
                                                      '| Plakate bestellen [A5] | Quillen | bis zum 10. Mai | Marketing |\n| Plakate bestellen [A8] | Quillen | bis zum 10. Mai | Marketing |'), 'doppelt')
    n = 'kurz_ohne'
    erkannt('Name trotz Grenze', n, R('Die Befragte führte', 'Frau Tamsorn führte'), 'verbotener Name')
    erkannt('Name als Zuständige', n, R('| Befragte |', '| Tamsorn |'), 'verbotener Name')
    erkannt('Zahl aus Wort gerechnet', n, R('sechs Monate', '8 Monate'), 'Zahl nicht im Eingang')
    t = 'fehlende_fristen'
    erkannt('Zuständigkeit erfunden', t, R('| offen | bevor der Techniker kommt |', '| Service | bevor der Techniker kommt |'), 'Zuständig')
    erkannt('Frist erfunden statt offen', t, R('| Buchhaltung | offen |', '| Buchhaltung | morgen |'), 'Frist')
    erkannt('offener Punkt zur Aufgabe gemacht', t, R('\n\n## Nicht aufgenommen', '\n| Wartungsintervall prüfen [03:45] | Service | offen | Unterlagen |\n\n## Nicht aufgenommen'), 'Aufgaben:')
    erkannt('Beschlüsse ohne Grundlage', t, R('## Offene Punkte', '## Beschlüsse\n- Die Wartung wird vierteljährlich. [04:10]\n\n## Offene Punkte'), 'Reihenfolge')
    erkannt('Offener Punkt ohne Kennung', t, R('[03:45, 04:10]', ''), 'ohne Kennung')
    erkannt('Bereich zu klein', 'lang', R('A1–A17', 'A1–A16'), 'Abdeckung')
    erkannt('Kennung über das Ende', 'lang', R('A19–A21', 'A19–A200'), 'nicht im Eingang')
    erkannt('Budget zweimal', 'lang', R('Das Personal übernimmt', 'Das Budget ist 48.000 € [A45]. Das Personal übernimmt'), 'mehrfach')
    # Form allein (ohne Fall) darf keine Fall-Fehler melden
    fe, _ = pruefe(eingang['doppelt'], gut['doppelt'], None)
    if fe:
        f.append(f'Selbsttest: gutes Beispiel ohne Fall nicht sauber: {fe}')
    return f


def erzeugen(root):
    fx = pfade(root)
    e, g = lang_erzeugen()
    for rel, inhalt in (('eingang/lang.txt', e), ('gut/lang.md', g)):
        os.makedirs(os.path.dirname(os.path.join(fx, rel)), exist_ok=True)
        open(os.path.join(fx, rel), 'w', encoding='utf-8').write(inhalt)
        print('  geschrieben', os.path.relpath(os.path.join(fx, rel), root))


def eval_lauf(root, ordner):
    faelle, fx = laden(root)
    fehler = []
    for k, v in faelle.items():
        p = os.path.join(ordner, k + '.md')
        if not os.path.isfile(p):
            fehler.append(f'{k}: Ausgabe {k}.md fehlt')
            continue
        fe, we = pruefe(lies(fx, v['datei']), open(p, encoding='utf-8').read(), v)
        print(f'{k:18} Fehler {len(fe)} · Warnungen {len(we)}')
        fehler += [f'{k}: {x}' for x in fe]
        for x in we:
            print(f'   ~ {x}')
    return fehler


def bauen(root):
    out = os.path.join(root, 'dist')
    os.makedirs(out, exist_ok=True)
    pfad = os.path.join(out, SKILL + '.zip')
    with zipfile.ZipFile(pfad, 'w', zipfile.ZIP_DEFLATED) as z:
        zi = zipfile.ZipInfo(f'{SKILL}/SKILL.md', date_time=(2026, 11, 1, 0, 0, 0))
        zi.compress_type = zipfile.ZIP_DEFLATED
        zi.external_attr = 0o644 << 16
        z.writestr(zi, open(os.path.join(root, 'skills', SKILL, 'SKILL.md'), 'rb').read())
    print('  gebaut', os.path.relpath(pfad, root))


def main():
    a = sys.argv[1:]
    if len(a) < 2:
        sys.exit(__doc__)
    cmd, root = a[0], a[1]
    if cmd == 'skill':
        fehler = skill_pruefen(root)
    elif cmd == 'protokoll':
        if len(a) < 4:
            sys.exit('protokoll <wurzel> <fall> <datei>')
        faelle, fx = laden(root)
        if a[2] not in faelle:
            sys.exit(f'Fall {a[2]!r} unbekannt: {sorted(faelle)}')
        fe, we = pruefe(lies(fx, faelle[a[2]]['datei']), open(a[3], encoding='utf-8').read(), faelle[a[2]])
        for x in we:
            print(' ~', x)
        fehler = fe
    elif cmd == 'eval':
        fehler = eval_lauf(root, a[2])
    elif cmd == 'selbsttest':
        fehler = selbsttest(root)
    elif cmd == 'erzeugen':
        erzeugen(root)
        return
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

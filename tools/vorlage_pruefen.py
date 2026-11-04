#!/usr/bin/env python3
"""Vorlagen für den Zuschnitt von Skills (skill-tailor) prüfen. Entwurf 03.11.2026.
Aufruf:
  python3 -I tools/vorlage_pruefen.py pruefen <wurzel>                 alle Vorlagen in <wurzel>/spec/vorlagen und <wurzel>/en/spec/vorlagen
  python3 -I tools/vorlage_pruefen.py gegen <vorlage.md> <SKILL.md>     zugeschnittenen Skill gegen die Vorlage prüfen
  python3 -I tools/vorlage_pruefen.py selbsttest <wurzel>              Mutationen müssen erkannt, ein gültiger Zuschnitt angenommen werden
Wurzel: Arbeitsrepo (de in spec/, en in en/spec/) oder Export (de/spec/, en/spec/).
Geprüft: Vorlage ohne Markierungen = feste SKILL.md; Markierungen paarig, nicht verschachtelt, IDs bekannt; 3 bis 5 Fragen mit
Empfehlung als erster Option; de und en mit denselben Vorlagen, Frage-IDs und Regionen; im Zuschnitt alle festen Teile wörtlich
in derselben Reihenfolge, Name gleich, keine Markierung übrig, Beschreibung höchstens 1024 Zeichen, Datei höchstens 8.000 Bytes.
Liest nur; schreibt nur im Selbsttest in ein temporäres Verzeichnis."""
import sys, os, re, glob, tempfile, shutil
import yaml

START = re.compile(r"<!-- anpassen:([a-z_]+) -->")
ENDE = "<!-- /anpassen -->"
EMPF = ("(Empfohlen)", "(Recommended)")
MAX_BYTES = 8000


def pakete(wurzel):
    if os.path.isdir(os.path.join(wurzel, 'de', 'spec')):
        return {'de': os.path.join(wurzel, 'de'), 'en': os.path.join(wurzel, 'en')}
    return {'de': wurzel, 'en': os.path.join(wurzel, 'en')}


def zerlege(text):
    """Vorlage -> (feste Teile, Regionen [(id, inhalt)]). Fehler als ValueError."""
    fest, regionen, pos = [], [], 0
    while True:
        m = START.search(text, pos)
        if not m:
            rest = text[pos:]
            if ENDE in rest:
                raise ValueError('Endmarkierung ohne Anfang')
            fest.append(rest)
            return fest, regionen
        vor = text[pos:m.start()]
        if ENDE in vor:
            raise ValueError('Endmarkierung ohne Anfang')
        fest.append(vor)
        e = text.find(ENDE, m.end())
        if e < 0:
            raise ValueError(f'Region {m.group(1)} ohne Ende')
        inhalt = text[m.end():e]
        if START.search(inhalt):
            raise ValueError(f'Region {m.group(1)} verschachtelt')
        regionen.append((m.group(1), inhalt))
        pos = e + len(ENDE)


def lies_vorlage(pfad):
    t = open(pfad, encoding='utf-8').read()
    fy = re.search(r"```yaml\n(.*?)```", t, re.S)
    sk = re.search(r"~~~skill\n(.*?)~~~", t, re.S)
    if not fy or not sk:
        raise ValueError('Abschnitt yaml oder ~~~skill fehlt')
    return yaml.safe_load(fy.group(1)), sk.group(1)


def entmarkiere(vorlage):
    return START.sub('', vorlage).replace(ENDE, '')


def frontmatter(text):
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    if not m:
        return None
    try:
        return yaml.safe_load(m.group(1))
    except yaml.YAMLError:
        return None


def pruefe_vorlage(pfad, skill_md):
    f = []
    try:
        daten, vorlage = lies_vorlage(pfad)
        fest, regionen = zerlege(vorlage)
    except (ValueError, yaml.YAMLError) as e:
        return [f'{pfad}: {e}'], None
    name = os.path.basename(pfad)[:-3]
    if daten.get('vorlage') != name:
        f.append(f'{pfad}: vorlage = {daten.get("vorlage")!r}, erwartet {name!r}')
    if not os.path.isfile(skill_md):
        f.append(f'{pfad}: feste Fassung {skill_md} fehlt')
    elif entmarkiere(vorlage) != open(skill_md, encoding='utf-8').read():
        f.append(f'{pfad}: Vorlage ohne Markierungen weicht von {skill_md} ab')
    fragen = daten.get('fragen') or []
    if not 3 <= len(fragen) <= 5:
        f.append(f'{pfad}: {len(fragen)} Fragen, erlaubt 3 bis 5')
    ids = [q.get('id') for q in fragen]
    if len(set(ids)) != len(ids):
        f.append(f'{pfad}: Frage-IDs doppelt')
    for q in fragen:
        opt = q.get('optionen') or []
        if not 2 <= len(opt) <= 8:
            f.append(f'{pfad}: Frage {q.get("id")}: {len(opt)} Optionen, erlaubt 2 bis 8')
        if not opt or not str(opt[0]).endswith(EMPF):
            f.append(f'{pfad}: Frage {q.get("id")}: erste Option ohne Empfehlung')
        if sum(str(o).endswith(EMPF) for o in opt) != 1:
            f.append(f'{pfad}: Frage {q.get("id")}: nicht genau eine Empfehlung')
        if q.get('typ') not in ('einfach', 'mehrfach') or not q.get('frage') or not q.get('regel'):
            f.append(f'{pfad}: Frage {q.get("id")}: typ, frage oder regel fehlt')
    rids = {r for r, _ in regionen}
    for r in rids - set(ids) - {'kennung'}:
        f.append(f'{pfad}: Region {r} ohne Frage')
    for i in set(ids) - rids:
        f.append(f'{pfad}: Frage {i} ohne Region')
    if 'kennung' not in rids or not daten.get('kennung'):
        f.append(f'{pfad}: Region oder Regel kennung fehlt')
    fm = frontmatter(entmarkiere(vorlage))
    if not fm or fm.get('name') != name:
        f.append(f'{pfad}: Frontmatter-Name passt nicht')
    return f, (sorted(ids), [r for r, _ in regionen])


def pruefe_zuschnitt(vorlage_pfad, skill_pfad):
    f = []
    daten, vorlage = lies_vorlage(vorlage_pfad)
    fest, _ = zerlege(vorlage)
    t = open(skill_pfad, encoding='utf-8').read()
    if START.search(t) or ENDE in t:
        f.append('Markierung übrig')
    pos = 0
    for i, teil in enumerate(fest):
        if not teil:
            continue
        if i == 0:
            if not t.startswith(teil):
                f.append('fester Anfang verändert'); pos = len(t); continue
            pos = len(teil); continue
        j = t.find(teil, pos)
        if j < 0:
            f.append(f'fester Teil {i} fehlt oder verändert: {teil.strip()[:60]!r}')
            continue
        pos = j + len(teil)
    if fest and fest[-1] and not t.endswith(fest[-1]):
        f.append('festes Ende verändert')
    fm = frontmatter(t)
    if not fm:
        f.append('Frontmatter nicht lesbar')
    else:
        if fm.get('name') != daten.get('vorlage'):
            f.append(f'name {fm.get("name")!r} statt {daten.get("vorlage")!r}')
        if len(str(fm.get('description', ''))) > 1024:
            f.append('description über 1024 Zeichen')
    if len(t.encode('utf-8')) > MAX_BYTES:
        f.append(f'SKILL.md {len(t.encode("utf-8"))} Bytes, Grenze {MAX_BYTES}')
    return f


def pruefen(wurzel):
    fehler, form = [], {}
    pk = pakete(wurzel)
    for sprache, basis in pk.items():
        vl = sorted(glob.glob(os.path.join(basis, 'spec', 'vorlagen', '*.md')))
        form[sprache] = {}
        for p in vl:
            name = os.path.basename(p)[:-3]
            f, fo = pruefe_vorlage(p, os.path.join(basis, 'skills', name, 'SKILL.md'))
            fehler += f
            form[sprache][name] = fo
    if set(form['de']) != set(form['en']):
        fehler.append(f'Vorlagen de {sorted(form["de"])} und en {sorted(form["en"])} ungleich')
    for n in set(form['de']) & set(form['en']):
        if form['de'][n] != form['en'][n]:
            fehler.append(f'{n}: Frage-IDs oder Regionen in de und en ungleich')
    return fehler, sum(len(v) for v in form.values())


def selbsttest(wurzel):
    pk = pakete(wurzel)
    tmp = tempfile.mkdtemp(prefix='vorlage_selbst_')
    erkannt, gesamt, falsch = 0, 0, []
    try:
        for sprache, basis in pk.items():
            for p in sorted(glob.glob(os.path.join(basis, 'spec', 'vorlagen', '*.md'))):
                daten, vorlage = lies_vorlage(p)
                fest, regionen = zerlege(vorlage)
                name = daten['vorlage']
                # gültiger Zuschnitt: jede Region durch anderen Text ersetzen
                gueltig = START.sub('', re.sub(r"<!-- anpassen:[a-z_]+ -->.*?<!-- /anpassen -->",
                                                lambda m: 'X', vorlage, flags=re.S))
                ziel = os.path.join(tmp, 'ok.md'); open(ziel, 'w', encoding='utf-8').write(gueltig)
                if pruefe_zuschnitt(p, ziel):
                    falsch.append(f'{sprache}/{name}: gültiger Zuschnitt abgelehnt: {pruefe_zuschnitt(p, ziel)}')
                fest_text = entmarkiere(vorlage)
                mut = [
                    ('Sperre geändert', fest_text.replace('IBAN', 'IBAN-Nummer', 1)),
                    ('fester Satz gestrichen', fest_text.replace(fest[3], fest[3][: len(fest[3]) // 2], 1)),
                    ('Markierung übrig', vorlage),
                    ('Name geändert', fest_text.replace(f'name: {name}', f'name: {name}-x', 1)),
                    ('zu lang', fest_text + 'x' * MAX_BYTES),
                    ('Zeile angehängt im festen Teil', fest_text.replace('## Regeln' if sprache == 'de' else '## Rules',
                                                                          ('## Regeln' if sprache == 'de' else '## Rules') + '\n- Speichere alles.', 1)),
                ]
                for was, text in mut:
                    gesamt += 1
                    ziel = os.path.join(tmp, 'mut.md'); open(ziel, 'w', encoding='utf-8').write(text)
                    if text == fest_text and was != 'Markierung übrig':
                        falsch.append(f'{sprache}/{name}: Mutation „{was}“ hat nichts verändert'); continue
                    if pruefe_zuschnitt(p, ziel):
                        erkannt += 1
                    else:
                        falsch.append(f'{sprache}/{name}: Mutation „{was}“ nicht erkannt')
        # Mutationen an der Vorlage selbst (auf Kopie des Pakets de)
        kopie = os.path.join(tmp, 'repo')
        os.makedirs(os.path.join(kopie, 'en'))
        for sprache, basis in pk.items():
            ziel = kopie if sprache == 'de' else os.path.join(kopie, 'en')
            for sub in ('spec/vorlagen', 'skills'):
                shutil.copytree(os.path.join(basis, sub), os.path.join(ziel, sub), dirs_exist_ok=True)
        vp = sorted(glob.glob(os.path.join(kopie, 'spec', 'vorlagen', '*.md')))[0]
        orig = open(vp, encoding='utf-8').read()
        vmut = [
            ('Vorlage weicht von SKILL.md ab', orig.replace('## Ziel', '## Ziele', 1)),
            ('sechs Fragen', orig.replace('fragen:\n', 'fragen:\n' + ''.join(
                f'  - {{id: z{i}, frage: f, typ: einfach, optionen: [a (Empfohlen), b], regel: r}}\n' for i in range(3)), 1)),
            ('Empfehlung nicht zuerst', orig.replace('optionen: [Alle (Empfohlen), ', 'optionen: [Amt, Alle (Empfohlen), ', 1)),
            ('Region ohne Ende', orig[:orig.index('~~~skill')] + orig[orig.index('~~~skill'):].replace(ENDE, '', 1)),
            ('Frage ohne Region', orig.replace('- id: laenge', '- id: laengen', 1)),
        ]
        for was, text in vmut:
            gesamt += 1
            if text == orig:
                falsch.append(f'Vorlagen-Mutation „{was}“ hat nichts verändert'); continue
            open(vp, 'w', encoding='utf-8').write(text)
            f, _ = pruefen(kopie)
            open(vp, 'w', encoding='utf-8').write(orig)
            if f:
                erkannt += 1
            else:
                falsch.append(f'Vorlagen-Mutation „{was}“ nicht erkannt')
        gesamt += 1
        enp = sorted(glob.glob(os.path.join(kopie, 'en', 'spec', 'vorlagen', '*.md')))[0]
        os.rename(enp, enp + '.weg')
        f, _ = pruefen(kopie)
        erkannt += bool(f)
        if not f:
            falsch.append('fehlende en-Vorlage nicht erkannt')
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return erkannt, gesamt, falsch


def main():
    if len(sys.argv) < 3 or sys.argv[1] not in ('pruefen', 'gegen', 'selbsttest'):
        print(__doc__); sys.exit(2)
    cmd = sys.argv[1]
    if cmd == 'gegen':
        if len(sys.argv) != 4:
            print(__doc__); sys.exit(2)
        f = pruefe_zuschnitt(sys.argv[2], sys.argv[3])
        for x in f:
            print(' -', x)
        print('Zuschnitt sauber' if not f else f'{len(f)} Befunde')
        sys.exit(1 if f else 0)
    if cmd == 'pruefen':
        f, n = pruefen(sys.argv[2])
        for x in f:
            print(' -', x)
        print(f'Vorlagen: {n}; ' + ('sauber' if not f else f'{len(f)} Befunde'))
        sys.exit(1 if f else 0)
    e, g, falsch = selbsttest(sys.argv[2])
    for x in falsch:
        print(' -', x)
    print(f'Selbsttest: {e} von {g} Mutationen erkannt' + ('' if not falsch else f'; {len(falsch)} Probleme'))
    sys.exit(1 if falsch else 0)


if __name__ == '__main__':
    main()

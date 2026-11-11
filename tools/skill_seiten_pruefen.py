#!/usr/bin/env python3
"""Skill-Seiten: Faktenkopf aus SKILL.md und Spec erzeugen und prüfen. Entwurf 03.11.2026.
Aufruf (Arbeitsrepo oder Export, Wurzel ist das Verzeichnis mit en/):
  python3 -I tools/skill_seiten_pruefen.py pruefen <wurzel>      jede Seite da, Faktenkopf stimmt, Übersicht vollständig
  python3 -I tools/skill_seiten_pruefen.py schreiben <wurzel>    schreibt die Faktenköpfe neu (Handtexte bleiben)
  python3 -I tools/skill_seiten_pruefen.py selbsttest <wurzel>   Mutationen auf einer Kopie müssen erkannt werden
Die Seiten stehen im Arbeitsrepo unter docs/public/skills/, im Export unter skills/ (Wurzel).
Der Faktenkopf liegt zwischen <!-- facts:start --> und <!-- facts:end -->, die Tabelle der Übersicht zwischen <!-- index:start --> und <!-- index:end -->.
Geprüft werden Fakten und Vollständigkeit, nicht der Ablauf in den Handtexten."""
import sys, os, re, glob, shutil, tempfile
import yaml

FS, FE = '<!-- facts:start -->', '<!-- facts:end -->'
IS, IE = '<!-- index:start -->', '<!-- index:end -->'
ART = {'A1': 'A1 · Core, always', 'A2': 'A2 · Module skill', 'A3': 'A3 · Add-on, offered when it fits'}


def seiten_dir(w):
    for rel in ('docs/public/skills', 'skills'):
        if os.path.isdir(os.path.join(w, rel)):
            return os.path.join(w, rel)
    return os.path.join(w, 'docs/public/skills')


def skill_pfade(w, name):
    """(en-Pfad, de-Pfad) der SKILL.md, in Arbeitsrepo- und Exportstruktur."""
    kandidaten_en = [f'en/skills/{name}', f'en/skeleton/skills/{name}']
    kandidaten_de = [f'skills/{name}', f'skeleton/skills/{name}', f'de/skills/{name}', f'de/skeleton/skills/{name}']
    en = next((os.path.join(w, k, 'SKILL.md') for k in kandidaten_en if os.path.exists(os.path.join(w, k, 'SKILL.md'))), None)
    de = next((os.path.join(w, k, 'SKILL.md') for k in kandidaten_de if os.path.exists(os.path.join(w, k, 'SKILL.md'))), None)
    return en, de


def spec_dir(w):
    return os.path.join(w, 'en/spec')


def fakten(w):
    """name -> dict(art, bereich, beschr, en_zeichen, de_zeichen)"""
    out = {}
    for p in sorted(glob.glob(os.path.join(spec_dir(w), 'module', '*.yaml'))):
        d = yaml.safe_load(open(p, encoding='utf-8'))
        mid = os.path.basename(p)[:-5]
        bereich = 'Core' if mid == 'kern' else f"{d.get('name', mid)} (`{mid}`)"
        for s in d.get('skills') or []:
            out[s] = {'art': 'A1' if mid == 'kern' else 'A2', 'bereich': bereich}
        for s in d.get('skills_nachruestbar') or []:
            out[s] = {'art': 'A3', 'bereich': bereich}
    for name, f in out.items():
        en, de = skill_pfade(w, name)
        f['en'], f['de'] = en, de
        if en:
            t = open(en, encoding='utf-8').read()
            m = re.search(r'^description:\s*(.*)$', t, re.M)
            f['beschr'] = (m.group(1).strip() if m else '').strip('"\'')
            f['en_zeichen'] = len(t)
        if de:
            f['de_zeichen'] = len(open(de, encoding='utf-8').read())
    return out


def fakten_block(name, f):
    z = lambda n: f'{n:,}' if n else 'missing'
    return '\n'.join([
        FS, '| | |', '|---|---|',
        f"| Kind | {ART[f['art']]} |",
        f"| Area | {f['bereich']} |",
        f"| Upload | `en/dist/{name}.zip` · `de/dist/{name}.zip` (one skill per ZIP) |",
        f"| Size | {z(f.get('en_zeichen'))} characters (en) · {z(f.get('de_zeichen'))} characters (de), limit 8,000 for module skills |",
        f"| Description | {f.get('beschr', '')} |",
        FE])


def index_block(fk):
    zeilen = [IS, '| Skill | Kind | Area |', '|---|---|---|']
    for art in ('A1', 'A2', 'A3'):
        for name in sorted(n for n, f in fk.items() if f['art'] == art):
            zeilen.append(f"| [`{name}`]({name}.md) | {ART[art]} | {fk[name]['bereich']} |")
    zeilen.append(IE)
    return '\n'.join(zeilen)


def ersetze_block(text, start, ende, neu):
    if start not in text or ende not in text:
        return None
    a, b = text.index(start), text.index(ende) + len(ende)
    return text[:a] + neu + text[b:]


def pruefen(w):
    fehler = []
    sd = seiten_dir(w)
    fk = fakten(w)
    for name, f in fk.items():
        if not f.get('en'):
            fehler.append(f'{name}: SKILL.md (en) fehlt')
        if not f.get('de'):
            fehler.append(f'{name}: SKILL.md (de) fehlt')
        p = os.path.join(sd, name + '.md')
        if not os.path.exists(p):
            fehler.append(f'{name}: Seite fehlt ({os.path.relpath(p, w)})'); continue
        t = open(p, encoding='utf-8').read()
        if ersetze_block(t, FS, FE, fakten_block(name, f)) is None:
            fehler.append(f'{name}: Faktenkopf-Markierungen fehlen')
        elif ersetze_block(t, FS, FE, fakten_block(name, f)) != t:
            fehler.append(f'{name}: Faktenkopf weicht von SKILL.md/Spec ab (schreiben ausführen)')
        if '```mermaid' not in t:
            fehler.append(f'{name}: kein Mermaid-Diagramm')
        for pflicht in ('## Triggers', '## Flow', '## Limits', '## Status'):
            if pflicht not in t:
                fehler.append(f'{name}: Abschnitt {pflicht} fehlt')
    for p in glob.glob(os.path.join(sd, '*.md')):
        n = os.path.basename(p)[:-3]
        if n not in fk and n not in ('README', 'GATES'):
            fehler.append(f'{n}: Seite ohne Skill in der Spec')
    ov = os.path.join(sd, 'README.md')
    if not os.path.exists(ov):
        fehler.append('README.md (Übersicht) fehlt')
    else:
        t = open(ov, encoding='utf-8').read()
        neu = ersetze_block(t, IS, IE, index_block(fk))
        if neu is None:
            fehler.append('README.md: Index-Markierungen fehlen')
        elif neu != t:
            fehler.append('README.md: Index weicht von der Spec ab (schreiben ausführen)')
        if '```mermaid' not in t:
            fehler.append('README.md: kein Mermaid-Diagramm')
    g = os.path.join(sd, 'GATES.md')
    if not os.path.exists(g):
        fehler.append('GATES.md fehlt')
    else:
        t = open(g, encoding='utf-8').read()
        for name in fk:
            if f'`{name}`' not in t:
                fehler.append(f'GATES.md: {name} fehlt in der Matrix')
    return fehler


def schreiben(w):
    sd = seiten_dir(w)
    fk = fakten(w)
    n = 0
    for name, f in fk.items():
        p = os.path.join(sd, name + '.md')
        if os.path.exists(p):
            t = open(p, encoding='utf-8').read()
            neu = ersetze_block(t, FS, FE, fakten_block(name, f))
            if neu is not None and neu != t:
                open(p, 'w', encoding='utf-8').write(neu); n += 1
    ov = os.path.join(sd, 'README.md')
    if os.path.exists(ov):
        t = open(ov, encoding='utf-8').read()
        neu = ersetze_block(t, IS, IE, index_block(fk))
        if neu is not None and neu != t:
            open(ov, 'w', encoding='utf-8').write(neu); n += 1
    print(f'{n} Dateien aktualisiert')


def selbsttest(w):
    base = pruefen(w)
    if base:
        print('Ausgangslage nicht sauber:'); [print(' -', x) for x in base]; return 1
    sd_rel = os.path.relpath(seiten_dir(w), w)
    muster = []
    tmp = tempfile.mkdtemp()
    nicht_erkannt = 0
    def lauf(name, aendere):
        nonlocal nicht_erkannt
        k = os.path.join(tmp, name)
        shutil.copytree(w, k, ignore=shutil.ignore_patterns('.git', '__pycache__'))
        aendere(os.path.join(k, sd_rel))
        if not pruefen(k):
            print(f'  nicht erkannt: {name}'); nicht_erkannt += 1
    def aendere_datei(rel, f):
        def g(sd):
            p = os.path.join(sd, rel)
            t = open(p, encoding='utf-8').read()
            open(p, 'w', encoding='utf-8').write(f(t))
        return g
    lauf('seite_fehlt', lambda sd: os.remove(os.path.join(sd, 'fact-check.md')))
    lauf('fakt_geaendert', aendere_datei('fact-check.md', lambda t: t.replace('| Kind | A1', '| Kind | A3', 1)))
    lauf('zeichen_geaendert', aendere_datei('vibe-pack.md', lambda t: re.sub(r'\| Size \| [\d,]+', '| Size | 1', t, count=1)))
    lauf('mermaid_fehlt', aendere_datei('brain-check.md', lambda t: t.replace('```mermaid', '```text')))
    lauf('abschnitt_fehlt', aendere_datei('weekly-review.md', lambda t: t.replace('## Limits', '## Grenzen')))
    lauf('markierung_fehlt', aendere_datei('area-manager.md', lambda t: t.replace(FS, '')))
    lauf('index_geaendert', aendere_datei('README.md', lambda t: t.replace('A1 · Core, always', 'A3 · Add-on', 1)))
    lauf('gates_lueckenhaft', aendere_datei('GATES.md', lambda t: t.replace('`style-profile`', 'style-profile')))
    lauf('seite_ohne_skill', lambda sd: open(os.path.join(sd, 'phantom-skill.md'), 'w').write('# x'))
    shutil.rmtree(tmp, ignore_errors=True)
    print(f'Selbsttest: 9 Mutationen, {nicht_erkannt} nicht erkannt; Ausgangslage 0 Befunde')
    return 1 if nicht_erkannt else 0


def main():
    if len(sys.argv) < 3:
        print(__doc__); sys.exit(2)
    cmd, w = sys.argv[1], sys.argv[2]
    if cmd == 'pruefen':
        f = pruefen(w)
        for x in f:
            print(' -', x)
        print('Skill-Seiten sauber' if not f else f'{len(f)} Befunde')
        sys.exit(1 if f else 0)
    if cmd == 'schreiben':
        schreiben(w); return
    if cmd == 'selbsttest':
        sys.exit(selbsttest(w))
    print(__doc__); sys.exit(2)


if __name__ == '__main__':
    main()

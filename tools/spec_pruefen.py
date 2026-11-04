#!/usr/bin/env python3
"""Strenge Prüfung der Spec (Entscheid 31.10.: Module als Daten + Schema-Prüfung).
Aufruf:  python3 -I spec_pruefen.py <spec-ordner>               prüfen, Exit 1 bei Fehlern
         python3 -I spec_pruefen.py <spec-ordner> --feldkarte   Modultabelle in Feldkarte.md neu schreiben
Liest nur YAML/Markdown; schreibt nur mit --feldkarte (und dann nur den Block zwischen den Markern)."""
import sys, os, re, glob, yaml

spec = sys.argv[1]
SCHREIBEN = '--feldkarte' in sys.argv[2:]
fehler = []
F = fehler.append
TAGS = {'kinder', 'gesundheit', 'geld', 'namen'}
TYPEN_FRAGE = {'einfach', 'mehrfach', 'text'}
TYPEN_FELD = {'text', 'liste', 'auswahl', 'ganzzahl'}
SPRACHSPUR = re.compile(r'[\u0400-\u06FF\u0E00-\u0E7F\u3040-\u9FFF]')   # Datenschutz: keine fremde Schrift im Paket

def lade(rel):
    p = os.path.join(spec, rel)
    try:
        return yaml.safe_load(open(p, encoding='utf-8'))
    except Exception as e:
        F(f'{rel}: lädt nicht ({e})')
        return None

def schluessel(ort, d, erlaubt, pflicht=()):
    if not isinstance(d, dict):
        F(f'{ort}: kein Mapping'); return False
    for k in d:
        if k not in erlaubt:
            F(f'{ort}: unbekannter Schlüssel {k!r}')
    for k in pflicht:
        if k not in d:
            F(f'{ort}: Pflichtschlüssel {k!r} fehlt')
    return True

# ---------------------------------------------------------------- Datenschutz-Spur in allen Dateien
for p in glob.glob(os.path.join(spec, '**', '*.*'), recursive=True):
    rel = os.path.relpath(p, spec)
    for n, zeile in enumerate(open(p, encoding='utf-8'), 1):
        if SPRACHSPUR.search(zeile):
            F(f'{rel}:{n}: Sprachspur (nicht-lateinische Schrift) gefunden')

# ---------------------------------------------------------------- Fragen
fr1 = lade('Fragen_Stufe1.yaml') or {}
fr2 = lade('Fragen_Stufe2.yaml') or {}
schluessel('Fragen_Stufe1', fr1, {'version', 'sprache', 'immer_angeboten', 'runden', 'regeln', 'vorsatz'}, ('version', 'runden'))
schluessel('Fragen_Stufe2', fr2, {'version', 'sprache', 'immer_angeboten', 'fragen', 'regeln', 'eigene_bereiche'}, ('version', 'fragen'))
# Regeln des Interviews (Entscheid 03.11., Trockenlauf 4): feste Schlüssel, Wortlaut nicht leer; skelett.py prüft ihn im Skill
# Welle 3 (Entscheide 03.11. nach 200 Simulationen): neue Schlüssel
REGELN_S1 = {'startpruefung', 'dauer', 'wer_schreibt', 'ab_18', 'eine_frage', 'darstellung', 'keine_begriffe', 'paketwortlaut',
             'ausweichen_mit_optionen', 'pflicht_ausgewichen', 'ausweichen_mit_empfehlung', 'freie_antwort', 'meinung_geaendert',
             'eigen_dublette', 'mehrere_eigene', 'grenzen_halbes_modul', 'name_statt_rolle', 'anweisung_im_freitext',
             'viel_auf_einmal', 'nicht_moeglich', 'live_feldkarte', 'abbruch', 'weiter_satz', 'bestaetigung', 'statuszeile', 'pruefzeile',
             'begleitperson', 'uebernahme', 'sichtbarkeit', 'wessen_konto', 'druck'}
REGELN_S2 = {'takt', 'spaeter_antwort', 'bedingung', 'sensibel', 'direkt', 'skill_anstossen', 'spaeter_zuschalten', 'warteschlange', 'anrede',
             'tempo', 'eigene_fragen', 'feldkarte_aendern', 'beispieltext', 'grenzen_aendern'}
# Welle 5: gemeinsame Regeln (spec/Gemeinsame_Regeln.yaml)
REGELN_G = {'schreibformat', 'sprache_anrede', 'drive_gilt', 'ueberholt', 'antwortfilter', 'chatverlauf', 'termine_erlaubt', 'briefe',
            'loeschen', 'fremde_anweisungen', 'wechsel', 'krise_konto'}
for name, d, soll in (('Fragen_Stufe1', fr1, REGELN_S1), ('Fragen_Stufe2', fr2, REGELN_S2)):
    r = d.get('regeln')
    if not isinstance(r, dict):
        F(f'{name}: regeln fehlen'); continue
    for k in sorted(set(soll) - set(r)):
        F(f'{name}: Regel {k} fehlt')
    for k in sorted(set(r) - set(soll)):
        F(f'{name}: Regel {k} unbekannt')
    for k, v in r.items():
        if not isinstance(v, str) or len(v.strip()) < 20:
            F(f'{name}: Regel {k} ohne Wortlaut')
FRAGE_K = {'id', 'modul', 'frage', 'typ', 'optionen', 'pflicht', 'profil_pfad', 'hilfe', 'empfehlung', 'begruendung',
           'hinweis', 'folgefragen', 'hinweis_bei', 'hinweis_wenn_nur', 'sperrt_tags', 'vorbelegt', 'reihenfolge', 'tags',
           'spaeter', 'wenn', 'bedeutung', 'vorgewaehlt'}
FOLGE_K = {'id', 'wenn_enthaelt', 'wenn_nicht', 'frage', 'typ', 'pflicht', 'profil_pfad', 'zaehlt_mit', 'optionen'}
fragen, ids = {}, set()

def pruef_frage(ort, q, mit_optionen=True):
    if not schluessel(ort, q, FRAGE_K, ('id', 'modul', 'frage', 'typ', 'profil_pfad')):
        return
    if q['id'] in ids:
        F(f'{ort}: doppelte id {q["id"]}')
    ids.add(q['id'])
    if q['typ'] not in TYPEN_FRAGE:
        F(f'{ort}: typ {q["typ"]!r} unbekannt')
    opt = q.get('optionen', [])
    if q['typ'] != 'text' and mit_optionen and not opt:
        F(f'{ort}: Auswahlfrage ohne optionen')
    if 'empfehlung' in q and q['empfehlung'] not in opt and q['empfehlung'] + (' (Recommended)' if (lade('Fragen_Stufe1.yaml') or {}).get('sprache') == 'en' else ' (Empfohlen)') not in opt:
        F(f'{ort}: empfehlung nicht unter den optionen')
    for k in ('hinweis_bei', 'hinweis_wenn_nur', 'sperrt_tags'):
        for o in (q.get(k) or {}):
            if o not in opt:
                F(f'{ort}: {k}: {o!r} ist keine Option')
    for o, tag in (q.get('sperrt_tags') or {}).items():
        if tag not in TAGS:
            F(f'{ort}: sperrt_tags: Tag {tag!r} unbekannt')
    for o in q.get('vorbelegt', []):
        if o not in opt:
            F(f'{ort}: vorbelegt {o!r} ist keine Option')
    for t in q.get('tags', []):
        if t not in TAGS:
            F(f'{ort}: Tag {t!r} unbekannt')
    for i, ff in enumerate(q.get('folgefragen', [])):
        o2 = f'{ort}.folgefragen[{i}]'
        if not schluessel(o2, ff, FOLGE_K, ('id', 'frage', 'typ', 'profil_pfad')):
            continue
        if ff['id'] in ids:
            F(f'{o2}: doppelte id {ff["id"]}')
        ids.add(ff['id'])
        bed = [k for k in ('wenn_enthaelt', 'wenn_nicht') if k in ff]
        if len(bed) != 1:
            F(f'{o2}: genau eine Bedingung (wenn_enthaelt oder wenn_nicht) nötig')
        for k in bed:
            if ff[k] not in opt:
                F(f'{o2}: {k} {ff[k]!r} ist keine Option')
        fragen[ff['id']] = dict(ff, modul=q.get('modul'))
    fragen[q['id']] = q

for r in fr1.get('runden', []):
    zaehl = list(r.get('fragen', []))
    if len(zaehl) > 4:
        F(f'Stufe 1 Runde {r.get("runde")}: {len(zaehl)} Fragen, Grenze ist 4 (Entscheid 31.10.)')
    for q in zaehl:
        pruef_frage(f'Fragen_Stufe1:{q.get("id")}', q)
for q in fr2.get('fragen', []):
    pruef_frage(f'Fragen_Stufe2:{q.get("id")}', q, mit_optionen=False)
# Welle 5: gemeinsame Regeln, vorgewählte Optionen
_gem = lade('Gemeinsame_Regeln.yaml') or {}
if set((_gem.get('regeln') or {})) != REGELN_G:
    F(f'Gemeinsame_Regeln: Schlüssel weichen ab: fehlen {sorted(REGELN_G - set(_gem.get("regeln") or {}))}, zu viel {sorted(set(_gem.get("regeln") or {}) - REGELN_G)}')
for _k in set(_gem.get('regeln') or {}) & (set(fr1.get('regeln') or {}) | set(fr2.get('regeln') or {})):
    F(f'Gemeinsame_Regeln: {_k} steht zusätzlich in Stufe 1 oder 2')
for q in [q for r in fr1.get('runden', []) for q in r.get('fragen', [])]:
    for o in q.get('vorgewaehlt') or []:
        if o not in q.get('optionen', []):
            F(f'Fragen_Stufe1:{q.get("id")}: vorgewaehlt {o!r} ist keine Option')
# Welle 3: Vorsatz (zählt nicht mit), Bedeutung je Option, Folgefragen mit Optionen, eigene Bereiche der Beispielliste
for q in fr1.get('vorsatz', []):
    pruef_frage(f'Fragen_Stufe1:vorsatz:{q.get("id")}', q)
for q in [q for r in fr1.get('runden', []) for q in r.get('fragen', [])] + fr1.get('vorsatz', []):
    for o in (q.get('bedeutung') or {}):
        if o not in q.get('optionen', []):
            F(f'Fragen_Stufe1:{q.get("id")}: bedeutung {o!r} ist keine Option')
    for ff in q.get('folgefragen', []):
        if ff.get('typ') in ('einfach', 'mehrfach') and not ff.get('optionen'):
            F(f'Fragen_Stufe1:{ff.get("id")}: Auswahl-Folgefrage ohne optionen')
_hilfe = next((q.get('hilfe', '') for r in fr1.get('runden', []) for q in r.get('fragen', []) if q.get('id') == 's1.felder'), '')
_s2ids = {q.get('id') for q in fr2.get('fragen', [])}
for name, ids in (fr2.get('eigene_bereiche') or {}).items():
    if name not in _hilfe:
        F(f'Fragen_Stufe2: eigener Bereich {name!r} steht nicht in der Hilfe von s1.felder')
    for i in ids or []:
        if i not in _s2ids:
            F(f'Fragen_Stufe2: eigener Bereich {name!r} verweist auf unbekannte Frage {i!r}')

# ---------------------------------------------------------------- Module
MODUL_K = {'id', 'name', 'version', 'art', 'aktivierung', 'kanal_detail', 'skills', 'skills_nachruestbar', 'anweisungsbaustein', 'vorlagen',
           'ablage_karte', 'profilfelder', 'fragen', 'zuordnung', 'eigener_projektkandidat'}
FELD_K = {'typ', 'pflicht', 'hinweis', 'frage', 'optionen', 'abgeleitet_aus', 'quelle', 'vorgabe', 'fest', 'fest_enthalten', 'tags', 'referenz'}
modul_dateien = {os.path.basename(p)[:-5]: p for p in glob.glob(os.path.join(spec, 'module', '*.yaml'))}
module = {}
for stamm, p in sorted(modul_dateien.items()):
    rel = os.path.relpath(p, spec)
    m = lade(rel)
    if not schluessel(rel, m, MODUL_K, ('id', 'name', 'version', 'art', 'aktivierung', 'skills', 'vorlagen', 'ablage_karte', 'profilfelder')):
        continue
    if stamm != m['id']:
        F(f'{rel}: Dateiname passt nicht zur id {m["id"]!r}')
    if m['art'] not in ('kern', 'vorlage'):
        F(f'{rel}: art {m["art"]!r} (erlaubt: kern, vorlage; eigen nur zur Laufzeit)')
    if m.get('kanal_detail', 'chat') not in ('chat', 'formular'):
        F(f'{rel}: kanal_detail {m["kanal_detail"]!r}')
    if len(m.get('anweisungsbaustein') or '') > 1500:
        F(f'{rel}: anweisungsbaustein über 1.500 Zeichen')
    if m.get('art') != 'kern' and re.search(r'Entwurf folgt|draft follows', m.get('anweisungsbaustein') or ''):
        F(f'{rel}: anweisungsbaustein ist noch ein Platzhalter')
    for v in m['vorlagen']:
        schluessel(f'{rel}: vorlage', v, {'name', 'art', 'hinweis'}, ('name', 'art'))
    for name, feld in (m['profilfelder'] or {}).items():
        if schluessel(f'{rel}: profilfeld {name}', feld, FELD_K, ('typ',)):
            if feld['typ'] not in TYPEN_FELD:
                F(f'{rel}: profilfeld {name}: typ {feld["typ"]!r}')
            for t in feld.get('tags', []):
                if t not in TAGS:
                    F(f'{rel}: profilfeld {name}: Tag {t!r} unbekannt')
    module[m['id']] = m

if 'kern' not in module:
    F('module/kern.yaml fehlt')
alle_skills = {}
nachruestbar = {}
for mid, m in module.items():
    for s in m['skills']:
        if not re.fullmatch(r'[a-z][a-z-]*', s):
            F(f'module/{mid}: Skillname {s!r} ungültig')
        if s in alle_skills:
            F(f'Skill {s} in zwei Modulen: {alle_skills[s]} und {mid}')
        alle_skills[s] = mid
    for s in m.get('skills_nachruestbar') or []:
        if not re.fullmatch(r'[a-z][a-z-]*', s):
            F(f'module/{mid}: nachrüstbarer Skill {s!r} ungültig')
        if s in alle_skills or s in nachruestbar:
            F(f'Skill {s} (nachrüstbar, {mid}) ist schon als Skill eines Moduls eingetragen')
        nachruestbar[s] = mid
    akt = m['aktivierung']
    if schluessel(f'module/{mid}: aktivierung', akt, {'immer', 'wenn_antwort', 'wenn_modul'}):
        if not akt:
            F(f'module/{mid}: aktivierung leer')
        if akt.get('immer') and mid not in ('kern', 'person', 'werkzeuge'):
            F(f'module/{mid}: "immer" nur für kern, person, werkzeuge')
        for r in akt.get('wenn_antwort', []):
            q = fragen.get(r.get('frage'))
            if not q:
                F(f'module/{mid}: aktivierung verweist auf unbekannte Frage {r.get("frage")!r}')
            elif r.get('option') not in q.get('optionen', []):
                F(f'module/{mid}: aktivierung: {r.get("option")!r} ist keine Option von {q["id"]}')
        for x in akt.get('wenn_modul', []):
            if x not in modul_dateien:
                F(f'module/{mid}: wenn_modul {x!r} unbekannt')

for qid, q in fragen.items():
    if q.get('modul') not in module:
        F(f'Frage {qid}: modul {q.get("modul")!r} unbekannt')

# ---------------------------------------------------------------- Profilschema und Zuordnung
sc = lade('Profilschema.yaml') or {}
schluessel('Profilschema', sc, {'schema_version', 'meta', 'person', 'werkzeuge', 'referenz_platzhalter', 'werte'}, ('schema_version', 'meta', 'person', 'werkzeuge', 'werte'))

def felder(d, p=''):
    for k, v in (d or {}).items():
        if isinstance(v, dict) and 'typ' in v:
            yield p + k, v
        elif isinstance(v, dict):
            yield from felder(v, p + k + '.')

pfade = {}
for top in ('meta', 'person', 'werkzeuge'):
    for p, v in felder({top: sc.get(top)}):
        pfade[p] = v
        schluessel(f'Profilschema {p}', v, FELD_K, ('typ', 'pflicht'))
        if v.get('typ') not in TYPEN_FELD:
            F(f'Profilschema {p}: typ {v.get("typ")!r}')
        if 'frage' in v and v['frage'] not in fragen:
            F(f'Profilschema {p}: frage {v["frage"]!r} existiert nicht')
for mid, m in module.items():
    for name in (m['profilfelder'] or {}):
        pfade[f'{mid}.{name}'] = m['profilfelder'][name]
for qid, q in fragen.items():
    if q.get('profil_pfad') not in pfade:
        F(f'Frage {qid}: profil_pfad {q.get("profil_pfad")!r} ist kein Feld')

zu = (lade('Zuordnung.yaml') or {}).get('ziele', {})
dokumente = {v['name'] for m in module.values() for v in m['vorlagen']}
for p in pfade:
    if p.split('.')[0] in ('meta', 'person', 'werkzeuge') and p not in zu:
        F(f'Zuordnung: Profilfeld {p} ohne Ziel')
for p, ziele in zu.items():
    if p not in pfade:
        F(f'Zuordnung: {p} ist kein Profilfeld')
    for z in ziele or []:
        if schluessel(f'Zuordnung {p}', z, {'dokument', 'abschnitt'}, ('dokument', 'abschnitt')) and z['dokument'] not in dokumente:
            F(f'Zuordnung {p}: Dokument {z["dokument"]!r} legt kein Modul an')

# ---------------------------------------------------------------- Stufe 2: Bedingungen und Sperren (Trockenlauf 4)
def feldtags(pfad):
    return set((pfade.get(pfad) or {}).get('tags', []))
optionen_je_pfad = {}
for q in fragen.values():
    optionen_je_pfad.setdefault(q.get('profil_pfad'), set()).update(q.get('optionen', []))
for q in fr2.get('fragen', []):
    ort = f'Fragen_Stufe2:{q.get("id")}'
    if 'spaeter' in q and not isinstance(q['spaeter'], bool):
        F(f'{ort}: spaeter muss true oder false sein')
    fehlt = feldtags(q.get('profil_pfad')) - set(q.get('tags', []))
    if fehlt:
        F(f'{ort}: Sperrverletzung, das Feld {q.get("profil_pfad")} trägt {sorted(fehlt)}, die Frage nicht')
    w = q.get('wenn')
    if w is None:
        continue
    if not schluessel(f'{ort}: wenn', w, {'modul_aktiv', 'antwort', 'antwort_profil'}) or not w:
        F(f'{ort}: wenn leer oder kein Mapping'); continue
    for x in w.get('modul_aktiv', []):
        if x not in module:
            F(f'{ort}: wenn.modul_aktiv {x!r} unbekannt')
    for fid, opts in (w.get('antwort') or {}).items():
        if fid not in fragen:
            F(f'{ort}: wenn.antwort verweist auf unbekannte Frage {fid!r}'); continue
        for o in opts if isinstance(opts, list) else [opts]:
            if o not in fragen[fid].get('optionen', []):
                F(f'{ort}: wenn.antwort {o!r} ist keine Option von {fid}')
    for pf, wert in (w.get('antwort_profil') or {}).items():
        if pf not in pfade:
            F(f'{ort}: wenn.antwort_profil {pf!r} ist kein Feld')
        elif wert not in optionen_je_pfad.get(pf, set()):
            F(f'{ort}: wenn.antwort_profil {wert!r} ist keine Option einer Frage zu {pf}')

# ---------------------------------------------------------------- Budget und Personas
bud = lade('Budget.yaml') or {}
schluessel('Budget', bud, {'version', 'status', 'stufe1', 'einrichtung', 'stufe2'}, ('stufe1', 'einrichtung'))
if 'stufe2' in bud:
    schluessel('Budget stufe2', bud['stufe2'], {'max_fragen_je_sitzung', 'max_fragen_je_modul', 'ein_modul_je_sitzung'},
               ('max_fragen_je_sitzung', 'max_fragen_je_modul'))
PERS_K = {'id', 'fiktiv', 'autor', 'kurz', 'testet', 'antworten', 'erwartung', 'erwartung_nutzer', 'anmerkungen',
          'sprache', 'geraet', 'zeit_minuten', 'digital', 'ablauf', 'nachruesten', 'freie_zuordnung'}
SPR_P = fr1.get('sprache', 'de')
for p in sorted(glob.glob(os.path.join(spec, 'personas', 'persona_*.yaml'))):
    rel = os.path.relpath(p, spec)
    d = lade(rel)
    if schluessel(rel, d, PERS_K, ('id', 'fiktiv', 'antworten', 'erwartung')) and d['fiktiv'] is not True:
        F(f'{rel}: fiktiv muss true sein (nur erfundene Personas)')
    if isinstance(d, dict) and d.get('sprache', 'de') != SPR_P:
        F(f'{rel}: Persona in Sprache {d.get("sprache", "de")!r} liegt im Paket {SPR_P!r}')
    for qid in (d or {}).get('freie_zuordnung') or {}:
        if qid not in fragen:
            F(f'{rel}: freie_zuordnung für unbekannte Frage {qid!r}')

# ---------------------------------------------------------------- Feldkarte: Modultabelle aus den Moduldateien
SPR = (lade('Fragen_Stufe1.yaml') or {}).get('sprache', 'de')
LBL = {
    'de': {'immer': 'immer', 'enthaelt': 'enthält', 'q': ('„', '“'), 'modul': 'Modul `{x}` aktiv', 'oder': ' oder ',
           'kopf': '| ID | Modul | Aktiviert durch (Stufe 1) | Skills | Kanal Detail | Drive-Vorlagen |',
           'nachr': 'nachrüstbar', 'eigen': 'eigener Bereich', 'eigen_wenn': 'Folgefrage `s1.felder.eigen` oder später im Chat', 'kanal': {}},
    'en': {'immer': 'always', 'enthaelt': 'contains', 'q': ('“', '”'), 'modul': 'module `{x}` active', 'oder': ' or ',
           'kopf': '| ID | Module | Activated by (stage 1) | Skills | Detail channel | Drive templates |',
           'nachr': 'optional add-on', 'eigen': 'own area', 'eigen_wenn': 'follow-up question `s1.felder.eigen` or later in the chat', 'kanal': {'formular': 'form'}},
}[SPR]

def bedingung(m):
    a = m['aktivierung']
    if a.get('immer'):
        return LBL['immer']
    q0, q1 = LBL['q']
    teile = [f'`{r["frage"].split(".")[-1]}` {LBL["enthaelt"]} {q0}{r["option"]}{q1}' for r in a.get('wenn_antwort', [])]
    teile += [LBL['modul'].format(x=x) for x in a.get('wenn_modul', [])]
    return LBL['oder'].join(teile)

zeilen = [LBL['kopf'], '|---|---|---|---|---|---|']
reihe = ['person', 'werkzeuge', 'arbeit', 'entscheidungen', 'familie', 'wissen', 'termine', 'lernen', 'schreibstil']
for mid in reihe + sorted(set(module) - set(reihe) - {'kern'}):
    if mid not in module:
        F(f'Modul {mid} fehlt in spec/module/'); continue
    m = module[mid]
    sk = ', '.join(f'`{s}`' for s in m['skills']) or '–'
    zus = ', '.join(f'`{s}`' for s in m.get('skills_nachruestbar') or [])
    if zus:
        sk = (sk + ', ' if sk != '–' else '') + zus + ' (' + LBL['nachr'] + ')'
    vl = ', '.join(v['name'] for v in m['vorlagen']) or '–'
    zeilen.append(f'| `{mid}` | {m["name"]} | {bedingung(m)} | {sk} | {LBL['kanal'].get(m.get('kanal_detail', 'chat'), m.get('kanal_detail', 'chat'))} | {vl} |')
zeilen.append(f'| `eigen:<name>` | {LBL["eigen"]} | {LBL["eigen_wenn"]} | – | chat | State_<name> |')
block = '<!-- module:start -->\n' + '\n'.join(zeilen) + '\n<!-- module:end -->'
fk = os.path.join(spec, 'Feldkarte.md')
t = open(fk, encoding='utf-8').read()
alt = re.search(r'<!-- module:start -->.*?<!-- module:end -->', t, re.S)
if not alt:
    F('Feldkarte.md: Marker module:start/module:end fehlen')
elif SCHREIBEN:
    open(fk, 'w', encoding='utf-8').write(t[:alt.start()] + block + t[alt.end():])
    print('Feldkarte.md: Modultabelle neu geschrieben')
elif alt.group(0) != block:
    F('Feldkarte.md: Modultabelle weicht von spec/module/ ab (neu erzeugen mit --feldkarte)')

# ---------------------------------------------------------------- Ergebnis
print(f'Module: {len(module)}, Fragen (inkl. Folgefragen): {len(fragen)}, Profilfelder: {len(pfade)}, Skills: {len(alle_skills)}, nachrüstbar: {len(nachruestbar)}')
if fehler:
    print(f'FEHLER: {len(fehler)}')
    for f in fehler:
        print(' -', f)
    sys.exit(1)
print('Spec sauber')

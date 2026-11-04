#!/usr/bin/env python3
"""Trockenlauf: Personas gegen die Spec. Aufruf:
    python3 -I personas_gegen_spec.py <spec-ordner> [<persona-ordner> ...]
Ohne Persona-Ordner: <spec-ordner>/personas. Es zählen nur Personas mit der Sprache der Spec
(Feld `sprache` der Persona, Vorgabe de; Spec-Sprache aus Fragen_Stufe1.yaml).
Version 4 (03.11.2026): beide Sprachpakete; Regeln für Ausweichen aus Fragen_Stufe1.yaml (`regeln`),
Standardwerte für nicht gestellte Fragen (`standardwerte`), Stufe 2 (Fragen je Modul, Sperren, Obergrenzen je
Sitzung und je Modul aus Budget.yaml `stufe2`), Nachrüsten (`nachruesten` in der Persona), Sperrverletzung.
Liest nur, schreibt nichts. Befund = Lücke in der Spec oder Budget überschritten. Info = Regel greift.
Exit 0 immer (Trockenlauf, keine Prüfung); Befunde stehen in der Ausgabe."""
import sys, glob, os, math, yaml

spec = sys.argv[1]
ordner = sys.argv[2:] or [os.path.join(spec, 'personas')]
L = lambda rel: yaml.safe_load(open(os.path.join(spec, rel), encoding='utf-8'))
fr1, sc, budget = L('Fragen_Stufe1.yaml'), L('Profilschema.yaml'), L('Budget.yaml')
fr2 = L('Fragen_Stufe2.yaml') if os.path.exists(os.path.join(spec, 'Fragen_Stufe2.yaml')) else {}
SPRACHE = fr1.get('sprache', 'de')
module = {m['id']: m for m in (L(os.path.relpath(p, spec)) for p in glob.glob(os.path.join(spec, 'module', '*.yaml')))}
fragen = {q['id']: q for r in fr1['runden'] for q in r['fragen']}
folge = {ff['id']: (qid, ff) for qid, q in fragen.items() for ff in q.get('folgefragen', [])}
ANGEBOTEN = list(fr1.get('immer_angeboten', []))
AUSWEICH = set(ANGEBOTEN[1:])          # erstes Element ist "freie Antwort"
REGELN = fr1.get('regeln') or {}       # leer = keine Regel entschieden
STANDARD = fr1.get('standardwerte') or {}
ABGELEITET = {'meta.module_aktiv', 'meta.paket_version', 'meta.profil_version', 'werkzeuge.ordner_id', 'werkzeuge.ordnername'}
EIGEN_OPT = next((ff['wenn_enthaelt'] for fid, (qid, ff) in folge.items() if qid == 's1.felder' and 'wenn_enthaelt' in ff), None)
EIGEN_FID = next((fid for fid, (qid, ff) in folge.items() if qid == 's1.felder' and 'wenn_enthaelt' in ff), None)
B2 = budget.get('stufe2') or {}

def pfade(d, p=''):
    for k, v in d.items():
        if isinstance(v, dict) and 'typ' in v:
            yield p + k, v
        elif isinstance(v, dict):
            yield from pfade(v, p + k + '.')
schema = {p: v for k in ('meta', 'person', 'werkzeuge') for p, v in pfade({k: sc[k]})}
pflicht = {p for p, v in schema.items() if v.get('pflicht')}
fragen2 = list(fr2.get('fragen', [])) + [dict(q, modul=q.get('modul', mid)) for mid, m in module.items() for q in (m.get('fragen') or [])]
s2_pflicht = {q['profil_pfad'] for q in fragen2 if q.get('pflicht')}
liste = lambda a: a if isinstance(a, list) else ([] if a is None else [a])
namen_module = {mid: m['name'].lower() for mid, m in module.items()}

def feld(pfad):
    """Profilfeld zu einem Pfad (Schema oder Modulfeld)."""
    if pfad in schema:
        return schema[pfad]
    mid, _, name = pfad.partition('.')
    return ((module.get(mid) or {}).get('profilfelder') or {}).get(name, {})

def aktivieren(gilt):
    aktiv = {mid for mid, m in module.items() if m['aktivierung'].get('immer')}
    while True:
        neu = set(aktiv)
        for mid, m in module.items():
            akt = m['aktivierung']
            if any(r['option'] in gilt.get(r['frage'], []) for r in akt.get('wenn_antwort', [])) or \
               any(x in aktiv for x in akt.get('wenn_modul', [])):
                neu.add(mid)
        if neu == aktiv:
            return aktiv
        aktiv = neu

personas = sorted(p for o in ordner for p in glob.glob(os.path.join(o, 'persona_*.yaml')))
gezaehlt = 0
for datei in personas:
    P = yaml.safe_load(open(datei, encoding='utf-8'))
    if P.get('sprache', 'de') != SPRACHE:
        continue
    gezaehlt += 1
    A = P['antworten']
    zuord = P.get('freie_zuordnung') or {}
    befunde, infos, erfragt = [], [], set()
    print('=' * 70)
    print(P['id'], f"(Autor: {P.get('autor', 'claude')}, Gerät: {P.get('geraet', '?')}, Zeit: {P.get('zeit_minuten', '?')})")

    # 0. Antworten auf Fragen, die diese Spec nicht stellt
    for qid in A:
        if qid not in fragen and qid not in folge:
            infos.append(f'{qid}: Antwort ohne Frage in dieser Spec (entfällt oder Standardwert)')

    # 1. Antworten einordnen: Option / Ausweichen / freie Antwort
    gilt = {}
    for qid, q in fragen.items():
        a = liste(A.get(qid))
        opt = [w for w in a if w in q['optionen']]
        aus = [w for w in a if w in AUSWEICH]
        frei = [w for w in a if w not in q['optionen'] and w not in AUSWEICH]
        for w in frei:
            if REGELN.get('freie_antwort') and qid in zuord:
                infos.append(f'{qid}: freie Antwort → Vorschlag {zuord[qid]} und Bestätigung (Regel freie_antwort)')
            elif REGELN.get('freie_antwort'):
                befunde.append(f'{qid}: freie Antwort {w[:60]!r} – Regel greift, aber die Persona nennt keine Zuordnung (freie_zuordnung)')
            else:
                befunde.append(f'{qid}: freie Antwort {w[:60]!r} – keine Regel, wie sie ausgewertet wird (Module, Profil)')
        if frei and REGELN.get('freie_antwort') and qid in zuord:
            opt = [o for o in liste(zuord[qid]) if o in q['optionen']] + opt
            for o in liste(zuord[qid]):
                if o not in q['optionen'] and o not in AUSWEICH:
                    befunde.append(f'{qid}: Zuordnung {o!r} ist keine Option')
        gilt[qid] = opt
        if opt:
            erfragt.add(q['profil_pfad'])
        if not a:
            befunde.append(f'{qid}: keine Antwort in der Persona')
        if aus and opt:
            if REGELN.get('ausweichen_mit_optionen'):
                infos.append(f'{qid}: „{aus[0]}“ zusammen mit Optionen → Optionen zählen (Regel ausweichen_mit_optionen)')
            else:
                befunde.append(f'{qid}: „{aus[0]}“ zusammen mit Optionen – keine Regel, was gilt')
        if aus and not opt:
            if q.get('empfehlung') and REGELN.get('ausweichen_mit_empfehlung'):
                emp = next(o for o in q['optionen'] if o.startswith(q['empfehlung']))
                gilt[qid] = [emp]
                erfragt.add(q['profil_pfad'])
                infos.append(f'{qid}: „{aus[0]}“ → Empfehlung „{q["empfehlung"]}“ als Vorgabe, gesagt (Regel ausweichen_mit_empfehlung)')
            elif q.get('pflicht') and REGELN.get('pflicht_ausgewichen'):
                infos.append(f'{qid}: Pflichtfrage „{aus[0]}“ → einmal nachfragen, dann „offen“ in 02_Offene_Fragen (Regel pflicht_ausgewichen)')
                erfragt.add(q['profil_pfad'] + '#offen')
            elif q.get('pflicht'):
                befunde.append(f'{qid}: Pflichtfrage mit „{aus[0]}“ – keine Regel (Nachfrage? Vorgabe? offene Frage?)')
            elif q.get('empfehlung'):
                infos.append(f'{qid}: „{aus[0]}“ – Empfehlung „{q["empfehlung"]}“ könnte greifen; Regel fehlt noch, ob und mit Hinweis')
        for o in q.get('vorbelegt', []):
            if o not in gilt[qid]:
                gilt[qid] = gilt[qid] + [o]
            erfragt.add(q['profil_pfad'])   # vorbelegte Werte gelten auch bei Ausweichen (Trockenlauf 4)

    # 2. Folgefragen
    for fid, (qid, ff) in folge.items():
        a = gilt[qid]
        ausgeloest = (ff['wenn_enthaelt'] in a) if 'wenn_enthaelt' in ff else (bool(a) and ff['wenn_nicht'] not in a)
        wert = A.get(fid)
        if ausgeloest and (wert is None or wert in AUSWEICH):
            if ff.get('pflicht'):
                befunde.append(f'Folgefrage {fid} ausgelöst, Persona liefert keinen Wert')
            else:
                infos.append(f'Folgefrage {fid} ausgelöst, ausgewichen (freiwillig)')
        elif not ausgeloest and wert not in (None,) and wert not in AUSWEICH:
            befunde.append(f'Folgefrage {fid} nicht ausgelöst, Persona liefert trotzdem einen Wert')
        elif ausgeloest:
            erfragt.add(ff['profil_pfad'])
            infos.append(f'Folgefrage {fid} gestellt (zählt nicht mit)')

    # 3. Standardwerte für nicht gestellte Fragen
    for pfad, wert in STANDARD.items():
        if pfad not in erfragt:
            erfragt.add(pfad)
            infos.append(f'Standardwert {pfad} = {wert!r} (Herkunft abgeleitet, in Stufe 2 änderbar)')

    # 4. Module (bis zum Fixpunkt wegen wenn_modul)
    aktiv = aktivieren(gilt)
    eigene = []
    if EIGEN_OPT and EIGEN_OPT in gilt.get('s1.felder', []):
        roh = str((zuord.get(EIGEN_FID) if REGELN.get('freie_antwort') and EIGEN_FID in zuord else None)
                  or A.get(EIGEN_FID) or '').strip()
        teile = [t.strip() for t in roh.replace(',', ';').split(';') if t.strip()] if ';' in roh else ([roh] if roh else [])
        if len(teile) > 1:
            if REGELN.get('mehrere_eigene'):
                infos.append(f'{len(teile)} eigene Bereiche in einer Antwort → je ein Bereich, Bestätigung (Regel mehrere_eigene)')
            else:
                befunde.append(f'{len(teile)} eigene Bereiche in einer Antwort („{roh}“) – keine Regel')
        for e in teile:
            el = e.lower()
            treffer = [mid for mid, n in namen_module.items() if el == mid or el == n or el in n.replace(',', ' ').split()]
            if treffer:
                if REGELN.get('eigen_dublette'):
                    infos.append(f'eigener Bereich „{e}“ heißt wie Modul {treffer} → zusammenlegen oder umbenennen anbieten (Regel eigen_dublette)')
                    aktiv |= set(treffer)
                    continue
                befunde.append(f'eigener Bereich „{e}“ heißt wie Modul {treffer} – keine Regel (zusammenlegen? umbenennen?)')
            eigene.append('eigen:' + el)
    aktiv |= set(eigene)
    aktiv_ohne_kern = sorted(aktiv - {'kern'})

    # 5. Vergleich mit der Erwartung (aus der Persona, nicht aus der Spec)
    soll = set((P.get('erwartung') or {}).get('module_aktiv') or [])
    if soll and set(aktiv_ohne_kern) != soll:
        befunde.append(f'Module weichen von der Erwartung ab: zusätzlich {sorted(set(aktiv_ohne_kern) - soll)}, fehlend {sorted(soll - set(aktiv_ohne_kern))}')
    skills = [s for mid in sorted(aktiv) if mid in module for s in module[mid]['skills']]
    nachruestbar = [s for mid in sorted(aktiv) if mid in module for s in (module[mid].get('skills_nachruestbar') or [])]
    spaet_skills = []
    if P.get('nachruesten'):
        g3 = {k: list(v) for k, v in gilt.items()}
        for qid, extra in P['nachruesten'].items():
            g3[qid] = g3.get(qid, []) + [o for o in liste(extra) if o in fragen.get(qid, {}).get('optionen', [])]
        spaet_skills = [s for mid in sorted(aktivieren(g3) - aktiv) if mid in module for s in module[mid]['skills']]
    for s in (P.get('erwartung_nutzer') or {}).get('skills', []):
        if s not in skills and s not in nachruestbar and s not in spaet_skills:
            befunde.append(f'Skill {s} erwartet, aber nicht aktiv')

    # 6. Pflichtfelder
    for p in sorted(pflicht):
        if p in erfragt or p + '#offen' in erfragt or p in ABGELEITET:
            continue
        if p in s2_pflicht:
            infos.append(f'Pflichtfeld {p} kommt als Frage in Stufe 2')
        elif schema.get(p, {}).get('fest'):
            infos.append(f'Pflichtfeld {p} fest aus dem Sprachpaket ({schema[p]["fest"]})')
        else:
            befunde.append(f'Pflichtfeld {p} bleibt offen (in Stufe 1 ausgewichen, keine Nachfrage-Regel)')

    # 7. Hinweise
    for qid, q in fragen.items():
        for o, text in (q.get('hinweis_bei') or {}).items():
            if o in gilt[qid]:
                infos.append('Hinweis: ' + text)
        for o, text in (q.get('hinweis_wenn_nur') or {}).items():
            if gilt[qid] == [o]:
                infos.append('Hinweis: ' + text)

    # 8. Grenzen (Sensibel-Tags) gegen Modulfelder
    g = fragen.get('s1.grenzen', {})
    gesperrt = {g.get('sperrt_tags', {}).get(x) for x in gilt.get('s1.grenzen', [])} - {None}
    for mid in sorted(aktiv & set(module)):
        felder = module[mid]['profilfelder'] or {}
        weg = [f for f, v in felder.items() if gesperrt & set(v.get('tags', []))]
        if weg:
            infos.append(f'Grenze unterdrückt in {mid}: {", ".join(weg)} (Vermerk in 00_Status)')
            if len(weg) * 2 >= len(felder):
                if REGELN.get('grenzen_halbes_modul'):
                    infos.append(f'Modul {mid}: Grenzen sperren {len(weg)} von {len(felder)} Feldern → sagen und fragen, ob anlegen (Regel grenzen_halbes_modul)')
                else:
                    befunde.append(f'Modul {mid}: Grenzen sperren {len(weg)} von {len(felder)} Feldern – keine Regel, ob das Modul dann noch sinnvoll ist')

    # 9. Stufe 2: Fragen der aktiven Module ohne gesperrte Tags, Obergrenzen, Sperrverletzung
    s2 = [q for q in fragen2 if q.get('modul') in aktiv]
    gestellt, weggelassen = [], []
    for q in s2:
        tags = set(q.get('tags', [])) | set(feld(q['profil_pfad']).get('tags', []))
        bed = q.get('wenn') or {}
        if bed.get('modul_aktiv') and not set(liste(bed['modul_aktiv'])) & aktiv:
            continue
        if bed.get('antwort') and not any(o in gilt.get(r, []) for r, os_ in bed['antwort'].items() for o in liste(os_)):
            continue
        if tags & gesperrt:
            weggelassen.append(q['id'])
            if not set(q.get('tags', [])) & gesperrt:
                befunde.append(f'Sperrverletzung: {q["id"]} fragt ein gesperrtes Feld, trägt aber das Tag nicht selbst')
            continue
        gestellt.append(q)
    spaeter = [q for q in gestellt if q.get('spaeter')]
    gestellt = [q for q in gestellt if not q.get('spaeter')]
    je_modul = {}
    for q in gestellt:
        je_modul.setdefault(q['modul'], []).append(q)
    max_s, max_m = B2.get('max_fragen_je_sitzung'), B2.get('max_fragen_je_modul')
    sitzungen, ueber = 0, []
    for mid, qs in je_modul.items():
        if max_m and len(qs) > max_m:
            ueber.append(f'{mid} {len(qs)}>{max_m}')
        if max_s:
            sitzungen += math.ceil(min(len(qs), max_m or len(qs)) / max_s) if B2.get('ein_modul_je_sitzung') else 0
    if max_s and not B2.get('ein_modul_je_sitzung'):
        sitzungen = math.ceil(sum(min(len(qs), max_m or len(qs)) for qs in je_modul.values()) / max_s)
    for x in ueber:
        befunde.append(f'Stufe 2: Modul {x} Fragen (Obergrenze je Modul)')
    module_ohne_s2 = sorted(m for m in aktiv_ohne_kern if m in module and m not in je_modul and m not in ('werkzeuge',))
    s2_text = f'Stufe 2 {len(gestellt)} Fragen' + (f' in ~{sitzungen} Sitzungen' if max_s else '') + (f', {len(spaeter)} später' if spaeter else '') + (f', {len(weggelassen)} gesperrt' if weggelassen else '')
    if weggelassen:
        infos.append('Stufe 2 weggelassen (Sperre): ' + ', '.join(weggelassen))
    if fragen2 and len(fragen2) > 1 and module_ohne_s2:
        infos.append('Stufe 2 ohne Fragen: ' + ', '.join(module_ohne_s2))

    # 10. Budget (Schätzung mit den Annahmen aus Budget.yaml)
    b1, be = budget['stufe1'], budget['einrichtung']
    folgen = [fid for fid in folge if fid in A and A[fid] not in AUSWEICH]
    sek = sum(b1['sekunden_je_typ'][q['typ']] for q in fragen.values()) + sum(b1['sekunden_je_typ'][folge[f][1]['typ']] for f in folgen)
    uploads = len(skills)
    drive = 1 + sum(len(module[mid]['vorlagen'] or []) for mid in aktiv if mid in module) + sum(1 for mid in aktiv if mid.startswith('eigen:'))
    minuten = be['grundaufwand_minuten'] + uploads * be['minuten_je_upload'] + drive * be['sekunden_je_drive_aktion'] / 60
    print(f'Module: {aktiv_ohne_kern}')
    print(f'Budget: Stufe 1 {len(fragen)}+{len(folgen)} Fragen, ~{sek/60:.1f} min | Einrichtung {uploads} Skill-Uploads, '
          f'{drive} Drive-Aktionen, ~{minuten:.0f} min | {s2_text}')
    if len(fragen) > b1['max_fragen'] or len(folgen) > b1['max_folgefragen'] or sek / 60 > b1['max_minuten']:
        befunde.append('Budget Stufe 1 überschritten')
    if uploads > be['max_skill_uploads']:
        befunde.append(f'Budget: {uploads} Skill-Uploads > {be["max_skill_uploads"]}')
    if drive > be['max_drive_aktionen']:
        befunde.append(f'Budget: {drive} Drive-Aktionen > {be["max_drive_aktionen"]}')
    if minuten > be['max_minuten']:
        befunde.append(f'Budget: Einrichtung ~{minuten:.0f} min > {be["max_minuten"]} min')
    zm = P.get('zeit_minuten')
    if isinstance(zm, (int, float)) and sek / 60 > zm:
        befunde.append(f'Stufe 1 (~{sek/60:.1f} min) länger als die Zeit der Persona ({zm} min)')

    # 11. Nachrüsten in einer späteren Sitzung
    if P.get('nachruesten'):
        g2 = {k: list(v) for k, v in gilt.items()}
        for qid, extra in P['nachruesten'].items():
            g2[qid] = g2.get(qid, []) + [o for o in liste(extra) if o in fragen.get(qid, {}).get('optionen', [])]
        neu = aktivieren(g2) | set(eigene)
        dazu = sorted(neu - aktiv)
        s_neu = [s for mid in dazu if mid in module for s in module[mid]['skills']]
        skills_nachher = skills + s_neu
        d_neu = sum(len(module[mid]['vorlagen'] or []) for mid in dazu if mid in module)
        print(f'Nachrüsten: +{dazu}, +{len(s_neu)} Skill-Uploads, +{d_neu} Drive-Aktionen')
        soll2 = set((P.get('erwartung') or {}).get('module_nachher') or [])
        if soll2 and set(neu - {'kern'}) != soll2:
            befunde.append(f'Nachrüsten weicht ab: {sorted(neu - {"kern"})} statt {sorted(soll2)}')
        if len(skills) + len(s_neu) > be['max_skill_uploads']:
            befunde.append(f'Budget nach Nachrüsten: {len(skills) + len(s_neu)} Skill-Uploads > {be["max_skill_uploads"]}')

    print(f'Befunde: {len(befunde)}' if befunde else 'Keine Befunde')
    for x in befunde:
        print(' -', x)
    for x in infos:
        print(' *', x)

print('=' * 70)
print(f'Personas ({SPRACHE}): {gezaehlt}')

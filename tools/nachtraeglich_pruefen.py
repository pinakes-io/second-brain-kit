#!/usr/bin/env python3
"""Simuliert das nachträgliche Dazunehmen von Bereichen (Skill area-manager) für jede Persona. Entwurf 03.11.2026.
Aufruf: python3 -I tools/nachtraeglich_pruefen.py <spec-ordner>      z. B. spec
Für jede Persona und jeden noch nicht aktiven Bereich wird gerechnet:
  - Skills: Zahl der Skills des Kerns plus der aktiven Bereiche plus des neuen Bereichs (ohne Obergrenze, Entscheid 11.11.)
  - Folgeangebote: Bereiche, deren Aktivierung wenn_modul auf den neuen Bereich zeigt
  - Sperren: Anteil der Profilfelder des neuen Bereichs, den die Grenzen der Persona sperren
  - Dokumente, die neu angelegt würden
Fehlt bei einer Persona erwartung.module_aktiv, werden die aktiven Bereiche aus den Antworten nach den Aktivierungsregeln
der Bereichsdateien abgeleitet (gekennzeichnet). Hat sie den Eintrag, wird die Ableitung dagegen geprüft; eine Abweichung
ist ein Fehler (Exit 1).
Das ist eine Rechnung gegen die Spec, kein Lauf in claude.ai."""
import sys, os, glob
import yaml

spec = sys.argv[1]
L = lambda rel: yaml.safe_load(open(os.path.join(spec, rel), encoding='utf-8'))
module = {os.path.basename(p)[:-5]: yaml.safe_load(open(p, encoding='utf-8')) for p in glob.glob(os.path.join(spec, 'module', '*.yaml'))}
fragen = L('Fragen_Stufe1.yaml')
sperr = {}
for r in fragen['runden']:
    for q in r['fragen']:
        if q['id'] == 's1.grenzen':
            sperr = q.get('sperrt_tags', {})
kern_skills = len(module['kern']['skills'])
immer = {m for m, d in module.items() if d['aktivierung'].get('immer')}


def aktivieren(antworten):
    """Aktive Bereiche aus den Rohantworten, bis zum Fixpunkt wegen wenn_modul."""
    gilt = {k: (v if isinstance(v, list) else [v]) for k, v in (antworten or {}).items() if v is not None}
    aktiv = set(immer)
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


fehler = []

gesamt = 0
for p in sorted(glob.glob(os.path.join(spec, 'personas', 'persona_*.yaml'))):
    d = yaml.safe_load(open(p, encoding='utf-8'))
    abgeleitet = aktivieren(d.get('antworten')) - {'kern'}
    erw = (d.get('erwartung') or {}).get('module_aktiv')
    if erw is None:
        aktiv, quelle = abgeleitet, ' (abgeleitet)'
    else:
        aktiv, quelle = {m for m in erw if not m.startswith('eigen:')} - {'kern'}, ''
        if abgeleitet != aktiv:
            fehler.append(f"{d['id']}: Ableitung {sorted(abgeleitet)} weicht von erwartung {sorted(aktiv)} ab")
    gesperrt = {sperr.get(g) for g in d['antworten'].get('s1.grenzen', [])} - {None}
    skills = kern_skills + sum(len(module[m]['skills']) for m in aktiv if m in module and m != 'kern')
    print(f"{d['id']}: aktiv{quelle} {sorted(aktiv - immer)}, Skills {skills}")
    for mid in sorted(set(module) - aktiv - immer - {'kern'}):
        m = module[mid]
        neu = len(m['skills'])
        zeilen = []
        zeilen.append(f'Skills danach: {skills + neu}')
        folge = [x for x, dx in module.items() if mid in dx['aktivierung'].get('wenn_modul', []) and x not in aktiv]
        if folge:
            zeilen.append(f'Folgeangebot: {", ".join(folge)}')
        felder = m.get('profilfelder') or {}
        weg = [f for f, v in felder.items() if gesperrt & set(v.get('tags', []))]
        if felder and len(weg) * 2 >= len(felder):
            zeilen.append(f'Sperre: {len(weg)} von {len(felder)} Feldern gesperrt')
        docs = len(m['vorlagen'])
        print(f"  + {mid}: {docs} neue Dokumente, {neu} Skills" + (' · ' + ' · '.join(zeilen) if zeilen else ''))
        gesamt += len(zeilen)
print(f'{gesamt} Hinweise (Rechnung gegen die Spec, kein Lauf in claude.ai)')
if fehler:
    print(f'FEHLER: {len(fehler)}')
    for x in fehler:
        print(' -', x)
    sys.exit(1)

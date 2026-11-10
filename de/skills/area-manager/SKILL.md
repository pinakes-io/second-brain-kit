---
name: area-manager
description: Nimmt Bereiche (Module) im laufenden Betrieb dazu, pausiert sie oder aktualisiert ihre Regeln. Verwenden, wenn die Person „neuer Bereich“, „Bereich dazunehmen“, „Bereich pausieren“, „Regeln aktualisieren“ oder „ich will auch … nutzen“ schreibt. Ändert nur additiv und nach einem Ja und löscht nie.
---

# Bereiche verwalten (Entwurf 0.1)

## Ziel
Das Second Brain wächst mit mir: neue Bereiche kommen dazu, ungenutzte ruhen, Regeln werden besser. Jede Änderung ist additiv, steht nach einem Ja, lässt sich wiederholen und wird vermerkt. Du löschst nie.

## Vorbereitung (still)
Lies `00_Status` (Versionsstempel, Feldkarte mit Status und Version, Grenzen, Bereichsregeln) und liste den Ordner „Second Brain“. Fehlt `00_Status`, sage es und biete setup-brain an. Ohne Schreibrecht gibst du jede Änderung als Block aus: „Füge in Dokument X unter Abschnitt Y ein: …“.

## A. Bereich dazunehmen
1. **Klären:** Welcher Bereich? Zeige aus dem Verzeichnis unten die Bereiche, die noch nicht aktiv sind, dazu „eigener Bereich (bitte benennen)“. Frage genau einmal.
2. **Prüfen:** (a) Grenzen: Felder und Fragen mit gesperrtem Tag lässt du weg und vermerkst sie unter „Unterdrückte Felder“. (b) Upload-Budget: Zähle die Skills in deiner eigenen Skill-Liste (sonst frage); mehr als 12 geht nicht, sage dann, was eine Pause bringt. (c) Folgeangebote aus der Spalte Hinweis, zum Beispiel entscheidungen bei arbeit.
3. **Plan zeigen:** Dokumente, die angelegt werden, Baustein, Skills, die ich noch laden muss. Frage genau einmal: „So dazunehmen? (ja / ändern)“.
4. **Anlegen:** Rufe nach dem Ja setup-brain auf (es legt nur an, was fehlt, und ergänzt den Baustein). Trage danach in `00_Status` ein: Zeile in der Feldkarte (Status aktiv, Version, warum „später dazugenommen am <Datum>“), Ablage-Karte, aktive Module, Profilversion plus 1. Schreibe einen Eintrag in `Journal`.
5. **Skills:** Nenne die noch fehlenden ZIPs eines nach dem anderen und halte nach jedem an: „Stopp: sag Bescheid, wenn es geladen ist.“
6. **Fragen:** Offene Pflichtfelder des Bereichs kommen als Zeilen in `02_Offene_Fragen` (Abschnitt = Bereich). Biete höchstens drei Fragen jetzt an, den Rest später.
Eigener Bereich: nur `State_<Name>`, eine Zeile in Ablage-Karte und Feldkarte und der Baustein „Eigene Bereiche“. Ähnelt der Name einem Bereich im Verzeichnis, frage, ob stattdessen dieser passt.

## B. Bereich pausieren oder wieder zuschalten
1. **Pausieren:** Setze in der Feldkarte den Status „pausiert“ mit Datum und ergänze am Baustein in `00_Status` den Vermerk „(pausiert seit <Datum>, nicht befolgen)“. Dokumente und Skills bleiben. Sage, dass ich die Skills in den Einstellungen ausschalten kann, wenn ich Platz im Budget brauche.
2. **Archiv:** Nur wenn ich es wünsche, schlage vor, die Dokumente des Bereichs ins `Archiv` zu verschieben, je Datei einzeln, nach meinem Ja, mit Rücklesen.
3. **Wieder zuschalten:** Status „aktiv“, Vermerk entfernen, Eintrag in `Journal`. Ist die Version des Bausteins älter als die im Verzeichnis, biete C an.

## C. Regeln aktualisieren
1. Vergleiche je aktivem oder pausiertem Bereich die Version in der Feldkarte mit der Version im Verzeichnis.
2. Weicht sie ab, zeige den Baustein aus `00_Status` und den neuen Baustein untereinander und nenne die Unterschiede in zwei, drei Zeilen. Frage je Bereich: „Übernehmen? (ja / nein / später)“.
3. Nach „ja“: ersetze den Baustein, trage die neue Version ein und frage, welche eigenen Zeilen im alten Baustein bleiben sollen. Setze sie unter den neuen Baustein mit dem Vermerk „eigene Ergänzung“. Schreibe einen Eintrag in `Journal`.
4. Nach „nein“ oder „später“ änderst du nichts und fragst in dieser Sitzung nicht erneut.

## Regeln
- Nur additiv und nach meinem Ja; eine Bestätigung je Plan, nicht je Dokument.
- Lies nach jeder Änderung zurück. Prüfzeile: `🔎 Gelesen: 00_Status ✓ · Ordner ✓ · 📝 Abgelegt: 00_Status, Journal, <neue Dokumente>`. Fehlt ein Schritt, schreibe ✗ und den Grund.
- Keine Ausweis-, Konto-, Steuer- oder Versicherungsnummern.
- Sage ich „überspringen“ oder „nur ansehen“, ändere nichts.
- Dieser Skill ist optional. Ohne ihn legt setup-brain die Bereiche beim ersten Aufbau an.

## Verzeichnis der Bereiche
| Bereich | Version | Dokumente | Skills | Hinweis |
|---|---|---|---|---|
| person | 0.1 | – | keine | immer aktiv |
| werkzeuge | 0.1 | – | keine | immer aktiv |
| arbeit | 0.1 | State_Arbeit | keine | nachrüstbar: transcript-minutes; bei arbeit auch entscheidungen anbieten |
| entscheidungen | 0.1 | Entscheidungen | decision-clarify, decision-check | wird bei arbeit mit angeboten |
| familie | 0.1 | State_Familie | keine | – |
| wissen | 0.1 | Knowledge, 00_Knowledge_Index | knowledge-note | – |
| termine | 0.1 | State_Termine, Briefe_Scans | appointment-prep, letter-explain | – |
| lernen | 0.1 | State_Lernen, Lernprotokoll | keine | Kandidat für ein eigenes Projekt |
| schreibstil | 0.2 | Stilprofil | plain-prose-de, plain-prose-en | – |
| bauen | 0.1 | Bauprojekte | build-router, vibe-pack | Ablauf-Skill (n8n) nachrüstbar |
| eigen:<Name> | – | State_<Name> | keine | der Baustein „Eigene Bereiche“ |

## Bausteine
Schreibe den Baustein wörtlich in den Abschnitt „Bereichsregeln“ von `00_Status`, die Überschrift „## Bereich …“ als „### Bereich …“.
```
## Bereich Person und Situation
- Mein Ton und meine Vorlieben stehen in `01_Profil`, Abschnitte „So spricht Claude mit mir“ und „Regeln“. Halte dich daran.
- Die Grenzen in `00_Status` gehen vor. Gesperrte Angaben fragst du nicht ab und speicherst du nicht.
- Änderungen am Profil erst nach meinem Ja, mit Wert, Status, Herkunft und Datum.

## Bereich Werkzeuge
- Geräte und Werkzeuge stehen in `01_Profil`, Abschnitt Technik. Du schreibst auch am Smartphone direkt in die Dokumente; Blöcke zum Einfügen gibst du nur aus, wenn Google Docs nicht verbunden ist.
- Kannst du ein Werkzeug nicht nutzen (zum Beispiel Drive nicht verbunden), sag das in einer Zeile und biete den Block-Modus an.

## Bereich Arbeit und Ziele
- Stand, Ziele und Belege stehen in `State_Arbeit`. Lies es, bevor du zu Arbeit, Beruf oder Ausbildung etwas rätst.
- Angaben zu Abschlüssen, Fristen oder Anforderungen laufen durch fact-check. Ist transcript-minutes installiert, nutze ihn für Gesprächsprotokolle.

## Bereich Entscheidungen
- Steht eine echte Entscheidung an und eine falsche Annahme wäre teuer („ich muss mich entscheiden“, „A oder B“), nutze decision-clarify. Sage ich „final“ oder „ich habe mich entschieden“, nutze decision-check, einmal.
- Anstehendes und Getroffenes stehen im Dokument Entscheidungen, mit Warum. Du trägst nur nach meinem Ja ein.
- Was von außen vorgegeben ist (Pflicht, Gesetz), erklärst du, du klärst es nicht.

## Bereich Familie und Haushalt
- Stand und Termine stehen in `State_Familie`. Sind Angaben zu Kindern gesperrt, stehen zu Kindern nur Termine (Datum, Uhrzeit, Ort) mit „Kind 1“, „Kind 2“; sind Namen gesperrt, schreibst du Rollen („Partnerin“).
- Gesperrte Felder lässt du aus und fragst sie nicht ab.

## Bereich Wissen und Quellen
- Nach einer Recherche, die ich später wieder brauche, und bei „als Wissen ablegen“ nutze knowledge-note: eine Notiz je Thema im Ordner Knowledge, vorher im 00_Knowledge_Index nachsehen.
- Zahlen, Fristen und Regeln darin laufen durch fact-check und stehen zusätzlich im Fakten-Ledger.
- Gibt es zu einem Thema schon eine Notiz, lies erst sie, dann antworte.

## Bereich Termine, Post und Ämter
- Bei einem Brief oder Bescheid nutze letter-explain, bei einem Termin oder einer Einladung appointment-prep. Ergebnis, Fristen und Belege trägst du nach dem Termin in State_Termine ein.
- Fristen ohne Termin kommen mit Quelle in State_Termine, Zahlen laufen durch fact-check. Ist Gesundheit auf „nur Termine“ gesetzt, trägst du bei Arztterminen nur Datum, Uhrzeit und „Termin“ ein, höchstens mit der Stadt.

## Bereich Lernen
- Lernstand und Fokus stehen in `State_Lernen`, Übungen im `Lernprotokoll`. Frage vor einer Übung nach Zeit und Ziel und passe die Schwierigkeit an den Stand an.
- Nach einer Einheit schlägst du eine Zeile für das `Lernprotokoll` vor (Datum, was, wie lief es) und schreibst sie nur nach meinem Ja.

## Bereich Schreibstil
- Deutsche Texte überarbeiten („überarbeiten“, „straffen“, „Klartext“) → plain-prose-de; englische → plain-prose-en. Du sprichst dabei Deutsch, nur der Text bleibt englisch.
- Stilregeln und Wörter stehen im Stilprofil. Neue Regeln legst du dort nur nach meiner Zustimmung ab.

## Bereich Bauen
- Will ich etwas bauen (App, Skript, Ablauf), startet zuerst der Skill build-router. Er leitet an vibe-pack (Code) oder, wenn installiert, an den Ablauf-Skill.
- Ist ein Skill nicht geladen, sag das in einer Zeile und stopp. Baue keinen Plan aus dem Gedächtnis.
- Der Projektstand steht im Doc Bauprojekte. Bis zur Abnahme kommen nur erfundene Beispieldaten in ein Projekt, keine echten.
- Werkzeug, Vorkenntnisse und Datenart stehen im Profil, Abschnitt Bauen.

## Eigene Bereiche
- Für einen eigenen Bereich <Name> gilt `State_<Name>`: Lies es zuerst und lege Stand, Ziele und Belege dort ab.
```

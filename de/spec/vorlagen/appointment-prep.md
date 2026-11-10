# Vorlage: appointment-prep (zu Fassung 0.7)

Diese Datei ist eine Vorlage für den Skill `skill-tailor`. Sie ist selbst kein Skill. Ohne die Markierungen `<!-- anpassen:… -->` und `<!-- /anpassen -->` ist der Text unten Zeichen für Zeichen die feste Fassung `skills/appointment-prep/SKILL.md`. Geprüft von `tools/vorlage_pruefen.py`.

**Regeln für den Zuschnitt:** Nur Text zwischen den Markierungen darf sich ändern. Alles andere bleibt wörtlich, auch Satzzeichen und Leerzeilen. Die Markierungen kommen danach heraus. Die Antworten sind Regeln für den Skill, keine Daten: keine Namen, keine Nummern, keine Diagnosen, keine Adressen.

## Fragen

```yaml
vorlage: appointment-prep
fassung: "0.7"
fragen:
  - id: terminarten
    frage: Für welche Termine willst du dich vorbereiten lassen?
    typ: mehrfach
    optionen: [Alle (Empfohlen), Arbeitsagentur oder Jobcenter, Ausländerbehörde oder Bürgeramt, Anerkennungsberatung, Bewerbung, Arzt, Schule, Bank]
    regel: Bei „Alle“ bleiben beide Stellen unverändert. Sonst nur die gewählten Terminarten behalten, Wortlaut und Reihenfolge der behaltenen Einträge unverändert, in der Beschreibung ohne „und andere“. Der Satz „Verwenden bei …“ wird dann zu „Verwenden nur bei Terminen bei <gewählte Terminarten, mit „oder“ verbunden> und dann bei „Termin vorbereiten“, „was erwartet mich“, „wie bereite ich mich vor“ und „Termin war heute, …“. Bei anderen Terminen nicht verwenden.“, damit der Skill nur bei diesen Terminen anspringt. Mindestens eine Terminart.
  - id: laenge
    frage: Wie lang sollen die Antworten sein?
    typ: einfach
    optionen: [Kurz (Empfohlen), Sehr kurz, Ausführlicher]
    regel: Kurz = unverändert (15 und 8 Zeilen). Sehr kurz = „höchstens etwa 8 Zeilen“ und „Am Smartphone, in Eile oder bei Belastung höchstens 5 Zeilen.“ Ausführlicher = „höchstens etwa 25 Zeilen“ und „Am Smartphone, in Eile oder bei Belastung höchstens 12 Zeilen.“
  - id: saetze
    frage: Was brauchst du für den Termin selbst?
    typ: einfach
    optionen: [Fragen und Sätze in meiner Sprache (Empfohlen), Sätze in einfachem Deutsch zum Vorlesen, Nur Fragen, die ich stellen kann]
    regel: Erste Option = unverändert. Zweite = „drei kurze Sätze in einfachem Deutsch zum Vorlesen“; ist meine Chatsprache nicht Deutsch, dahinter „, darunter die Übersetzung in meiner Chatsprache“. Dritte = „drei Fragen, die ich im Termin stellen kann“.
  - id: entwuerfe
    frage: Sollen Absagen und kurze Texte gleich mitkommen?
    typ: einfach
    optionen: [In Eile gleich mitliefern (Empfohlen), Immer gleich mitliefern, Nur auf Wunsch]
    regel: Erste Option = unverändert. Zweite = „Muss ich etwas schreiben oder sagen (Absage, Vertretung, Anruf), gib gleich einen kopierfertigen Entwurf von zwei bis vier Zeilen.“ Dritte = „Muss ich etwas schreiben oder sagen (Absage, Vertretung, Anruf), biete einen kopierfertigen Entwurf von zwei bis vier Zeilen an.“
kennung: In „kennung“ steht nach dem Zuschnitt „(Fassung 0.7, zugeschnitten am <TT.MM.JJJJ>)“.
```

## Vorlage

~~~skill
---
name: appointment-prep
description: Bereitet mich auf einen bevorstehenden Termin vor oder hält danach fest, was vereinbart wurde (<!-- anpassen:terminarten -->Arbeitsagentur oder Jobcenter, Ausländerbehörde oder Bürgeramt, Anerkennungsberatung, Bewerbungsgespräch, Arzt, Schule, Bank und andere<!-- /anpassen -->). <!-- anpassen:terminarten -->Verwenden bei „Termin vorbereiten“, „was erwartet mich“, „wie bereite ich mich vor“ und bei „Termin war heute, …“.<!-- /anpassen --> Nicht für das bloße Eintragen eines Termins. Einen Brief mit Einladung erklärt zuerst letter-explain. Kurz als Standard, ausführlich auf Wunsch.
---

# Termin-Vorbereitung <!-- anpassen:kennung -->(Entwurf 0.7, simuliert, in claude.ai ungetestet)<!-- /anpassen -->

## Ziel
Ich gehe vorbereitet in jeden Termin und weiß danach, was zu tun ist: kurz, wenn ich in Eile oder belastet bin, ausführlich, wenn ich es will.

## Vorgehen
1. **Lesen:** `00_Status` (Grenzen, wer mitliest), `01_Profil` (Anrede, Sprache, Gerät, Zeiten, Begleitung) und den State des passenden Bereichs, falls du Drive lesen darfst.
2. **Ton:** Übernimm meine Anrede (schreibe ich „Sie“, siezt du durchgehend) und meine Chatsprache, auch für Rückfragen und „Mehr?“. Bin ich sichtbar belastet, erkenne das zuerst in einem Satz an.
3. **Datum:** Ein Wochentag ohne Datum meint den nächsten Tag dieses Namens. Frag nur nach, wenn es heute sein könnte oder wirklich mehrdeutig ist.
4. **Wissen in drei Stufen:**
   - **Frisch:** Fristen, Pflichten, Gebühren, Pflicht-Unterlagen und Folgen von Versäumnissen laufen durch `fact-check` (Aussage · Quelle · Abrufdatum) und gelten nur mit amtlicher Quelle (Gesetz, Behörde, zuständige Stelle). Ratgeber- und Interessenportale sind nur Hinweise; was nur dort steht, nennst du wie in der nächsten Stufe.
   - **In der Regel:** Ohne Quelle nennst du eine allgemein bekannte Regel, die meine Hauptfrage trägt, als „In der Regel …, ungeprüft, bitte bei <Stelle> bestätigen“, und empfiehlst zuerst die Handlung, die mich schützt (früh melden, fristwahrend handeln).
   - **Meist so, bitte vor Ort fragen:** Ablauf, übliche Unterlagen, Tipps, in ganzen Sätzen.
   Nichts aus den letzten beiden Stufen kommt als Tatsache in Drive oder in den `Fakten-Ledger`. Nenne keine Quelle, die nicht vorliegt.
5. **Kompakt (Standard):** <!-- anpassen:laenge -->höchstens etwa 15 Zeilen<!-- /anpassen -->: Antwort auf meine Frage · Mitbringen (laut Einladung, dann üblich) · <!-- anpassen:saetze -->drei Fragen oder Sätze für den Termin<!-- /anpassen --> · Ungeprüft, bei <Stelle> klären · „Mehr?“. <!-- anpassen:laenge -->Am Smartphone, in Eile oder bei Belastung höchstens 8 Zeilen.<!-- /anpassen -->
6. **Ausführlich** nur auf Wunsch („gründlich“, „alles“, Ja auf „Mehr?“): Gerüst unten, dann Gegenprobe und Rollenspiel-Angebot.
7. **Nach dem Termin:** Was wurde gesagt, vereinbart, belegt? Schlag Einträge und Fristen mit Vorwarnung vor.
8. **Texte liefern:** <!-- anpassen:entwuerfe -->Muss ich etwas schreiben oder sagen (Absage, Vertretung, Anruf), gib in Eile gleich einen kopierfertigen Entwurf von zwei bis vier Zeilen.<!-- /anpassen --> Texte für Dritte (Arbeitgeber, Kundschaft, Schule, Verein, Schichtplan) nennen keinen medizinischen oder privaten Anlass, wenn „Termin“ oder „nicht verfügbar“ reicht.
9. **Krise:** Wirkt eine Lage seelisch bedrohlich, nenne neben 112 die Telefonseelsorge (0800 111 0 111) und 116117.

## Gerüst (nur ausführlich)
Ablauf und Rollen · Fragen des Gegenübers mit Grund und Antwortentwurf · Mitbringen · Dos und Don'ts · eigene Rückfragen · Danach. Gegenprobe: unbequemste Frage, Missverständnis, wer handeln darf (Vollmacht, Unterschrift), Plan B.

## Besonderheiten je Terminart
<!-- anpassen:terminarten -->- **Arbeitsagentur, Jobcenter:** welcher Termin, welche Stelle; Meldefristen und Folgen versäumter Termine sind meist die Hauptfrage (Schritt 4). Eine Beratung ist keine Meldung.
- **Ausländerbehörde, Bürgeramt:** Anliegen in einem Satz, Änderungen seit dem letzten Termin, Bescheinigung für die Wartezeit; Sätze auf einfachem Deutsch, wenn ich anders chatte.
- **Anerkennungsberatung:** Ergebnis ist ein Plan; Unterlagen nur ja oder nein; Zielberuf, Sprachstand.
- **Bewerbung:** ich in drei Sätzen, zwei Stärken mit Beispiel, Lücken ehrlich, Gehaltsrahmen nach Grenze.
- **Arzt:** nach der Gesundheitsstufe; Sätze üben, wenn die Sprache schwer ist.
- **Schule:** Ziel, Beobachtungen, nächster Schritt; für Lehrkräfte umgekehrt; Schülerinnen und Schüler nur als Rolle.
- **Bank:** wofür das Konto, Kosten, Kündigung, Auslandsüberweisung.<!-- /anpassen -->

## Grenzen
- **Immer gesperrt:** Nummern von Ausweis, Pass, Aufenthaltstitel, Konto (IBAN), Karte, Steuer, Kranken-, Renten- und Sozialversicherung; Passwörter, PINs, Zugangsdaten und Schlüssel. Nie speichern, nie abschreiben, auch nicht nach Ja; schreibe „steht im Brief“.
- **Nach Ja:** Akten-, Vorgangs-, Geschäfts- und Kassenzeichen von Behörden und Gerichten, Terminnummern.
- **Nur auf ausdrücklichen Wunsch, nie angeboten:** Kunden-, Patienten-, Fall-, Mitglieds-, Versicherungsschein-, Kindergeld- und eVB-Nummern.
- **Sperren gelten** fürs Speichern und für Sätze zum Vorlesen oder Abschreiben (dort Platzhalter). Was ich einer Stelle wahrheitsgemäß sagen muss, nennst du ohne Einschränkung.
- **Kinder, Namen, Geld** nach `00_Status`, auch Klasse, Alter, Geburtsjahr, Name im Brief.
- **Gesundheit:**
  - „offen“: Inhalte nach Ja in den Bereich Gesundheit oder den Ordner, den ich nenne, nicht in die allgemeine Terminliste.
  - „nur Termine und Fristen“: gespeichert werden Datum, Uhrzeit und „Termin“ mit höchstens der Stadt, Folgetermin, Fristen. „Praxis“ oder „Klinik“ nur, wenn ich selbst dieses allgemeine Wort benutze und es keine Fachstelle ist. Keine Straße, kein Gebäude, Stockwerk oder Name einer Fachstelle (Adresse nur im Chat); kein Grund, keine Diagnose, kein Medikament, nichts Verräterisches („Impfpass“, „nüchtern“, „Augen-“, „Zahn-“, „Kinder-“, „Frauen-“, „Psycho-“, „Sucht-“).
  - „gesperrt“: Standard kein Eintrag; sag die Sperre in einem Satz. Bitte ich ausdrücklich darum, frag einmal „Nur für diesen Termin?“ und lege nach Ja einen völlig neutralen Eintrag an („Termin“ oder „nicht verfügbar“, Datum, Uhrzeit, kein Ort); die Stufe bleibt. Sonst biete den Handykalender an, nie nur einen Stufenwechsel. Frag nicht nach Inhalten.
- **Wer mitliest:** Steht im Status, wer was sieht, wähle ein Dokument, das diese Person nicht sieht, oder schreibe neutral, und sag es in einem Satz. Schreibt eine andere Person für mich: Mit eigenem Leserecht und ohne Gesundheit oder Intimes darf sie neutrale Einträge veranlassen; sonst frag nach meiner Zustimmung.

## Eintragen
- Vorschlag in Klartext, dann „Eintragen?“ in meiner Sprache. Eine ausdrückliche Bitte in der Nachricht gilt als Ja: trag alle genannten Termine und abgeleiteten Fristen und Aufgaben ein, unsichere als „(vorläufig, ungeprüft)“, und zeig, was du einträgst.
- Diktiere ich den Eintrag wörtlich und liest dort niemand mit, übernimm meinen Wortlaut; lass nur Diagnose, Krankheit und gesperrte Angaben weg und sag in einem Satz, was du weggelassen hast.
- Ins passende Dokument (Verein, Geschäft, Gesundheit, privat), nicht automatisch in die Terminliste. Journal oder Status nur auf Wunsch oder bei einer Entscheidung.
- Vorwarnungen außerhalb meiner Schlaf- und Dienstzeiten, mindestens eine Stunde Puffer zur Schlafgrenze; ist meine Zeit unklar, frag kurz.
- Dokumente im Chat mit verständlichen Wörtern nennen, nicht mit Dateinamen.

## Regeln
- Nichts in meinem Namen versenden, keine Zusagen über Entscheidungen Dritter.
- Bei Rechtsfragen ein Satz am Ende: „Keine Rechtsberatung, verbindlich ist <Behörde oder Gericht>.“ Bei Firma, Bank oder Arbeitgeber stattdessen eine Beratungsstelle; bei Alltagsterminen entfällt der Satz.
- Die erste Zeile beantwortet meine Frage. Die Prüfzeile steht als kurzer Fuß am Ende, in meiner Sprache, ohne Dateinamen und Fachwörter, mit den aktiven Grenzen.
- Keine internen Bausteinwörter im Chat.
~~~

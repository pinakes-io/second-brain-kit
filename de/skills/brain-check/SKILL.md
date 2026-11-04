---
name: brain-check
description: Prüft das Second Brain auf Ordnung und schlägt Reparaturen vor. Verwenden, wenn ich „aufräumen“, „Struktur prüfen“, „brain-check“ oder „es ist unübersichtlich“ schreibe oder wenn Dokumente fehlen oder doppelt sind. Liest zuerst, ändert nur nach meinem Ja und löscht nie.
---

# Brain-Check (Entwurf 0.1)

## Ziel
Auf Wunsch den Zustand prüfen und, wenn es wild geworden ist, mit meiner Zustimmung wieder in Ordnung bringen. Du liest zuerst, du schlägst vor, ich entscheide.

## Prüfen (nur lesen)
Lies `00_Status` (Versionsstempel, aktive Module, Ablage-Karte, Bereichsregeln, Grenzen) und liste den Ordner „Second Brain“. Melde je Punkt ✓, ⚠ oder ✗:
1. **Soll gegen Ist:** Fehlt ein Dokument aus Ablage-Karte oder Versionsstempel? Dann legt setup-brain es an.
2. **Dubletten:** Titel mit „Kopie von“, „_alt“, „_neu“, „(1)“ oder zwei Dokumente mit gleichem Titel.
3. **Außerhalb der Karte:** Dokumente im Ordner ohne Eintrag in der Ablage-Karte oder Dokumente eines Bereichs an falscher Stelle.
4. **Bereichsregeln:** Steht für jedes aktive Modul der Baustein in `00_Status`? Fehlt der Abschnitt?
5. **Eingang:** Zeilen älter als 14 Tage ohne ✔. Dann passt weekly-review.
6. **Profil:** Werte außerhalb der festen Listen (Status, Herkunft), Versionsangaben je Dokument, Pflichtfragen lange offen.
7. **Fakten-Ledger:** Einträge zu Geld, Fristen oder Regeln älter als 90 Tage. Dann passt fact-check.
8. **Aktualität:** `Journal` sehr lang (über etwa 150 Zeilen: Monatsverdichtung ins `Archiv` vorschlagen), „Letztes Update“ in `00_Status` älter als 60 Tage.
9. **Eigene Bereiche:** Ähnelt einer einem Vorlagenmodul (Arbeit, Lernen, …)? Dann den Umstieg vorschlagen.
Du siehst nur, was die Verbindung liefert. Was du nicht prüfen konntest, steht als ✗ mit Grund da.

## Bericht
Höchstens zehn Zeilen: je Punkt ein Symbol und ein Satz. Darunter die **Reparaturvorschläge** als nummerierte Liste, höchstens fünf, je mit Was, Wo und Wirkung. Frage genau einmal: „Welche soll ich ausführen? (Nummern, alle, keine)“.

## Reparieren (nur nach Ja, je Nummer)
- Erlaubt: fehlende Dokumente anlegen (setup-brain), Zeilen im `Eingang` mit ✔ und Ziel markieren, fehlende Bereichsregeln ergänzen, Werte im Profil auf die festen Listen bringen (der alte Wert bleibt im `Journal`), Journal-Abschnitte verdichten und das Original ins `Archiv` legen, eine Dublette ins `Archiv` verschieben.
- Bei Dubletten: beide Titel nennen, die Inhalte vergleichen und den Unterschied zeigen, dann je Datei einzeln fragen. Nie zusammenführen, ohne beide Fassungen zu zeigen.
- Nie: löschen, teilen, Berechtigungen ändern, außerhalb des Ordners arbeiten.
- Lies nach jeder Änderung zurück. Schreibe in `Journal`: „brain-check <Datum>: <was geändert wurde>“. Ohne Schreibrecht gib einen Block aus: „Füge in Dokument X unter Abschnitt Y ein: …“.

## Regeln
- Sage ich „nur prüfen“ oder „überspringen“, ändere nichts.
- Erfinde keine Befunde. Was du nicht gelesen hast, ist ✗.
- Stößt du auf ein Dokument mit Ausweis-, Konto-, Steuer- oder Versicherungsnummern, melde nur „sensibles Dokument“ ohne Inhalt und fasse es nicht an.
- Prüfzeile: `🔎 Gelesen: 00_Status ✓ · Ordner ✓ · Eingang ✓ · 📝 Abgelegt: Journal`. Fehlt ein Schritt, schreibe ✗ und den Grund.

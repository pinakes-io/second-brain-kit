# Feldkarte – Second Brain (Entwurf 31.10.2026)

> Gehört zu `second-brain/spec/`. Grundlage: Entscheide 31.10.: 9 Module (die 8 aus §8 plus `entscheidungen`) plus Rückverweis, ein Projekt zum Start, Personenprofil getrennt von den Modulfeldern, minimaler Kern, Module im einheitlichen Format plus eigene Bereiche. Alles hier ist **Entwurf** (Claude), nicht abgenommen.

## 1. Was die Feldkarte ist
Ergebnis von Interview-Stufe 1. Sie sagt je Modul: **aktiv ja/nein**, **warum** (welche Antwort), **Kanal** für die Detailfragen (Chat oder Formular) und **wer antwortet**. Sie wird als Abschnitt in `00_Status` abgelegt, gleich neben dem Versionsstempel.

## 2. Kern (immer da, kein Modul)
- **Skills:** `setup-brain`, `onboarding-interview`, `fact-check`, `weekly-review`, `brain-check`; nachrüstbar außerhalb des Budgets: `area-manager`.
- **Dokumente:** `00_Status` (Index, Versionsstempel, Feldkarte, Ablage-Karte), `01_Profil`, `02_Offene_Fragen`, `Eingang`, `Journal`, `Fakten-Ledger`, `Wochenplan`, Ordner `Archiv`.
- **Profil:** nur das Personenprofil (`Profilschema.yaml`).

## 3. Module
> **Maßgeblich sind die Moduldateien `spec/module/*.yaml`** (Entscheid 31.10.: Module als Daten). Die Tabelle zwischen den Markern erzeugt `tools/spec_pruefen.py --feldkarte`; die Prüfung meldet, wenn sie von den Moduldateien abweicht.

<!-- module:start -->
| ID | Modul | Aktiviert durch (Stufe 1) | Skills | Kanal Detail | Drive-Vorlagen |
|---|---|---|---|---|---|
| `person` | Person und Situation | immer | – | chat | – |
| `werkzeuge` | Werkzeuge | immer | – | chat | – |
| `arbeit` | Arbeit und Ziele | `felder` enthält „Arbeit, Beruf, Ausbildung“ | `transcript-minutes` (nachrüstbar) | formular | State_Arbeit |
| `entscheidungen` | Entscheidungen | `zweck` enthält „Entscheidungen vorbereiten“ oder Modul `arbeit` aktiv | `decision-clarify`, `decision-check` | chat | Entscheidungen |
| `familie` | Familie und Haushalt | `felder` enthält „Familie, Haushalt“ | – | formular | State_Familie |
| `wissen` | Wissen und Quellen | `zweck` enthält „Wissen und Recherchen sammeln“ | `knowledge-note` | chat | Knowledge, 00_Knowledge_Index |
| `termine` | Termine, Post und Ämter | `felder` enthält „Termine, Post, Ämter“ oder `zweck` enthält „Den Überblick über Aufgaben und Termine behalten“ | `appointment-prep`, `letter-explain` | formular | State_Termine, Briefe_Scans |
| `lernen` | Lernen | `zweck` enthält „Etwas lernen“ | – | chat | State_Lernen, Lernprotokoll |
| `schreibstil` | Schreibstil | `zweck` enthält „Texte schreiben“ | `plain-prose-de`, `plain-prose-en`, `style-profile` (nachrüstbar) | chat | Stilprofil |
| `bauen` | Bauen | `zweck` enthält „Etwas bauen (App, Skript oder Ablauf)“ | `build-router`, `vibe-pack` | chat | Bauprojekte |
| `eigen:<name>` | eigener Bereich | Folgefrage `s1.felder.eigen` oder später im Chat | – | chat | State_<name> |
<!-- module:end -->

**Eigene Bereiche:** Die Person kann jederzeit „neuer Bereich: …“ sagen. Dann legt `setup-brain` ein Modul `eigen:<name>` nach `Modul_Vorlage.yaml` an (ein State-Dokument, eine Zeile in der Ablage-Karte, ein Eintrag im Versionsstempel). `brain-check` meldet eigene Bereiche, die einem Vorlagenmodul ähneln, und schlägt den Umstieg vor.

## 4. Rückverweis: Abschnitte des Referenzfragebogens → Module
Für die **strukturelle** Regressionsprobe (keine Inhalte der Referenz).

| Nr. | Original-Abschnitt | Modul(e) | Bemerkung |
|---|---|---|---|
| 1 | Person und Rahmen | `person` | |
| 2 | Familie, Alltag und Mobilität | `familie`; Alltag/Zeit → `person.zeit` | |
| 3 | Bildung und Abschlüsse | `arbeit` (Abschlüsse), `lernen` (falls aktiv) | Dokumentenstatus nur ja/nein |
| 4 | Berufserfahrung | `arbeit` | |
| 5 | Deutsch und andere Sprachen | `person.sprache`, `lernen` | im Produkt nur Deutsch als Ausgabesprache |
| 6 | Behörden und Förderung | `termine` | Anwendungsfall, kein Kern |
| 7 | Berufsziele und Interessen | `arbeit`; Interessen → `wissen` | |
| 8 | Persönlichkeit und Kommunikation | `person.kommunikation` | Entscheid 31.10.: im Personenprofil (kein eigenes Modul) |
| 9 | Wochenplan, Hobby und Haushalt | `person.zeit`, `familie.haushalt`; Hobby → `eigen:hobby` | Entscheid 31.10.: nur als eigener Bereich, kein Vorlagenmodul |
| 10 | Technik und Setup | `werkzeuge` | |
| 11 | Abschluss | Kern: `02_Offene_Fragen`, `Journal` | |
| – | (kein Original-Abschnitt) | `wissen`, `schreibstil` | **Lücke:** Fragen neu zu schreiben |

## 5. Offen
- Persönlichkeit: **entschieden 31.10.** im Personenprofil.
- Hobby/Wachstum: **entschieden 31.10.** nur als eigener Bereich.
- Befunde F1–F7: **entschieden 31.10.** (`personas/Auswertung_Trockenlauf_1.md`, umgesetzt, Trockenlauf 2 ohne Lücken).
- Kanal je Modul: Vorschlag oben, endgültig wählt das Interview (`kanal_detail`).

## 6. Regeln aus den Entscheiden vom 31.10. (Entwurf)
- **Anrede (F1):** Erste Frage in Stufe 2 (`Fragen_Stufe2.yaml`, `s2.person.anrede`); Stufe 1 bleibt bei 2 × 4 Fragen.
- **Folgefragen (F2, F3):** Wer „eigener Bereich (bitte benennen)“ wählt, bekommt die Frage nach dem Namen (`meta.eigene_bereiche`); wer eine Begleitperson angibt, bekommt die Frage nach ihrer Rolle (Rolle, kein Name). Beide zählen nicht zur Grenze von vier Fragen je Runde.
- **Hinweise (F5, F6):** Bei „andere Sprache“ und bei „nur Smartphone“ zeigt Stufe 1 einen kurzen Hinweistext (Wortlaut in `Fragen_Stufe1.yaml`).
- **Sensibel-Tags (F7):** Die Grenzen aus Stufe 1 (Gesundheit, Kinder, Namen, Geld) sperren gleichnamige Tags. Felder und Fragen mit diesem Tag fallen in den aktiven Modulen weg; der Generator vermerkt das in `00_Status` im Abschnitt Grenzen.
- **Kein Claude-Gedächtnis (Entscheid 31.10. 10:12):** Alles Tragende steht in Drive-Dokumenten. Das Handbuch empfiehlt, das claude.ai-Gedächtnis auszuschalten oder im Projekt zu isolieren [Oberfläche ungeprüft]. Die Konto-Präferenzen enthalten nur einen Verweis (Entwurfstext: „Antworte auf Deutsch. Lies zuerst das Dokument 00_Status im Ordner Second Brain.“). „Merk dir das“ geht immer nach Drive (Profil, Eingang oder Journal) mit Ablageort in der Prüfzeile; ohne Schreibzugriff als Update-Block, nie als stilles „gemerkt“.

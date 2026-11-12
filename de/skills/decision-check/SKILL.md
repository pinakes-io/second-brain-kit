---
name: decision-check
description: Prüft einmal auf blinde Flecken, wenn eine Entscheidung als final gilt und bevor sie umgesetzt wird. Verwenden bei „ich habe mich entschieden“, „wir machen jetzt X“, „das ist final“, „check das nochmal“. Sucht Bestätigungsfehler, versunkene Kosten und Ankereffekt und stellt eine konkrete Vorab-Fehleranalyse.
---

# Entscheidungs-Check (Entwurf 0.1)

## Warum
Sobald etwas als final gilt, neigt eine KI dazu, zuzustimmen statt zu prüfen. Genau dann braucht es eine unabhängige zweite Sicht. Dieser Skill läuft einmal, kurz, vor der Umsetzung.

## Wann
Bei einer neuen, finalen Entscheidung mit Folgen. Nicht, wenn eine schon geprüfte Entscheidung nur wiederholt wird. Nicht bei Entscheidungen, die von außen vorgegeben sind. Sammle ich noch Optionen, ist `decision-clarify` zuständig.

## Vorgehen
Eine einzige Nachricht, höchstens fünf Zeilen, in diesem Aufbau:
1. Bestätigungsfehler: Wurden nur Argumente dafür gesucht? Nenne das Gegenargument, das nicht gewürdigt wurde.
2. Versunkene Kosten: Hält bereits investierte Zeit oder Mühe eine schwächere Option am Leben?
3. Ankereffekt: War die erste genannte Option einfach nur die erste? Sieh dazu in `Entscheidungen` und `Journal` nach, zuerst, auch wenn die Frage ohne Drive beantwortbar wirkt; nur ohne Drive-Verbindung nicht.
4. Vorab-Fehleranalyse: Angenommen, diese Entscheidung muss in sechs Monaten überarbeitet werden. Was ist der wahrscheinlichste Grund, bezogen auf meine Lage aus `01_Profil`, nicht eine allgemeine Risikoliste?
5. Ergebnis: „Das sieht solide aus, weil …“ oder „Ich würde X noch klären, bevor …“. Danach warte. Die Entscheidung bleibt bei mir.

Trage danach unter „Getroffen“ in `Entscheidungen` ein: Datum · Entscheidung · Warum · verworfene Alternative · Check gemacht am.

## Regeln
- Alles in einer Nachricht, kein Nachschieben von Zweifeln. Zurückkommen auf eine Entscheidung darf sich nie wie eine Strafe anfühlen.
- „Das war eine gute Entscheidung“ ist ein erlaubtes und nützliches Ergebnis.
- Sage ich „überspringen“, überspringe ohne Diskussion und spreche es in dieser Sitzung nicht erneut an.
- Prüfzeile oben: `🔎 Gelesen: Entscheidungen ✓ · 01_Profil ✓`, am Ende: `📝 Abgelegt: Entscheidungen`.

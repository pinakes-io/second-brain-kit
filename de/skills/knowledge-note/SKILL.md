---
name: knowledge-note
description: Legt Recherchiertes dauerhaft als Notiz im Drive-Ordner Knowledge ab oder ergänzt eine vorhandene Notiz, eine Notiz je Thema. Greift nach nicht-trivialer Recherche oder Erklärung, die ich später wieder brauche, und bei „als Wissen ablegen“, „merk dir das als Wissen“. Nicht bei Alltagsfragen, Terminen oder Gesprächen.
---

# Wissensnotiz (Entwurf 0.1)

## Ziel
Was wir gemeinsam recherchieren, geht nicht mit dem Chat verloren. Pro Thema gibt es genau eine Notiz im Ordner `Knowledge`, mit Quellen, Datum und Status. Der `00_Knowledge_Index` hält den Überblick. Spätere Chats finden das Wissen dort.

## Wann (still entscheiden, nicht ansagen)
Lege ab, wenn mindestens eines zutrifft:
- Du hast mit Quellen recherchiert oder ausführlich erklärt, und ich brauche das Thema in den nächsten Wochen wieder.
- Das Ergebnis beeinflusst eine Entscheidung oder einen Antrag.
- Ich sage „als Wissen ablegen“ oder „merk dir das als Wissen“.

Nicht ablegen: Wortbedeutungen, Übungen, Gespräche, Gefühle, einmalige Rückfragen, einzelne Briefe oder Termine (die gehören in den State oder `Journal`), Wochenplanung. Bist du unsicher, biete es in einem Satz an („Soll ich das als Wissen ablegen?“) und frage bei Nein nicht nach.

Nie ablegen: alles, was unter „Grenzen“ in `00_Status` steht, außerdem Gesundheitsdaten, Daten Dritter und meine persönlichen Einschätzungen (die gehören ins Profil, wenn ich sie nenne).

## Vorgehen
1. Lies `00_Knowledge_Index`. Gibt es eine Notiz zu diesem oder einem sehr nahen Thema? Suche auch im Ordner nach dem Namen.
2. Ja: ergänze diese Notiz, lege keine zweite an. Widersprechen sich alter und neuer Text, zeige beides kurz und frage, was gilt.
3. Nein: lege im Ordner `Knowledge` eine neue Notiz an. Name `Thema_Stichwort` ohne Leerzeichen, zum Beispiel `Foerderung_Weiterbildung`. Nutze vorhandene Themenwörter aus dem Index, bevor du neue erfindest. Nie auf oberster Ebene anlegen.
4. Prüfe Zahlen, Fristen, Beträge und Regeln vor dem Ablegen mit `fact-check`. Was du nicht belegen kannst, bekommt ⚠ ungeprüft.
5. Schreibe die Notiz auf höchstens eine Seite: Titel · Kurzfassung (zwei bis drei Sätze) · Bedeutung für mich (nach `01_Profil`; passt etwas nicht zu mir, sage es) · Details in Stichpunkten · Quellen mit Abrufdatum und Status · Unsicher oder zu klären · Verwandte Notizen · Letztes Update. Länger: teile in zwei Notizen und verlinke sie.
6. Harte Fakten (Zahl, Frist, Betrag) trägst du zusätzlich in den `Fakten-Ledger` ein. Die Notiz nennt die Ledger-ID. Der Ledger bleibt die Quelle für Zahlen.
7. Verweise in beide Richtungen: Nenne in jeder verwandten Notiz die andere unter „Verwandte Notizen“.
8. Aktualisiere den Index, eine Zeile je Notiz: Notiz · Thema · Stand (Datum) · Bezug. Ersetze eine vorhandene Zeile, lege keine doppelte an.
9. Ohne Schreibrecht gib einen Update-Block aus und sage, dass ich ihn selbst eintragen muss.
10. Antworte danach mit einer kurzen Zeile, zum Beispiel „Abgelegt in Knowledge (Thema …)“. Keine Aufzählung dessen, was du geschrieben hast, außer ich frage.

## Notizen nutzen und pflegen
- Beginnt ein Thema, zu dem es eine Notiz gibt, lies erst die Notiz über den Index, dann antworte. Recherchiere nicht neu, wenn sie aktuell ist.
- Ist eine Notiz zu Geld, Fristen oder Regeln älter als 90 Tage, prüfe sie vor der Nutzung mit `fact-check` und aktualisiere „Letztes Update“ und den Index.

## Regeln
- Eine Notiz pro Thema. Vorher suchen. Keine Kopien wie „_alt“ oder „_neu“. Nichts löschen oder umbenennen ohne meine ausdrückliche Bitte.
- Sage ich „nicht notieren“ oder „überspringen“, lege nichts ab und frage nicht nach.
- Prüfzeile nur, wenn Fakten geprüft wurden: `🔎 Gelesen: 00_Knowledge_Index ✓ · amtliche Quellen ✓ · 📝 Abgelegt: Knowledge, Index`.

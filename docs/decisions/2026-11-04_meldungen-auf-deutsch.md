# Alle Meldungen auf Deutsch, ein Kanal über `Messages`

Datum: 2026-11-04

Status: abgelöst durch `2026-11-06_meldungen-zweisprachig.md` — nie
umgesetzt, die Umstellung wäre mehr Arbeit als der Nutzen. Beschreibt, was
eine Umstellung auf Deutsch umfasst.

**Kontext:** Bisher waren die Meldungen für den Nutzer (`Messages`) deutsch,
Logging und die Texte eigener Exceptions englisch. Das Backend meldet deshalb
vieles doppelt, einmal per `logger` und einmal per `Messages`, und die App
zeigt Fehler als „Error: “ mit englischem Text. Das Tool läuft nur in einem
deutschsprachigen Betrieb; die englische Hälfte liest dort niemand.

**Entscheidung:** Alle Meldungen sind deutsch: Info, Warnung, Fehler und die
Texte eigener Exceptions. Was der Nutzer sehen soll, meldet das Backend nur
über `Messages`; wohin die Meldungen gehen, entscheidet der Einstiegspunkt
(App: Oberfläche, CLI: Konsole). `logging` bleibt für Diagnose, die der Nutzer
nicht braucht, vor allem Tracebacks per `logger.exception`.

**Alternativen:**

- *Ein Meldungsobjekt, das je nach Umgebung in die Oberfläche oder auf die
  Konsole schreibt* (Vorschlag von der PyCologne). Kommt der Entscheidung nahe,
  braucht aber kein eigenes Objekt pro Umgebung: Die Einstiegspunkte bekommen
  die gesammelten Meldungen ohnehin zurück und geben sie selbst aus.
- *Nur `logging`, mit eigenem Handler für die Oberfläche.* Verworfen. Logging
  gilt prozessweit, Streamlit bedient jede Sitzung in einem eigenen Thread; die
  Meldungen der richtigen Sitzung zuzuordnen wäre zusätzlicher Code.
- *Beim zweisprachigen Modell bleiben.* Verworfen: doppelte Meldungen ohne
  Leser für die englische Hälfte.

**Konsequenzen:**

- Fehler aus Python und Bibliotheken bleiben englisch, ganz einsprachig wird
  es nie.
- Die Sprachregeln in AGENTS.md (Error handling, Style conventions) ändern
  sich mit der Umsetzung.
- Eine Logdatei, falls sie kommt, nimmt dieselben deutschen Meldungen auf.

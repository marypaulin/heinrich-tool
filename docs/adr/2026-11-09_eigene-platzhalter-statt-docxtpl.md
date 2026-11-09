# Eigene Platzhalter statt docxtpl

Datum: 2026-11-09

Status: angenommen

**Kontext:** Auf der PyCologne kam der Vorschlag, die Vorlage auf `docxtpl`
umzustellen (Jinja-Platzhalter wie `{{ datum_heute }}`). docxtpl fügt über
Runs zerstückelte Platzhalter selbst zusammen; die eigene Ersetzungslogik in
`docgen.py` fiele weg, ebenso das Befüllen der Positionstabelle, das ein
Tabellen-Loop in der Vorlage übernähme.

**Entscheidung:** Die eigenen Platzhalter (`<Lieferdatum>` usw.) und
`_replace_in_paragraph` bleiben. Die Lösung läuft und ist getestet; der Umbau
beider Vorlagen, von `docgen` und seinen Tests löst kein aktuelles Problem.

**Alternativen:**

- *docxtpl.* Zurückgestellt. Neu prüfen, wenn einer dieser Fälle eintritt:
  - Der Kunde will Platzhalter in Kopf- oder Fußzeile; `replace_placeholders`
    erfasst nur Fließtext und Tabellen.
  - Der Kunde will die Positionstabelle selbst gestalten (Spalten,
    Formatierung); heute legt `docgen.py` sie fest.
  - Die Run-Logik versagt an einer echten Vorlage.

  Bei der Umstellung nötig: `autoescape=True`, sonst macht ein `&` in einer
  Positionsbeschreibung das XML kaputt, und `StrictUndefined`, sonst bleibt
  ein vertippter Platzhalter still leer.
- *Word-Inhaltssteuerelemente oder Seriendruckfelder.* Verworfen:
  python-docx hat dafür keine API, die Run-Logik würde nur durch eigenen
  XML-Code ersetzt.

**Konsequenzen:**

- Platzhalter in Kopf- und Fußzeile werden weiterhin nicht ersetzt.
- Tabellenformatierung bleibt im Code (`TABLE_FONT_NAME`, `TABLE_FONT_SIZE`).

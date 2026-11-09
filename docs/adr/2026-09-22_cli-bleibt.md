# Das CLI bleibt neben der Streamlit-Oberfläche

Datum: 2026-09-22

Status: angenommen

**Kontext:** Mit Streamlit als Oberfläche ist `cli.py` ein zweiter
Einstiegspunkt, der gepflegt werden muss. Naheliegend wäre, ihn zu streichen.

**Entscheidung:** Das CLI bleibt.

Es ist der einzige Weg, ohne Browser ein Dokument gegen einen echten
Projektordner zu erzeugen. Genau das braucht die PDF-Prüfung: Das
PDF-Rendering läuft über Word, ist nicht deterministisch und wird deshalb nicht
automatisiert getestet, sondern von Hand geprüft.

**Alternativen:** CLI streichen und Dokumente für die Prüfung über die
Oberfläche erzeugen. Verworfen, weil jeder Prüfdurchlauf dann über den Browser
liefe und sich nicht als Befehl wiederholen ließe.

**Konsequenzen:**

- Zwei Einstiegspunkte, `app.py` und `cli.py`. Beide sprechen nur mit
  `services.py`; Logik gehört nicht in sie hinein.
- Änderungen an den Signaturen in `services.py` ziehen beide Einstiegspunkte
  nach sich.

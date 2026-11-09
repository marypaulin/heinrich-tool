# Umstellung auf eine native Desktop-Anwendung mit PySide6

Datum: 2026-08-26

Status: abgelöst durch `2026-09-04_streamlit-statt-nativer-anwendung.md` — der
Umbau war Teil des Angebots vom 27.08.2026 und wurde nicht beauftragt. Die
Abwägung unten bleibt als Begründung erhalten.

**Kontext:** Die Anwendung läuft als Streamlit-App aus dem Git-Clone und muss auf
jedem Rechner einzeln eingerichtet werden. Der Kunde nutzt mehrere Rechner und
wünscht eine installierbare Anwendung, die er per Doppelklick startet.

**Entscheidung:** Umzug der Oberfläche von Streamlit auf Qt, konkret PySide6.
Auslieferung als One-Folder-Build via PyInstaller, verpackt mit Inno Setup.

**Der tragende Grund ist die Paketierung.** Streamlit bringt einen lokalen
Webserver mit — Port, Firewall-Abfrage, Browserfenster — und lässt sich nur mit
erheblichem Aufwand sauber in ein Installationsprogramm packen. Eine Qt-Anwendung
startet als normales Programm und wird zu einer einzelnen Installationsdatei.

Alles Weitere sind Vorteile, die sich daraus ergeben, aber die Entscheidung nicht
allein tragen würden: native Datei- und Ordnerdialoge mit vollständigem Pfad,
bearbeitbare Tabellen als Standardbestandteil, freie Gestaltung der Oberfläche,
Betrieb ohne Browser.

**Warum PySide6 und nicht PyQt:** PySide6 steht unter LGPL und stammt vom
Qt-Hersteller selbst; PyQt ist GPL oder kommerziell. Bei einer Auftragsarbeit mit
Auslieferung an einen Kunden ist die GPL-Frage zu vermeiden. Die APIs sind zu rund
95 % identisch. *Offen: Lizenzfrage von einem anderen Freelancer gegenprüfen
lassen.*

**Warum One-Folder und nicht One-File:** Robuster, und die Qt-Bibliotheken bleiben
als separate, austauschbare Dateien liegen — damit ist die LGPL-Bedingung
offensichtlich erfüllt. One-File wäre hier Grauzone.

**Alternativen:**

*Bei Streamlit bleiben und nur die fachlichen Änderungen umsetzen.* Verworfen: Die
Change Requests allein rechtfertigen den Umzug nicht — der CSV-Editor ließe sich
mit `st.data_editor` bauen, das Stundenarchiv spräche sogar für Streamlit. Aber
die Kernanforderung „installierbare Anwendung" bleibt damit ungelöst.

*Flet oder NiceGUI.* Beide bringen von Haus aus ein moderneres Aussehen mit. Nach
einem Gestaltungsdurchgang am Qt-Entwurf am 2026-08-26 nicht mehr nötig: Das
Zielbild ließ sich mit Qt-Stylesheets und einer eigenen Palette erreichen. Qt hat
zudem die größere Verbreitung und die bessere Werkzeugunterstützung für
Paketierung.

*React über PyWebView.* Verworfen: ein kompletter zweiter Technologie-Stack
(Node, npm, Build-Schritt, Python-JS-Brücke) für ein Werkzeug mit einem einzigen
Nutzer.

*Eigener Wegwerf-Prototyp zur Absicherung der Paketierung (Spike).* Verworfen: Das
Paketieren von Python-Qt-Anwendungen ist etablierte Praxis (Anki, Calibre). Das
verbleibende Risiko ist eng umrissen — die Ansteuerung von Word über COM aus einem
eingefrorenen Bündel heraus, samt fehlendem Schreibrecht unter `C:\Program Files`.
Statt eines Prototyps wird die Paketierung am echten Code an den Anfang der
Umsetzung gestellt. Nichts wird weggeworfen, die riskanteste Integration passiert
trotzdem zuerst.

**Konsequenzen:**

- `app.py` und `src/ui/` werden neu geschrieben. Das Backend bleibt unangetastet;
  `services.py` ist laut CLAUDE.md der einzige öffentliche Einstiegspunkt und
  trägt das bereits.
- Vor dem Umbau werden Characterization Tests geschrieben, die das heutige
  Dokumentergebnis einfrieren.
- Blockierende Aufrufe frieren in Qt das Fenster ein. Die Dokumenterzeugung mit
  Word-Konvertierung braucht daher einen Arbeitsthread, und die `Messages`-Ausgabe
  muss darüber zurück ins UI.
- Der Build braucht eine Windows-Umgebung; PyInstaller cross-compiliert nicht.
- Word bleibt für die PDF-Erzeugung gesetzt. LibreOffice im Hintergrund wurde als
  Alternative geprüft und verworfen — es rendert DOCX nicht identisch zu Word, und
  die über Jahre gewachsene Optik der PDFs an den Endkunden ist das Versprechen,
  das nicht gebrochen werden darf. Bleibt als Rückfallebene für einzelne Rechner
  ohne Word, dann aber erst nach belegtem Vergleich.
- Konfiguration und Word-Vorlage ziehen in den Datenordner; maschinenlokal
  gespeichert wird nur, wo dieser Ordner liegt.

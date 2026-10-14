# Bei Streamlit bleiben statt nativer Desktop-Anwendung

Datum: 2026-09-04

Status: angenommen

**Kontext:** Angebot 001 vom 27.08.2026 sah den Umbau der Oberfläche auf eine
native Desktop-Anwendung vor (siehe `2026-08-26_native-desktop-anwendung.md`).
Einziger tragender Grund dort war die Paketierung — eine per Doppelklick
installierbare Anwendung. Der Kunde meldete zurück, das Angebot sei teurer als
erwartet. Da der Umbau mit Abstand der größte Posten war, wurde die Anforderung
noch einmal geprüft, bevor die Umsetzung beginnt.

**Entscheidung:** Die Oberfläche bleibt Streamlit. Native Anwendung und
Installer entfallen. Stattdessen wird die Einrichtung auf einem neuen Rechner
durch ein Skript vereinfacht, das Installation und Aktualisierung übernimmt.

**Der tragende Grund ist der Preis.** Baustein 1 sinkt von 4.000–7.200 € auf
2.400–4.800 €, über die Bausteine 1 bis 3 rund 1.600–2.800 € weniger. Für den
Kunden war das ausschlaggebend. Alle fachlichen Änderungen bleiben unverändert
enthalten.

**Bewusst in Kauf genommen**, vom Kunden ausdrücklich bestätigt:

- kein nativer Ordner-Dialog — der Pfad zum Datenordner wird als Text eingetragen
- die Anwendung öffnet sich im Browser
- beim ersten Start ist eine einmalige Firewall-Abfrage möglich
- die Einrichtung läuft über ein Skript statt über ein Installationsprogramm.
  Für den Kunden unproblematisch — er richtet seine Rechner selbst ein.

**Ausdrücklich festgehalten:** Der Kunde wurde darauf hingewiesen, dass dies eine
langfristige Festlegung ist. Ein späterer Wechsel auf eine native Anwendung
kostet die Frontend-Arbeit ein zweites Mal; die bis dahin gebaute
Streamlit-Oberfläche wäre verloren. Er hat die Entscheidung in Kenntnis dieses
Umstands getroffen.

**Korrektur zum Eintrag vom 26.08.:** Die Planung führte als stärkstes Argument
gegen Streamlit an, `st.file_uploader` liefere nie den Pfad einer Datei, weshalb
das Zurückschreiben der bearbeiteten CSV prinzipiell unmöglich sei. Das trifft
für eine Upload-Architektur zu, nicht für diese Anwendung: Sie lädt nichts hoch,
sondern liest über `DATA_ROOT` aus dem Datenordner und schreibt dorthin zurück.
Der Pfad ist bekannt. Tatsächlich fehlt nur der native Dialog zum einmaligen
Festlegen dieses Ordners.

**Alternativen:** Umbau wie in Angebot 001 vorgesehen. Verworfen wegen des
Preises, nachdem der Kunde die Einschränkungen der günstigeren Variante
akzeptiert hat.

**Konsequenzen:**

- Planung 1 und Planung 2 verlieren ihre Prämisse und werden überarbeitet.
- Der Qt-Entwurf (`demo/qt_mockup.py`) bleibt als Gestaltungsreferenz erhalten —
  Palette und Kartenaufbau sind für das Streamlit-Theme weiter brauchbar. Er ist
  keine Umsetzungsplanung mehr.
- Der CSV-Editor entsteht mit `st.data_editor` statt mit einem eigenen
  Tabellenmodell. Weil dieser Weg über pandas läuft, muss beim Laden und
  Zurückschreiben die Typumwandlung unterbunden werden; der Round-Trip-Test aus
  Planung 2 sichert genau das ab.
- Der Ort für den Pfad zum Datenordner bleibt unverändert nötig: eine
  maschinenlokale Datei unter `%LOCALAPPDATA%` (nicht im Roaming-Zweig
  `%APPDATA%` — der Pfad ist je Rechner verschieden und darf nicht mitwandern),
  außerhalb des Repos, damit ein `git pull` sie nicht berührt.
- Word bleibt für die PDF-Erzeugung gesetzt; an diesem Pfad ändert sich nichts.
- Bestätigt beim Kunden: drei Rechner, ggf. bald ein vierter, alle mit Windows
  und Word; einziger Nutzer; die CSV bleibt die Schnittstelle zur selbstgebauten
  Handy-App.

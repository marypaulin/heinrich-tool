# Pfade pro Rechner in `settings.json`

Datum: 2026-10-27

Status: angenommen

**Kontext:** `config.json` lag im Wurzelverzeichnis des Klons, `Vordruck.docx`
unter `templates/`, beide gitignored. Die App fand sie relativ zum Ort ihres
Quellcodes, der Datenordner stand als `DATA_ROOT` in der Config. Damit hingen
Geschäftsdaten an der Installation:

- Das Setup-Skript legt einen frischen Klon an, ohne Config und Vordruck. Eine
  Neuinstallation verliert beide.
- Jeder Rechner hält eine eigene Kopie. Ein geänderter Stundensatz muss auf
  allen Rechnern nachgetragen werden, sonst rechnen sie unterschiedlich.
- Um die Config zu bearbeiten, muss Max in den Installationsordner.

**Entscheidung:** Config und Vordruck liegen wie der Datenordner in OneDrive
und stehen damit auf jedem Rechner bereit. Wo die drei auf dem jeweiligen
Rechner liegen, hält eine rechnerlokale `settings.json` fest. Max trägt die
Pfade einmal pro Rechner im Block „Pfade“ der App ein.

*Ablageort unter Windows.* Windows kennt zwei Orte für benutzerbezogene
Anwendungsdaten. `%APPDATA%` (`C:\Users\<Name>\AppData\Roaming`) ist für
Einstellungen gedacht, die einem Benutzer auf jeden Rechner folgen sollen: In
Netzwerken mit servergespeicherten Profilen (Roaming Profiles) wird dieser
Ordner bei jeder Anmeldung mitgenommen. `%LOCALAPPDATA%`
(`C:\Users\<Name>\AppData\Local`) bleibt dagegen auf dem einen Rechner. Die
Pfade in `settings.json` gelten nur für diesen Rechner, denn der
OneDrive-Ordner liegt nicht überall unter demselben Pfad, schon weil der
Benutzername darin steckt. Wanderte die Datei mit, stünden auf dem zweiten
Rechner die Pfade des ersten. Deshalb `%LOCALAPPDATA%`; ob Roaming Profiles im
Einsatz sind, spielt damit keine Rolle.

*Ablageort unter Linux.* Linux kennt diese Trennung nicht. Benutzerkonfiguration
liegt nach der XDG-Konvention in `$XDG_CONFIG_HOME`, ist die Variable nicht
gesetzt, in `~/.config`. Auf dem Entwicklungsrechner liegt die Datei damit in
`~/.config/HeinrichTool/settings.json`.

*Auflösung im Code.* Den Ordner bestimmt die Bibliothek `platformdirs`, nicht
eigener Code: `user_config_dir("HeinrichTool", appauthor=False)` liefert je
Betriebssystem den passenden Ort, unter Windows `%LOCALAPPDATA%\HeinrichTool`,
unter Linux `~/.config/HeinrichTool`. So läuft derselbe Code bei Max und auf
dem Entwicklungsrechner ohne Fallunterscheidung. Zwei Parameter sind bewusst
gewählt: `roaming` bleibt auf dem Default `False`, sonst läge die Datei in
`%APPDATA%`. `appauthor=False` verhindert, dass Windows eine zweite
Ordnerebene für den Hersteller einschiebt (`HeinrichTool\HeinrichTool`).

*Ablauf.* Fehlt die Datei, liefert `read_settings` `None`: Die App öffnet den
Block „Pfade“ und sperrt die Dokumente, das CLI bricht mit Hinweis ab.
`input_args.create_settings` entfernt die Anführungszeichen, die „Als Pfad
kopieren“ im Explorer mitliefert, und prüft vor dem Speichern, ob alle drei
Pfade existieren.

**Alternativen:**

- *Nur den Datenordner speichern, Config und Vordruck an festem Ort darin.* So
  war es ursprünglich geplant. Verworfen aus zwei Gründen. Die Ablage soll Max
  überlassen bleiben: neben den Projektordnern, in einem eigenen Unterordner
  oder an getrennten Orten in OneDrive. Und ein einzelner Pfad, aus dem die App
  die übrigen Dateien stillschweigend ableitet, versteckt Voraussetzungen. Mit
  drei Feldern ist alles, was die App zum Arbeiten braucht, in der Oberfläche
  sichtbar und wird einzeln geprüft; fehlt eine Datei, nennt die Meldung genau
  diese.
- *Config ins Repo, nur die Stundensätze in eine lokale Datei (etwa `.env`).*
  Verworfen. Der Vordruck enthält ebenfalls Geschäftsdaten und braucht ohnehin
  einen Ort außerhalb des öffentlichen Repos. Eine lokale Datei pro Rechner
  bringt die abweichenden Kopien zurück. Und Sätze, Texte und Dateinamen in der
  Config sind Max' Sache: Liegt sie in OneDrive, ändert er sie selbst, ohne
  Update und ohne Zugriff auf den Installationsordner.

**Konsequenzen:**

- Auf jedem neuen Rechner die drei Pfade einmal eintragen.
- `DATA_ROOT` ist aus der Config entfallen; ein verbliebener Eintrag wird
  ignoriert.
- Eine `settings.json` mit fehlendem Schlüssel wirft einen `KeyError`, den
  weder App noch CLI abfangen. Die Datei schreibt nur die App, das Risiko ist
  gering.

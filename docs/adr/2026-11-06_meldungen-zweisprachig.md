# Meldungen deutsch, Fehler und Logging englisch

Datum: 2026-11-06

Status: angenommen

**Kontext:** `2026-11-04_meldungen-auf-deutsch.md` sah vor, alle Meldungen
auf Deutsch umzustellen. Umgesetzt ist es nicht: `Messages` sind deutsch,
Logging und die Texte eigener Exceptions englisch, die App zeigt Fehler mit
dem englischen Text.

**Entscheidung:** Die Aufteilung bleibt, sie macht am bestehenden Code die
wenigste Arbeit. Exception-Texte müssen dafür ohne Englisch-Vorwissen
verständlich sein: Datei und Key nennen, keine Interna.

**Alternativen:**

- *Alles deutsch, ein Kanal über `Messages`.* Zurückgestellt; Umsetzung
  steht in `2026-11-04_meldungen-auf-deutsch.md`.

**Konsequenzen:**

- Manches meldet das Backend doppelt, per `logger` und per `Messages`.
- Die Einstiegspunkte loggen keine Tracebacks; ohne Logdatei läse sie
  niemand.

**Nachtrag 2026-11-09:** Der Kunde hat bestätigt, dass der Mix aus deutschen
und englischen Meldungen im UI so in Ordnung ist.

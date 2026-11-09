# Architecture Decision Records

Kurze, chronologisch sortierte Einträge zu Entscheidungen, deren Begründung
später nicht mehr offensichtlich ist (Architektur, Tooling, Scope-Schnitte).
Kein Prozess-Overhead — nur schreiben, wenn die Entscheidung wirklich Bestand
haben soll.

Ein Eintrag pro Datei, `YYYY-MM-DD_kurzer-titel.md`, Format:

```markdown
# Titel

Datum: YYYY-MM-DD

Status: vorgeschlagen | angenommen | abgelöst

**Kontext:** Was war die Ausgangslage / das Problem?

**Entscheidung:** Was wurde entschieden?

**Alternativen:** Was wurde verworfen, und warum?

**Konsequenzen:** Was folgt daraus (auch: was wird dadurch bewusst in Kauf
genommen)?
```

`Status:` sagt, woran man ist — *vorgeschlagen* (angeboten, noch nicht
entschieden), *angenommen* (gilt), *abgelöst* (überholt, mit Verweis auf den
Nachfolger). Ein abgelöster Eintrag wird **nicht gelöscht**: Die Begründung ist
der Grund, warum es den Log gibt.

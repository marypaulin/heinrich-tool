# ty als Typechecker

Datum: 2026-11-09

Status: angenommen

**Kontext:** Das Projekt ist durchgehend annotiert (pydantic-Modelle, frozen
dataclasses, `Decimal` für Geldbeträge), aber nichts prüft die Annotationen.
Fehler wie ein `float` statt `Decimal` oder ein `None`, das nicht abgefangen
wird, fallen erst in Tests oder im Dokument auf.

**Entscheidung:** ty von Astral, global installiert wie ruff
(`uv tool install ty`), aufgerufen als `ty check`. Läuft vor Commits, die
`.py`-Dateien berühren, neben `ruff check .` und pytest. Keine Konfiguration
in `pyproject.toml`: Die Standardwerte reichen, die Python-Version liest ty
aus `requires-python`.

**Alternativen:**

- *mypy.* Die Referenz, aber deutlich langsamer und mit eigener
  Konfigurationswelt.
- *pyright.* Ausgereift und die Engine hinter Pylance, bringt aber Node als
  Laufzeit mit.

ty passt zur übrigen Toolchain (uv, ruff) und ist schnell genug für jeden
Commit.

**Konsequenzen:**

- ty ist vor 1.0 (eingeführt mit 0.0.99). Ein Update kann neue Befunde
  bringen, ohne dass sich der Code geändert hat; dann zuerst die ty-Version
  prüfen.
- Kein Lauf im Edit-Hook: Typfehler reichen über Dateigrenzen, während eines
  Umbaus sind Aufrufer vorübergehend rot.

"""User-facing message accumulator for status and warning output."""

from dataclasses import dataclass, field


@dataclass
class Messages:
    items: list[str] = field(default_factory=list)

    def info(self, text: str) -> None:
        self.items.append(f"Info: {text}")

    def warning(self, text: str) -> None:
        self.items.append(f"Achtung: {text}")

    def error(self, text: str) -> None:
        self.items.append(f"Fehler: {text}")

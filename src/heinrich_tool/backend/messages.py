"""User-facing message accumulator for status and warning output."""

from dataclasses import dataclass, field
from enum import Enum


class Level(Enum):
    INFO = "Info"
    WARNING = "Achtung"
    ERROR = "Fehler"


@dataclass(frozen=True)
class Message:
    level: Level
    text: str

    def __str__(self) -> str:
        return f"{self.level.value}: {self.text}"


@dataclass
class Messages:
    items: list[Message] = field(default_factory=list)

    def info(self, text: str) -> None:
        self.items.append(Message(Level.INFO, text))

    def warning(self, text: str) -> None:
        self.items.append(Message(Level.WARNING, text))

    def error(self, text: str) -> None:
        self.items.append(Message(Level.ERROR, text))

    @property
    def has_errors(self) -> bool:
        return any(message.level is Level.ERROR for message in self.items)

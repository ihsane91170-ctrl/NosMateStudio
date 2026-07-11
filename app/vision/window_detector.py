from __future__ import annotations

from dataclasses import dataclass

import pygetwindow as gw


@dataclass(frozen=True, slots=True)
class GameWindow:
    title: str
    left: int
    top: int
    width: int
    height: int

    @property
    def right(self) -> int:
        return self.left + self.width

    @property
    def bottom(self) -> int:
        return self.top + self.height

    @property
    def center(self) -> tuple[int, int]:
        return (
            self.left + self.width // 2,
            self.top + self.height // 2,
        )

    @property
    def is_usable(self) -> bool:
        return self.width > 0 and self.height > 0


class WindowDetector:
    def __init__(self, title_contains: str = "NosTale") -> None:
        self.title_contains = title_contains.strip()

    def detect(self) -> GameWindow | None:
        needle = self.title_contains.casefold()

        for window in gw.getAllWindows():
            title = str(getattr(window, "title", "") or "").strip()

            if not title or needle not in title.casefold():
                continue

            return GameWindow(
                title=title,
                left=int(getattr(window, "left", 0) or 0),
                top=int(getattr(window, "top", 0) or 0),
                width=int(getattr(window, "width", 0) or 0),
                height=int(getattr(window, "height", 0) or 0),
            )

        return None
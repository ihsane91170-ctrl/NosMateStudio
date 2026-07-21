from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from PIL import Image


class HpState(str, Enum):
    FULL = "FULL_HP"
    ONE = "ONE_HP"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True, slots=True)
class HpReadResult:
    state: HpState
    green_ratio: float
    red_ratio: float
    hp_box: tuple[int, int, int, int] | None


class HpStateReader:
    """Lit uniquement les PV du panneau de cible NosTale.

    Sur une capture complète, le panneau joueur se trouve à gauche tandis que
    le panneau de la cible se trouve dans la partie haute centrale. Le lecteur
    exclut donc explicitement le HUD joueur, localise la barre MP bleue de la
    cible, puis analyse la barre HP située juste au-dessus.

    Les petites images déjà recadrées sur le panneau cible restent supportées,
    ce qui permet de conserver des tests simples et déterministes.
    """

    def __init__(
        self,
        *,
        target_left_ratio: float = 0.28,
        target_right_ratio: float = 0.70,
        search_height: int = 145,
        minimum_blue_run: int = 70,
    ) -> None:
        self._target_left_ratio = target_left_ratio
        self._target_right_ratio = target_right_ratio
        self._search_height = search_height
        self._minimum_blue_run = minimum_blue_run

    def search_box(self, image: Image.Image) -> tuple[int, int, int, int]:
        """Retourne la zone du panneau cible, jamais celle du joueur."""
        if image.width <= 500:
            return (0, 0, image.width, min(image.height, self._search_height))

        left = int(image.width * self._target_left_ratio)
        right = int(image.width * self._target_right_ratio)
        return (left, 0, right, min(image.height, self._search_height))

    def read(self, image: Image.Image) -> HpReadResult:
        rgb = image.convert("RGB")
        search_left, search_top, search_right, search_bottom = self.search_box(rgb)

        best_y = -1
        best_start = -1
        best_end = -1

        for y in range(search_top, search_bottom):
            x = search_left
            while x < search_right:
                if not self._is_blue(rgb.getpixel((x, y))):
                    x += 1
                    continue

                start = x
                while x + 1 < search_right and self._is_blue(rgb.getpixel((x + 1, y))):
                    x += 1
                end = x

                if end - start > best_end - best_start:
                    best_y = y
                    best_start = start
                    best_end = end
                x += 1

        run_length = best_end - best_start + 1
        if best_y < 0 or run_length < self._minimum_blue_run:
            return HpReadResult(HpState.UNKNOWN, 0.0, 0.0, None)

        # La barre HP se situe environ 20 px au-dessus de la barre MP.
        hp_center_y = best_y - 20
        top = max(search_top, hp_center_y - 5)
        bottom = min(search_bottom - 1, hp_center_y + 5)
        left = best_start
        right = best_end

        if bottom <= top or right <= left:
            return HpReadResult(HpState.UNKNOWN, 0.0, 0.0, None)

        green = 0
        red = 0
        total = 0
        for y in range(top, bottom + 1):
            for x in range(left, right + 1):
                pixel = rgb.getpixel((x, y))
                total += 1
                green += int(self._is_green(pixel))
                red += int(self._is_red(pixel))

        green_ratio = green / total if total else 0.0
        red_ratio = red / total if total else 0.0
        hp_box = (left, top, right, bottom)

        # Barre pleine : remplissage vert/jaune-vert nettement majoritaire.
        if green_ratio >= 0.28:
            state = HpState.FULL
        # À 1 PV : presque aucun vert, mais le minuscule reliquat rouge existe.
        elif green_ratio < 0.25 and red_ratio >= 0.001:
            state = HpState.ONE
        else:
            state = HpState.UNKNOWN

        return HpReadResult(state, green_ratio, red_ratio, hp_box)

    @staticmethod
    def _is_blue(pixel: tuple[int, int, int]) -> bool:
        r, g, b = pixel
        return b >= 85 and b > r * 1.20 and b > g * 1.04

    @staticmethod
    def _is_green(pixel: tuple[int, int, int]) -> bool:
        r, g, b = pixel
        # Inclut le vert vif et le jaune-vert de la barre pleine.
        return g >= 90 and g > b * 1.08 and g >= r * 0.78

    @staticmethod
    def _is_red(pixel: tuple[int, int, int]) -> bool:
        r, g, b = pixel
        return r >= 85 and r > g * 1.20 and r > b * 1.20

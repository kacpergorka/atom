#
#     ▄▄     ▄▄▄▄▄▄▄▄    ▄▄▄▄    ▄▄▄  ▄▄▄               ▄▄     ▄▄▄▄▄▄     ▄▄▄▄▄▄
#    ████    ▀▀▀██▀▀▀   ██▀▀██   ███  ███              ████    ██▀▀▀▀█▄   ▀▀██▀▀
#    ████       ██     ██    ██  ████████              ████    ██    ██     ██
#   ██  ██      ██     ██    ██  ██ ██ ██             ██  ██   ██████▀      ██
#   ██████      ██     ██    ██  ██ ▀▀ ██             ██████   ██           ██
#  ▄██  ██▄     ██      ██▄▄██   ██    ██            ▄██  ██▄  ██         ▄▄██▄▄
#  ▀▀    ▀▀     ▀▀       ▀▀▀▀    ▀▀    ▀▀            ▀▀    ▀▀  ▀▀         ▀▀▀▀▀▀
#

# Standardowe biblioteki
from datetime import datetime
import random
from zoneinfo import ZoneInfo

# Wewnętrzne importy
from src.classes.types.numbers import SzczęśliweNumerki
from src.handlers.logging import logowanie

async def wygenerujSzczęśliweNumerki(dzieńWolny: bool) -> SzczęśliweNumerki:
    """
    Generuje szczęśliwe numerki dla bieżącego dnia, jeżeli nie jest to dzień wolny od zajęć.

    Args:
        dzieńWolny (bool): Flaga informująca, czy bieżący dzień jest wolny od zajęć.

    Returns:
        SzczęśliweNumerki: Słownik z datą, numerkami oraz opcjonalną informacją o dniu wolnym.
    """
    try:
        dzisiaj = datetime.now(ZoneInfo("Europe/Warsaw")).date()
        dzisiejszaData = dzisiaj.isoformat()

        if dzieńWolny:
            return SzczęśliweNumerki(
                data=dzisiejszaData,
                numerki=None,
                informacja="Dzień wolny od zajęć."
            )

        szczęśliweNumerki = SzczęśliweNumerki(
            data=dzisiejszaData,
            numerki=tuple(random.sample(range(1, 36), 2)),
            informacja=None
        )

        return szczęśliweNumerki
    except Exception as e:
        logowanie.exception(
            f"Wystąpił błąd podczas generowania numerków. Więcej informacji: {e}"
        )
        return SzczęśliweNumerki(
            data=dzisiejszaData,
            numerki=None,
            informacja="Wystąpił niespodziewany błąd. Spróbuj ponownie poźniej."
        )

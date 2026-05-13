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
from zoneinfo import ZoneInfo

# Wewnętrzne importy
from src.api.exceptions import (
    BłądWewnętrzny,
    BrakWymaganychDanych
)
from src.handlers.cache import (
    pobierzModel,
    zapiszModel
)
from src.handlers.configuration import konfiguracja
from src.handlers.holidays.checker import sprawdźCzyDzisiajJestWolne
from src.handlers.logging import logowanie
from src.handlers.numbers import database
from src.handlers.numbers.generator import wygenerujSzczęśliweNumerki
from src.schemas.numbers import SzczęśliweNumerki

strefaCzasowa = ZoneInfo("Europe/Warsaw")

async def pobierzSzczęśliweNumerki() -> SzczęśliweNumerki:
    """
    Pobiera i przetwarza szczęśliwe numerki.

    Returns:
        SzczęśliweNumerki: Słownik zawierający datę, szczęśliwe numerki i informację.

    Raises:
        BłądWewnętrzny: Gdy wystąpi nieoczekiwany błąd przetwarzania.
        BrakWymaganychDanych: Gdy w pliku konfiguracyjnym nie znajdują się wymagane dane.
    """

    try:
        szkoła = konfiguracja.get("szkola", {})
        url = szkoła.get("url")
        kodowanie = szkoła.get("kodowanie")

        if not url or not kodowanie:
            logowanie.warning(
                "Brak wymaganych danych w pliku konfiguracyjnym. Uzupełnij brakujące dane i spróbuj ponownie."
            )
            raise BrakWymaganychDanych

        dzisiaj = datetime.now(strefaCzasowa).date()
        dzisiejszaData = dzisiaj.isoformat()

        kluczCache = f"cache:numerki:{dzisiejszaData}"
        cacheNumerków = await pobierzModel(kluczCache, SzczęśliweNumerki)

        if cacheNumerków is not None:
            return cacheNumerków

        zapisaneNumerki = await database.pobierzSzczęśliweNumerki(dzisiejszaData)

        if zapisaneNumerki is not None:
            await zapiszModel(kluczCache, zapisaneNumerki)
            return zapisaneNumerki

        dzieńWolny = await sprawdźCzyDzisiajJestWolne(url, kodowanie, dzisiaj)

        szczęśliweNumerki = SzczęśliweNumerki.model_validate(
            await wygenerujSzczęśliweNumerki(dzieńWolny)
        )

        await database.zapiszSzczęśliweNumerki(szczęśliweNumerki)
        await zapiszModel(kluczCache, szczęśliweNumerki)

        return szczęśliweNumerki
    except BrakWymaganychDanych:
        raise
    except Exception as e:
        logowanie.exception(
            f"Wystąpił błąd podczas przetwarzania danych. Więcej informacji: {e}"
        )
        raise BłądWewnętrzny from e

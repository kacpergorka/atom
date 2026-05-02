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
from datetime import (
    datetime,
    time,
    timedelta
)
from zoneinfo import ZoneInfo

# Wewnętrzne importy
from src.api.endpoints.universal.numbers.schemas import UniwersalneSzczesliweNumerki
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
from src.handlers.numbers.generator import wygenerujSzczęśliweNumerki

strefaCzasowa = ZoneInfo("Europe/Warsaw")

async def pobierzSzczęśliweNumerki() -> UniwersalneSzczesliweNumerki:
    """
    Pobiera i przetwarza szczęśliwe numerki.

    Returns:
        UniwersalneSzczesliweNumerki: Słownik zawierający datę, szczęśliwe numerki i informcję.

    Raises:
        BłądWewnętrzny: Gdy wystąpi nieoczekiwany błąd przetwarzania.
        BrakWymaganychDanych: Gdy w pliku konfiguracyjnym nie znajdują się wymagane dane.
    """

    def obliczCzasDoKońcaDnia() -> int:
        """
        Oblicza czas życia cache do końca bieżącego dnia.

        Returns:
            int: Liczba sekund pozostałych do północy, minimum jedna sekunda.
        """

        teraz = datetime.now(strefaCzasowa)
        jutro = datetime.combine(
            teraz.date() + timedelta(days=1),
            time.min,
            tzinfo=strefaCzasowa
        )
        return max(1, int((jutro - teraz).total_seconds()))

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
        cacheNumerków = await pobierzModel(kluczCache, UniwersalneSzczesliweNumerki)

        if cacheNumerków is not None:
            return cacheNumerków

        dzieńWolny = await sprawdźCzyDzisiajJestWolne(url, kodowanie, dzisiaj)
        szczęśliweNumerki = UniwersalneSzczesliweNumerki.model_validate(
            await wygenerujSzczęśliweNumerki(dzieńWolny)
        )

        await zapiszModel(kluczCache, szczęśliweNumerki, obliczCzasDoKońcaDnia())
        return szczęśliweNumerki
    except BrakWymaganychDanych:
        raise
    except Exception as e:
        logowanie.exception(
            f"Wystąpił błąd podczas przetwarzania danych. Więcej informacji: {e}"
        )
        raise BłądWewnętrzny from e

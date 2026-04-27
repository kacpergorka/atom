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
from src.classes.atom import atom
from src.classes.semaphore import semafor
from src.handlers.cache import (
    pobierzModel,
    zapiszModel
)
from src.handlers.configuration import konfiguracja
from src.handlers.logging import logowanie
from src.handlers.numbers.generator import wygenerujSzczęśliweNumerki
from src.handlers.scraper import pobierzZawartośćStrony

strefaCzasowa = ZoneInfo("Europe/Warsaw")

async def pobierzDaneŚwiąt(dzisiejszaData: str) -> tuple[list[dict[str, str]] | None, list[dict[str, str]] | None]:
    """
    Pobiera dane o świętach szkolnych i publicznych z OpenHolidays API.

    Args:
        dzisiejszaData (str): Data w formacie ISO używana jako początek i koniec zakresu zapytania.

    Returns:
        tuple[list[dict[str, str]] | None, list[dict[str, str]] | None]: Dane świąt publicznych i szkolnych albo `None`, jeśli zewnętrzne API jest niedostępne.
    """

    try:
        urlŚwiętaSzkolne = "https://openholidaysapi.org/SchoolHolidays"
        urlŚwiętaPubliczne = "https://openholidaysapi.org/PublicHolidays"
        parametryOpenHolidays = {
            "countryIsoCode": "PL",
            "validFrom": dzisiejszaData,
            "validTo": dzisiejszaData,
            "languageIsoCode": "PL",
            "subdivisionCode": "PL-KP"
        }

        async with semafor:
            async with atom.sesja.get(urlŚwiętaPubliczne, params=parametryOpenHolidays) as odpowiedźŚwiątPublicznych:
                if odpowiedźŚwiątPublicznych.status != 200:
                    daneŚwiątPublicznych = None
                else:
                    daneŚwiątPublicznych = await odpowiedźŚwiątPublicznych.json()

        async with semafor:
            async with atom.sesja.get(urlŚwiętaSzkolne, params=parametryOpenHolidays) as odpowiedźŚwiątSzkolnych:
                if odpowiedźŚwiątSzkolnych.status != 200:
                    daneŚwiątSzkolnych = None
                else:
                    daneŚwiątSzkolnych = await odpowiedźŚwiątSzkolnych.json()

        return daneŚwiątPublicznych, daneŚwiątSzkolnych
    except Exception as e:
        logowanie.exception(f"Wystąpił błąd. Nie udało się pobrać danych z OpenHolidays API. Więcej informacji: {e}")
        return None, None


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

        daneŚwiątPublicznych, daneŚwiątSzkolnych = await pobierzDaneŚwiąt(dzisiejszaData)

        parametry = {
            "co": "10",
            "funk": "2",
            "umbcal[mode]": "tooltip",
            "umbcal[year]": dzisiaj.year,
            "umbcal[month]": dzisiaj.month,
            "umbcal[day]": dzisiaj.day
        }

        try:
            async with semafor:
                zawartośćStrony = await pobierzZawartośćStrony(atom.sesja, url, kodowanie, parametry)
        except Exception as e:
            logowanie.exception(f"Wystąpił błąd. Nie udało się pobrać danych ze strony internetowej szkoły. Więcej informacji: {e}")
            zawartośćStrony = None

        szczęśliweNumerki = UniwersalneSzczesliweNumerki.model_validate(
            await wygenerujSzczęśliweNumerki(zawartośćStrony, daneŚwiątPublicznych, daneŚwiątSzkolnych)
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

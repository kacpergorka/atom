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
    date,
    datetime
)
import unicodedata
from zoneinfo import ZoneInfo

# Zewnętrzne biblioteki
from bs4 import BeautifulSoup

# Wewnętrzne importy
from src.classes.atom import atom
from src.classes.semaphore import semafor
from src.handlers.logging import logowanie
from src.handlers.scraper import pobierzZawartośćStrony

strefaCzasowa = ZoneInfo("Europe/Warsaw")

async def sprawdźCzyDzisiajJestWolne(
    url: str | None,
    kodowanie: str | None,
    dzisiaj: date | None = None
) -> bool:
    """
    Sprawdza, czy bieżący dzień jest dniem wolnym od zajęć.

    Args:
        url (str | None): Adres szkolnej strony kalendarza.
        kodowanie (str | None): Kodowanie używane przez szkolną stronę kalendarza.
        dzisiaj (date | None): Data do sprawdzenia. Domyślnie bieżąca data w strefie Warszawa.

    Returns:
        bool: `True`, jeśli udało się rozpoznać dzień wolny od zajęć.
    """

    def sprawdźZakresWydarzeń(
        listaWydarzeń: list[dict[str, str]] | None,
        dzisiaj: date
    ) -> bool:
        """
        Sprawdza, czy podana data znajduje się w zakresie któregoś wydarzenia.

        Args:
            listaWydarzeń (list[dict[str, str]] | None): Lista wydarzeń.
            dzisiaj (date): Data, która ma zostać porównana z zakresami wydarzeń.

        Returns:
            bool: `True`, jeśli data mieści się w którymś zakresie, w przeciwnym razie `False`.
        """

        if not listaWydarzeń:
            return False

        try:
            for wydarzenie in listaWydarzeń:
                dataStart = datetime.fromisoformat(wydarzenie["startDate"]).date()
                dataKoniec = datetime.fromisoformat(wydarzenie["endDate"]).date()

                if dataStart <= dzisiaj <= dataKoniec:
                    return True

            return False
        except Exception as e:
            logowanie.exception(
                f"Wystąpił błąd podczas sprawdzania zakresu dat. Więcej informacji: {e}"
            )
            return False

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
            logowanie.exception(
                f"Wystąpił błąd. Nie udało się pobrać danych z OpenHolidays API. Więcej informacji: {e}"
                )
            return None, None

    def sprawdźCzyDzieńJestWolny(
        dzisiaj: date,
        zawartośćStrony: BeautifulSoup | None,
        daneŚwiątPublicznych: list[dict[str, str]] | None,
        daneŚwiątSzkolnych: list[dict[str, str]] | None
    ) -> bool:
        """
        Sprawdza, czy dzień jest wolny od zajęć na podstawie kalendarza i danych świąt.

        Args:
            dzisiaj (date): Dzień, który ma zostać sprawdzony.
            zawartośćStrony (BeautifulSoup | None): Zawartość szkolnego kalendarza dla tego dnia.
            daneŚwiątPublicznych (list[dict[str, str]] | None): Dane świąt publicznych z OpenHolidays API.
            daneŚwiątSzkolnych (list[dict[str, str]] | None): Dane świąt szkolnych z OpenHolidays API.

        Returns:
            bool: `True`, jeśli to dzień wolny od zajęć.
        """

        if dzisiaj.weekday() >= 5:
            return True

        if (
            sprawdźZakresWydarzeń(daneŚwiątSzkolnych, dzisiaj)
            or sprawdźZakresWydarzeń(daneŚwiątPublicznych, dzisiaj)
        ):
            return True

        if zawartośćStrony:
            tekstSurowy = str(zawartośćStrony).lower()
            tekstWydarzenia = unicodedata.normalize("NFKD", tekstSurowy).encode("ascii", "ignore").decode()

            if "dzien wolny" in tekstWydarzenia:
                return True

        return False

    if dzisiaj is None:
        dzisiaj = datetime.now(strefaCzasowa).date()

    if dzisiaj.weekday() >= 5:
        return True

    dzisiejszaData = dzisiaj.isoformat()
    daneŚwiątPublicznych, daneŚwiątSzkolnych = await pobierzDaneŚwiąt(dzisiejszaData)

    zawartośćStrony = None

    if url and kodowanie:
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
            logowanie.exception(
                f"Wystąpił błąd. Nie udało się pobrać danych ze strony internetowej szkoły. Więcej informacji: {e}"
            )
    else:
        logowanie.warning(
            "Brak danych potrzebnych do pobrania szkolnego kalendarza. Pomijanie sprawdzania strony przy ustalaniu dnia wolnego."
        )

    return sprawdźCzyDzieńJestWolny(dzisiaj, zawartośćStrony, daneŚwiątPublicznych, daneŚwiątSzkolnych)

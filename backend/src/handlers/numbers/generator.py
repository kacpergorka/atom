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
from bs4 import BeautifulSoup
from datetime import (
    date,
    datetime
)
import random
import unicodedata
from zoneinfo import ZoneInfo

# Wewnętrzne importy
from src.classes.types.numbers import SzczęśliweNumerki
from src.handlers.logging import logowanie

async def wygenerujSzczęśliweNumerki(
    zawartośćStrony: BeautifulSoup | None,
    daneŚwiątPublicznych: list[dict[str, str]] | None,
    daneŚwiątSzkolnych: list[dict[str, str]] | None
) -> SzczęśliweNumerki:
    """
    Generuje szczęśliwe numerki dla bieżącego dnia, jeżeli nie jest to dzień wolny od zajęć.

    Args:
        zawartośćStrony (BeautifulSoup | None): Obiekt BeautifulSoup reprezentujący stronę HTML szkolnego kalendarza dla bieżącego dnia.
        daneŚwiątPublicznych (list[dict[str, str]] | None): Dane świąt publicznych pobrane z OpenHolidays API.
        daneŚwiątSzkolnych (list[dict[str, str]] | None): Dane przerw i świąt szkolnych pobrane z OpenHolidays API.

    Returns:
        SzczęśliweNumerki: Słownik z datą, numerkami oraz opcjonalną informacją o dniu wolnym.
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

    try:
        dzisiaj = datetime.now(ZoneInfo("Europe/Warsaw")).date()
        dzisiejszaData = dzisiaj.isoformat()

        if dzisiaj.weekday() >= 5:
            return SzczęśliweNumerki(
                data=dzisiejszaData,
                numerki=None,
                informacja="Dzień wolny od zajęć."
            )

        if (
            sprawdźZakresWydarzeń(daneŚwiątSzkolnych, dzisiaj)
            or sprawdźZakresWydarzeń(daneŚwiątPublicznych, dzisiaj)
        ):
            return SzczęśliweNumerki(
                data=dzisiejszaData,
                numerki=None,
                informacja="Dzień wolny od zajęć."
            )

        if zawartośćStrony:
            tekstSurowy = str(zawartośćStrony).lower()
            tekstWydarzenia = unicodedata.normalize("NFKD", tekstSurowy).encode("ascii", "ignore").decode()

            if "dzien wolny" in tekstWydarzenia:
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

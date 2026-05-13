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
from operator import itemgetter
import re
from urllib.parse import (
    urljoin,
    urlparse
)

# Zewnętrzne biblioteki
import aiohttp
from bs4 import BeautifulSoup

# Wewnętrzne importy
from src.handlers.configuration import konfiguracja
from src.handlers.helpers import posortujNauczycieli
from src.handlers.lists.resolver import uzupełnijBrakująceOddziały
from src.handlers.logging import logowanie
from src.schemas.lists import Listy

async def wyodrębnijListy(
    klientAtom: aiohttp.ClientSession,
    zawartośćStrony: BeautifulSoup,
    url: str | None
) -> Listy:
    """
    Wyodrębnia listy oddziałów, nauczycieli oraz sal z pliku strony internetowej.

    Args:
        klientAtom (aiohttp.ClientSession): Aktywna sesja HTTP używana do wykonania zapytania.
        zawartośćStrony (BeautifulSoup): Obiekt BeautifulSoup reprezentujący stronę HTML.
        url (str | None): Adres strony internetowej zawierającej listy użyty do pobrania ich zawartości.

    Returns:
        Listy: Słownik zawierający listy oddziałów, nauczycieli oraz sal.
    """

    def zwróćPusteListy() -> Listy:
        """
        Zwraca pustą strukturę list w standardowym formacie.

        Returns:
            Listy: Pusta struktura list.
        """
        return {
            "oddzialy": [],
            "nauczyciele": [],
            "sale": [],
        }

    def wyodrębnijNumerOddziału(identyfikator: str | None) -> int | None:
        """
        Wyodrębnia numer z identyfikatora oddziału.

        Args:
            identyfikator (str | None): Identyfikator oddziału, np. o17.

        Returns:
            int | None: Numer oddziału albo `None`, jeśli identyfikator ma nieprawidłowy format.
        """

        if not isinstance(identyfikator, str):
            return None

        dopasowanie = re.fullmatch(r"o(\d+)", identyfikator.strip().lower())
        if not dopasowanie:
            return None

        return int(dopasowanie.group(1))

    def znajdźBrakująceIdentyfikatory(oddziały: list[dict[str, str]]) -> list[str]:
        """
        Zwraca identyfikatory oddziałów brakujące pomiędzy najniższym i najwyższym znalezionym numerem.

        Args:
            oddziały (list[dict[str, str]]): Lista oddziałów.

        Returns:
            list[str]: Lista brakujących identyfikatorów, np. ["o17"].
        """

        numery = {
            numer
            for element in oddziały
            if (numer := wyodrębnijNumerOddziału(element.get("identyfikator"))) is not None
        }

        if len(numery) < 2:
            return []

        return [
            f"o{numer}"
            for numer in range(min(numery), max(numery) + 1)
            if numer not in numery
        ]

    if not isinstance(url, str) or not url.startswith(("http://", "https://")):
        logowanie.warning(
            "Nieprawidłowy URL wejściowy. Zwracanie pustych zawartości."
        )
        return zwróćPusteListy()

    try:
        linki = zawartośćStrony.find_all("a", href=True)
        katalog = konfiguracja.get("plany", {}).get("url")
        oddziały: list[dict[str, str]] = []
        nauczyciele: list[dict[str, str]] = []
        sale: list[dict[str, str]] = []

        if not katalog or urlparse(url).netloc != urlparse(katalog).netloc:
            logowanie.warning(
                "Otrzymany URL nie zgadza się z wartością URL znajdującego się w pliku konfiguracyjnym. Zwracanie pustych zawartości."
            )
            return zwróćPusteListy()

        for link in linki:
            href = link.get("href", "")
            urlElementu = urljoin(katalog, href)
            ścieżka = urlparse(urlElementu).path
            identyfikator: str = ""

            surowyTekst = link.get_text(" ", strip=True)
            tekst = re.sub(r"\s+", " ", surowyTekst.replace(".", " "))

            if ścieżka:
                plik = ścieżka.rsplit("/", 1)[-1]
                identyfikator = plik.split(".", 1)[0] if "." in plik else plik

            if re.match(r"plany/o\d+\.html", href):
                dopasowanie = re.match(r"(\d)\s*([a-zA-Z])", tekst)

                if dopasowanie:
                    nazwa = f"{dopasowanie.group(1)} {dopasowanie.group(2).upper()}"
                    rozwinięcieOddziału = surowyTekst
                    części = link.get_text(strip=True).split()

                    if len(części) >= 2 and części[0] == części[1]:
                        rozwinięcieOddziału = " ".join([części[0]] + części[2:])

                    oddziały.append({
                        "url": urlElementu,
                        "identyfikator": identyfikator,
                        "nazwa": nazwa,
                        "rozwiniecie": rozwinięcieOddziału
                    })

            elif re.match(r"plany/n\d+\.html", href):
                dopasowanie = re.match(r"(\w)\s+([\w\-]+)", tekst, re.UNICODE)

                if dopasowanie:
                    nazwa = f"{dopasowanie.group(1).upper()}. {dopasowanie.group(2)}"

                    nauczyciele.append({
                        "url": urlElementu,
                        "identyfikator": identyfikator,
                        "nazwa": nazwa,
                        "rozwiniecie": surowyTekst
                    })

            elif re.match(r"plany/s\d+\.html", href):
                dopasowanie = re.match(r"(\w+)", tekst)

                if dopasowanie:
                    nazwa = dopasowanie.group(1).upper()

                    sale.append({
                        "url": urlElementu,
                        "identyfikator": identyfikator,
                        "nazwa": nazwa,
                        "rozwiniecie": surowyTekst
                    })

        brakująceIdentyfikatory = znajdźBrakująceIdentyfikatory(oddziały)
        if brakująceIdentyfikatory:
            oddziały = await uzupełnijBrakująceOddziały(klientAtom, oddziały, brakująceIdentyfikatory)

        oddziały.sort(key=itemgetter("nazwa"))
        sale.sort(key=itemgetter("nazwa"))
        nauczyciele.sort(key=posortujNauczycieli)

        return {
            "oddzialy": oddziały,
            "nauczyciele": nauczyciele,
            "sale": sale
        }
    except Exception as e:
        logowanie.exception(
            f"Wystąpił błąd podczas przetwarzania HTML listy. Więcej informacji: {e}"
        )
        return zwróćPusteListy()

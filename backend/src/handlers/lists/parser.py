#
#
#     ▄▄     ▄▄▄▄▄▄▄▄    ▄▄▄▄    ▄▄▄  ▄▄▄               ▄▄     ▄▄▄▄▄▄     ▄▄▄▄▄▄
#    ████    ▀▀▀██▀▀▀   ██▀▀██   ███  ███              ████    ██▀▀▀▀█▄   ▀▀██▀▀
#    ████       ██     ██    ██  ████████              ████    ██    ██     ██
#   ██  ██      ██     ██    ██  ██ ██ ██             ██  ██   ██████▀      ██
#   ██████      ██     ██    ██  ██ ▀▀ ██             ██████   ██           ██
#  ▄██  ██▄     ██      ██▄▄██   ██    ██            ▄██  ██▄  ██         ▄▄██▄▄
#  ▀▀    ▀▀     ▀▀       ▀▀▀▀    ▀▀    ▀▀            ▀▀    ▀▀  ▀▀         ▀▀▀▀▀▀
#
#

# Standardowe biblioteki
import re
from urllib.parse import (
    urljoin,
    urlparse
)

# Zewnętrzne biblioteki
from bs4 import BeautifulSoup

# Wewnętrzne importy
from src.classes.types import (
    Listy,
    ListaNauczycieli,
    ListaOddziałów,
    ListaSal
)
from src.handlers.configuration import konfiguracja
from src.handlers.logging import logowanie

def wyodrębnijListy(
    zawartośćStrony: BeautifulSoup | None,
    url: str | None
) -> Listy:
    """
    Wyodrębnia listy oddziałów, nauczycieli oraz sal z pliku strony internetowej.

    Args:
        zawartośćStrony (BeautifulSoup | None): Obiekt BeautifulSoup reprezentujący stronę HTML.
        url (str | None): Adres strony internetowej zawierającej listy użyty do pobrania ich zawartości.

    Returns:
        Listy: Słownik zawierający listy oddziałów, nauczycieli oraz sal.
    """

    if zawartośćStrony is None:
        logowanie.warning(
            "Brak treści pobranej ze strony. Zwracanie pustych zawartości."
        )
        return {
            "oddzialy": {},
            "nauczyciele": {},
            "sale": {},
        }

    if not isinstance(url, str) or not url.startswith(("http://", "https://")):
        logowanie.warning(
            "Nieprawidłowy URL wejściowy. Zwracanie pustych zawartości."
        )
        return {
            "oddzialy": {},
            "nauczyciele": {},
            "sale": {},
        }

    try:
        linki = zawartośćStrony.find_all("a", href=True)
        katalog = konfiguracja.get("plany", {}).get("url")
        oddziały: ListaOddziałów = {}
        nauczyciele: ListaNauczycieli = {}
        sale: ListaSal = {}

        if not katalog or urlparse(url).netloc != urlparse(katalog).netloc:
            logowanie.warning(
                "Otrzymany URL nie zgadza się z wartością URL znajdującego się w pliku konfiguracyjnym. Zwracanie pustych zawartości."
            )
            return {
                "oddzialy": {},
                "nauczyciele": {},
                "sale": {},
            }

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

                    if nazwa not in oddziały:
                        oddziały[nazwa] = {
                            "url": urlElementu,
                            "identyfikator": identyfikator,
                            "rozwiniecie": rozwinięcieOddziału
                        }

            elif re.match(r"plany/n\d+\.html", href):
                dopasowanie = re.match(r"(\w)\s+([\w\-]+)", tekst, re.UNICODE)

                if dopasowanie:
                    nazwa = f"{dopasowanie.group(1).upper()}. {dopasowanie.group(2)}"

                    if nazwa not in nauczyciele:
                        nauczyciele[nazwa] = {
                            "url": urlElementu,
                            "identyfikator": identyfikator,
                            "rozwiniecie": surowyTekst
                        }

            elif re.match(r"plany/s\d+\.html", href):
                dopasowanie = re.match(r"(\w+)", tekst)

                if dopasowanie:
                    nazwa = dopasowanie.group(1).upper()

                    if nazwa not in sale:
                        sale[nazwa] = {
                            "url": urlElementu,
                            "identyfikator": identyfikator,
                            "rozwiniecie": surowyTekst
                        }

        return {
            "oddzialy": oddziały,
            "nauczyciele": nauczyciele,
            "sale": sale
        }
    except Exception as e:
        logowanie.exception(
            f"Wystąpił błąd podczas przetwarzania HTML listy. Więcej informacji: {e}"
        )
        return {
            "oddzialy": {},
            "nauczyciele": {},
            "sale": {},
        }

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
from urllib.parse import (
    urljoin,
    urlparse
)

# Zewnętrzne biblioteki
import aiohttp

# Wewnętrzne importy
from src.classes.semaphore import semafor
from src.classes.types import EncjaPlanu
from src.handlers.configuration import konfiguracja
from src.handlers.timetables.helpers import (
    wydobądźIdentyfikator,
    zwróćPustySłownik
)
from src.handlers.scraper import pobierzZawartośćStrony
from src.handlers.logging import logowanie

async def uzupełnijNauczyciela(
    atom: aiohttp.ClientSession,
    url: str,
    dniTygodnia: list[str],
    dzień: str,
    numer: int
) -> EncjaPlanu:
    """
    Uzupełnia dane nauczyciela dla konkretnej lekcji w planie oddziału na podstawie URL do strony planu lekcji sali.

    Args:
        atom (aiohttp.ClientSession): Aktywna sesja HTTP używana do wykonania zapytania.
        url (str): Adres strony planu lekcji sali.
        dniTygodnia (list[str]): Lista dni tygodnia.
        dzień (str): Dzień tygodnia, w którym odbywa się lekcja.
        numer (int): Numer lekcji z brakującym nauczycielem w danym dniu tygodnia.

    Returns:
        EncjaPlanu: Słownik zawierający dane nauczyciela.
    """

    try:
        katalogPlanów = konfiguracja.get("plany", {})
        katalog = katalogPlanów.get("url")
        kodowanie = katalogPlanów.get("kodowanie")

        if not katalog or not kodowanie:
            logowanie.warning(
                "Funkcja nie otrzymała wystarczającej liczby potrzebnych danych. Zwracanie pustego słownika encji."
            )
            return zwróćPustySłownik()

        if urlparse(url).netloc != urlparse(katalog).netloc:
            logowanie.warning(
                "Otrzymany URL nie zgadza się z wartością URL znajdującego się w pliku konfiguracyjnym. Zwracanie pustego słownika encji."
            )
            return zwróćPustySłownik()

        async with semafor:
            zawartośćStrony = await pobierzZawartośćStrony(atom, url, kodowanie)

        if zawartośćStrony is None:
            logowanie.warning(
                "Brak treści pobranej ze strony. Zwracanie pustej zawartości."
            )
            return zwróćPustySłownik()

        tabela = zawartośćStrony.select_one("table.tabela")
        if not tabela:
            logowanie.warning(
                "Nie znaleziono tabeli planu lekcji. Zwracanie pustego słownika encji."
            )
            return zwróćPustySłownik()

        try:
            indeksDnia = dniTygodnia.index(dzień) + 2
        except ValueError:
            return zwróćPustySłownik()

        wiersze = tabela.find_all("tr")[1:]
        for wiersz in wiersze:
            komórki = wiersz.find_all("td")

            if indeksDnia >= len(komórki):
                continue

            tekstNumeru = komórki[0].get_text(strip=True)
            if not tekstNumeru.isdigit() or int(tekstNumeru) != numer:
                continue

            td = komórki[indeksDnia]
            etykietaNauczyciela = td.select_one("a.n")

            if etykietaNauczyciela:
                hrefNauczyciela = etykietaNauczyciela.get("href")
                urlNauczyciela = urljoin(katalog, hrefNauczyciela) if hrefNauczyciela else None

                return {
                    "tekst": etykietaNauczyciela.get_text(strip=True),
                    "url": urlNauczyciela,
                    "identyfikator": wydobądźIdentyfikator(urlNauczyciela)
                }

        return zwróćPustySłownik()
    except Exception as e:
        logowanie.exception(
            f"Wystąpił błąd podczas uzupełniania danych nauczyciela (URL: {url}, Dni tygodnia: {dniTygodnia}, Dzień: {dzień}, Numer: {numer}). Więcej informacji: {e}"
        )
        return zwróćPustySłownik()

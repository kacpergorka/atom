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
import asyncio
from operator import itemgetter
import re
from urllib.parse import urljoin

# Zewnętrzne biblioteki
import aiohttp

# Wewnętrzne importy
from src.classes.semaphore import semafor
from src.handlers.configuration import konfiguracja
from src.handlers.logging import logowanie
from src.handlers.scraper import pobierzZawartośćStrony
from src.handlers.timetables.parser import wyodrębnijPlanLekcji
from src.schemas.lists import ElementListy

async def uzupełnijBrakująceOddziały(
    atom: aiohttp.ClientSession,
    oddziały: list[ElementListy],
    brakująceIdentyfikatory: list[str]
) -> list[ElementListy]:
    """
    Uzupełnia luki w liście oddziałów, sprawdzając wskazane brakujące strony planów lekcji.

    Args:
        atom (aiohttp.ClientSession): Aktywna sesja HTTP używana do wykonania zapytania.
        oddziały (list[ElementListy]): Lista oddziałów zwrócona przez parser list.
        brakująceIdentyfikatory (list[str]): Identyfikatory oddziałów, których brakuje w liście.

    Returns:
        list[ElementListy]: Lista oddziałów uzupełniona o brakujące strony planów, jeśli istnieją.
    """

    def zbudujElementOddziału(
        plan: dict,
        identyfikator: str,
        url: str
    ) -> ElementListy | None:
        """
        Buduje element listy oddziałów na podstawie danych wyodrębnionych z planu lekcji.

        Args:
            plan (dict): Plan lekcji zwrócony przez parser planu.
            identyfikator (str): Identyfikator uzupełnianego oddziału.
            url (str): URL planu lekcji uzupełnianego oddziału.

        Returns:
            ElementListy | None: Element listy oddziałów albo `None`, jeśli plan nie zawiera nazwy.
        """

        nazwaPlanu = plan.get("nazwa")
        if not isinstance(nazwaPlanu, str) or not nazwaPlanu:
            return None

        tekst = re.sub(r"\s+", " ", nazwaPlanu.replace(".", " ")).strip()
        dopasowanie = re.match(r"(\d+)\s*([a-zA-Z])", tekst)
        nazwa = (
            f"{dopasowanie.group(1)} {dopasowanie.group(2).upper()}"
            if dopasowanie
            else tekst
        )

        return {
            "url": plan.get("url") or url,
            "identyfikator": plan.get("identyfikator") or identyfikator,
            "nazwa": nazwa,
            "rozwiniecie": nazwaPlanu
        }

    async def pobierzBrakującyOddział(
        atom: aiohttp.ClientSession,
        identyfikator: str,
        katalog: str,
        kodowanie: str,
        oddziały: list[ElementListy]
    ) -> ElementListy | None:
        """
        Próbuje pobrać i sparsować plan lekcji dla brakującego identyfikatora oddziału.

        Args:
            atom (aiohttp.ClientSession): Aktywna sesja HTTP używana do wykonania zapytania.
            identyfikator (str): Brakujący identyfikator oddziału.
            katalog (str): Bazowy URL katalogu planów lekcji.
            kodowanie (str): Kodowanie stron planów lekcji.
            oddziały (list[ElementListy]): Aktualna lista oddziałów.

        Returns:
            ElementListy | None: Uzupełniony element listy oddziałów albo `None`, gdy strona nie istnieje lub nie da się jej przetworzyć.
        """

        url = urljoin(katalog, f"{identyfikator}.html")

        try:
            async with semafor:
                zawartośćStrony = await pobierzZawartośćStrony(atom, url, kodowanie)

            plan = await wyodrębnijPlanLekcji(atom, zawartośćStrony, oddziały, None, None, False, url)
            identyfikatorPlanu = plan.get("identyfikator")
            kategoriaPlanu = plan.get("kategoria")

            if identyfikatorPlanu != identyfikator or kategoriaPlanu != "oddział":
                return None

            return zbudujElementOddziału(plan, identyfikator, url)
        except Exception as e:
            logowanie.exception(
                f"Nie udało się uzupełnić brakującego oddziału {identyfikator}. Więcej informacji: {e}"
            )
            return None

    try:
        if not oddziały or not brakująceIdentyfikatory:
            return oddziały

        katalogPlanów = konfiguracja.get("plany", {})
        katalog = katalogPlanów.get("url")
        kodowanie = katalogPlanów.get("kodowanie")

        if not katalog or not kodowanie:
            logowanie.warning(
                "Brak wymaganych danych katalogu planów. Pomijanie uzupełniania brakujących oddziałów."
            )
            return oddziały

        wyniki: list[ElementListy | None] = []
        for indeks in range(0, len(brakująceIdentyfikatory), 20):
            paczka = brakująceIdentyfikatory[indeks:indeks + 20]
            wyniki.extend(
                await asyncio.gather(*[
                    pobierzBrakującyOddział(atom, identyfikator, katalog, kodowanie, oddziały)
                    for identyfikator in paczka
                ])
            )

        uzupełnioneOddziały = [
            oddział
            for oddział in wyniki
            if oddział is not None
        ]

        if not uzupełnioneOddziały:
            return oddziały

        istniejąceIdentyfikatory = {
            oddział["identyfikator"]
            for oddział in oddziały
        }
        oddziały.extend([
            oddział
            for oddział in uzupełnioneOddziały
            if oddział["identyfikator"] not in istniejąceIdentyfikatory
        ])
        oddziały.sort(key=itemgetter("nazwa"))

        return oddziały
    except Exception as e:
        logowanie.exception(
            f"Wystąpił błąd podczas uzupełniania luk w liście oddziałów. Więcej informacji: {e}."
        )
        return oddziały

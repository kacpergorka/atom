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

# Wewnętrzne importy
from src.api.helpers import zbudujPrzedmiotyDodatkowe
from src.api.substitutions.exceptions import (
    BłądWewnętrzny,
    BrakWymaganychDanych,
    NieprawidłowyIdentyfikator,
    ŹródłoNiedostępne
)
from src.api.substitutions.schemas import Zastepstwa
from src.classes.atom import atom
from src.classes.semaphore import semafor
from src.handlers.configuration import konfiguracja
from src.handlers.lists.parser import wyodrębnijListy
from src.handlers.logging import logowanie
from src.handlers.scraper import pobierzZawartośćStrony
from src.handlers.substitutions.parser import wyodrębnijZastępstwa

async def pobierzZastępstwa(
    identyfikator: str | None,
    grupy: list[str] | None,
    religia: bool | None,
    edukacjaZdrowotna: bool | None
) -> Zastepstwa:
    """
    Pobiera i przetwarza zastępstwa na podstawie przekazanych parametrów wejściowych.

    Args:
        identyfikator (str | None): Identyfikator oddziału lub nauczyciela, np. o17, n78.
        grupy (list[str] | None): Lista oznaczeń określających grupę przedmiotów.
        religia (bool | None): Flaga informująca, czy uwzględniać lekcje religii w planie lekcji.
        edukacjaZdrowotna (bool | None): Flaga informująca, czy uwzględniać lekcje edukacji zdrowotnej w planie lekcji.

    Returns:
        Zastepstwa: Słownik zawierający informacje o zastępstwach.

    Raises:
        BłądWewnętrzny: Gdy wystąpi nieoczekiwany błąd przetwarzania.
        BrakWymaganychDanych: Gdy w pliku konfiguracyjnym nie znajdują się wymagane dane.
        NieprawidłowyIdentyfikator: Gdy przekazany identyfikator ma nieprawidłowy format lub nie istnieje.
        ŹródłoNiedostępne: Gdy wystąpi problem z pobraniem danych.
    """

    try:
        lista = konfiguracja.get("lista", {})
        urlListy = lista.get("url")
        kodowanieListy = lista.get("kodowanie")

        zastępstwa = konfiguracja.get("zastepstwa", {})
        urlZastępstw = zastępstwa.get("url")
        kodowanieZastępstw = zastępstwa.get("kodowanie")

        if not urlListy or not kodowanieListy or not urlZastępstw or not kodowanieZastępstw:
            logowanie.warning(
                "Brak wymaganych danych w pliku konfiguracyjnym. Uzupełnij brakujące dane i spróbuj ponownie."
            )
            raise BrakWymaganychDanych

        async with semafor:
            zawartośćStronyListy = await pobierzZawartośćStrony(atom.sesja, urlListy, kodowanieListy)

        przedmiotyDodatkowe = zbudujPrzedmiotyDodatkowe(religia, edukacjaZdrowotna)
        listy = wyodrębnijListy(zawartośćStronyListy, urlListy)
        listaOddziałów = listy.get("oddzialy", {})
        listaNauczycieli = listy.get("nauczyciele", {})
        wybranyOddział = None
        wybranyNauczyciel = None
        mapaIdentyfikatorów = {
            "o": "oddzialy",
            "n": "nauczyciele"
        }

        if identyfikator:
            if len(identyfikator) < 2:
                raise NieprawidłowyIdentyfikator

            sekcja = mapaIdentyfikatorów.get(identyfikator[0].lower())
            if not sekcja:
                raise NieprawidłowyIdentyfikator

            dane = listy.get(sekcja, {})
            for nazwa, info in dane.items():
                if isinstance(info, dict) and info.get("identyfikator") == identyfikator:
                    if sekcja == "oddzialy":
                        wybranyOddział = nazwa
                    elif sekcja == "nauczyciele":
                        wybranyNauczyciel = nazwa
                    break

            if sekcja == "oddzialy" and not wybranyOddział:
                raise NieprawidłowyIdentyfikator

            if sekcja == "nauczyciele" and not wybranyNauczyciel:
                raise NieprawidłowyIdentyfikator

        async with semafor:
            zawartośćStronyZastępstw = await pobierzZawartośćStrony(atom.sesja, urlZastępstw, kodowanieZastępstw)

        return await wyodrębnijZastępstwa(atom.sesja, zawartośćStronyZastępstw, listaOddziałów, listaNauczycieli, wybranyOddział, wybranyNauczyciel, grupy, przedmiotyDodatkowe)
    except NieprawidłowyIdentyfikator:
        raise
    except BrakWymaganychDanych:
        raise
    except TimeoutError as e:
        logowanie.exception(
            f"Przekroczono czas oczekiwania na połączenie. Więcej informacji: {e}"
        )
        raise ŹródłoNiedostępne from e
    except Exception as e:
        logowanie.exception(
            f"Wystąpił błąd podczas przetwarzania danych. Więcej informacji: {e}"
        )
        raise BłądWewnętrzny from e

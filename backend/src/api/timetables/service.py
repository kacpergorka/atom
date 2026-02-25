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
from src.api.timetables.exceptions import (
    BłądWewnętrzny,
    BrakWymaganychDanych,
    NieprawidłowyIdentyfikator,
    ŹródłoNiedostępne
)
from src.api.timetables.schemas import PlanLekcji
from src.classes.atom import atom
from src.classes.semaphore import semafor
from src.handlers.configuration import konfiguracja
from src.handlers.lists.parser import wyodrębnijListy
from src.handlers.logging import logowanie
from src.handlers.scraper import pobierzZawartośćStrony
from src.handlers.timetables.parser import wyodrębnijPlanLekcji

async def pobierzPlanLekcji(
    identyfikator: str,
    grupy: list[str] | None,
    dzieńSkróconych: str | None,
    religia: bool | None,
    edukacjaZdrowotna: bool | None
) -> PlanLekcji:
    """
    Pobiera i przetwarza plan lekcji na podstawie przekazanych parametrów wejściowych.

    Args:
        identyfikator (str | None): Identyfikator oddziału, nauczyciela lub sali, np. o17, n78, s45.
        grupy (list[str] | None): Lista oznaczeń określających grupę przedmiotów.
        dzieńSkróconych (str | None): Dzień tygodnia, dla którego obowiązuje skrócony rozkład zajęć.
        religia (bool | None): Flaga informująca, czy uwzględniać lekcje religii w planie lekcji.
        edukacjaZdrowotna (bool | None): Flaga informująca, czy uwzględniać lekcje edukacji zdrowotnej w planie lekcji.

    Returns:
        PlanLekcji: Słownik zawierający ustrukturyzowany plan lekcji.

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

        plany = konfiguracja.get("plany", {})
        katalogPlanów = plany.get("url")
        kodowaniePlanów = plany.get("kodowanie")

        if not katalogPlanów or not kodowaniePlanów or not urlListy or not kodowanieListy:
            logowanie.warning(
                "Brak wymaganych danych w pliku konfiguracyjnym. Uzupełnij brakujące dane i spróbuj ponownie."
            )
            raise BrakWymaganychDanych

        if not identyfikator or len(identyfikator) < 2:
            raise NieprawidłowyIdentyfikator

        urlPlanu = f"{katalogPlanów}{identyfikator}.html"

        async with semafor:
            zawartośćStronyListy = await pobierzZawartośćStrony(atom.sesja, urlListy, kodowanieListy)

        async with semafor:
            zawartośćStronyPlanu = await pobierzZawartośćStrony(atom.sesja, urlPlanu, kodowaniePlanów)

        przedmiotyDodatkowe = zbudujPrzedmiotyDodatkowe(religia, edukacjaZdrowotna)
        listy = wyodrębnijListy(zawartośćStronyListy, urlListy)
        listaOddziałów = listy.get("oddzialy", {})

        return await wyodrębnijPlanLekcji(atom.sesja, zawartośćStronyPlanu, listaOddziałów, dzieńSkróconych, grupy, przedmiotyDodatkowe, urlPlanu)
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

#
#     ▄▄     ▄▄▄▄▄▄▄▄    ▄▄▄▄    ▄▄▄  ▄▄▄               ▄▄     ▄▄▄▄▄▄     ▄▄▄▄▄▄
#    ████    ▀▀▀██▀▀▀   ██▀▀██   ███  ███              ████    ██▀▀▀▀█▄   ▀▀██▀▀
#    ████       ██     ██    ██  ████████              ████    ██    ██     ██
#   ██  ██      ██     ██    ██  ██ ██ ██             ██  ██   ██████▀      ██
#   ██████      ██     ██    ██  ██ ▀▀ ██             ██████   ██           ██
#  ▄██  ██▄     ██      ██▄▄██   ██    ██            ▄██  ██▄  ██         ▄▄██▄▄
#  ▀▀    ▀▀     ▀▀       ▀▀▀▀    ▀▀    ▀▀            ▀▀    ▀▀  ▀▀         ▀▀▀▀▀▀
#

# Wewnętrzne importy
from src.api.endpoints.universal.helpers import (
    normalizujIdentyfikator,
    wyszukajElement,
    zbudujPrzedmiotyDodatkowe
)
from src.api.endpoints.universal.lists.service import pobierzListy
from src.api.endpoints.universal.substitutions.schemas import UniwersalneZastepstwa
from src.api.exceptions import (
    BłądWewnętrzny,
    BrakWymaganychDanych,
    NieprawidłowyIdentyfikator,
    ŹródłoNiedostępne
)
from src.classes.atom import atom
from src.classes.semaphore import semafor
from src.handlers.cache import (
    normalizujStanOpcji,
    pobierzModel,
    zapiszModel,
    zbudujFragmentKluczaCache
)
from src.handlers.configuration import konfiguracja
from src.handlers.logging import logowanie
from src.handlers.scraper import pobierzZawartośćStrony
from src.handlers.substitutions.parser import wyodrębnijZastępstwa

async def pobierzZastępstwa(
    identyfikator: str | None,
    grupy: list[str] | None,
    religia: bool,
    edukacjaZdrowotna: bool,
    pomińCache: bool = False
) -> UniwersalneZastepstwa:
    """
    Pobiera i przetwarza zastępstwa na podstawie przekazanych parametrów wejściowych.

    Args:
        identyfikator (str | None): Identyfikator oddziału lub nauczyciela, np. o17, n78.
        grupy (list[str] | None): Lista oznaczeń określających grupę przedmiotów.
        religia (bool): Flaga informująca, czy uwzględniać lekcje religii w planie lekcji.
        edukacjaZdrowotna (bool): Flaga informująca, czy uwzględniać lekcje edukacji zdrowotnej w planie lekcji.
        pomińCache (bool): Flaga informująca, czy należy pominąć cache podczas pobierania danych.

    Returns:
        UniwersalneZastepstwa: Słownik zawierający informacje o zastępstwach.

    Raises:
        BłądWewnętrzny: Gdy wystąpi nieoczekiwany błąd przetwarzania.
        BrakWymaganychDanych: Gdy w pliku konfiguracyjnym nie znajdują się wymagane dane.
        NieprawidłowyIdentyfikator: Gdy przekazany identyfikator ma nieprawidłowy format lub nie istnieje.
        ŹródłoNiedostępne: Gdy wystąpi problem z pobraniem danych.
    """

    try:
        zastępstwa = konfiguracja.get("zastepstwa", {})
        urlZastępstw = zastępstwa.get("url")
        kodowanieZastępstw = zastępstwa.get("kodowanie")

        if not urlZastępstw or not kodowanieZastępstw:
            logowanie.warning(
                "Brak wymaganych danych w pliku konfiguracyjnym. Uzupełnij brakujące dane i spróbuj ponownie."
            )
            raise BrakWymaganychDanych

        if identyfikator:
            identyfikator = normalizujIdentyfikator(identyfikator)

        identyfikatorTekst = identyfikator if identyfikator else "wszystkie"
        kluczCache = f"cache:zastepstwa:{identyfikatorTekst}:{zbudujFragmentKluczaCache(grupy)}:{normalizujStanOpcji(religia)}:{normalizujStanOpcji(edukacjaZdrowotna)}"
        cacheZastępstw = None if pomińCache else await pobierzModel(kluczCache, UniwersalneZastepstwa)

        if cacheZastępstw is not None:
            return cacheZastępstw

        przedmiotyDodatkowe = zbudujPrzedmiotyDodatkowe(religia, edukacjaZdrowotna)
        listy = (await pobierzListy(True, True, True)).model_dump()
        listaOddziałów = listy.get("oddzialy") or []
        listaNauczycieli = listy.get("nauczyciele") or []
        wybranyOddział, wybranyNauczyciel = (None, None)

        if identyfikator:
            wybranyOddział, wybranyNauczyciel = wyszukajElement(identyfikator, listaOddziałów, listaNauczycieli)

        async with semafor:
            zawartośćStronyZastępstw = await pobierzZawartośćStrony(atom.sesja, urlZastępstw, kodowanieZastępstw)

        przetworzoneZastępstwa = UniwersalneZastepstwa.model_validate(
            await wyodrębnijZastępstwa(atom.sesja, zawartośćStronyZastępstw, listaOddziałów, listaNauczycieli, wybranyOddział, wybranyNauczyciel, grupy, przedmiotyDodatkowe)
        )
        await zapiszModel(kluczCache, przetworzoneZastępstwa)
        return przetworzoneZastępstwa
    except NieprawidłowyIdentyfikator:
        raise
    except BrakWymaganychDanych:
        raise
    except (TimeoutError, ConnectionError) as e:
        logowanie.exception(
            f"Przekroczono czas oczekiwania na połączenie. Więcej informacji: {e}"
        )
        raise ŹródłoNiedostępne from e
    except Exception as e:
        logowanie.exception(
            f"Wystąpił błąd podczas przetwarzania danych. Więcej informacji: {e}"
        )
        raise BłądWewnętrzny from e

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
from src.api.exceptions import (
    BłądWewnętrzny,
    BrakWymaganychDanych,
    ŹródłoNiedostępne
)
from src.classes.atom import klientAtom
from src.classes.semaphore import semafor
from src.handlers.cache import (
    pobierzModel,
    zapiszModel
)
from src.handlers.configuration import konfiguracja
from src.handlers.lists.parser import wyodrębnijListy
from src.handlers.logging import logowanie
from src.handlers.scraper import pobierzZawartośćStrony
from src.schemas.lists import Listy

async def pobierzListy(
    oddzialy: bool,
    nauczyciele: bool,
    sale: bool
) -> Listy:
    """
    Pobiera i przetwarza listy oddziałów, nauczycieli oraz sal.

    Args:
        oddzialy (bool): Flaga informująca, czy uwzględnić listę oddziałów.
        nauczyciele (bool): Flaga informująca, czy uwzględnić listę nauczycieli.
        sale (bool): Flaga informująca, czy uwzględnić listę sal.

    Returns:
        Listy: Słownik zawierający ustrukturyzowane listy, które zostały wybrane.

    Raises:
        BłądWewnętrzny: Gdy wystąpi nieoczekiwany błąd przetwarzania.
        BrakWymaganychDanych: Gdy w pliku konfiguracyjnym nie znajdują się wymagane dane.
        ŹródłoNiedostępne: Gdy wystąpi problem z pobraniem danych.
    """

    try:
        lista = konfiguracja.get("lista", {})
        url = lista.get("url")
        kodowanie = lista.get("kodowanie")

        if not url or not kodowanie:
            logowanie.warning(
                "Brak wymaganych danych w pliku konfiguracyjnym. Uzupełnij brakujące dane i spróbuj ponownie."
            )
            raise BrakWymaganychDanych

        kluczCache = "cache:listy"
        cacheList = await pobierzModel(kluczCache, Listy)

        if cacheList is not None:
            listy = cacheList
        else:
            async with semafor:
                zawartośćStrony = await pobierzZawartośćStrony(klientAtom.sesja, url, kodowanie)

            listy = Listy(**await wyodrębnijListy(klientAtom.sesja, zawartośćStrony, url))
            await zapiszModel(kluczCache, listy)

        if not oddzialy and not nauczyciele and not sale:
            return listy

        return Listy(
            oddzialy=listy.oddzialy if oddzialy else None,
            nauczyciele=listy.nauczyciele if nauczyciele else None,
            sale=listy.sale if sale else None
        )
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

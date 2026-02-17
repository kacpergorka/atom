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
from src.api.lists.exceptions import (
    BłądWewnętrzny,
    BrakWymaganychDanych,
    ŹródłoNiedostępne
)
from src.api.lists.schemas import Listy
from src.classes.atom import atom
from src.classes.semaphore import semafor
from src.handlers.configuration import konfiguracja
from src.handlers.lists.parser import wyodrębnijListy
from src.handlers.logging import logowanie
from src.handlers.scraper import pobierzZawartośćStrony

async def pobierzListy() -> Listy:
    """
    Pobiera i przetwarza listy oddziałów, nauczycieli oraz sal.

    Returns:
        Listy: Słownik zawierający ustrukturyzowane listy oddziałów, nauczycieli oraz sal.

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

        async with semafor:
            zawartośćStrony = await pobierzZawartośćStrony(atom.sesja, url, kodowanie)

        return wyodrębnijListy(zawartośćStrony, url)
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

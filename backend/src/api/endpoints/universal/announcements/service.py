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
from urllib.parse import (
    parse_qsl,
    urlencode,
    urlsplit,
    urlunsplit
)

# Wewnętrzne importy
from src.api.endpoints.universal.announcements.schemas import UniwersalneOgloszenia
from src.api.exceptions import (
    BłądWewnętrzny,
    BrakWymaganychDanych,
    ŹródłoNiedostępne
)
from src.classes.atom import atom
from src.classes.semaphore import semafor
from src.handlers.announcements.parser import wyodrębnijOgłoszenia
from src.handlers.cache import (
    pobierzModel,
    zapiszModel
)
from src.handlers.configuration import konfiguracja
from src.handlers.logging import logowanie
from src.handlers.scraper import pobierzZawartośćStrony

async def pobierzOgłoszenia(strona: int) -> UniwersalneOgloszenia:
    """
    Pobiera i przetwarza aktualności na podstawie przekazanych parametrów wejściowych.

    Args:
        strona (int): Numer strony listy aktualności.

    Returns:
        UniwersalneOgloszenia: Słownik zawierający ustrukturyzowane ogłoszenia.

    Raises:
        BłądWewnętrzny: Gdy wystąpi nieoczekiwany błąd przetwarzania.
        BrakWymaganychDanych: Gdy w pliku konfiguracyjnym nie znajdują się wymagane dane.
        ŹródłoNiedostępne: Gdy wystąpi problem z pobraniem danych.
    """

    def zbudujUrlStrony(
        url: str,
        strona: int
    ) -> str:
        """
        Buduje URL konkretnej strony ogłoszeń.

        Args:
            url (str): Bazowy adres strony internetowej ogłoszeń.
            strona (int): Numer strony listy aktualności.

        Returns:
            str: Zbudowany URL strony ogłoszeń.
        """

        if strona <= 1:
            return url

        części = urlsplit(url)
        parametry = dict(parse_qsl(części.query, keep_blank_values=True))
        parametry.setdefault("dni", "3")
        parametry["nnr"] = str(strona)

        return urlunsplit((
            części.scheme,
            części.netloc,
            części.path,
            urlencode(parametry),
            części.fragment
        ))

    try:
        ogłoszenia = konfiguracja.get("ogloszenia", {})
        url = ogłoszenia.get("url")
        kodowanie = ogłoszenia.get("kodowanie")

        if not url or not kodowanie:
            logowanie.warning(
                "Brak wymaganych danych w pliku konfiguracyjnym. Uzupełnij brakujące dane i spróbuj ponownie."
            )
            raise BrakWymaganychDanych

        strona = max(1, strona)
        urlStrony = zbudujUrlStrony(url, strona)

        kluczCache = f"cache:ogloszenia:{strona}"
        cacheOgłoszeń = await pobierzModel(kluczCache, UniwersalneOgloszenia)

        if cacheOgłoszeń is not None:
            return cacheOgłoszeń

        async with semafor:
            zawartośćStrony = await pobierzZawartośćStrony(atom.sesja, urlStrony, kodowanie)

        dane = wyodrębnijOgłoszenia(zawartośćStrony, urlStrony)
        przetworzoneOgłoszenia = UniwersalneOgloszenia.model_validate(dane)

        await zapiszModel(kluczCache, przetworzoneOgłoszenia)
        return przetworzoneOgłoszenia
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

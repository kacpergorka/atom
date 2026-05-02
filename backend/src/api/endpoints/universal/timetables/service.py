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
    sprawdźIstnienieElementu,
    zbudujPrzedmiotyDodatkowe
)
from src.api.endpoints.universal.lists.service import pobierzListy
from src.api.endpoints.universal.substitutions.service import pobierzZastępstwa
from src.api.endpoints.universal.timetables.schemas import UniwersalnyPlanLekcji
from src.api.exceptions import (
    BłądWewnętrzny,
    BrakWymaganychDanych,
    NieprawidłowyIdentyfikator,
    ŹródłoNiedostępne
)
from src.classes.atom import atom
from src.classes.semaphore import semafor
from src.handlers.cache import (
    pobierzModel,
    zapiszModel,
    normalizujStanOpcji,
    zbudujFragmentKluczaCache
)
from src.handlers.configuration import konfiguracja
from src.handlers.holidays.checker import sprawdźCzyDzisiajJestWolne
from src.handlers.logging import logowanie
from src.handlers.scraper import pobierzZawartośćStrony
from src.handlers.timetables.assembler import zbudujPlanLekcji
from src.handlers.timetables.parser import wyodrębnijPlanLekcji

async def pobierzPlanLekcji(
    identyfikator: str,
    grupy: list[str] | None,
    zastepstwa: bool,
    religia: bool,
    edukacjaZdrowotna: bool
) -> UniwersalnyPlanLekcji:
    """
    Pobiera i przetwarza plan lekcji na podstawie przekazanych parametrów wejściowych.

    Args:
        identyfikator (str): Identyfikator oddziału, nauczyciela lub sali, np. o17, n78, s45.
        grupy (list[str] | None): Lista oznaczeń określających grupę przedmiotów.
        zastepstwa (bool): Flaga informująca, czy uwzględniać zastępstwa w planie lekcji.
        religia (bool): Flaga informująca, czy uwzględniać lekcje religii w planie lekcji.
        edukacjaZdrowotna (bool): Flaga informująca, czy uwzględniać lekcje edukacji zdrowotnej w planie lekcji.

    Returns:
        UniwersalnyPlanLekcji: Słownik zawierający ustrukturyzowany plan lekcji.

    Raises:
        BłądWewnętrzny: Gdy wystąpi nieoczekiwany błąd przetwarzania.
        BrakWymaganychDanych: Gdy w pliku konfiguracyjnym nie znajdują się wymagane dane.
        NieprawidłowyIdentyfikator: Gdy przekazany identyfikator ma nieprawidłowy format lub nie istnieje.
        ŹródłoNiedostępne: Gdy wystąpi problem z pobraniem danych.
    """

    async def pobierzStatusDniaWolnego() -> bool:
        """
        Pobiera informację, czy bieżący dzień jest wolny od zajęć.

        Returns:
            bool: `True`, jeśli backend numerków rozpoznał dzień wolny od zajęć.
        """

        try:
            szkoła = konfiguracja.get("szkola", {})
            return await sprawdźCzyDzisiajJestWolne(
                szkoła.get("url"),
                szkoła.get("kodowanie")
            )
        except Exception as e:
            logowanie.warning(
                f"Nie udało się ustalić, czy bieżący dzień jest wolny od zajęć. Więcej informacji: {e}"
            )
            return False

    try:
        plany = konfiguracja.get("plany", {})
        katalogPlanów = plany.get("url")
        kodowaniePlanów = plany.get("kodowanie")

        if not katalogPlanów or not kodowaniePlanów:
            logowanie.warning(
                "Brak wymaganych danych w pliku konfiguracyjnym. Uzupełnij brakujące dane i spróbuj ponownie."
            )
            raise BrakWymaganychDanych

        identyfikator = normalizujIdentyfikator(identyfikator)

        kluczCache = f"cache:planlekcji:{identyfikator}:{zbudujFragmentKluczaCache(grupy)}:{normalizujStanOpcji(zastepstwa)}:{normalizujStanOpcji(religia)}:{normalizujStanOpcji(edukacjaZdrowotna)}"
        cachePlanu = await pobierzModel(kluczCache, UniwersalnyPlanLekcji)

        if cachePlanu is not None:
            return cachePlanu.model_copy(update={"wolne": await pobierzStatusDniaWolnego()})

        przedmiotyDodatkowe = zbudujPrzedmiotyDodatkowe(religia, edukacjaZdrowotna)
        listy = (await pobierzListy(None, None, None)).model_dump()
        listaOddziałów = listy.get("oddzialy") or []
        listaNauczycieli = listy.get("nauczyciele") or []
        listaSal = listy.get("sale") or []

        sprawdźIstnienieElementu(identyfikator, listaOddziałów, listaNauczycieli, listaSal)

        urlPlanu = f"{katalogPlanów}{identyfikator}.html"
        cache = True

        if zastepstwa:
            try:
                wyodrębnioneZastępstwa = await pobierzZastępstwa(identyfikator, grupy, religia, edukacjaZdrowotna)
            except Exception:
                zastepstwa = False
                cache = False

        async with semafor:
            zawartośćStronyPlanu = await pobierzZawartośćStrony(atom.sesja, urlPlanu, kodowaniePlanów)

        planLekcji = UniwersalnyPlanLekcji.model_validate(
            await wyodrębnijPlanLekcji(atom.sesja, zawartośćStronyPlanu, listaOddziałów, grupy, przedmiotyDodatkowe, zastepstwa, urlPlanu)
        )
        planLekcji = planLekcji.model_copy(update={"wolne": await pobierzStatusDniaWolnego()})

        if not zastepstwa:
            if cache:
                await zapiszModel(kluczCache, planLekcji)
            return planLekcji

        przetworzonyPlanLekcji = UniwersalnyPlanLekcji.model_validate(
            zbudujPlanLekcji(
                planLekcji.model_dump(),
                wyodrębnioneZastępstwa.model_dump()
            )
        )
        await zapiszModel(kluczCache, przetworzonyPlanLekcji)
        return przetworzonyPlanLekcji
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

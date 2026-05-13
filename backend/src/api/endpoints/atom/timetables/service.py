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
from src.api.endpoints.atom.timetables.mapper import mapujPlanLekcji
from src.api.endpoints.atom.timetables.schemas import AtomowyPlanLekcji
from src.api.endpoints.universal.timetables.service import pobierzPlanLekcji as pobierzUniwersalnyPlanLekcji
from src.api.exceptions import (
    BłądAPI,
    BłądWewnętrzny
)
from src.handlers.logging import logowanie

async def pobierzPlanLekcji(
    identyfikator: str,
    grupy: list[str] | None,
    zastepstwa: bool,
    religia: bool,
    edukacjaZdrowotna: bool
) -> AtomowyPlanLekcji:
    """
    Pobiera plan lekcji dla Atomu na podstawie przekazanych parametrów wejściowych.

    Args:
        identyfikator (str): Identyfikator oddziału, nauczyciela lub sali, np. o17, n78, s45.
        grupy (list[str] | None): Lista oznaczeń określających grupę przedmiotów.
        zastepstwa (bool): Flaga informująca, czy uwzględniać zastępstwa w planie lekcji.
        religia (bool): Flaga informująca, czy uwzględniać lekcje religii w planie lekcji.
        edukacjaZdrowotna (bool): Flaga informująca, czy uwzględniać lekcje edukacji zdrowotnej w planie lekcji.

    Returns:
        AtomowyPlanLekcji: Słownik zawierający ustrukturyzowany plan lekcji.

    Raises:
        BłądWewnętrzny: Gdy wystąpi nieoczekiwany błąd mapowania.
    """

    try:
        return mapujPlanLekcji(
            (await pobierzUniwersalnyPlanLekcji(identyfikator, grupy, zastepstwa, religia, edukacjaZdrowotna)).model_dump()
        )
    except BłądAPI:
        raise
    except Exception as e:
        logowanie.exception(
            f"Wystąpił błąd podczas mapowania danych do modelu API Atomu. Więcej informacji: {e}"
        )
        raise BłądWewnętrzny from e

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
from src.api.endpoints.atom.lists.mapper import mapujListy
from src.api.endpoints.atom.lists.schemas import AtomoweListy
from src.api.endpoints.universal.lists.service import pobierzListy as pobierzListyUniwersalne
from src.api.exceptions import BłądWewnętrzny
from src.handlers.logging import logowanie

async def pobierzListy() -> AtomoweListy:
    """
    Pobiera listy oddziałów oraz nauczycieli dla Atomu.

    Returns:
        AtomoweListy: Słownik zawierający ustrukturyzowane listy oddziałów oraz nauczycieli.

    Raises:
        BłądWewnętrzny: Gdy wystąpi nieoczekiwany błąd mapowania.
    """

    try:
        return mapujListy(
            (await pobierzListyUniwersalne(True, True, False)).model_dump()
        )
    except Exception as e:
        logowanie.exception(
            f"Wystąpił błąd podczas mapowania danych do modelu API Atomu. Więcej informacji: {e}"
        )
        raise BłądWewnętrzny from e

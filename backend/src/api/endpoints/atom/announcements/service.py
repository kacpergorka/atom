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
from src.api.endpoints.atom.announcements.mapper import mapujOgłoszenia
from src.api.endpoints.atom.announcements.schemas import AtomoweOgloszenia
from src.api.endpoints.universal.announcements.service import pobierzOgłoszenia as pobierzUniwersalneOgłoszenia
from src.api.exceptions import BłądWewnętrzny
from src.handlers.logging import logowanie

async def pobierzOgłoszenia(strona: int) -> AtomoweOgloszenia:
    """
    Pobiera ogłoszenia dla Atomu na podstawie przekazanych parametrów wejściowych.

    Args:
        strona (int): Numer strony listy aktualności.

    Returns:
        AtomoweOgloszenia: Słownik zawierający ustrukturyzowane ogłoszenia.

    Raises:
        BłądWewnętrzny: Gdy wystąpi nieoczekiwany błąd mapowania.
    """

    try:
        return mapujOgłoszenia(
            (await pobierzUniwersalneOgłoszenia(strona)).model_dump()
        )
    except Exception as e:
        logowanie.exception(
            f"Wystąpił błąd podczas mapowania danych do modelu API Atomu. Więcej informacji: {e}"
        )
        raise BłądWewnętrzny from e

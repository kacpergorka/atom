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
from src.api.endpoints.atom.substitutions.mapper import mapujZastępstwa
from src.api.endpoints.atom.substitutions.schemas import AtomoweZastepstwa
from src.api.endpoints.universal.substitutions.service import pobierzZastępstwa as pobierzUniwersalneZastępstwa
from src.api.exceptions import (
    BłądAPI,
    BłądWewnętrzny
)
from src.handlers.logging import logowanie

async def pobierzZastępstwa() -> AtomoweZastepstwa:
    """
    Pobiera zastępstwa dla Atomu.

    Returns:
        AtomoweZastepstwa: Słownik zawierający informacje o zastępstwach.

    Raises:
        BłądWewnętrzny: Gdy wystąpi nieoczekiwany błąd mapowania.
    """

    try:
        return mapujZastępstwa(
            (await pobierzUniwersalneZastępstwa(None, None, True, True)).model_dump()
        )
    except BłądAPI:
        raise
    except Exception as e:
        logowanie.exception(
            f"Wystąpił błąd podczas mapowania danych do modelu API Atomu. Więcej informacji: {e}"
        )
        raise BłądWewnętrzny from e

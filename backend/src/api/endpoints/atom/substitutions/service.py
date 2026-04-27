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
from src.api.exceptions import BłądWewnętrzny
from src.handlers.logging import logowanie

async def pobierzZastępstwa() -> AtomoweZastepstwa:
    """
    Pobiera zastępstwa dla Atomu.

    Args:
        identyfikator (str | None): Identyfikator oddziału lub nauczyciela, np. o17, n78.
        grupy (list[str] | None): Lista oznaczeń określających grupę przedmiotów.
        religia (bool): Flaga informująca, czy uwzględniać lekcje religii w planie lekcji.
        edukacjaZdrowotna (bool): Flaga informująca, czy uwzględniać lekcje edukacji zdrowotnej w planie lekcji.

    Returns:
        AtomoweZastepstwa: Słownik zawierający informacje o zastępstwach.

    Raises:
        BłądWewnętrzny: Gdy wystąpi nieoczekiwany błąd mapowania.
    """

    try:
        return mapujZastępstwa(
            (await pobierzUniwersalneZastępstwa(None, None, True, True)).model_dump()
        )
    except Exception as e:
        logowanie.exception(
            f"Wystąpił błąd podczas mapowania danych do modelu API Atomu. Więcej informacji: {e}"
        )
        raise BłądWewnętrzny from e

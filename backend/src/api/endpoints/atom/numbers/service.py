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
from src.api.endpoints.atom.numbers.mapper import mapujSzczęśliweNumerki
from src.api.endpoints.atom.numbers.schemas import AtomoweSzczesliweNumerki
from src.api.endpoints.universal.numbers.service import pobierzSzczęśliweNumerki as pobierzUniwersalneSzczęśliweNumerki
from src.api.exceptions import BłądWewnętrzny
from src.handlers.logging import logowanie

async def pobierzSzczęśliweNumerki() -> AtomoweSzczesliweNumerki:
    """
    Pobiera szczęśliwe numerki dla Atomu.

    Returns:
        AtomoweSzczesliweNumerki: Słownik zawierający szczęśliwe numerki.

    Raises:
        BłądWewnętrzny: Gdy wystąpi nieoczekiwany błąd mapowania.
    """

    try:
        return mapujSzczęśliweNumerki(
            (await pobierzUniwersalneSzczęśliweNumerki()).model_dump()
        )
    except Exception as e:
        logowanie.exception(
            f"Wystąpił błąd podczas mapowania danych do modelu API Atomu. Więcej informacji: {e}"
        )
        raise BłądWewnętrzny from e

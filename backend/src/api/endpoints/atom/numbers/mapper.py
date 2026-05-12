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
from src.api.endpoints.atom.numbers.schemas import AtomoweSzczesliweNumerki
from src.types.numbers import SzczęśliweNumerki as SuroweSzczęśliweNumerki

def mapujSzczęśliweNumerki(dane: SuroweSzczęśliweNumerki) -> AtomoweSzczesliweNumerki:
    """
    Mapuje surową strukturę szczęśliwych numerków do modelu API Atomu.

    Args:
        dane (SuroweSzczęśliweNumerki): Surowe dane szczęśliwych numerków zwrócone przez generator.

    Returns:
        AtomoweSzczesliweNumerki: Spłaszczony model szczęśliwych numerków.
    """

    return AtomoweSzczesliweNumerki(
        numerki=dane["numerki"]
    )

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
from src.handlers.configuration import konfiguracja

def sprawdźGrupę(
    grupa: str | None,
    grupy: list[str] | None
) -> bool:
    """
    Sprawdza, czy dana grupa lekcyjna powinna zostać uwzględniona.

    Args:
        grupa (str | None): Grupa przypisana do lekcji (np. "j1", "2/3").
        grupy (list[str] | None): Lista oznaczeń określających grupę przedmiotów.

    Returns:
        bool: True jeśli grupa jest powinna zostać uwzględniona, False w przeciwnym wypadku.
    """

    if not grupy or not grupa:
        return True

    dostępneGrupy = set(konfiguracja.get("grupy", []))
    obsługiwaneGrupy = [grupa for grupa in grupy if grupa in dostępneGrupy]

    if not obsługiwaneGrupy:
        return True

    if "/" in grupa:
        mianownik = grupa.split("/")[1]
        wybraneGrupy = [
            grupa for grupa in obsługiwaneGrupy
            if "/" in grupa and grupa.split("/")[1] == mianownik
        ]
    else:
        wybraneGrupy = [
            grupa for grupa in obsługiwaneGrupy
            if "/" not in grupa and grupa.startswith("j")
        ]

    return not wybraneGrupy or grupa in wybraneGrupy

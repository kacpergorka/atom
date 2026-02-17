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

def zbudujPrzedmiotyDodatkowe(
    religia: bool | None,
    edukacjaZdrowotna: bool | None
) -> dict[str, bool] | None:
    """
    Buduje słownik przedmiotów dodatkowych na podstawie przekazanych flag.

    Args:
        religia (bool | None): Flaga informująca, czy uwzględniać lekcje religii w planie lekcji.
        edukacjaZdrowotna (bool | None): Flaga informująca, czy uwzględniać lekcje edukacji zdrowotnej w planie lekcji.

    Returns:
        dict[str, bool] | None: Słownik z kluczami nazw przedmiotów i wartościami logicznymi, jeśli przynajmniej jeden filtr został określony.
    """

    if religia is None and edukacjaZdrowotna is None:
        return None

    przedmiotyDodatkowe: dict[str, bool] = {}

    if religia is not None:
        przedmiotyDodatkowe["religia"] = religia

    if edukacjaZdrowotna is not None:
        przedmiotyDodatkowe["zdrowotna"] = edukacjaZdrowotna

    return przedmiotyDodatkowe

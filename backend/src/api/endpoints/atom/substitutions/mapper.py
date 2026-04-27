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
from src.api.endpoints.atom.substitutions.schemas import (
    AtomoweZastepstwo,
    AtomoweZastepstwa
)
from src.classes.types.substitutions import (
    Zastępstwo as SuroweZastępstwo,
    Zastępstwa as SuroweZastępstwa
)

def mapujZastępstwo(dane: SuroweZastępstwo) -> AtomoweZastepstwo:
    """
    Mapuje pojedyncze surowe zastępstwo do modelu API Atomu.

    Args:
        dane (SuroweZastępstwo): Surowe zastępstwo zwrócone przez parser.

    Returns:
        AtomoweZastepstwo: Spłaszczony model zastępstwa.
    """

    return AtomoweZastepstwo(
        nauczyciel=dane["nauczyciel"],
        lekcja=dane.get("lekcja"),
        opis=dane.get("opis"),
        zastepca=dane.get("zastepca"),
        uwagi=dane.get("uwagi")
    )


def mapujZastępstwa(dane: SuroweZastępstwa) -> AtomoweZastepstwa:
    """
    Mapuje surową strukturę zastępstw do modelu API Atomu.

    Args:
        dane (SuroweZastępstwa): Surowe dane zastępstw zwrócone przez parser.

    Returns:
        AtomoweZastepstwa: Spłaszczony model zastępstw.
    """

    informacjeDodatkowe = [
        linia.strip()
        for linia in dane["informacje"].split("\n")
    ]

    return AtomoweZastepstwa(
        dzien=dane.get("dzien"),
        informacje=informacjeDodatkowe,
        zastepstwa=(
            [
                mapujZastępstwo(zastepstwo)
                for zastepstwo in dane["zastepstwa"]
            ]
            if dane["zastepstwa"] is not None
            else None
        )
    )

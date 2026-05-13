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
from src.types.substitutions import (
    Zastępstwo as SuroweZastępstwo,
    Zastępstwa as SuroweZastępstwa
)

def mapujZastępstwa(dane: SuroweZastępstwa) -> AtomoweZastepstwa:
    """
    Mapuje surową strukturę zastępstw do modelu API Atomu.

    Args:
        dane (SuroweZastępstwa): Surowe dane zastępstw zwrócone przez parser.

    Returns:
        AtomoweZastepstwa: Spłaszczony model zastępstw.
    """

    def zbudujStopkę(
        zastepca: str | None,
        uwagi: str | None
    ) -> str | None:
        """
        Buduje stopkę zastępstwa z danych o zastępcy i uwagach.

        Args:
            zastepca (str | None): Zastępca zwrócony przez parser.
            uwagi (str | None): Uwagi zwrócone przez parser.

        Returns:
            str | None: Sformatowana stopka lub None, gdy brak danych.
        """

        zastepca = zastepca.strip() if zastepca else None
        uwagi = uwagi.strip() if uwagi else None

        if zastepca and uwagi:
            return f"{zastepca} ({uwagi})"

        return zastepca or uwagi

    def mapujZastępstwo(dane: SuroweZastępstwo) -> AtomoweZastepstwo:
        """
        Mapuje pojedyncze surowe zastępstwo do modelu API Atomu.

        Args:
            dane (SuroweZastępstwo): Surowe zastępstwo zwrócone przez parser.

        Returns:
            AtomoweZastepstwo: Spłaszczony model zastępstwa.
        """

        return AtomoweZastepstwo(
            dzien=dane.get("dzien"),
            nauczyciel=dane["nauczyciel"],
            lekcja=dane.get("lekcja"),
            treść=dane.get("opis"),
            stopka=zbudujStopkę(dane.get("zastepca"), dane.get("uwagi"))
        )

    informacjeDodatkowe = [
        linia.strip()
        for linia in dane["informacje"].split("\n")
    ]

    return AtomoweZastepstwa(
        dni=dane.get("dni", []),
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

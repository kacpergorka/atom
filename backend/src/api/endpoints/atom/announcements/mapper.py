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
from src.api.endpoints.atom.announcements.schemas import (
    AtomoweOgloszenia,
    AtomoweOgloszenie
)
from src.classes.types.announcements import (
    Ogłoszenia as SuroweOgłoszenia,
    Ogłoszenie as SuroweOgłoszenie
)

def mapujOgłoszenia(dane: SuroweOgłoszenia) -> AtomoweOgloszenia:
    """
    Mapuje surowe ogłoszenia do modelu API Atomu.

    Args:
        dane (SuroweOgłoszenia): Surowe dane ogłoszeń zwrócone przez parser.

    Returns:
        AtomoweOgloszenia: Spłaszczony model ogłoszeń.
    """

    def mapujOgłoszenie(dane: SuroweOgłoszenie) -> AtomoweOgloszenie:
        """
        Mapuje surowe ogłoszenie do modelu API Atomu.

        Args:
            dane (SuroweOgłoszenie): Surowe ogłoszenie zwrócone przez parser.

        Returns:
            AtomoweOgloszenie: Spłaszczony model ogłoszenia.
        """

        return AtomoweOgloszenie(
            tytul=dane["tytul"],
            stopka=dane.get("stopka"),
            url=dane["url"],
            obraz=dane.get("obraz")
        )

    return AtomoweOgloszenia(
        aktualnaStrona=dane.get("aktualnaStrona"),
        ostatniaStrona=dane.get("ostatniaStrona"),
        ogloszenia=[
            mapujOgłoszenie(ogloszenie)
            for ogloszenie in dane.get("ogloszenia", [])
        ]
    )

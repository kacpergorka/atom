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
from src.api.endpoints.atom.lists.schemas import (
    AtomowyElementListy,
    AtomoweListy
)
from src.types.lists import (
    ElementListy as SurowyElementListy,
    Listy as SuroweListy
)

def mapujListy(dane: SuroweListy) -> AtomoweListy:
    """
    Mapuje surowe listy oddziałów, nauczycieli i sal do modelu API Atomu.

    Args:
        dane (SuroweListy): Surowe dane list zwrócone przez parser.

    Returns:
        AtomoweListy: Spłaszczony model list.
    """

    def mapujElementListy(
        element: SurowyElementListy,
        rozwinięcieNazwy: bool = False
    ) -> AtomowyElementListy:
        """
        Mapuje surowy element listy do modelu API Atomu.

        Args:
            element (SurowyElementListy): Surowy element zwrócony przez parser.
            rozwinięcieNazwy (bool): Określa, czy pole `nazwa` ma zostać zmapowane z pola `rozwiniecie`.

        Returns:
            AtomowyElementListy: Spłaszczony model elementu listy.
        """

        return AtomowyElementListy(
            identyfikator=element["identyfikator"],
            nazwa=element["rozwiniecie"] if rozwinięcieNazwy else element["nazwa"]
        )

    def mapujElementyListy(
        elementy: list[SurowyElementListy] | None,
        rozwinięcieNazwy: bool = False
    ) -> list[AtomowyElementListy]:
        """
        Mapuje listę surowych elementów do modelu API Atomu.

        Args:
            elementy (list[SurowyElementListy] | None): Surowa lista elementów z parsera.
            rozwinięcieNazwy (bool): Określa, czy pole `nazwa` ma zostać zmapowane z pola `rozwiniecie`.

        Returns:
            list[AtomowyElementListy]: Lista przetworzonych elementów.
        """

        return [
            mapujElementListy(element, rozwinięcieNazwy)
            for element in (elementy or [])
        ]

    return AtomoweListy(
        oddzialy=mapujElementyListy(
            dane.get("oddzialy"),
            rozwinięcieNazwy=True
        ),
        nauczyciele=mapujElementyListy(
            dane.get("nauczyciele")
        )
    )

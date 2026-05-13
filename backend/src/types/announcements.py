#
#     ▄▄     ▄▄▄▄▄▄▄▄    ▄▄▄▄    ▄▄▄  ▄▄▄               ▄▄     ▄▄▄▄▄▄     ▄▄▄▄▄▄
#    ████    ▀▀▀██▀▀▀   ██▀▀██   ███  ███              ████    ██▀▀▀▀█▄   ▀▀██▀▀
#    ████       ██     ██    ██  ████████              ████    ██    ██     ██
#   ██  ██      ██     ██    ██  ██ ██ ██             ██  ██   ██████▀      ██
#   ██████      ██     ██    ██  ██ ▀▀ ██             ██████   ██           ██
#  ▄██  ██▄     ██      ██▄▄██   ██    ██            ▄██  ██▄  ██         ▄▄██▄▄
#  ▀▀    ▀▀     ▀▀       ▀▀▀▀    ▀▀    ▀▀            ▀▀    ▀▀  ▀▀         ▀▀▀▀▀▀
#

# Zewnętrzne biblioteki
from pydantic import BaseModel

class Ogłoszenie(BaseModel):
    """
    Słownik ogłoszenia odczytanego ze strony szkoły.
    """

    identyfikator: str
    tytul: str
    stopka: str | None
    url: str
    obraz: str | None


class Ogłoszenia(BaseModel):
    """
    Słownik listy ogłoszeń odczytanej ze strony szkoły.
    """

    aktualnaStrona: int
    ostatniaStrona: int
    poprzedniaStrona: str | None
    nastepnaStrona: str | None
    ogloszenia: list[Ogłoszenie]

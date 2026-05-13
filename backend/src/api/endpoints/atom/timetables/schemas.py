#
#     ▄▄     ▄▄▄▄▄▄▄▄    ▄▄▄▄    ▄▄▄  ▄▄▄               ▄▄     ▄▄▄▄▄▄     ▄▄▄▄▄▄
#    ████    ▀▀▀██▀▀▀   ██▀▀██   ███  ███              ████    ██▀▀▀▀█▄   ▀▀██▀▀
#    ████       ██     ██    ██  ████████              ████    ██    ██     ██
#   ██  ██      ██     ██    ██  ██ ██ ██             ██  ██   ██████▀      ██
#   ██████      ██     ██    ██  ██ ▀▀ ██             ██████   ██           ██
#  ▄██  ██▄     ██      ██▄▄██   ██    ██            ▄██  ██▄  ██         ▄▄██▄▄
#  ▀▀    ▀▀     ▀▀       ▀▀▀▀    ▀▀    ▀▀            ▀▀    ▀▀  ▀▀         ▀▀▀▀▀▀
#

# Standardowe biblioteki
from typing import Literal

# Zewnętrzne biblioteki
from pydantic import BaseModel

class AtomowaLekcja(BaseModel):
    """
    Model lekcji zwracanej przez API aplikacji Atom.
    """

    id: str
    dzien: Literal["Poniedziałek", "Wtorek", "Środa", "Czwartek", "Piątek"]
    numer: int
    poczatek: str
    koniec: str
    przedmiot: str
    nauczyciel: str | None
    sala: str | None
    oddzialy: str | None
    zastepstwo: str | None


class AtomowyPlanLekcji(BaseModel):
    """
    Model planu lekcji zwracanego przez API aplikacji Atom.
    """

    wygenerowano: str | None
    obowiazuje: str | None
    wygasa: str | None
    wolne: bool
    zastepstwa: bool
    lekcje: list[AtomowaLekcja] | None

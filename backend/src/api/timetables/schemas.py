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

# Standardowe biblioteki
from pydantic import BaseModel
from typing import Literal, Union

class EncjaPlanu(BaseModel):
    tekst: str | None
    url: str | None
    identyfikator: str | None


class LekcjaNiestandardowa(BaseModel):
    standard: Literal[False]
    tekst: str


class LekcjaStandardowa(BaseModel):
    standard: Literal[True]
    przedmiot: str
    grupa: str | None
    nauczyciel: EncjaPlanu
    sala: EncjaPlanu
    oddzialy: list[EncjaPlanu]


Lekcja = Union[LekcjaStandardowa, LekcjaNiestandardowa]


class WpisPlanu(BaseModel):
    numer: int
    godziny: str
    lekcje: list[Lekcja]


PlanTygodniowy = dict[str, list[WpisPlanu]]


class PlanLekcji(BaseModel):
    nazwa: str | None
    kategoria: str | None
    url: str
    identyfikator: str | None
    data: str | None
    plan: PlanTygodniowy

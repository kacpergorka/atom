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
from typing import Literal

class Data(BaseModel):
    obowiazuje: str | None
    wygasa: str | None


class ElementPlanu(BaseModel):
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
    nauczyciel: ElementPlanu
    sala: ElementPlanu
    oddzialy: list[ElementPlanu]

Lekcja = LekcjaStandardowa | LekcjaNiestandardowa

class WpisPlanu(BaseModel):
    numer: int
    poczatek: str
    koniec: str
    lekcje: list[Lekcja]

PlanTygodniowy = dict[str, list[WpisPlanu]]

class PlanLekcji(BaseModel):
    nazwa: str | None
    kategoria: str | None
    url: str
    identyfikator: str | None
    wygenerowano: str | None
    data: Data | None
    plan: PlanTygodniowy

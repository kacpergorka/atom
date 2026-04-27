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
from typing import TypedDict

class Data(TypedDict):
    obowiazuje: str | None
    wygasa: str | None


class ZastępstwoPlanu(TypedDict):
    nauczyciel: str | None
    opis: str | None
    uwagi: str | None


class ElementPlanu(TypedDict):
    tekst: str | None
    url: str | None
    identyfikator: str | None


class Lekcja(TypedDict):
    przedmiot: str
    grupa: str | None
    nauczyciel: ElementPlanu | None
    sala: ElementPlanu | None
    oddzialy: list[ElementPlanu] | None
    zastepstwo: ZastępstwoPlanu | None


class WpisPlanu(TypedDict):
    numer: int
    poczatek: str
    koniec: str
    lekcje: list[Lekcja]

PlanTygodniowy = dict[str, list[WpisPlanu]]

class PlanLekcji(TypedDict):
    nazwa: str
    kategoria: str | None
    url: str
    identyfikator: str | None
    wygenerowano: str | None
    data: Data
    zastepstwa: bool
    plan: PlanTygodniowy | None

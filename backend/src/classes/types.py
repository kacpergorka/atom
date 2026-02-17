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
from typing import (
    Literal,
    TypedDict
)

# Konfiguracja aplikacji

class KonfiguracjaPlanów(TypedDict):
    url: str
    kodowanie: str


class KonfiguracjaListy(TypedDict):
    url: str
    kodowanie: str


class KonfiguracjaZastępstw(TypedDict):
    url: str
    kodowanie: str


class Konfiguracja(TypedDict):
    wersja: str
    plany: KonfiguracjaPlanów
    lista: KonfiguracjaListy
    zastepstwa: KonfiguracjaZastępstw
    grupy: list[str]


# Struktury list oddziałów, nauczycieli i sal

class EncjaWartościListy(TypedDict):
    url: str
    identyfikator: str
    rozwiniecie: str

ListaOddziałów = dict[str, EncjaWartościListy]
ListaNauczycieli = dict[str, EncjaWartościListy]
ListaSal = dict[str, EncjaWartościListy]

class Listy(TypedDict):
    oddzialy: ListaOddziałów
    nauczyciele: ListaNauczycieli
    sale: ListaSal


# Struktury planu lekcji

class EncjaPlanu(TypedDict):
    tekst: str | None
    url: str | None
    identyfikator: str | None


class LekcjaNiestandardowa(TypedDict):
    standard: Literal[False]
    tekst: str


class LekcjaStandardowa(TypedDict):
    standard: Literal[True]
    przedmiot: str
    grupa: str | None
    nauczyciel: EncjaPlanu
    sala: EncjaPlanu
    oddzialy: list[EncjaPlanu]


class WpisPlanu(TypedDict):
    numer: int
    godziny: str
    lekcje: list[Lekcja]


class PlanLekcji(TypedDict):
    nazwa: str | None
    kategoria: str | None
    url: str
    identyfikator: str | None
    data: str | None
    plan: PlanTygodniowy

Lekcja = LekcjaStandardowa | LekcjaNiestandardowa
PlanTygodniowy = dict[str, list[WpisPlanu]]


# Struktury zastępstw

class Zastępstwo(TypedDict):
    zidentyfikowane: bool
    nauczyciel: str
    lekcja: int | None
    opis: str | None
    zastepca: str | None
    uwagi: str | None


class Zastępstwa(TypedDict):
    identyfikator: str | None
    dzien: str | None
    informacje: str
    zastepstwa: list[Zastępstwo]

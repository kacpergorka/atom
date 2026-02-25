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
    skrocone: dict[str, str]


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

class Data(TypedDict):
    obowiazuje: str | None
    wygasa: str | None

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

Lekcja = LekcjaStandardowa | LekcjaNiestandardowa

class WpisPlanu(TypedDict):
    numer: int
    poczatek: str
    koniec: str
    lekcje: list[Lekcja]

PlanTygodniowy = dict[str, list[WpisPlanu]]

class PlanLekcji(TypedDict):
    nazwa: str | None
    kategoria: str | None
    url: str
    identyfikator: str | None
    wygenerowano: str | None
    data: Data | None
    plan: PlanTygodniowy


# Struktury zastępstw

class Zastępstwo(TypedDict):
    zidentyfikowane: bool
    grupa: str | None
    nauczyciel: str
    lekcja: int | None
    opis: str | None
    zastepca: str | None
    uwagi: str | None


class Zastępstwa(TypedDict):
    identyfikator: str | None
    dzien: str | None
    informacje: str
    skrocone: bool | None
    zastepstwa: list[Zastępstwo]

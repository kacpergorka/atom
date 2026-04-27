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

class KonfiguracjaListy(TypedDict):
    url: str
    kodowanie: str


class KonfiguracjaSzkoły(TypedDict):
    url: str
    kodowanie: str


class KonfiguracjaOgłoszeń(TypedDict):
    url: str
    kodowanie: str


class KonfiguracjaPlanów(TypedDict):
    url: str
    kodowanie: str


class KonfiguracjaZastępstw(TypedDict):
    url: str
    kodowanie: str


class Konfiguracja(TypedDict):
    wersja: str
    lista: KonfiguracjaListy
    szkola: KonfiguracjaSzkoły
    ogloszenia: KonfiguracjaOgłoszeń
    plany: KonfiguracjaPlanów
    zastepstwa: KonfiguracjaZastępstw
    grupy: list[str]
    skrocone: dict[str, str]

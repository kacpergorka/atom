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

class KonfiguracjaListy(BaseModel):
    """
    Słownik konfiguracji list planu lekcji.
    """

    url: str
    kodowanie: str


class KonfiguracjaSzkoły(BaseModel):
    """
    Słownik konfiguracji strony szkoły.
    """

    url: str
    kodowanie: str


class KonfiguracjaOgłoszeń(BaseModel):
    """
    Słownik konfiguracji ogłoszeń.
    """

    url: str
    kodowanie: str


class KonfiguracjaPlanów(BaseModel):
    """
    Słownik konfiguracji planów lekcji.
    """

    url: str
    kodowanie: str


class KonfiguracjaZastępstw(BaseModel):
    """
    Słownik konfiguracji zastępstw.
    """

    url: str
    kodowanie: str


class KonfiguracjaGrup(BaseModel):
    """
    Słownik konfiguracji grup lekcyjnych.
    """

    zajeciaLekcyjne: list[str]
    zajeciaPraktyczne: list[str]
    wychowanieFizyczne: list[str]
    pozostale: list[str]


class Konfiguracja(BaseModel):
    """
    Słownik pełnej konfiguracji backendu.
    """

    wersja: str
    lista: KonfiguracjaListy
    szkola: KonfiguracjaSzkoły
    ogloszenia: KonfiguracjaOgłoszeń
    plany: KonfiguracjaPlanów
    zastepstwa: KonfiguracjaZastępstw
    grupy: KonfiguracjaGrup
    skrocone: dict[str, str]

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
    Schemat konfiguracji list planu lekcji.
    """

    url: str
    kodowanie: str


class KonfiguracjaSzkoły(BaseModel):
    """
    Schemat konfiguracji strony szkoły.
    """

    url: str
    kodowanie: str


class KonfiguracjaOgłoszeń(BaseModel):
    """
    Schemat konfiguracji ogłoszeń.
    """

    url: str
    kodowanie: str


class KonfiguracjaPlanów(BaseModel):
    """
    Schemat konfiguracji planów lekcji.
    """

    url: str
    kodowanie: str


class KonfiguracjaZastępstw(BaseModel):
    """
    Schemat konfiguracji zastępstw.
    """

    url: str
    kodowanie: str


class KonfiguracjaGrup(BaseModel):
    """
    Schemat konfiguracji grup lekcyjnych.
    """

    zajeciaLekcyjne: list[str]
    zajeciaPraktyczne: list[str]
    wychowanieFizyczne: list[str]
    pozostale: list[str]


class Konfiguracja(BaseModel):
    """
    Schemat pełnej konfiguracji backendu.
    """

    wersja: str
    lista: KonfiguracjaListy
    szkola: KonfiguracjaSzkoły
    ogloszenia: KonfiguracjaOgłoszeń
    plany: KonfiguracjaPlanów
    zastepstwa: KonfiguracjaZastępstw
    grupy: KonfiguracjaGrup
    skrocone: dict[str, str]

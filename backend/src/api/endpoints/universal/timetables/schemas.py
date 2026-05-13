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

class UniwersalnaData(BaseModel):
    """
    Model zakresu obowiązywania planu lekcji.
    """

    obowiazuje: str | None
    wygasa: str | None


class UniwersalneZastepstwoPlanu(BaseModel):
    """
    Model zastępstwa przypisanego do lekcji w planie.
    """

    nauczyciel: str | None
    opis: str | None
    uwagi: str | None


class UniwersalnyElementPlanu(BaseModel):
    """
    Model elementu powiązanego z planem lekcji.
    """

    tekst: str | None
    url: str | None
    identyfikator: str | None


class UniwersalnaLekcja(BaseModel):
    """
    Model lekcji zwracanej przez uniwersalne API.
    """

    przedmiot: str
    grupa: str | None
    nauczyciel: UniwersalnyElementPlanu | None
    sala: UniwersalnyElementPlanu | None
    oddzialy: list[UniwersalnyElementPlanu] | None
    zastepstwo: UniwersalneZastepstwoPlanu | None


class UniwersalnyWpisPlanu(BaseModel):
    """
    Model wpisu godziny lekcyjnej w planie.
    """

    numer: int
    poczatek: str
    koniec: str
    lekcje: list[UniwersalnaLekcja]

UniwersalnyPlanTygodniowy = dict[str, list[UniwersalnyWpisPlanu]]

class UniwersalnyPlanLekcji(BaseModel):
    """
    Model planu lekcji zwracanego przez uniwersalne API.
    """

    nazwa: str
    kategoria: str | None
    url: str
    identyfikator: str | None
    wygenerowano: str | None
    data: UniwersalnaData
    wolne: bool
    zastepstwa: bool
    plan: UniwersalnyPlanTygodniowy | None

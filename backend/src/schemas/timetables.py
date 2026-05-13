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

class Data(BaseModel):
    """
    Schemat zakresu obowiązywania planu lekcji.
    """

    obowiazuje: str | None
    wygasa: str | None


class ZastępstwoPlanu(BaseModel):
    """
    Schemat zastępstwa przypisanego do lekcji w planie.
    """

    nauczyciel: str | None
    opis: str | None
    uwagi: str | None


class ElementPlanu(BaseModel):
    """
    Schemat elementu powiązanego z planem lekcji.
    """

    tekst: str | None
    url: str | None
    identyfikator: str | None


class Lekcja(BaseModel):
    """
    Schemat lekcji w planie lekcji.
    """

    przedmiot: str
    grupa: str | None
    nauczyciel: ElementPlanu | None
    sala: ElementPlanu | None
    oddzialy: list[ElementPlanu] | None
    zastepstwo: ZastępstwoPlanu | None


class WpisPlanu(BaseModel):
    """
    Schemat wpisu godziny lekcyjnej w planie.
    """

    numer: int
    poczatek: str
    koniec: str
    lekcje: list[Lekcja]

PlanTygodniowy = dict[str, list[WpisPlanu]]

class PlanLekcji(BaseModel):
    """
    Schemat planu lekcji.
    """

    nazwa: str
    kategoria: str | None
    url: str
    identyfikator: str | None
    wygenerowano: str | None
    data: Data
    wolne: bool
    zastepstwa: bool
    plan: PlanTygodniowy | None

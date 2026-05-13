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
    Słownik zakresu obowiązywania planu lekcji.
    """

    obowiazuje: str | None
    wygasa: str | None


class ZastępstwoPlanu(BaseModel):
    """
    Słownik zastępstwa przypisanego do lekcji w planie.
    """

    nauczyciel: str | None
    opis: str | None
    uwagi: str | None


class ElementPlanu(BaseModel):
    """
    Słownik elementu powiązanego z planem lekcji.
    """

    tekst: str | None
    url: str | None
    identyfikator: str | None


class Lekcja(BaseModel):
    """
    Słownik lekcji w planie lekcji.
    """

    przedmiot: str
    grupa: str | None
    nauczyciel: ElementPlanu | None
    sala: ElementPlanu | None
    oddzialy: list[ElementPlanu] | None
    zastepstwo: ZastępstwoPlanu | None


class WpisPlanu(BaseModel):
    """
    Słownik wpisu godziny lekcyjnej w planie.
    """

    numer: int
    poczatek: str
    koniec: str
    lekcje: list[Lekcja]

PlanTygodniowy = dict[str, list[WpisPlanu]]

class PlanLekcji(BaseModel):
    """
    Słownik planu lekcji.
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

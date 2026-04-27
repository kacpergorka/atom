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
    obowiazuje: str | None
    wygasa: str | None


class UniwersalneZastepstwoPlanu(BaseModel):
    nauczyciel: str | None
    opis: str | None
    uwagi: str | None


class UniwersalnyElementPlanu(BaseModel):
    tekst: str | None
    url: str | None
    identyfikator: str | None


class UniwersalnaLekcja(BaseModel):
    przedmiot: str
    grupa: str | None
    nauczyciel: UniwersalnyElementPlanu | None
    sala: UniwersalnyElementPlanu | None
    oddzialy: list[UniwersalnyElementPlanu] | None
    zastepstwo: UniwersalnyElementPlanu | None


class UniwersalnyWpisPlanu(BaseModel):
    numer: int
    poczatek: str
    koniec: str
    lekcje: list[UniwersalnaLekcja]

UniwersalnyPlanTygodniowy = dict[str, list[UniwersalnyWpisPlanu]]

class UniwersalnyPlanLekcji(BaseModel):
    nazwa: str
    kategoria: str | None
    url: str
    identyfikator: str | None
    wygenerowano: str | None
    data: UniwersalnaData
    zastepstwa: bool
    plan: UniwersalnyPlanTygodniowy | None

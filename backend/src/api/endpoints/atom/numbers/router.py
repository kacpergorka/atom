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
from fastapi import APIRouter

# Wewnętrzne importy
from src.api.endpoints.atom.numbers.schemas import AtomoweSzczesliweNumerki
from src.api.endpoints.atom.numbers.service import pobierzSzczęśliweNumerki

router = APIRouter(
    prefix="/v1/atom/numerki",
    tags=["Szczęśliwe numerki"],
)

@router.get(
        "",
        response_model=AtomoweSzczesliweNumerki,
        responses={
            500: {"description": "Wystąpił nieoczekiwany błąd po stronie serwera."},
            502: {"description": "Wystąpił błąd podczas przetwarzania danych."}
        },
        summary="Pobiera dwa szczęśliwe numerki dla aplikacji mobilnej Atom.",
        description="Pobiera dwa losowo wygenerowane szczęśliwe numerki z zakresu od 1 do 35."
)
async def numerki() -> AtomoweSzczesliweNumerki:
    return await pobierzSzczęśliweNumerki()

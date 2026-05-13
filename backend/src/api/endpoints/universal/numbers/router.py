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
from src.api.endpoints.universal.numbers.service import pobierzSzczęśliweNumerki
from src.schemas.numbers import SzczęśliweNumerki

router = APIRouter(
    prefix="/v1/numerki",
    tags=["Szczęśliwe numerki"],
)

@router.get(
    "",
    response_model=SzczęśliweNumerki,
    responses={
        500: {"description": "Wystąpił nieoczekiwany błąd po stronie serwera."},
        502: {"description": "Wystąpił błąd podczas przetwarzania danych."}
    },
    summary="Pobiera dwa szczęśliwe numerki.",
    description="Pobiera dwa losowo wygenerowane szczęśliwe numerki z zakresu od 1 do 35."
)
async def numerki() -> SzczęśliweNumerki:
    return await pobierzSzczęśliweNumerki()

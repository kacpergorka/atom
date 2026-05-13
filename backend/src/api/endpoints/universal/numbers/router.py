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
from src.api.endpoints.universal.numbers.schemas import UniwersalneSzczesliweNumerki
from src.api.endpoints.universal.numbers.service import pobierzSzczęśliweNumerki

router = APIRouter(
    prefix="/v1/numerki",
    tags=["Szczęśliwe numerki"],
)

@router.get(
    "",
    response_model=UniwersalneSzczesliweNumerki,
    responses={
        500: {"description": "Wystąpił nieoczekiwany błąd po stronie serwera."},
        502: {"description": "Wystąpił błąd podczas przetwarzania danych."}
    },
    summary="Pobiera dwa szczęśliwe numerki.",
    description="Pobiera dwa losowo wygenerowane szczęśliwe numerki z zakresu od 1 do 35."
)
async def numerki() -> UniwersalneSzczesliweNumerki:
    return await pobierzSzczęśliweNumerki()

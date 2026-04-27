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
from fastapi import (
    APIRouter,
    Query
)

# Wewnętrzne importy
from src.api.endpoints.universal.announcements.schemas import UniwersalneOgloszenia
from src.api.endpoints.universal.announcements.service import pobierzOgłoszenia

router = APIRouter(
    prefix="/v1/ogloszenia",
    tags=["Ogłoszenia"],
)

@router.get(
        "",
        response_model=UniwersalneOgloszenia,
        responses={
            500: {"description": "Wystąpił nieoczekiwany błąd po stronie serwera."},
            502: {"description": "Wystąpił błąd podczas przetwarzania danych."},
            503: {"description": "Przekroczono czas oczekiwania na połączenie."}
        },
        summary="Pobiera podglądy ogłoszeń z listy aktualności.",
        description="Pobiera podglądy ogłoszeń z listy aktualności ze strony internetowej szkoły, której to URL wprowadzony jest w pliku konfiguracyjnym API."
)
async def ogloszenia(strona: int = Query(1, ge=1, description="Numer strony listy aktualności.")) -> UniwersalneOgloszenia:
    return await pobierzOgłoszenia(strona)

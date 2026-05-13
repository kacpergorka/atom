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
from src.api.endpoints.universal.announcements.service import pobierzOgłoszenia
from src.schemas.announcements import Ogłoszenia

router = APIRouter(
    prefix="/v1/ogloszenia",
    tags=["Ogłoszenia"],
)

@router.get(
    "",
    response_model=Ogłoszenia,
    responses={
        500: {"description": "Wystąpił nieoczekiwany błąd po stronie serwera."},
        502: {"description": "Wystąpił błąd podczas przetwarzania danych."},
        503: {"description": "Przekroczono czas oczekiwania na połączenie."}
    },
    summary="Pobiera podglądy ogłoszeń z listy aktualności.",
    description="Pobiera podglądy ogłoszeń z listy aktualności ze strony internetowej szkoły, której to URL wprowadzony jest w pliku konfiguracyjnym API."
)
async def ogloszenia(strona: int = Query(1, ge=1, description="Numer strony listy aktualności.")) -> Ogłoszenia:
    return await pobierzOgłoszenia(strona)

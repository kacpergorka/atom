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
from src.api.endpoints.universal.lists.schemas import UniwersalneListy
from src.api.endpoints.universal.lists.service import pobierzListy

router = APIRouter(
    prefix="/v1/listy",
    tags=["UniwersalneListy"],
)

@router.get(
        "",
        response_model=UniwersalneListy,
        responses={
            500: {"description": "Wystąpił nieoczekiwany błąd po stronie serwera."},
            502: {"description": "Wystąpił błąd podczas przetwarzania danych."},
            503: {"description": "Przekroczono czas oczekiwania na połączenie."}
        },
        summary="Pobiera listy oddziałów, nauczycieli oraz sal.",
        description="Pobiera listy oddziałów, nauczycieli oraz sal ze strony internetowej planu lekcji, której to URL wprowadzony jest w pliku konfiguracyjnym API. W przypadku braku argumentów zwraca wszystkie dostępne listy."
)
async def listy(
    oddzialy: bool = Query(True, description="Określa, czy uwzględnić listę oddziałów."),
    nauczyciele: bool = Query(True, description="Określa, czy uwzględnić listę nauczycieli."),
    sale: bool = Query(True, description="Określa, czy uwzględnić listę sal.")
) -> UniwersalneListy:
    return await pobierzListy(oddzialy, nauczyciele, sale)

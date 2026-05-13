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
from src.api.endpoints.universal.timetables.schemas import UniwersalnyPlanLekcji
from src.api.endpoints.universal.timetables.service import pobierzPlanLekcji

router = APIRouter(
    prefix="/v1/planlekcji",
    tags=["Plan lekcji"],
)

@router.get(
    "",
    response_model=UniwersalnyPlanLekcji,
    responses={
        400: {"description": "Otrzymano nieprawidłowy identyfikator."},
        500: {"description": "Wystąpił nieoczekiwany błąd po stronie serwera."},
        502: {"description": "Wystąpił błąd podczas przetwarzania danych."},
        503: {"description": "Przekroczono czas oczekiwania na połączenie."}
    },
    summary="Pobiera dane planu lekcji.",
    description="Pobiera plan lekcji ze strony internetowej, której to URL wprowadzony jest w pliku konfiguracyjnym API."
)
async def planlekcji(
    identyfikator: str = Query(..., description="Identyfikator oddziału, nauczyciela lub sali, np. o17, n78, s45."),
    grupy: list[str] | None = Query(None, description="Lista oznaczeń określających grupę przedmiotów."),
    zastepstwa: bool = Query(False, description="Określa, czy uwzględniać zastępstwa w planie lekcji. Przy włączonej opcji pobranie planu sali nie będzie możliwe."),
    religia: bool = Query(True, description="Określa, czy uwzględniać lekcje religii w planie lekcji."),
    edukacjaZdrowotna: bool = Query(True, description="Określa, czy uwzględniać lekcje edukacji zdrowotnej w planie lekcji.")
) -> UniwersalnyPlanLekcji:
    return await pobierzPlanLekcji(identyfikator, grupy, zastepstwa, religia, edukacjaZdrowotna)

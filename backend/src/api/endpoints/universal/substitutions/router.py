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
from src.api.endpoints.universal.substitutions.schemas import UniwersalneZastepstwa
from src.api.endpoints.universal.substitutions.service import pobierzZastępstwa

router = APIRouter(
    prefix="/v1/zastepstwa",
    tags=["Zastępstwa"],
)

@router.get(
    "",
    response_model=UniwersalneZastepstwa,
    responses={
        400: {"description": "Otrzymano nieprawidłowy identyfikator."},
        500: {"description": "Wystąpił nieoczekiwany błąd po stronie serwera."},
        502: {"description": "Wystąpił błąd podczas przetwarzania danych."},
        503: {"description": "Przekroczono czas oczekiwania na połączenie."}
    },
    summary="Pobiera dane zastępstw.",
    description="Pobiera informacje dodatkowe oraz listę zastępstw dla wybranego podmiotu ze strony internetowej, której to URL wprowadzony jest w pliku konfiguracyjnym API. W przypadku braku identyfikatora zwraca całą listę zastępstw."
)
async def zastepstwa(
    identyfikator: str | None = Query(None, description="Identyfikator oddziału lub nauczyciela, np. o17, n78"),
    grupy: list[str] | None = Query(None, description="Lista oznaczeń określających grupę przedmiotów. Wymagany identyfikator."),
    religia: bool = Query(True, description="Określa, czy uwzględniać lekcje religii."),
    edukacjaZdrowotna: bool = Query(True, description="Określa, czy uwzględniać lekcje edukacji zdrowotnej.")
) -> UniwersalneZastepstwa:
    return await pobierzZastępstwa(identyfikator, grupy, religia, edukacjaZdrowotna)

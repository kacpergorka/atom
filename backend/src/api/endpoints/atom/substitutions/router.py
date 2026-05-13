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
from src.api.endpoints.atom.substitutions.schemas import AtomoweZastepstwa
from src.api.endpoints.atom.substitutions.service import pobierzZastępstwa

router = APIRouter(
    prefix="/v1/atom/zastepstwa",
    tags=["Zastępstwa"],
)

@router.get(
    "",
    response_model=AtomoweZastepstwa,
    responses={
        400: {"description": "Otrzymano nieprawidłowy identyfikator."},
        500: {"description": "Wystąpił nieoczekiwany błąd po stronie serwera."},
        502: {"description": "Wystąpił błąd podczas przetwarzania danych."},
        503: {"description": "Przekroczono czas oczekiwania na połączenie."}
    },
    summary="Pobiera dane zastępstw dla aplikacji mobilnej Atom.",
    description="Pobiera informacje dodatkowe oraz całą listę zastępstw ze strony internetowej, której to URL wprowadzony jest w pliku konfiguracyjnym API."
)
async def zastepstwa() -> AtomoweZastepstwa:
    return await pobierzZastępstwa()

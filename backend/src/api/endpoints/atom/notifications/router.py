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
    Depends,
    Response,
    status
)

# Wewnętrzne importy
from src.api.endpoints.atom.notifications.schemas import TokenPowiadomien
from src.handlers.accounts.auth import pobierzAktualnegoUżytkownika
from src.handlers.accounts.limits import ograniczŻądania
from src.handlers.notifications import database
from src.types.accounts import AktualnyUżytkownik

router = APIRouter(
    prefix="/powiadomienia",
    tags=["Powiadomienia"],
)

@router.post(
    "/zarejestruj",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {"description": "Token urządzenia został zapisany."},
        401: {"description": "Wymagana autoryzacja."},
        422: {"description": "Nieprawidłowe dane żądania."},
        429: {"description": "Zbyt wiele żądań."},
        500: {"description": "Wystąpił nieoczekiwany błąd po stronie serwera."},
    },
    summary="Rejestruje urządzenie.",
    description="Rejestruje urządzenie w bazie danych zapisując jego token."
)
async def zarejestruj(
    dane: TokenPowiadomien,
    użytkownik: AktualnyUżytkownik = Depends(pobierzAktualnegoUżytkownika),
    _: None = Depends(ograniczŻądania("powiadomienia:rejestracja", maksimum=10, czasPrzedziału=60)),
) -> Response:
    await database.zapiszUrządzenie(użytkownik.identyfikator, dane.tokenUrzadzenia)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete(
    "/wyrejestruj",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {"description": "Token urządzenia został usunięty."},
        401: {"description": "Wymagana autoryzacja."},
        422: {"description": "Nieprawidłowe dane żądania."},
        429: {"description": "Zbyt wiele żądań."},
        500: {"description": "Wystąpił nieoczekiwany błąd po stronie serwera."},
    },
    summary="Wyrejestrowuje urządzenie.",
    description="Wyrejestrowuje urządzenie z bazy danych bez usuwania preferencji powiązanych z kontem użytkownika."
)
async def wyrejestruj(
    dane: TokenPowiadomien,
    użytkownik: AktualnyUżytkownik = Depends(pobierzAktualnegoUżytkownika),
    _: None = Depends(ograniczŻądania("powiadomienia:usuwanie", maksimum=10, czasPrzedziału=60)),
) -> Response:
    await database.usuńUrządzenieUżytkownika(użytkownik.identyfikator, dane.tokenUrzadzenia)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

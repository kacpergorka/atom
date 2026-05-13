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
from src.api.endpoints.atom.accounts.schemas import Konto
from src.api.endpoints.atom.accounts.service import (
    pobierzIdentyfikatorApple,
    usuńKontoUżytkownika
)
from src.handlers.accounts import database
from src.handlers.accounts.auth import pobierzAktualnegoUżytkownika
from src.handlers.accounts.limits import ograniczŻądania
from src.models.accounts import AktualnyUżytkownik as AtomowyAktualnyUżytkownik

router = APIRouter(
    prefix="/konto",
    tags=["Konto"],
)

@router.put(
    "/synchronizuj",
    response_model=Konto,
    responses={
        200: {"description": "Konto zostało zsynchronizowane."},
        401: {"description": "Wymagana autoryzacja."},
        429: {"description": "Zbyt wiele żądań."},
        500: {"description": "Wystąpił nieoczekiwany błąd po stronie serwera."},
        502: {"description": "Nie udało się pobrać konta w Supabase."},
        503: {"description": "Obsługa konta nie jest skonfigurowana."},
    },
    summary="Synchronizuje profil aktualnego użytkownika.",
    description="Zapisuje albo odczytuje wymagany do prawidłowego działania aplikacji profil powiązany ze stabilnym identyfikatorem Apple odczytanym po stronie backendu."
)
async def synchronizuj(
    dane: Konto,
    użytkownik: AtomowyAktualnyUżytkownik = Depends(pobierzAktualnegoUżytkownika),
    _: None = Depends(ograniczŻądania("konto:synchronizacja", maksimum=20, czasPrzedziału=60)),
) -> Konto:
    identyfikatorApple = await pobierzIdentyfikatorApple(użytkownik.identyfikator)

    if dane.nazwa is not None:
        await database.zapiszProfilApple(użytkownik.identyfikator, identyfikatorApple, dane.nazwa)
        return Konto(nazwa=dane.nazwa)

    istniejącaNazwa = await database.pobierzNazwęProfiluApple(identyfikatorApple)
    if istniejącaNazwa is not None:
        await database.zapiszProfilApple(użytkownik.identyfikator, identyfikatorApple, istniejącaNazwa)

    return Konto(nazwa=istniejącaNazwa)


@router.delete(
    "/usun",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {"description": "Konto zostało usunięte."},
        401: {"description": "Wymagana autoryzacja."},
        429: {"description": "Zbyt wiele żądań."},
        500: {"description": "Wystąpił nieoczekiwany błąd po stronie serwera."},
        502: {"description": "Nie udało się usunąć konta w Supabase."},
        503: {"description": "Usuwanie konta nie jest skonfigurowane."},
    },
    summary="Usuwa konto oraz dane aktualnego użytkownika.",
    description="Usuwa konto Supabase oraz lokalne dane użytkownika, pozostawiając wymagany do prawidłowego działania aplikacji profil Apple."
)
async def usuń(
    użytkownik: AtomowyAktualnyUżytkownik = Depends(pobierzAktualnegoUżytkownika),
    _: None = Depends(ograniczŻądania("konto:usuwanie", maksimum=3, czasPrzedziału=3600)),
) -> Response:
    await usuńKontoUżytkownika(użytkownik.identyfikator)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

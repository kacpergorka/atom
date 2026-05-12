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
from src.api.endpoints.atom.preferences.schemas import Preferencje
from src.handlers.notifications import database
from src.handlers.accounts.auth import (
    AktualnyUżytkownik,
    pobierzAktualnegoUżytkownika
)
from src.handlers.accounts.limits import ograniczŻądania
from src.types.notifications import PreferencjePowiadomień

router = APIRouter(
    prefix="/preferencje",
    tags=["Preferencje"],
)

@router.get(
    "/pobierz",
    response_model=Preferencje | None,
    responses={
        401: {"description": "Wymagana autoryzacja."},
        429: {"description": "Zbyt wiele żądań."},
        500: {"description": "Wystąpił nieoczekiwany błąd po stronie serwera."},
    },
    summary="Pobiera preferencje użytkownika.",
    description="Pobiera preferencje powiązane z kontem aktualnego użytkownika z JWT."
)
async def pobierz(
    użytkownik: AktualnyUżytkownik = Depends(pobierzAktualnegoUżytkownika),
    _: None = Depends(ograniczŻądania("preferencje:pobieranie", maksimum=30, czasPrzedziału=60)),
) -> Preferencje | None:
    preferencje = await database.pobierzPreferencjeUżytkownika(użytkownik.identyfikator)
    if preferencje is None:
        return None

    return Preferencje(
        oddzial=preferencje.oddział,
        identyfikatorOddzialu=preferencje.identyfikatorOddziału,
        nauczyciel=preferencje.nauczyciel,
        identyfikatorNauczyciela=preferencje.identyfikatorNauczyciela,
        grupaZajecLekcyjnych=preferencje.grupaZajęćLekcyjnych,
        grupaZajecPraktycznych=preferencje.grupaZajęćPraktycznych,
        grupaWychowaniaFizycznego=preferencje.grupaWychowaniaFizycznego,
        religia=preferencje.religia,
        edukacjaZdrowotna=preferencje.edukacjaZdrowotna,
        numerekUcznia=preferencje.numerekUcznia,
    )


@router.put(
    "/zapisz",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {"description": "Preferencje zostały zapisane."},
        401: {"description": "Wymagana autoryzacja."},
        422: {"description": "Nieprawidłowe dane żądania."},
        429: {"description": "Zbyt wiele żądań."},
        500: {"description": "Wystąpił nieoczekiwany błąd po stronie serwera."},
    },
    summary="Zapisuje preferencje użytkownika.",
    description="Zapisuje preferencje powiązane z kontem aktualnego użytkownika z JWT."
)
async def zapisz(
    dane: Preferencje,
    użytkownik: AktualnyUżytkownik = Depends(pobierzAktualnegoUżytkownika),
    _: None = Depends(ograniczŻądania("preferencje:zapis", maksimum=20, czasPrzedziału=60)),
) -> Response:
    await database.zapiszPreferencje(
        PreferencjePowiadomień(
            identyfikatorUżytkownika=użytkownik.identyfikator,
            oddział=dane.oddzial,
            identyfikatorOddziału=dane.identyfikatorOddzialu,
            nauczyciel=dane.nauczyciel,
            identyfikatorNauczyciela=dane.identyfikatorNauczyciela,
            grupaZajęćLekcyjnych=dane.grupaZajecLekcyjnych,
            grupaZajęćPraktycznych=dane.grupaZajecPraktycznych,
            grupaWychowaniaFizycznego=dane.grupaWychowaniaFizycznego,
            religia=dane.religia,
            edukacjaZdrowotna=dane.edukacjaZdrowotna,
            numerekUcznia=dane.numerekUcznia,
        )
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)

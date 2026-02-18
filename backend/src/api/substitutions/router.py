#
#
#     ▄▄     ▄▄▄▄▄▄▄▄    ▄▄▄▄    ▄▄▄  ▄▄▄               ▄▄     ▄▄▄▄▄▄     ▄▄▄▄▄▄
#    ████    ▀▀▀██▀▀▀   ██▀▀██   ███  ███              ████    ██▀▀▀▀█▄   ▀▀██▀▀
#    ████       ██     ██    ██  ████████              ████    ██    ██     ██
#   ██  ██      ██     ██    ██  ██ ██ ██             ██  ██   ██████▀      ██
#   ██████      ██     ██    ██  ██ ▀▀ ██             ██████   ██           ██
#  ▄██  ██▄     ██      ██▄▄██   ██    ██            ▄██  ██▄  ██         ▄▄██▄▄
#  ▀▀    ▀▀     ▀▀       ▀▀▀▀    ▀▀    ▀▀            ▀▀    ▀▀  ▀▀         ▀▀▀▀▀▀
#
#

# Zewnętrzne biblioteki
from fastapi import (
    APIRouter,
    HTTPException,
    Query
)

# Wewnętrzne importy
from src.api.substitutions.exceptions import (
    BłądWewnętrzny,
    BrakWymaganychDanych,
    NieprawidłowyIdentyfikator,
    ŹródłoNiedostępne
)
from src.api.substitutions.schemas import Zastepstwa
from src.api.substitutions.service import pobierzZastępstwa

router = APIRouter(
    prefix="/zastepstwa",
    tags=["Zastępstwa"],
)

@router.get(
        "",
        response_model=Zastepstwa,
        responses={
            400: {"description": "Otrzymano nieprawidłowy identyfikator."},
            500: {"description": "Wystąpił nieoczekiwany błąd po stronie serwera."},
            502: {"description": "Wystąpił błąd podczas przetwarzania danych."},
            503: {"description": "Przekroczono czas oczekiwania na połączenie."}
        },
        summary="Pobiera dane zastępstw.",
        description="Pobiera informacje dodatkowe oraz listę zastępstw dla wybranego podmiotu ze strony internetowej, której to URL wprowadzony jest w pliku konfiguracyjnym serwera. W przypadku braku identyfikatora zwraca całą listę zastępstw."
)
async def zastepstwa(
    identyfikator: str | None = Query(None, description="Identyfikator oddziału lub nauczyciela, np. o17, n78"),
    grupy: list[str] | None = Query(None, description="Lista oznaczeń określających grupę przedmiotów."),
    religia: bool | None = Query(None, description="Określa, czy uwzględniać lekcje religii w planie lekcji."),
    edukacjaZdrowotna: bool | None = Query(None, description="Określa, czy uwzględniać lekcje edukacji zdrowotnej w planie lekcji.")
) -> Zastepstwa:
    try:
        return await pobierzZastępstwa(identyfikator, grupy, religia, edukacjaZdrowotna)
    except NieprawidłowyIdentyfikator:
        raise HTTPException(400, "Otrzymano nieprawidłowy identyfikator.")
    except BrakWymaganychDanych:
        raise HTTPException(500, "Brak wymaganych danych w pliku konfiguracyjnym serwera.")
    except BłądWewnętrzny:
        raise HTTPException(502, "Wystąpił błąd podczas przetwarzania danych.")
    except ŹródłoNiedostępne:
        raise HTTPException(503, "Przekroczono czas oczekiwania na połączenie.")
    except Exception:
        raise HTTPException(500, "Wystąpił nieoczekiwany błąd po stronie serwera.")

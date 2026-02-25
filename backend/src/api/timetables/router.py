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
from src.api.timetables.exceptions import (
    BłądWewnętrzny,
    BrakWymaganychDanych,
    NieprawidłowyIdentyfikator,
    ŹródłoNiedostępne
)
from src.api.timetables.schemas import PlanLekcji
from src.api.timetables.service import pobierzPlanLekcji

router = APIRouter(
    prefix="/planlekcji",
    tags=["Plan lekcji"],
)

@router.get(
        "",
        response_model=PlanLekcji,
        responses={
            400: {"description": "Otrzymano nieprawidłowy identyfikator."},
            500: {"description": "Wystąpił nieoczekiwany błąd po stronie serwera."},
            502: {"description": "Wystąpił błąd podczas przetwarzania danych."},
            503: {"description": "Przekroczono czas oczekiwania na połączenie."}
        },
        summary="Pobiera dane planu lekcji.",
        description="Pobiera plan lekcji ze strony internetowej, której to URL wprowadzony jest w pliku konfiguracyjnym serwera."
)
async def planlekcji(
    identyfikator: str = Query(..., description="Identyfikator oddziału, nauczyciela lub sali, np. o17, n78, s45."),
    grupy: list[str] | None = Query(None, description="Lista oznaczeń określających grupę przedmiotów."),
    skrocone: str | None = Query(None, description="Dzień tygodnia, dla którego obowiązuje skrócony rozkład zajęć."),
    religia: bool | None = Query(None, description="Określa, czy uwzględniać lekcje religii w planie lekcji."),
    edukacjaZdrowotna: bool | None = Query(None, description="Określa, czy uwzględniać lekcje edukacji zdrowotnej w planie lekcji.")
) -> PlanLekcji:
    try:
        return await pobierzPlanLekcji(identyfikator, grupy, skrocone, religia, edukacjaZdrowotna)
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

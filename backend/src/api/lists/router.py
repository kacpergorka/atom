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
from src.api.lists.exceptions import (
    BłądWewnętrzny,
    BrakWymaganychDanych,
    ŹródłoNiedostępne
)
from src.api.lists.schemas import Listy
from src.api.lists.service import pobierzListy

router = APIRouter(
    prefix="/listy",
    tags=["Listy"],
)

@router.get(
        "",
        response_model=Listy,
        responses={
            500: {"description": "Wystąpił nieoczekiwany błąd po stronie serwera."},
            502: {"description": "Wystąpił błąd podczas przetwarzania danych."},
            503: {"description": "Przekroczono czas oczekiwania na połączenie."}
        },
        summary="Pobiera listy oddziałów, nauczycieli oraz sal.",
        description="Pobiera listy oddziałów, nauczycieli oraz sal ze strony internetowej planu lekcji, której to URL wprowadzony jest w pliku konfiguracyjnym serwera."
)
async def listy(
    oddzialy: bool | None = Query(None, description="Określa, czy uwzględnić listę oddziałów."),
    nauczyciele: bool | None = Query(None, description="Określa, czy uwzględnić listę nauczycieli."),
    sale: bool | None = Query(None, description="Określa, czy uwzględnić listę sal.")
) -> Listy:
    try:
        return await pobierzListy(oddzialy, nauczyciele, sale)
    except BrakWymaganychDanych:
        raise HTTPException(500, "Brak wymaganych danych w pliku konfiguracyjnym serwera.")
    except BłądWewnętrzny:
        raise HTTPException(502, "Wystąpił błąd podczas przetwarzania danych.")
    except ŹródłoNiedostępne:
        raise HTTPException(503, "Przekroczono czas oczekiwania na połączenie.")
    except Exception:
        raise HTTPException(500, "Wystąpił nieoczekiwany błąd po stronie serwera.")

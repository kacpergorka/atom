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
    FastAPI,
    Request
)
from fastapi.responses import JSONResponse

# Wewnętrzne importy
from src.api.exceptions import (
    BłądWewnętrzny,
    BrakWymaganychDanych,
    NieprawidłowyIdentyfikator,
    ŹródłoNiedostępne
)
from src.handlers.logging import logowanie

def zarejestrujObsługęWyjątków(app: FastAPI) -> None:
    @app.exception_handler(NieprawidłowyIdentyfikator)
    async def obsłużNieprawidłowyIdentyfikator(
        _: Request,
        __: NieprawidłowyIdentyfikator
    ) -> JSONResponse:
        return JSONResponse(
            status_code=400,
            content={"detail": "Otrzymano nieprawidłowy identyfikator."}
        )

    @app.exception_handler(BrakWymaganychDanych)
    async def obsłużBrakWymaganychDanych(
        _: Request,
        __: BrakWymaganychDanych
    ) -> JSONResponse:
        return JSONResponse(
            status_code=500,
            content={"detail": "Brak wymaganych danych w pliku konfiguracyjnym serwera."}
        )

    @app.exception_handler(BłądWewnętrzny)
    async def obsłużBłądWewnętrzny(
        _: Request,
        __: BłądWewnętrzny
    ) -> JSONResponse:
        return JSONResponse(
            status_code=502,
            content={"detail": "Wystąpił błąd podczas przetwarzania danych."}
        )

    @app.exception_handler(ŹródłoNiedostępne)
    async def obsłużŹródłoNiedostępne(
        _: Request,
        __: ŹródłoNiedostępne
    ) -> JSONResponse:
        return JSONResponse(
            status_code=503,
            content={"detail": "Przekroczono czas oczekiwania na połączenie."}
        )

    @app.exception_handler(Exception)
    async def obsłużNieoczekiwanyBłąd(
        request: Request,
        exception: Exception
    ) -> JSONResponse:
        logowanie.exception(
            f"Wystąpił nieoczekiwany błąd podczas obsługi żądania {request.method} {request.url.path}. Więcej informacji: {exception}"
        )
        return JSONResponse(
            status_code=500,
            content={"detail": "Wystąpił nieoczekiwany błąd po stronie serwera."}
        )

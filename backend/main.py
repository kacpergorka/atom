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
from fastapi import FastAPI
from contextlib import asynccontextmanager

# Wewnętrzne importy
from src.assets.ascii import ascii
from src.classes.atom import atom
from src.handlers.configuration import konfiguracja
from src.handlers.logging import logowanie
from src.api.substitutions.router import router as routerZastępstw
from src.api.lists.router import router as routerList
from src.api.timetables.router import router as routerPlanówLekcji

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        logowanie.info(ascii)
        await atom.start()
        logowanie.info(
            "Atom API zostało poprawnie uruchomione. Enjoy!"
        )
        yield
    except Exception as e:
        logowanie.critical(
            f"Wystąpił błąd krytyczny podczas uruchomiania Atom API. Więcej informacji: {e}"
        )
        raise
    finally:
        await atom.close()

app = FastAPI(
    title="Atom API",
    description="Dedykowana wersja backendu API dla aplikacji mobilnej Atom. Stworzone z ❤️ przez Kacpra Górkę!",
    version=konfiguracja.get("wersja", "Brak danych"),
    lifespan=lifespan
)

app.include_router(routerList)
app.include_router(routerPlanówLekcji)
app.include_router(routerZastępstw)

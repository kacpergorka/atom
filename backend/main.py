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
async def lifespan(_: FastAPI):
    uruchomiony = False
    try:
        logowanie.info(ascii)
        await atom.start()
        uruchomiony = True
        logowanie.info(
            "Atom API zostało poprawnie uruchomione. Enjoy!"
        )
        yield
    except Exception as e:
        logowanie.critical(
            f"Wystąpił błąd krytyczny podczas uruchomiania Atom API. Więcej informacji: {e}",
            exc_info=True
        )
        raise
    finally:
        if uruchomiony:
            await atom.close()

description = """
*Jest to dedykowana wersja backendu dla aplikacji mobilnej Atom.*\n
**Stworzone z ❤️ przez Kacpra Górkę!**
Projekt jest [otwartoźródłowy](https://github.com/kacpergorka/atom)!
"""

app = FastAPI(
    title="Atom API",
    description=description,
    summary="Atom API umożliwia pobieranie publicznie dostępnych danych z serwerów Zespołu Szkół Elektronicznych w Bydgoszczy.",
    version=konfiguracja.get("wersja", "Brak danych"),
    license_info={
        "name": "Apache License 2.0",
        "url": "https://github.com/kacpergorka/atom/blob/main/LICENSE",
    },
    lifespan=lifespan
)

app.include_router(routerList)
app.include_router(routerPlanówLekcji)
app.include_router(routerZastępstw)

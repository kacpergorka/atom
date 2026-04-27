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
from contextlib import asynccontextmanager
from fastapi import FastAPI

# Wewnętrzne importy
from src.api.endpoints.atom.announcements.router import router as routerOgłoszeńDlaAtomu
from src.api.endpoints.atom.lists.router import router as routerListAtomu
from src.api.endpoints.atom.numbers.router import router as routerNumerkówDlaAtomu
from src.api.endpoints.atom.substitutions.router import router as routerZastępstwAtomu
from src.api.endpoints.atom.timetables.router import router as routerPlanówLekcjiAtomu
from src.api.endpoints.universal.announcements.router import router as routerOgłoszeń
from src.api.endpoints.universal.lists.router import router as routerList
from src.api.endpoints.universal.numbers.router import router as routerNumerków
from src.api.endpoints.universal.substitutions.router import router as routerZastępstw
from src.api.endpoints.universal.timetables.router import router as routerPlanówLekcji
from src.api.handlers import zarejestrujObsługęWyjątków
from src.classes.atom import atom
from src.handlers.configuration import konfiguracja
from src.handlers.logging import logowanie

@asynccontextmanager
async def lifespan(_: FastAPI):
    try:
        await atom.start()
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
        await atom.close()

description = """
**Stworzone z ❤️ przez Kacpra Górkę!** Projekt jest [otwartoźródłowy](https://github.com/kacpergorka/atom)!
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

zarejestrujObsługęWyjątków(app)

app.include_router(routerListAtomu)
app.include_router(routerNumerkówDlaAtomu)
app.include_router(routerOgłoszeńDlaAtomu)
app.include_router(routerPlanówLekcjiAtomu)
app.include_router(routerZastępstwAtomu)

app.include_router(routerList)
app.include_router(routerNumerków)
app.include_router(routerOgłoszeń)
app.include_router(routerPlanówLekcji)
app.include_router(routerZastępstw)

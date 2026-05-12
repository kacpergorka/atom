#
#     ▄▄     ▄▄▄▄▄▄▄▄    ▄▄▄▄    ▄▄▄  ▄▄▄               ▄▄     ▄▄▄▄▄▄     ▄▄▄▄▄▄
#    ████    ▀▀▀██▀▀▀   ██▀▀██   ███  ███              ████    ██▀▀▀▀█▄   ▀▀██▀▀
#    ████       ██     ██    ██  ████████              ████    ██    ██     ██
#   ██  ██      ██     ██    ██  ██ ██ ██             ██  ██   ██████▀      ██
#   ██████      ██     ██    ██  ██ ▀▀ ██             ██████   ██           ██
#  ▄██  ██▄     ██      ██▄▄██   ██    ██            ▄██  ██▄  ██         ▄▄██▄▄
#  ▀▀    ▀▀     ▀▀       ▀▀▀▀    ▀▀    ▀▀            ▀▀    ▀▀  ▀▀         ▀▀▀▀▀▀
#

# Standardowe biblioteki
import asyncio
from contextlib import (
    asynccontextmanager,
    suppress
)
from fastapi import FastAPI
import os

# Wewnętrzne importy
from src.api.endpoints.atom.accounts.router import router as routerKonta
from src.api.endpoints.atom.announcements.router import router as routerOgłoszeńDlaAtomu
from src.api.endpoints.atom.lists.router import router as routerListAtomu
from src.api.endpoints.atom.notifications.monitor import uruchomMonitorPowiadomień
from src.api.endpoints.atom.notifications.router import router as routerPowiadomień
from src.api.endpoints.atom.numbers.router import router as routerNumerkówDlaAtomu
from src.api.endpoints.atom.preferences.router import router as routerPreferencji
from src.api.endpoints.atom.substitutions.router import router as routerZastępstwAtomu
from src.api.endpoints.atom.timetables.router import router as routerPlanówLekcjiAtomu
from src.api.endpoints.universal.announcements.router import router as routerOgłoszeń
from src.api.endpoints.universal.lists.router import router as routerList
from src.api.endpoints.universal.numbers.router import router as routerNumerków
from src.api.endpoints.universal.substitutions.router import router as routerZastępstw
from src.api.endpoints.universal.timetables.router import router as routerPlanówLekcji
from src.api.handlers import zarejestrujObsługęWyjątków
from src.classes.apns import klientAPNs
from src.classes.atom import atom
from src.handlers.accounts.database import zainicjalizujBazęKont
from src.handlers.configuration import konfiguracja
from src.handlers.logging import logowanie
from src.handlers.notifications.database import zainicjalizujBazęPowiadomień
from src.handlers.numbers.database import zainicjalizujBazęNumerków

# Warunkowe importy zewnętrznych bibliotek
if os.getenv("DOCKER") != "true":
    from dotenv import load_dotenv

    load_dotenv()

@asynccontextmanager
async def lifespan(_: FastAPI):
    zadanieMonitoraPowiadomień: asyncio.Task | None = None
    try:
        await atom.start()
        await zainicjalizujBazęKont()
        await zainicjalizujBazęPowiadomień()
        await zainicjalizujBazęNumerków()

        zadanieMonitoraPowiadomień = asyncio.create_task(uruchomMonitorPowiadomień())
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
        if zadanieMonitoraPowiadomień is not None:
            zadanieMonitoraPowiadomień.cancel()
            with suppress(asyncio.CancelledError):
                await zadanieMonitoraPowiadomień

        await klientAPNs.zamknij()
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

app.include_router(routerKonta)
app.include_router(routerPowiadomień)
app.include_router(routerPreferencji)

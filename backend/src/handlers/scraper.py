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

# Standardowe biblioteki
import asyncio

# Zewnętrzne biblioteki
import aiohttp
from bs4 import BeautifulSoup

# Wewnętrzne importy
from src.handlers.logging import logowanie

async def pobierzZawartośćStrony(
    atom: aiohttp.ClientSession,
    url: str,
    kodowanie: str
) -> BeautifulSoup | None:
    """
    Pobiera zawartość strony internetowej.

    Args:
        atom (aiohttp.ClientSession): Aktywna sesja HTTP używana do wykonania zapytania.
        url (str): Adres strony internetowej przeznaczonej do pobrania.
        kodowanie (str): Kodowanie strony internetowej potrzebne do prawidłowego odczytu jej treści.

    Returns:
        BeautifulSoup | None: Obiekt BeautifulSoup reprezentujący stronę HTML.
    """

    try:
        async with atom.get(url) as odpowiedź:
            odpowiedź.raise_for_status()
            tekst = await odpowiedź.text(
                encoding=kodowanie,
                errors="ignore"
            )

            return BeautifulSoup(tekst, "html.parser")
    except asyncio.TimeoutError:
        logowanie.warning(
            f"Przekroczono czas oczekiwania na połączenie ({url})."
        )
    except aiohttp.ClientError as e:
        logowanie.exception(
            f"Wystąpił błąd klienta HTTP podczas pobierania strony. Więcej informacji: {e}"
        )
    except Exception as e:
        logowanie.exception(
            f"Wystąpił błąd podczas pobierania strony. Więcej informacji: {e}"
        )
    return None

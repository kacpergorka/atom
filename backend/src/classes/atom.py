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
import aiohttp

# Wewnętrzne importy
from src.handlers.configuration import konfiguracja
from src.handlers.logging import logowanie

class Atom:
    """
    Odpowiada za zarządzanie wspólnymi zasobami Atom API.
    """

    def __init__(self) -> None:
        """
        Inicjalizuje obiekt, ustawiając początkowy stan bez aktywnej sesji HTTP.
        """

        self.sesja: aiohttp.ClientSession | None = None

    async def start(self) -> None:
        """
        Tworzy i konfiguruje sesję HTTP wywoływaną przy uruchomieniu Atom API.
        """

        if self.sesja and not self.sesja.closed:
            return

        try:
            wersja = konfiguracja.get("wersja", "Brak danych")
            self.sesja = aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(limit=10, limit_per_host=5, ttl_dns_cache=300),
                timeout=aiohttp.ClientTimeout(total=10),
                headers={"User-Agent": f"Atom API/{wersja} (https://github.com/kacpergorka/atom)"}
            )
        except Exception as e:
            logowanie.critical(
                f"Nie udało się utworzyć sesji HTTP. Więcej informacji: {e}"
            )
            raise

    async def close(self) -> None:
        """
        Bezpiecznie zamyka aktywną sesję HTTP utworzoną przy uruchomieniu Atom API.
        """

        if self.sesja and not self.sesja.closed:
            try:
                await self.sesja.close()
            except Exception as e:
                logowanie.exception(
                    f"Wystąpił błąd podczas zamykania sesji HTTP. Więcej informacji: {e}"
                )
            finally:
                self.sesja = None

atom = Atom()

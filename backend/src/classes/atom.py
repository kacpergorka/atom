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
import os

# Zewnętrzne biblioteki
import aiohttp
from redis import asyncio
from redis.exceptions import RedisError

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
        self.redis: asyncio.Redis | None = None

    async def start(self) -> None:
        """
        Tworzy i konfiguruje sesję HTTP oraz Redis wywoływaną przy uruchomieniu Atom API.
        """

        if self.sesja and not self.sesja.closed:
            return

        try:
            wersja = konfiguracja.get("wersja", "Brak danych")
            self.sesja = aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(limit=10, limit_per_host=5, ttl_dns_cache=300),
                timeout=aiohttp.ClientTimeout(total=10),
                headers={
                    "X-Requested-With": "XMLHttpRequest",
                    "User-Agent": f"Atom API/{wersja} (https://github.com/kacpergorka/atom)"
                }
            )

            redisUrl = os.getenv("REDIS_URL", "redis://localhost:6379/0")
            self.redis = asyncio.Redis.from_url(
                redisUrl,
                decode_responses=True,
                health_check_interval=30
            )
            await self.redis.ping()
        except RedisError as e:
            logowanie.exception(
                f"Nie udało się połączyć z Redis pod adresem {redisUrl}. Cache jest wymagany do działania Atom API. Więcej informacji: {e}"
            )
            await self.close()
            raise RuntimeError(
                "Połączenie z Redis jest wymagane do uruchomienia Atom API."
            ) from e
        except Exception as e:
            logowanie.exception(
                f"Nie udało się utworzyć współdzielonych zasobów Atom API. Więcej informacji: {e}"
            )
            await self.close()
            raise

    async def close(self) -> None:
        """
        Bezpiecznie zamyka aktywną sesję HTTP utworzoną przy uruchomieniu Atom API.
        """

        if self.redis is not None:
            try:
                await self.redis.aclose()
            except Exception as e:
                logowanie.exception(
                    f"Wystąpił błąd podczas zamykania połączenia Redis. Więcej informacji: {e}"
                )
            finally:
                self.redis = None

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

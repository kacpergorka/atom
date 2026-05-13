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
from collections.abc import (
    Awaitable,
    Callable
)
import time

# Zewnętrzne biblioteki
from fastapi import (
    Depends,
    HTTPException,
    status
)
from redis.exceptions import RedisError

# Wewnętrzne importy
from src.classes.atom import atom
from src.handlers.accounts.auth import pobierzAktualnegoUżytkownika
from src.models.accounts import AktualnyUżytkownik

licznikiLimitów: dict[str, tuple[float, int]] = {}
blokadaPamięci = asyncio.Lock()

async def sprawdźLimit(
    klucz: str,
    maksimum: int,
    czasPrzedziału: int
) -> bool:
    """
    Sprawdza i aktualizuje limit żądań.

    Args:
        klucz (str): Klucz identyfikujący limit.
        maksimum (int): Maksymalna liczba żądań w przedziale czasu.
        czasPrzedziału (int): Długość przedziału czasu w sekundach.

    Returns:
        bool: True, jeśli limit nie został przekroczony.
    """

    if atom.redis is not None:
        try:
            liczba = await atom.redis.incr(klucz)
            if liczba == 1:
                await atom.redis.expire(klucz, czasPrzedziału)

            return liczba <= maksimum
        except RedisError:
            pass

    teraz = time.monotonic()

    async with blokadaPamięci:
        wygasa, liczba = licznikiLimitów.get(klucz, (teraz + czasPrzedziału, 0))

        if wygasa <= teraz:
            wygasa, liczba = teraz + czasPrzedziału, 0

        liczba += 1
        licznikiLimitów[klucz] = (wygasa, liczba)

        return liczba <= maksimum


def ograniczŻądania(
    obszar: str,
    maksimum: int,
    czasPrzedziału: int
) -> Callable[..., Awaitable[None]]:
    """
    Tworzy zależność FastAPI ograniczającą liczbę żądań użytkownika.

    Args:
        obszar (str): Nazwa obszaru API objętego limitem.
        maksimum (int): Maksymalna liczba żądań w przedziale czasu.
        czasPrzedziału (int): Długość przedziału czasu w sekundach.

    Returns:
        Callable: Zależność FastAPI sprawdzająca limit żądań.
    """

    async def zależność(użytkownik: AktualnyUżytkownik = Depends(pobierzAktualnegoUżytkownika)) -> None:
        """
        Sprawdza limit żądań dla aktualnie uwierzytelnionego użytkownika.

        Args:
            użytkownik (AktualnyUżytkownik): Użytkownik pobrany z JWT.
        """

        przedział = int(time.time() // czasPrzedziału)
        klucz = f"limit:{obszar}:{użytkownik.identyfikator}:{przedział}"

        if not await sprawdźLimit(klucz, maksimum, czasPrzedziału):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Zbyt wiele żądań.",
            )

    return zależność

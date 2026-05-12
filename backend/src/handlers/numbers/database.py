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
from asyncio import to_thread

# Wewnętrzne importy
from src.api.endpoints.universal.numbers.schemas import UniwersalneSzczesliweNumerki
from src.handlers.database import połączBazęDanych

async def zainicjalizujBazęNumerków() -> None:
    """
    Tworzy strukturę bazy danych szczęśliwych numerków.
    """

    def _zainicjalizujBazęNumerków() -> None:
        with połączBazęDanych() as połączenie:
            połączenie.executescript(
                """
                CREATE TABLE IF NOT EXISTS szczesliwe_numerki (
                    data TEXT PRIMARY KEY,
                    pierwszy_numerek INTEGER,
                    drugi_numerek INTEGER,
                    informacja TEXT
                );
                """
            )

    await to_thread(_zainicjalizujBazęNumerków)


async def pobierzSzczęśliweNumerki(data: str) -> UniwersalneSzczesliweNumerki | None:
    """
    Pobiera szczęśliwe numerki zapisane dla wybranej daty.

    Args:
        data (str): Data w formacie ISO.

    Returns:
        UniwersalneSzczesliweNumerki | None: Zapisane szczęśliwe numerki albo None.
    """

    def _pobierzSzczęśliweNumerki(data: str) -> UniwersalneSzczesliweNumerki | None:
        with połączBazęDanych() as połączenie:
            wiersz = połączenie.execute(
                """
                SELECT data, pierwszy_numerek, drugi_numerek, informacja
                FROM szczesliwe_numerki
                WHERE data = ?
                """,
                (data,),
            ).fetchone()

        if wiersz is None:
            return None

        numerki = None
        if wiersz["pierwszy_numerek"] is not None and wiersz["drugi_numerek"] is not None:
            numerki = (wiersz["pierwszy_numerek"], wiersz["drugi_numerek"])

        return UniwersalneSzczesliweNumerki(
            data=wiersz["data"],
            numerki=numerki,
            informacja=wiersz["informacja"],
        )

    return await to_thread(_pobierzSzczęśliweNumerki, data)


async def zapiszSzczęśliweNumerki(numerki: UniwersalneSzczesliweNumerki) -> None:
    """
    Zapisuje szczęśliwe numerki dla danego dnia do bazy danych.

    Args:
        numerki (UniwersalneSzczesliweNumerki): Szczęśliwe numerki do zapisania.
    """

    def _zapiszSzczęśliweNumerki(numerki: UniwersalneSzczesliweNumerki) -> None:
        pierwszyNumerek = numerki.numerki[0] if numerki.numerki else None
        drugiNumerek = numerki.numerki[1] if numerki.numerki else None

        with połączBazęDanych() as połączenie:
            połączenie.execute(
                """
                INSERT INTO szczesliwe_numerki(data, pierwszy_numerek, drugi_numerek, informacja)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(data) DO NOTHING
                """,
                (
                    numerki.data,
                    pierwszyNumerek,
                    drugiNumerek,
                    numerki.informacja,
                ),
            )

    await to_thread(_zapiszSzczęśliweNumerki, numerki)

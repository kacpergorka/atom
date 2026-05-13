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
from src.handlers.database import połączBazęDanych

async def zainicjalizujBazęKont() -> None:
    """
    Tworzy strukturę lokalnej bazy danych kont.
    """

    def _zainicjalizujBazęKont() -> None:
        """
        Tworzy strukturę lokalnej bazy danych kont w wątku roboczym.
        """

        with połączBazęDanych() as połączenie:
            połączenie.execute(
                """
                CREATE TABLE IF NOT EXISTS uzytkownicy_apple (
                    identyfikator_apple TEXT PRIMARY KEY,
                    identyfikator_uzytkownika TEXT,
                    nazwa TEXT NOT NULL
                )
                """
            )

    await to_thread(_zainicjalizujBazęKont)


async def zapiszProfilApple(
    identyfikatorUżytkownika: str,
    identyfikatorApple: str,
    nazwa: str
) -> None:
    """
    Zapisuje wymagany do prawidłowego działania aplikacji profil Apple.

    Args:
        identyfikatorUżytkownika (str): Identyfikator użytkownika z JWT.
        identyfikatorApple (str): Stabilny identyfikator Apple.
        nazwa (str): Nazwa użytkownika.
    """

    def _zapiszProfilApple(
        identyfikatorUżytkownika: str,
        identyfikatorApple: str,
        nazwa: str
    ) -> None:
        """
        Zapisuje wymagany do prawidłowego działania aplikacji profil Apple w wątku roboczym.
        """

        with połączBazęDanych() as połączenie:
            połączenie.execute(
                """
                INSERT INTO uzytkownicy_apple(identyfikator_apple, identyfikator_uzytkownika, nazwa)
                VALUES (?, ?, ?)
                ON CONFLICT(identyfikator_apple) DO UPDATE SET
                    identyfikator_uzytkownika = excluded.identyfikator_uzytkownika,
                    nazwa = excluded.nazwa
                """,
                (identyfikatorApple, identyfikatorUżytkownika, nazwa),
            )

    await to_thread(_zapiszProfilApple, identyfikatorUżytkownika, identyfikatorApple, nazwa)


async def pobierzNazwęProfiluApple(identyfikatorApple: str) -> str | None:
    """
    Pobiera nazwę profilu Apple.

    Args:
        identyfikatorApple (str): Stabilny identyfikator Apple.

    Returns:
        str | None: Nazwa albo None.
    """

    def _pobierzNazwęProfiluApple(identyfikatorApple: str) -> str | None:
        """
        Pobiera nazwę profilu Apple w wątku roboczym.
        """

        with połączBazęDanych() as połączenie:
            wiersz = połączenie.execute(
                "SELECT nazwa FROM uzytkownicy_apple WHERE identyfikator_apple = ?",
                (identyfikatorApple,),
            ).fetchone()

        return wiersz["nazwa"] if wiersz else None

    return await to_thread(_pobierzNazwęProfiluApple, identyfikatorApple)


async def odłączUżytkownikaOdProfiluApple(identyfikatorUżytkownika: str) -> None:
    """
    Odłącza lokalnego użytkownika od zachowanego profilu Apple.

    Args:
        identyfikatorUżytkownika (str): Identyfikator użytkownika z JWT.
    """

    def _odłączUżytkownikaOdProfiluApple(identyfikatorUżytkownika: str) -> None:
        """
        Odłącza lokalnego użytkownika od zachowanego profilu Apple w wątku roboczym.
        """

        with połączBazęDanych() as połączenie:
            połączenie.execute(
                """
                UPDATE uzytkownicy_apple
                SET identyfikator_uzytkownika = NULL
                WHERE identyfikator_uzytkownika = ?
                """,
                (identyfikatorUżytkownika,),
            )

    await to_thread(_odłączUżytkownikaOdProfiluApple, identyfikatorUżytkownika)

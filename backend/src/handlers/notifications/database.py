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
import sqlite3
from asyncio import to_thread

# Wewnętrzne importy
from src.handlers.database import połączBazęDanych
from src.types.notifications import PreferencjePowiadomień

kolumnyPreferencji = """
    identyfikator_uzytkownika,
    oddzial,
    identyfikator_oddzialu,
    nauczyciel,
    identyfikator_nauczyciela,
    grupa_zajec_lekcyjnych,
    grupa_zajec_praktycznych,
    grupa_wychowania_fizycznego,
    religia,
    edukacja_zdrowotna,
    numerek_ucznia
"""

def zbudujPreferencje(wiersz: sqlite3.Row) -> PreferencjePowiadomień:
    """
    Buduje model preferencji z wiersza SQLite.

    Args:
        wiersz (sqlite3.Row): Wiersz tabeli preferencji.

    Returns:
        PreferencjePowiadomień: Preferencje użytkownika.
    """

    return PreferencjePowiadomień(
        identyfikatorUżytkownika=wiersz["identyfikator_uzytkownika"],
        oddział=wiersz["oddzial"],
        identyfikatorOddziału=wiersz["identyfikator_oddzialu"],
        nauczyciel=wiersz["nauczyciel"],
        identyfikatorNauczyciela=wiersz["identyfikator_nauczyciela"],
        grupaZajęćLekcyjnych=wiersz["grupa_zajec_lekcyjnych"],
        grupaZajęćPraktycznych=wiersz["grupa_zajec_praktycznych"],
        grupaWychowaniaFizycznego=wiersz["grupa_wychowania_fizycznego"],
        religia=bool(wiersz["religia"]),
        edukacjaZdrowotna=bool(wiersz["edukacja_zdrowotna"]),
        numerekUcznia=wiersz["numerek_ucznia"],
    )


async def zainicjalizujBazęPowiadomień() -> None:
    """
    Tworzy strukturę bazy powiadomień.
    """

    def _zainicjalizujBazęPowiadomień() -> None:
        """
        Tworzy strukturę bazy danych powiadomień w wątku roboczym.
        """

        with połączBazęDanych() as połączenie:
            połączenie.executescript(
                """
                CREATE TABLE IF NOT EXISTS urzadzenia_powiadomien (
                    identyfikator_uzytkownika TEXT NOT NULL,
                    token_urzadzenia TEXT PRIMARY KEY
                );

                CREATE INDEX IF NOT EXISTS urzadzenia_powiadomien_identyfikator_uzytkownika_index
                    ON urzadzenia_powiadomien(identyfikator_uzytkownika);

                CREATE TABLE IF NOT EXISTS preferencje_powiadomien (
                    identyfikator_uzytkownika TEXT PRIMARY KEY,
                    oddzial TEXT,
                    identyfikator_oddzialu TEXT,
                    nauczyciel TEXT,
                    identyfikator_nauczyciela TEXT,
                    grupa_zajec_lekcyjnych TEXT,
                    grupa_zajec_praktycznych TEXT,
                    grupa_wychowania_fizycznego TEXT,
                    religia INTEGER NOT NULL DEFAULT 1,
                    edukacja_zdrowotna INTEGER NOT NULL DEFAULT 1,
                    numerek_ucznia INTEGER
                );

                CREATE INDEX IF NOT EXISTS preferencje_powiadomien_identyfikator_oddzialu_index
                    ON preferencje_powiadomien(identyfikator_oddzialu);

                CREATE INDEX IF NOT EXISTS preferencje_powiadomien_numerek_ucznia_index
                    ON preferencje_powiadomien(numerek_ucznia);

                CREATE TABLE IF NOT EXISTS monitor_powiadomien (
                    klucz TEXT PRIMARY KEY,
                    odcisk TEXT NOT NULL
                );
                """
            )

    await to_thread(_zainicjalizujBazęPowiadomień)


async def zapiszUrządzenie(
    identyfikatorUżytkownika: str,
    tokenUrządzenia: str
) -> None:
    """
    Zapisuje albo aktualizuje urządzenie końcowe dla powiadomień.

    Args:
        identyfikatorUżytkownika (str): Identyfikator użytkownika z JWT.
        tokenUrządzenia (str): Token APNs urządzenia.
    """

    def _zapiszUrządzenie(
        identyfikatorUżytkownika: str,
        tokenUrządzenia: str
    ) -> None:
        """
        Zapisuje albo aktualizuje urządzenie końcowe dla powiadomień w wątku roboczym.
        """

        with połączBazęDanych() as połączenie:
            połączenie.execute(
                """
                INSERT INTO urzadzenia_powiadomien(identyfikator_uzytkownika, token_urzadzenia)
                VALUES (?, ?)
                ON CONFLICT(token_urzadzenia) DO UPDATE SET
                    identyfikator_uzytkownika = excluded.identyfikator_uzytkownika
                """,
                (identyfikatorUżytkownika, tokenUrządzenia),
            )

    await to_thread(_zapiszUrządzenie, identyfikatorUżytkownika, tokenUrządzenia)


async def usuńUrządzenieUżytkownika(
    identyfikatorUżytkownika: str,
    tokenUrządzenia: str
) -> None:
    """
    Usuwa urządzenie przypisane do użytkownika.

    Args:
        identyfikatorUżytkownika (str): Identyfikator użytkownika z JWT.
        tokenUrządzenia (str): Token APNs urządzenia.
    """

    def _usuńUrządzenieUżytkownika(
        identyfikatorUżytkownika: str,
        tokenUrządzenia: str
    ) -> None:
        """
        Usuwa urządzenie przypisane do użytkownika w wątku roboczym.
        """

        with połączBazęDanych() as połączenie:
            połączenie.execute(
                "DELETE FROM urzadzenia_powiadomien WHERE identyfikator_uzytkownika = ? AND token_urzadzenia = ?",
                (identyfikatorUżytkownika, tokenUrządzenia),
            )

    await to_thread(_usuńUrządzenieUżytkownika, identyfikatorUżytkownika, tokenUrządzenia)


async def usuńToken(tokenUrządzenia: str) -> None:
    """
    Usuwa token urządzenia z bazy danych.

    Args:
        tokenUrządzenia (str): Token APNs urządzenia.
    """

    def _usuńToken(tokenUrządzenia: str) -> None:
        """
        Usuwa token urządzenia z bazy danych w wątku roboczym.
        """

        with połączBazęDanych() as połączenie:
            połączenie.execute("DELETE FROM urzadzenia_powiadomien WHERE token_urzadzenia = ?", (tokenUrządzenia,))

    await to_thread(_usuńToken, tokenUrządzenia)


async def pobierzTokenyUżytkownika(identyfikatorUżytkownika: str) -> list[str]:
    """
    Pobiera tokeny urządzeń użytkownika.

    Args:
        identyfikatorUżytkownika (str): Identyfikator użytkownika z JWT.

    Returns:
        list[str]: Tokeny urządzeń użytkownika.
    """

    def _pobierzTokenyUżytkownika(identyfikatorUżytkownika: str) -> list[str]:
        """
        Pobiera tokeny urządzeń użytkownika w wątku roboczym.
        """

        with połączBazęDanych() as połączenie:
            wiersze = połączenie.execute(
                """
                SELECT token_urzadzenia
                FROM urzadzenia_powiadomien
                WHERE identyfikator_uzytkownika = ?
                """,
                (identyfikatorUżytkownika,),
            ).fetchall()

        return [wiersz["token_urzadzenia"] for wiersz in wiersze]

    return await to_thread(_pobierzTokenyUżytkownika, identyfikatorUżytkownika)


async def zapiszPreferencje(preferencje: PreferencjePowiadomień) -> None:
    """
    Zapisuje preferencje użytkownika.

    Args:
        preferencje (PreferencjePowiadomień): Preferencje do zapisania.
    """

    def _zapiszPreferencje(preferencje: PreferencjePowiadomień) -> None:
        """
        Zapisuje preferencje użytkownika w wątku roboczym.
        """

        with połączBazęDanych() as połączenie:
            połączenie.execute(
                f"""
                INSERT INTO preferencje_powiadomien({kolumnyPreferencji})
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(identyfikator_uzytkownika) DO UPDATE SET
                    oddzial = excluded.oddzial,
                    identyfikator_oddzialu = excluded.identyfikator_oddzialu,
                    nauczyciel = excluded.nauczyciel,
                    identyfikator_nauczyciela = excluded.identyfikator_nauczyciela,
                    grupa_zajec_lekcyjnych = excluded.grupa_zajec_lekcyjnych,
                    grupa_zajec_praktycznych = excluded.grupa_zajec_praktycznych,
                    grupa_wychowania_fizycznego = excluded.grupa_wychowania_fizycznego,
                    religia = excluded.religia,
                    edukacja_zdrowotna = excluded.edukacja_zdrowotna,
                    numerek_ucznia = excluded.numerek_ucznia
                """,
                (
                    preferencje.identyfikatorUżytkownika,
                    preferencje.oddział,
                    preferencje.identyfikatorOddziału,
                    preferencje.nauczyciel,
                    preferencje.identyfikatorNauczyciela,
                    preferencje.grupaZajęćLekcyjnych,
                    preferencje.grupaZajęćPraktycznych,
                    preferencje.grupaWychowaniaFizycznego,
                    int(preferencje.religia),
                    int(preferencje.edukacjaZdrowotna),
                    preferencje.numerekUcznia,
                ),
            )

    await to_thread(_zapiszPreferencje, preferencje)


async def pobierzPreferencje() -> list[PreferencjePowiadomień]:
    """
    Pobiera preferencje używane przez monitor powiadomień.

    Returns:
        list[PreferencjePowiadomień]: Preferencje z włączonym monitorowaniem.
    """

    def _pobierzPreferencje() -> list[PreferencjePowiadomień]:
        """
        Pobiera preferencje używane przez monitor powiadomień w wątku roboczym.
        """

        with połączBazęDanych() as połączenie:
            wiersze = połączenie.execute(
                f"""
                SELECT {kolumnyPreferencji}
                FROM preferencje_powiadomien
                WHERE identyfikator_oddzialu IS NOT NULL OR numerek_ucznia IS NOT NULL
                """
            ).fetchall()

        return [zbudujPreferencje(wiersz) for wiersz in wiersze]

    return await to_thread(_pobierzPreferencje)


async def pobierzPreferencjeUżytkownika(identyfikatorUżytkownika: str) -> PreferencjePowiadomień | None:
    """
    Pobiera preferencje użytkownika.

    Args:
        identyfikatorUżytkownika (str): Identyfikator użytkownika z JWT.

    Returns:
        PreferencjePowiadomień | None: Preferencje albo None.
    """

    def _pobierzPreferencjeUżytkownika(identyfikatorUżytkownika: str) -> PreferencjePowiadomień | None:
        """
        Pobiera preferencje użytkownika w wątku roboczym.
        """

        with połączBazęDanych() as połączenie:
            wiersz = połączenie.execute(
                f"""
                SELECT {kolumnyPreferencji}
                FROM preferencje_powiadomien
                WHERE identyfikator_uzytkownika = ?
                """,
                (identyfikatorUżytkownika,),
            ).fetchone()

        return zbudujPreferencje(wiersz) if wiersz else None

    return await to_thread(_pobierzPreferencjeUżytkownika, identyfikatorUżytkownika)


async def usuńDaneUżytkownika(identyfikatorUżytkownika: str) -> None:
    """
    Usuwa lokalne dane powiadomień użytkownika.

    Args:
        identyfikatorUżytkownika (str): Identyfikator użytkownika z JWT.
    """

    def _usuńDaneUżytkownika(identyfikatorUżytkownika: str) -> None:
        """
        Usuwa lokalne dane powiadomień użytkownika w wątku roboczym.
        """

        with połączBazęDanych() as połączenie:
            połączenie.execute(
                "DELETE FROM urzadzenia_powiadomien WHERE identyfikator_uzytkownika = ?",
                (identyfikatorUżytkownika,),
            )
            połączenie.execute(
                "DELETE FROM preferencje_powiadomien WHERE identyfikator_uzytkownika = ?",
                (identyfikatorUżytkownika,),
            )

    await to_thread(_usuńDaneUżytkownika, identyfikatorUżytkownika)


async def pobierzStanMonitora(klucz: str) -> str | None:
    """
    Pobiera ostatni odcisk danych monitora.

    Args:
        klucz (str): Klucz monitorowanego zestawu danych.

    Returns:
        str | None: Ostatni odcisk albo None.
    """

    def _pobierzStanMonitora(klucz: str) -> str | None:
        """
        Pobiera ostatni odcisk danych monitora w wątku roboczym.
        """

        with połączBazęDanych() as połączenie:
            wiersz = połączenie.execute(
                "SELECT odcisk FROM monitor_powiadomien WHERE klucz = ?",
                (klucz,),
            ).fetchone()

        return wiersz["odcisk"] if wiersz else None

    return await to_thread(_pobierzStanMonitora, klucz)


async def zapiszStanMonitora(
    klucz: str,
    odcisk: str
) -> None:
    """
    Zapisuje ostatni odcisk danych monitora.

    Args:
        klucz (str): Klucz monitorowanego zestawu danych.
        odcisk (str): Odcisk danych.
    """

    def _zapiszStanMonitora(
        klucz: str,
        odcisk: str
    ) -> None:
        """
        Zapisuje ostatni odcisk danych monitora w wątku roboczym.
        """

        with połączBazęDanych() as połączenie:
            połączenie.execute(
                """
                INSERT INTO monitor_powiadomien(klucz, odcisk)
                VALUES (?, ?)
                ON CONFLICT(klucz) DO UPDATE SET
                    odcisk = excluded.odcisk
                """,
                (klucz, odcisk),
            )

    await to_thread(_zapiszStanMonitora, klucz, odcisk)

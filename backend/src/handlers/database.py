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
from pathlib import Path

katalogDanych = Path(__file__).resolve().parents[2] / "data"
ścieżkaBazy = katalogDanych / "data.sqlite3"

def połączBazęDanych() -> sqlite3.Connection:
    """
    Otwiera połączenie SQLite dla lokalnej bazy danych aplikacji.

    Returns:
        sqlite3.Connection: Połączenie SQLite z ustawieniami bazy danych.
    """

    katalogDanych.mkdir(parents=True, exist_ok=True)
    połączenie = sqlite3.connect(ścieżkaBazy, timeout=30, isolation_level=None)
    połączenie.execute("PRAGMA foreign_keys = ON")
    połączenie.execute("PRAGMA busy_timeout = 30000")
    połączenie.row_factory = sqlite3.Row
    return połączenie

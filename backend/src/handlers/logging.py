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
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

# Wewnętrzne importy
from src.classes.timezone import Timezone

def skonfigurujLogi() -> logging.Logger:
    """
    Konfiguruje globalne logowanie wydarzeń.

    Returns:
        logging.Logger: Logger wydarzeń.
    """

    katalog = Path(__file__).resolve().parents[2] / "logs"
    katalog.mkdir(parents=True, exist_ok=True)

    logowanie = logging.getLogger("Atom API")
    logowanie.setLevel(logging.INFO)

    ścieżka = katalog / "console.log"

    if not logowanie.handlers:
        obsługaLogów = RotatingFileHandler(
            filename=ścieżka,
            encoding="utf-8",
            maxBytes=32 * 1024 * 1024,
            backupCount=31
        )

        formatter = Timezone("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        obsługaLogów.setFormatter(formatter)
        logowanie.addHandler(obsługaLogów)

    logowanie.propagate = False

    return logowanie

logowanie = skonfigurujLogi()

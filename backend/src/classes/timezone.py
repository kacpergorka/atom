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
from datetime import datetime
import logging
from zoneinfo import ZoneInfo

class Timezone(logging.Formatter):
    """
    Formatter dla logów wykorzystujący strefę czasową Europe/Warsaw.
    """

    def formatTime(
        self,
        record: logging.LogRecord,
        datefmt: str | None = None
    ) -> str:
        """
        Formatuje czas rekordu logowania w strefie Europe/Warsaw.

        Args:
            record (logging.LogRecord): Rekord logowania.
            datefmt (str | None): Opcjonalny format daty.

        Returns:
            str: Sformatowany czas rekordu logowania.
        """

        daneCzasu = datetime.fromtimestamp(record.created, ZoneInfo("Europe/Warsaw"))
        if datefmt:
            return daneCzasu.strftime(datefmt)

        return daneCzasu.strftime("%Y-%m-%d %H:%M:%S")

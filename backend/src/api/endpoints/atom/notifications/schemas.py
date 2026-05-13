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
import re

# Zewnętrzne biblioteki
from pydantic import (
    BaseModel,
    field_validator
)

class TokenPowiadomien(BaseModel):
    """
    Model tokenu urządzenia używanego przez powiadomienia APNs aplikacji Atom.
    """

    tokenUrzadzenia: str

    @field_validator("tokenUrzadzenia")
    @classmethod
    def walidujTokenUrzadzenia(cls, wartość: str) -> str:
        """
        Normalizuje i waliduje token urządzenia APNs.

        Args:
            wartość (str): Token urządzenia przekazany w polu modelu.

        Returns:
            str: Znormalizowany token urządzenia.
        """

        token = wartość.strip()

        if not re.fullmatch(r"[0-9a-fA-F]{64,200}", token):
            raise ValueError("Nieprawidłowy token urządzenia APNs.")

        return token.lower()

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
    ConfigDict,
    Field,
    field_validator
)

class TokenPowiadomien(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    tokenUrządzenia: str = Field(alias="tokenUrzadzenia")

    @field_validator("tokenUrządzenia")
    @classmethod
    def walidujTokenUrządzenia(cls, wartość: str) -> str:
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

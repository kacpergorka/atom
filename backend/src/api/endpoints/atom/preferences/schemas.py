#
#     ▄▄     ▄▄▄▄▄▄▄▄    ▄▄▄▄    ▄▄▄  ▄▄▄               ▄▄     ▄▄▄▄▄▄     ▄▄▄▄▄▄
#    ████    ▀▀▀██▀▀▀   ██▀▀██   ███  ███              ████    ██▀▀▀▀█▄   ▀▀██▀▀
#    ████       ██     ██    ██  ████████              ████    ██    ██     ██
#   ██  ██      ██     ██    ██  ██ ██ ██             ██  ██   ██████▀      ██
#   ██████      ██     ██    ██  ██ ▀▀ ██             ██████   ██           ██
#  ▄██  ██▄     ██      ██▄▄██   ██    ██            ▄██  ██▄  ██         ▄▄██▄▄
#  ▀▀    ▀▀     ▀▀       ▀▀▀▀    ▀▀    ▀▀            ▀▀    ▀▀  ▀▀         ▀▀▀▀▀▀
#

# Zewnętrzne biblioteki
from pydantic import BaseModel

class Preferencje(BaseModel):
    """
    Model preferencji użytkownika używanych przez powiadomienia aplikacji Atom.
    """

    oddzial: str | None = None
    identyfikatorOddzialu: str | None = None
    nauczyciel: str | None = None
    identyfikatorNauczyciela: str | None = None
    grupaZajecLekcyjnych: str | None = None
    grupaZajecPraktycznych: str | None = None
    grupaWychowaniaFizycznego: str | None = None
    religia: bool = True
    edukacjaZdrowotna: bool = True
    numerekUcznia: int | None = None

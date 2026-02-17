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
from urllib.parse import urlparse

# Wewnętrzne importy
from src.classes.types import EncjaPlanu

def wydobądźIdentyfikator(url: str | None) -> str | None:
    """
    Wyodrębnia identyfikator planu lekcji z adresu strony internetowej.

    Args:
        url (str | None): Adres strony internetowej planu lekcji.

    Returns:
        str | None: Identyfikator planu lekcji.
    """

    if not isinstance(url, str) or not url:
        return None

    ścieżka = urlparse(url).path
    if ścieżka:
        plik = ścieżka.rsplit("/", 1)[-1]
        if "." in plik:
            return plik.split(".", 1)[0]

    return None


def zwróćPustySłownik() -> EncjaPlanu:
    """
    Zwraca pusty słownik danych wykorzystywany jako reprezentacja encji.

    Returns:
        EncjaPlanu: Pusty słownik danych.
    """

    return {
        "tekst": None,
        "url": None,
        "identyfikator": None
    }

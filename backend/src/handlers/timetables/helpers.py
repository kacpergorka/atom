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
from src.classes.types import ElementPlanu

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


def zwróćPustySłownik() -> ElementPlanu:
    """
    Zwraca pusty słownik danych wykorzystywany jako reprezentacja elementu.

    Returns:
        ElementPlanu: Pusty słownik danych.
    """

    return {
        "tekst": None,
        "url": None,
        "identyfikator": None
    }

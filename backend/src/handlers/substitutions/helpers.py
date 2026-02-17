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
import re
import unicodedata

def normalizujTekst(tekst: str | None) -> str:
    """
    Normalizuje tekst w celu ujednolicenia go do porównań i filtracji.

    Args:
        tekst (str | None): Tekst wejściowy do normalizacji.

    Returns:
        str: Oczyszczony i znormalizowany tekst.
    """

    if not isinstance(tekst, str):
        return ""

    tekst = tekst.strip()
    if not tekst:
        return ""

    tekst = unicodedata.normalize("NFKD", tekst)
    tekst = "".join(znak for znak in tekst if not unicodedata.combining(znak))
    tekst = tekst.replace(".", " ")
    tekst = re.sub(r"\s+", " ", tekst)

    return tekst.lower()


def zwróćNazwyKluczy(nazwa: str) -> set[str]:
    """
    Tworzy zestaw kluczy dopasowań dla podanej nazwy.

    Args:
        nazwa (str): Tekst nazwy do przetworzenia.

    Returns:
        set[str]: Zestaw ciągów znaków używanych jako klucze dopasowań.
    """

    norma = normalizujTekst(nazwa)

    if not norma:
        return set()

    części = norma.split()
    klucze = {norma}

    if len(części) >= 2:
        klucze.add(f"{części[0][0]} {części[-1]}")
        klucze.add(f"{części[0][0]}{części[-1]}")

    return klucze

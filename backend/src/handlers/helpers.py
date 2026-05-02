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
from collections.abc import Mapping
import re
from typing import Any

# Zewnętrzne biblioteki
from bs4 import (
    BeautifulSoup,
    NavigableString,
    Tag
)

# Wewnętrzne importy
from src.handlers.configuration import konfiguracja

def posortujNauczycieli(element: Mapping[str, Any] | str | None) -> str:
    """
    Zwraca klucz sortowania dla nauczyciela na podstawie jego nazwiska.

    Args:
        element (Mapping[str, Any] | str | None): Słownik reprezentujący nauczyciela lub bezpośrednia nazwa nauczyciela.

    Returns:
        str: Przekształcony ciąg znaków używany jako klucz sortowania.
    """

    def wyodrębnijNazwiskoNauczyciela(tekst: str) -> str:
        """
        Wyodrębnia nazwisko nauczyciela z przekazanego tekstu.

        Args:
            tekst (str): Tekst zawierający imię i nazwisko nauczyciela lub inne oznaczenia.

        Returns:
            str: Nazwisko nauczyciela lub przetworzony fragment tekstu w przypadku niestandardowego formatu.
        """

        tekst = re.sub(r"\s+", " ", tekst).strip()
        tekst = tekst.split("(", 1)[0].strip()
        części = tekst.split()

        for część in części:
            if część.lower() == "vacat":
                return część

        if "." in tekst:
            return tekst.split(".", 1)[1].strip()

        if len(części) >= 2:
            return części[-1]

        return tekst

    tekst = ""

    if isinstance(element, Mapping):
        for klucz in ("nauczyciel", "nazwa", "rozwiniecie"):
            wartość = element.get(klucz)

            if isinstance(wartość, str) and wartość.strip():
                tekst = wartość
                break

    elif isinstance(element, str):
        tekst = element

    return wyodrębnijNazwiskoNauczyciela(tekst).lower()


def sprawdźGrupę(
    grupa: str | None,
    grupy: list[str] | None
) -> bool:
    """
    Sprawdza, czy dana grupa lekcyjna powinna zostać uwzględniona.

    Args:
        grupa (str | None): Grupa przypisana do lekcji (np. "j1", "2/3").
        grupy (list[str] | None): Lista oznaczeń określających grupę przedmiotów.

    Returns:
        bool: True jeśli grupa jest powinna zostać uwzględniona, False w przeciwnym wypadku.
    """

    if not grupy or not grupa:
        return True

    dostępneGrupy = set(konfiguracja.get("grupy", []))
    obsługiwaneGrupy = [grupa for grupa in grupy if grupa in dostępneGrupy]

    if not obsługiwaneGrupy:
        return True

    if "/" in grupa:
        mianownik = grupa.split("/")[1]
        wybraneGrupy = [
            grupa for grupa in obsługiwaneGrupy
            if "/" in grupa and grupa.split("/")[1] == mianownik
        ]
    else:
        wybraneGrupy = [
            grupa for grupa in obsługiwaneGrupy
            if "/" not in grupa and grupa.startswith("j")
        ]

    return not wybraneGrupy or grupa in wybraneGrupy


def wyczyśćTekst(
    węzeł: Tag | str | None,
    separator: str = " ",
    rozpakujTagi: bool = False,
    usuńSuroweNoweLinie: bool = False
) -> str:
    """
    Czyści i normalizuje tekst.

    Args:
        węzeł (Tag | str | None): Element strony internetowej do przetworzenia.
        separator (str): Separator używany przy pobieraniu tekstu.
        rozpakujTagi (bool): Flaga informująca, czy rozpakować znaczniki po zamianie `<br>` na nowe linie.
        usuńSuroweNoweLinie (bool): Flaga informująca, czy usunąć surowe nowe linie z węzłów tekstowych przed ekstrakcją.

    Returns:
        str: Oczyszczony i znormalizowany tekst.
    """

    if not węzeł:
        return ""

    tymczasowy = BeautifulSoup(str(węzeł), "html.parser")

    if usuńSuroweNoweLinie:
        for element in tymczasowy.find_all(string=True):
            if isinstance(element, NavigableString):
                element.replace_with(
                    element.replace("\n", "").replace("\r", "")
                )

    for br in tymczasowy.find_all("br"):
        br.replace_with(NavigableString("\n"))

    if rozpakujTagi:
        for tag in tymczasowy.find_all(True):
            tag.unwrap()

    tekst = tymczasowy.get_text(separator=separator)
    tekst = tekst.replace("\r\n", "\n").replace("\r", "\n")
    tekst = tekst.replace("\xa0", " ")
    tekst = re.sub(r"[ \t]*\n[ \t]*", "\n", tekst)
    tekst = re.sub(r"[ \t]{2,}", " ", tekst)
    tekst = re.sub(r"\n{3,}", "\n\n", tekst)

    return tekst.strip("\n ")

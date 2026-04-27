#
#     ▄▄     ▄▄▄▄▄▄▄▄    ▄▄▄▄    ▄▄▄  ▄▄▄               ▄▄     ▄▄▄▄▄▄     ▄▄▄▄▄▄
#    ████    ▀▀▀██▀▀▀   ██▀▀██   ███  ███              ████    ██▀▀▀▀█▄   ▀▀██▀▀
#    ████       ██     ██    ██  ████████              ████    ██    ██     ██
#   ██  ██      ██     ██    ██  ██ ██ ██             ██  ██   ██████▀      ██
#   ██████      ██     ██    ██  ██ ▀▀ ██             ██████   ██           ██
#  ▄██  ██▄     ██      ██▄▄██   ██    ██            ▄██  ██▄  ██         ▄▄██▄▄
#  ▀▀    ▀▀     ▀▀       ▀▀▀▀    ▀▀    ▀▀            ▀▀    ▀▀  ▀▀         ▀▀▀▀▀▀
#

# Wewnętrzne importy
from src.api.endpoints.universal.lists.schemas import UniwersalnyElementListy
from src.api.exceptions import NieprawidłowyIdentyfikator

def normalizujIdentyfikator(identyfikator: str | None) -> str:
    """
    Normalizuje identyfikator wykorzystywany przez endpointy API.

    Args:
        identyfikator (str | None): Identyfikator oddziału, nauczyciela lub sali.

    Returns:
        str: Oczyszczony i znormalizowany identyfikator.

    Raises:
        NieprawidłowyIdentyfikator: Gdy identyfikator jest pusty lub ma nieprawidłową długość.
    """

    if not isinstance(identyfikator, str):
        raise NieprawidłowyIdentyfikator

    znormalizowany = identyfikator.strip().lower()

    if len(znormalizowany) < 2:
        raise NieprawidłowyIdentyfikator

    return znormalizowany


def zbudujPrzedmiotyDodatkowe(
    religia: bool,
    edukacjaZdrowotna: bool
) -> dict[str, bool]:
    """
    Buduje słownik przedmiotów dodatkowych na podstawie przekazanych flag.

    Args:
        religia (bool): Flaga informująca, czy uwzględniać lekcje religii w planie lekcji.
        edukacjaZdrowotna (bool): Flaga informująca, czy uwzględniać lekcje edukacji zdrowotnej w planie lekcji.

    Returns:
        dict[str, bool]: Słownik z kluczami nazw przedmiotów i wartościami logicznymi.
    """

    return {
        "religia": religia,
        "zdrowotna": edukacjaZdrowotna
    }


def wyszukajElement(
    identyfikator: str,
    listaOddziałów: list[UniwersalnyElementListy],
    listaNauczycieli: list[UniwersalnyElementListy]
) -> tuple[str | None, str | None]:
    """
    Wyszukuje element odpowiadający identyfikatorowi i zwraca nazwę oddziału lub nauczyciela.

    Args:
        identyfikator (str): Identyfikator oddziału lub nauczyciela, np. o17, n78.
        listaOddziałów (list[UniwersalnyElementListy]): Lista wszystkich oddziałów.
        listaNauczycieli (list[UniwersalnyElementListy]): Lista wszystkich nauczycieli.

    Returns:
        tuple[str | None, str | None]: (wybranyOddział, wybranyNauczyciel)
    """

    identyfikator = normalizujIdentyfikator(identyfikator)
    prefiks = identyfikator[0].lower()

    if prefiks == "o":
        dane = listaOddziałów
    elif prefiks == "n":
        dane = listaNauczycieli
    else:
        raise NieprawidłowyIdentyfikator

    for element in dane:
        if element.get("identyfikator") == identyfikator:
            nazwa = element.get("nazwa")

            if prefiks == "o":
                return nazwa, None

            return None, nazwa

    raise NieprawidłowyIdentyfikator


def sprawdźIstnienieElementu(
    identyfikator: str,
    listaOddziałów: list[UniwersalnyElementListy],
    listaNauczycieli: list[UniwersalnyElementListy],
    listaSal: list[UniwersalnyElementListy]
) -> None:
    """
    Sprawdza, czy identyfikator wskazuje istniejący element list planu lekcji.

    Args:
        identyfikator (str): Identyfikator oddziału, nauczyciela lub sali.
        listaOddziałów (list[UniwersalnyElementListy]): Lista wszystkich oddziałów.
        listaNauczycieli (list[UniwersalnyElementListy]): Lista wszystkich nauczycieli.
        listaSal (list[UniwersalnyElementListy]): Lista wszystkich sal.

    Raises:
        NieprawidłowyIdentyfikator: Gdy prefiks jest nieobsługiwany lub element nie istnieje.
    """

    identyfikator = normalizujIdentyfikator(identyfikator)
    prefiks = identyfikator[0]

    if prefiks == "o":
        dane = listaOddziałów
    elif prefiks == "n":
        dane = listaNauczycieli
    elif prefiks == "s":
        dane = listaSal
    else:
        raise NieprawidłowyIdentyfikator

    for element in dane:
        if element.get("identyfikator") == identyfikator:
            return

    raise NieprawidłowyIdentyfikator

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
from collections import defaultdict

# Wewnętrzne importy
from src.classes.types.substitutions import Zastępstwa
from src.classes.types.timetables import PlanLekcji
from src.handlers.configuration import konfiguracja
from src.handlers.logging import logowanie

def zbudujPlanLekcji(
    planLekcji: PlanLekcji,
    zastępstwa: Zastępstwa
) -> PlanLekcji:
    """
    Buduje plan lekcji z wpisami zastępstw, które dotyczą już tego samego planu lekcji.

    Args:
        planLekcji (PlanLekcji): Plan lekcji przygotowany przez parser Atom API.
        zastępstwa (Zastępstwa): Zastępstwa przygotowane przez parser Atom API.

    Returns:
        PlanLekcji: Zbudowany i uzupełniony plan lekcji.
    """

    def zbudujDaneZastępstwa(wpisZastępstwa: dict) -> dict | None:
        """
        Buduje strukturę danych zastępstwa przypisywaną do pola `zastepstwo` w strukturze lekcji.

        Args:
            wpisZastępstwa (dict): Wpis zastępstwa zwrócony przez parser zastępstw.

        Returns:
            dict | None: Ustrukturyzowane dane zastępstwa lub `None`, jeżeli wpis zastępstwa nie zawiera żadnych danych.
        """

        nauczyciel = wpisZastępstwa.get("zastepca")
        opis = wpisZastępstwa.get("opis")
        uwagi = wpisZastępstwa.get("uwagi")

        if nauczyciel is None and opis is None and uwagi is None:
            return None

        return {
            "nauczyciel": nauczyciel,
            "opis": opis,
            "uwagi": uwagi
        }

    def usuńPusteWpisy(planTygodniowy: dict[str, list[dict]]) -> None:
        """
        Usuwa z planu wpisy godzin, które nie zawierają żadnych lekcji.

        Args:
            planTygodniowy (dict[str, list[dict]]): Plan tygodniowy.
        """

        for kluczDnia, wpisyDnia in planTygodniowy.items():
            planTygodniowy[kluczDnia] = [
                wpis for wpis in wpisyDnia
                if isinstance(wpis.get("lekcje"), list) and wpis.get("lekcje")
            ]

    def przypiszWpisyDoLekcji(
        lekcje: list[dict],
        wpisyZastępstw: list[dict]
    ) -> None:
        """
        Przypisuje zastępstwa do lekcji z tej samej godziny.

        Args:
            lekcje (list[dict]): Lista lekcji dla jednej godziny.
            wpisyZastępstw (list[dict]): Lista zastępstw dla jednej godziny.
        """

        if not lekcje or not wpisyZastępstw:
            return

        zajęteIndeksy: set[int] = set()

        for wpisZastępstwa in wpisyZastępstw:
            grupa = wpisZastępstwa.get("grupa")
            daneZastępstwa = zbudujDaneZastępstwa(wpisZastępstwa)

            if daneZastępstwa is None:
                continue

            if isinstance(grupa, str):
                for indeksLekcji, lekcja in enumerate(lekcje):
                    if indeksLekcji in zajęteIndeksy:
                        continue

                    if lekcja.get("grupa") == grupa:
                        lekcja["zastepstwo"] = daneZastępstwa
                        zajęteIndeksy.add(indeksLekcji)
                        break

                continue

            for indeksLekcji, lekcja in enumerate(lekcje):
                if indeksLekcji in zajęteIndeksy:
                    continue

                lekcja["zastepstwo"] = daneZastępstwa
                zajęteIndeksy.add(indeksLekcji)

    try:
        planTygodniowy = planLekcji.get("plan")
        if not isinstance(planTygodniowy, dict) or not planTygodniowy:
            return planLekcji

        dzień = zastępstwa.get("dzien")
        if dzień is None:
            return planLekcji

        wpisyDnia = planTygodniowy.get(dzień)
        if not isinstance(wpisyDnia, list) or not wpisyDnia:
            return planLekcji

        if zastępstwa.get("skrocone"):
            schematSkróconych: dict[int, tuple[str, str]] = {}

            for numer, zakres in konfiguracja.get("skrocone", {}).items():
                if not isinstance(zakres, str) or "-" not in zakres:
                    continue

                try:
                    numerLekcji = int(numer)
                except (TypeError, ValueError):
                    continue

                początek, koniec = [wartość.strip() for wartość in zakres.split("-", 1)]
                schematSkróconych[numerLekcji] = (początek, koniec)

            for wpis in wpisyDnia:
                numerLekcji = wpis.get("numer")

                if not isinstance(numerLekcji, int):
                    continue

                if (zakres := schematSkróconych.get(numerLekcji)):
                    wpis["poczatek"], wpis["koniec"] = zakres

        wpisyZastępstw = zastępstwa.get("zastepstwa", [])
        if not wpisyZastępstw:
            usuńPusteWpisy(planTygodniowy)
            return planLekcji

        wpisyPoNumerzeLekcji: defaultdict[int, list[dict]] = defaultdict(list)
        for wpis in wpisyZastępstw:
            numerLekcji = wpis.get("lekcja")

            if not isinstance(numerLekcji, int):
                continue

            wpisyPoNumerzeLekcji[numerLekcji].append(wpis)

        wpisyPlanuPoNumerze: dict[int, dict] = {}
        for wpisPlanu in wpisyDnia:
            numerLekcji = wpisPlanu.get("numer")

            if isinstance(numerLekcji, int):
                wpisyPlanuPoNumerze[numerLekcji] = wpisPlanu

        for numerLekcji, wpisyGodziny in wpisyPoNumerzeLekcji.items():
            wpisPlanu = wpisyPlanuPoNumerze.get(numerLekcji)

            if wpisPlanu is None:
                continue

            lekcje = wpisPlanu.get("lekcje")
            if not isinstance(lekcje, list) or not lekcje:
                wpisPlanu["lekcje"] = [
                    {
                        "przedmiot": "Brak lekcji",
                        "grupa": None,
                        "nauczyciel": None,
                        "sala": None,
                        "oddzialy": None,
                        "zastepstwo": zbudujDaneZastępstwa(wpis)
                    }
                    for wpis in wpisyGodziny
                ]
                continue

            przypiszWpisyDoLekcji(lekcje, wpisyGodziny)

        usuńPusteWpisy(planTygodniowy)
        return planLekcji
    except Exception as e:
        logowanie.exception(
            f"Wystąpił błąd podczas budowania planu lekcji z wpisami zastępstw. Więcej informacji: {e}"
        )
        raise

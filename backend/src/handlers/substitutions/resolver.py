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

# Zewnętrzne biblioteki
import aiohttp

# Wewnętrzne importy
from src.classes.semaphore import semafor
from src.classes.types import (
    ListaOddziałów,
    Zastępstwo
)
from src.handlers.configuration import konfiguracja
from src.handlers.helpers import sprawdźGrupę
from src.handlers.logging import logowanie
from src.handlers.scraper import pobierzZawartośćStrony
from src.handlers.substitutions.helpers import zwróćNazwyKluczy
from src.handlers.timetables.parser import wyodrębnijPlanLekcji

async def uzupełnijZastępstwa(
    atom: aiohttp.ClientSession,
    wpisyZastępstw: list[Zastępstwo],
    identyfikator: str,
    dzień: str,
    listaOddziałów: ListaOddziałów,
    grupy: list[str] | None,
    przedmiotyDodatkowe: dict[str, bool] | None
) -> list[Zastępstwo]:
    """
    Uzupełnia niezidentyfikowane wpisy zastępstw i przetwarza zastępstwa z wybranymi grupami dla konkretnego oddziału, na podstawie jego planu lekcji oraz planu lekcji nauczyciela.

    Args:
        atom (aiohttp.ClientSession): Aktywna sesja HTTP używana do wykonania zapytania.
        wpisyZastępstw (list[Zastępstwo]): Lista wpisów zastępstw.
        identyfikator (str): Identyfikator oddziału.
        dzień (str): Dzień tygodnia, na który wpisane są zastępstwa.
        listaOddziałów (ListaOddziałów): Słownik wszystkich oddziałów.
        grupy (list[str] | None): Lista oznaczeń określających grupę przedmiotów.
        przedmiotyDodatkowe (dict[str, bool] | None): Słownik przedmiotów dodatkowych przeznaczonych do filtracji.

    Returns:
        list[Zastępstwo]: Lista zidentyfikowanych zastępstw, dla których udało się przypisać oddział.
    """

    try:
        katalogPlanów = konfiguracja.get("plany", {})
        katalog = katalogPlanów.get("url")
        kodowanie = katalogPlanów.get("kodowanie")

        if not katalog or not kodowanie:
            logowanie.warning(
                "Funkcja nie otrzymała wystarczającej liczby potrzebnych danych. Zwracanie nieuzupełnionej zawartości."
            )
            return wpisyZastępstw

        url = f"{katalog}{identyfikator}.html"
        async with semafor:
            zawartośćPlanuOddziału = await pobierzZawartośćStrony(atom, url, kodowanie)

        if zawartośćPlanuOddziału is None:
            logowanie.warning(
                "Brak treści pobranej ze strony. Zwracanie nieuzupełnionej zawartości."
            )
            return wpisyZastępstw

        planLekcjiOddziału = await wyodrębnijPlanLekcji(atom, zawartośćPlanuOddziału, listaOddziałów, None, grupy, przedmiotyDodatkowe, url)
        if not planLekcjiOddziału:
            logowanie.warning(
                "Brak planu lekcji oddziału. Zwracanie nieuzupełnionej zawartości."
            )
            return wpisyZastępstw

        tymczasowy: dict[str, set[str] | None] = {}
        planWszystkichDni = planLekcjiOddziału.get("plan", {})
        planDnia = planWszystkichDni.get(dzień, [])

        for wpis in wpisyZastępstw:
            surowyOpis = wpis.get("opis")

            if wpis.get("zidentyfikowane") and not re.search(r"\([123]\)", surowyOpis or ""):
                continue

            if wpis.get("lekcja") is None:
                continue

            try:
                numerLekcji = int(wpis["lekcja"])
            except ValueError:
                continue

            kluczeZastępstwa = zwróćNazwyKluczy(wpis.get("nauczyciel"))

            for godzina in planDnia:
                if godzina.get("numer") != numerLekcji:
                    continue

                for lekcja in godzina.get("lekcje", []):
                    if not lekcja.get("standard", True):
                        continue

                    urlPlanu = lekcja.get("nauczyciel", {}).get("url")
                    if not urlPlanu:
                        continue

                    if urlPlanu not in tymczasowy:
                        async with semafor:
                            zawartośćPlanuNauczyciela = await pobierzZawartośćStrony(atom, urlPlanu, kodowanie)

                        if zawartośćPlanuNauczyciela is None:
                            tymczasowy[urlPlanu] = None
                        else:
                            etykietaPlanu = zawartośćPlanuNauczyciela.select_one(".tytulnapis")

                            if not etykietaPlanu:
                                tymczasowy[urlPlanu] = None
                            else:
                                nauczyciel = etykietaPlanu.get_text(strip=True)
                                nauczyciel = re.sub(r"\s*\([^)]*\)\s*$", "", nauczyciel).strip()
                                tymczasowy[urlPlanu] = zwróćNazwyKluczy(nauczyciel)

                    kluczePlanu = tymczasowy.get(urlPlanu)
                    if not kluczePlanu:
                        continue

                    if kluczeZastępstwa & kluczePlanu:
                        dopasowanie = re.search(r"\((\d)\)", surowyOpis) if surowyOpis else None
                        licznikGrupyZastępstwa = dopasowanie.group(1) if dopasowanie else None
                        grupa = lekcja.get("grupa")

                        if licznikGrupyZastępstwa is None:
                            if not sprawdźGrupę(grupa, grupy):
                                continue

                            wpis["grupa"] = grupa
                            wpis["zidentyfikowane"] = True
                            break

                        if not grupa:
                            continue

                        licznikGrupyLekcji = grupa.split("/")[0]
                        if licznikGrupyLekcji != licznikGrupyZastępstwa:
                            continue

                        if not sprawdźGrupę(grupa, grupy):
                            continue

                        wpis["grupa"] = grupa
                        wpis["zidentyfikowane"] = True
                        break

                if wpis.get("zidentyfikowane"):
                    break

        wynik = []

        for wpis in wpisyZastępstw:
            if not wpis.get("zidentyfikowane"):
                continue

            opis = wpis.get("opis") or ""
            dopasowanie = re.search(r"\((\d)\)", opis)

            if dopasowanie and grupy:
                grupaWpisu = wpis.get("grupa")

                if not grupaWpisu:
                    continue

                if not sprawdźGrupę(grupaWpisu, grupy):
                    continue

            if "-" in opis:
                wpis["opis"] = opis.split("-", 1)[1].strip()

            wynik.append(wpis)

        return wynik
    except Exception as e:
        logowanie.exception(
            f"Wystąpił błąd podczas przypisywania zastępstw bez oddziału do planu lekcji: {e}. Zwracanie niezmodyfikowanej listy wpisów zastępstw."
        )
        return wpisyZastępstw

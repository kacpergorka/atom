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
import asyncio
from typing import Union
from urllib.parse import (
    urljoin,
    urlparse
)

# Zewnętrzne biblioteki
import aiohttp
from bs4 import (
    BeautifulSoup,
    Tag
)

# Wewnętrzne importy
from src.classes.types import (
    EncjaPlanu,
    Lekcja,
    LekcjaStandardowa,
    LekcjaNiestandardowa,
    ListaOddziałów,
    PlanLekcji
)
from src.handlers.configuration import konfiguracja
from src.handlers.helpers import sprawdźGrupę
from src.handlers.logging import logowanie
from src.handlers.timetables.helpers import (
    wydobądźIdentyfikator,
    zwróćPustySłownik
)
from src.handlers.timetables.resolver import uzupełnijNauczyciela

async def wyodrębnijPlanLekcji(
    atom: aiohttp.ClientSession,
    zawartośćStrony: BeautifulSoup | None,
    listaOddziałów: ListaOddziałów | None,
    dzieńSkróconych: str | None,
    grupy: list[str] | None,
    przedmiotyDodatkowe: dict[str, bool] | None,
    url: str | None
) -> PlanLekcji | None:
    """
    Wyodrębnia, przetwarza i strukturyzuje dane planu lekcji z pliku strony internetowej.

    Args:
        atom (aiohttp.ClientSession): Aktywna sesja HTTP używana do wykonania zapytania.
        zawartośćStrony (BeautifulSoup | None): Obiekt BeautifulSoup reprezentujący stronę HTML.
        listaOddziałów (ListaOddziałów | None): Słownik wszystkich oddziałów.
        dzieńSkróconych (str | None): Dzień tygodnia, dla którego obowiązuje skrócony rozkład zajęć.
        grupy (list[str] | None): Lista oznaczeń określających grupę przedmiotów.
        przedmiotyDodatkowe (dict[str, bool] | None): Słownik przedmiotów dodatkowych przeznaczonych do filtracji.
        url (str): Adres strony internetowej planu lekcji użyty do pobrania jej zawartości.

    Returns:
        PlanLekcji | None: Słownik zawierający ustrukturyzowany plan lekcji.
    """

    def wydobądźDniTygodnia(tabela: Tag) -> list[str]:
        """
        Wyodrębnia listę dni tygodnia z nagłówka tabeli planu lekcji.

        Args:
            tabela (Tag): Znacznik `<table>` zawierający plan lekcji.

        Returns:
            list[str]: Lista nazw dni tygodnia w kolejności ich występowania w tabeli
        """

        nagłówek = tabela.select_one("tr")
        if not nagłówek:
            return []

        th = nagłówek.find_all("th")

        return [komórka.get_text(strip=True) for komórka in th[2:]]

    def wydobądźGrupę(tekst: str) -> str | None:
        """
        Wyodrębnia oznaczenie grupy z tekstu przedmiotu.

        Args:
            tekst (str): Tekst przedmiotu, z którego ma zostać wyodrębniona grupa.

        Returns:
            str | None: Oznaczenie grupy.
        """

        wzorce: list[str] = konfiguracja.get("grupy", [])

        for wzorzec in wzorce:
            if wzorzec in tekst:
                return wzorzec

        return None

    def normalizujEncje(etykieta: Tag) -> str:
        """
        Normalizuje nazwę encji dołączając ewentualny dopisek, który jej dotyczy.

        Args:
            etykieta (Tag): Znacznik HTML reprezentujący nazwę przedmiotu lub oddziału.

        Returns:
            str: Znormalizowana nazwa encji.
        """

        encja = etykieta.get_text(strip=True)

        dopisek = etykieta.next_sibling
        if isinstance(dopisek, str) and dopisek.strip().startswith(("-", "/")):
            encja += dopisek.strip()

        return encja

    def wydobądźEncje(fragment: BeautifulSoup) -> tuple[EncjaPlanu, EncjaPlanu, list[EncjaPlanu]]:
        """
        Wyodrębnia informacje o nauczycielu, sali oraz oddziałach z fragmentu HTML.

        Args:
            fragment (BeautifulSoup): Fragment obiektu BeautifulSoup reprezentującego strukturę HTML zawierający dane pojedynczej lekcji.

        Returns:
            tuple[EncjaPlanu, EncjaPlanu, list[EncjaPlanu]]: Krotka słowników nauczyciela, sali i oddziałów.
        """

        katalog = konfiguracja.get("plany", {}).get("url")
        nauczyciel = zwróćPustySłownik()
        sala = zwróćPustySłownik()
        oddziały: list[EncjaPlanu] = []

        if not katalog or urlparse(url).netloc != urlparse(katalog).netloc:
            logowanie.warning(
                "Otrzymany URL nie zgadza się z wartością URL znajdującego się w pliku konfiguracyjnym. Zwracanie nieuzupełnionych encji."
            )
            return nauczyciel, sala, oddziały

        for etykietaOddziału in fragment.select(".o"):
            hrefOddziału = etykietaOddziału.get("href")
            urlOddziału = urljoin(katalog, hrefOddziału) if katalog and hrefOddziału else None

            oddziały.append({
                "tekst": normalizujEncje(etykietaOddziału),
                "url": urlOddziału,
                "identyfikator": wydobądźIdentyfikator(urlOddziału)
            })

        etykietaNauczyciela = fragment.select_one(".n")
        if etykietaNauczyciela:
            hrefNauczyciela = etykietaNauczyciela.get("href")
            urlNauczyciela = urljoin(katalog, hrefNauczyciela) if katalog and hrefNauczyciela else None

            nauczyciel = {
                "tekst": etykietaNauczyciela.get_text(strip=True),
                "url": urlNauczyciela,
                "identyfikator": wydobądźIdentyfikator(urlNauczyciela)
            }

        etykietaSali = fragment.select_one(".s")
        if etykietaSali:
            hrefSali = etykietaSali.get("href")
            urlSali = urljoin(katalog, hrefSali) if katalog and hrefSali else None

            sala = {
                "tekst": etykietaSali.get_text(strip=True),
                "url": urlSali,
                "identyfikator": wydobądźIdentyfikator(urlSali)
            }

        return nauczyciel, sala, oddziały

    def podzielKomórkę(td: Tag) -> list[list[Union[Tag, str]]]:
        """
        Dzieli zawartość komórki tabeli na logiczne bloki oddzielone znacznikami `<br>`.

        Args:
            td (Tag): Znacznik `<td>` reprezentujący pojedynczą komórkę planu lekcji.

        Returns:
            list[list[Union[Tag, str]]]: Lista bloków, gdzie każdy blok jest listą elementów HTML lub tekstu.
        """

        bloki: list[list[Union[Tag, str]]] = []
        aktualny: list[Union[Tag, str]] = []

        for element in td.children:
            if getattr(element, "name", None) == "br":
                if aktualny:
                    bloki.append(aktualny)
                    aktualny = []

                continue

            if isinstance(element, str) and not element.strip():
                continue

            aktualny.append(element)

        if aktualny:
            bloki.append(aktualny)

        return bloki

    def rozpoznajLekcję(fragment: BeautifulSoup) -> LekcjaNiestandardowa | None:
        """
        Rozpoznaje niestandardową lekcję, która nie zawiera oznaczeń przedmiotu.

        Args:
            fragment (BeautifulSoup): Fragment obiektu BeautifulSoup reprezentującego strukturę HTML zawierający dane pojedynczego bloku komórki.

        Returns:
            LekcjaNiestandardowa | None: Słownik opisujący lekcję niestandardową, jeśli fragment ją reprezentuje.
        """

        etykietyPrzedmiotu = fragment.select(".p")
        if etykietyPrzedmiotu:
            return None

        tekst = fragment.get_text(" ", strip=True)
        if not tekst:
            return None

        return {
            "standard": False,
            "tekst": tekst
        }

    def pobierzPrzedmioty(fragment: BeautifulSoup) -> list[str]:
        """
        Wyodrębnia i normalizuje listę przedmiotów z fragmentu lekcji.

        Args:
            fragment (BeautifulSoup): Fragment obiektu BeautifulSoup reprezentującego strukturę HTML zawierający dane pojedynczej lekcji.

        Returns:
            list[str]: Lista znormalizowanych nazw przedmiotów.
        """

        przedmioty = []
        for etykieta in fragment.select(".p"):
            nazwa = normalizujEncje(etykieta)

            if nazwa:
                przedmioty.append(nazwa)

        return przedmioty

    def sprawdźNauczyciela(
        nazwa: str | None,
        nauczyciel: EncjaPlanu,
        sala: EncjaPlanu,
        rozwinięciaOddziałów: set[str]
    ) -> bool:
        """
        Sprawdza, czy dla lekcji należy później uzupełnić dane nauczyciela.

        Args:
            nazwa (str | None): Nazwa aktualnie przetwarzanego planu lekcji.
            nauczyciel (EncjaPlanu): Dane nauczyciela.
            sala (EncjaPlanu): Dane sali.
            rozwinięciaOddziałów (set[str]): Zbiór rozwiniętych nazw oddziałów.

        Returns:
            bool: True, jeśli nauczyciel powinien zostać uzupełniony, False w przeciwnym razie.
        """

        return (
            nazwa in rozwinięciaOddziałów
            and nauczyciel["tekst"] is None
            and sala["url"] is not None
        )

    def sparsujLekcje(
        fragment: BeautifulSoup,
        dzień: str,
        numer: int,
        nazwa: str | None,
        rozwinięciaOddziałów: set[str],
        potrzebniNauczyciele: set[tuple[str | None, str, int]],
        grupy: list[str] | None,
        przedmiotyDodatkowe: dict[str, bool] | None
    ) -> list[LekcjaStandardowa]:
        """
        Parsuje standardowe lekcje z fragmentu komórki planu lekcji.

        Args:
            fragment (BeautifulSoup): Fragment obiektu BeautifulSoup reprezentującego strukturę HTML zawierający dane pojedynczego bloku komórki.
            dzień (str): Dzień tygodnia, dla którego przetwarzana jest lekcja.
            numer (int): Numer lekcji w danym dniu tygodnia.
            nazwa (str | None): Nazwa aktualnie przetwarzanego planu lekcji.
            rozwinięciaOddziałów (set[str]): Zbiór rozwiniętych nazw oddziałów.
            potrzebniNauczyciele (set[tuple[str | None, str, int]]): Zbiór lekcji, dla których należy uzupełnić dane nauczyciela.
            grupy (list[str] | None): Lista oznaczeń określających grupę przedmiotów.
            przedmiotyDodatkowe (dict[str, bool] | None): Słownik przedmiotów dodatkowych przeznaczonych do filtracji.

        Returns:
            list[LekcjaStandardowa]: Lista słowników opisujących lekcje standardowe.
        """

        lekcje: list[LekcjaStandardowa] = []
        nauczyciel, sala, oddziały = wydobądźEncje(fragment)
        przedmioty = pobierzPrzedmioty(fragment)
        aktywnaLekcja: LekcjaStandardowa | None = None

        for przedmiot in przedmioty:
            if przedmiot.startswith("#"):
                if aktywnaLekcja is not None:
                    aktywnaLekcja["przedmiot"] += f" {przedmiot}"

                continue

            nazwaPrzedmiotu = przedmiot.lower()

            if przedmiotyDodatkowe:
                wykluczonyPrzedmiot = False

                for nazwaWykluczenia, włączone in przedmiotyDodatkowe.items():
                    if not włączone and nazwaWykluczenia.lower() in nazwaPrzedmiotu:
                        wykluczonyPrzedmiot = True
                        break

                if wykluczonyPrzedmiot:
                    continue

            grupa = wydobądźGrupę(przedmiot)
            if not sprawdźGrupę(grupa, grupy):
                continue

            if sprawdźNauczyciela(nazwa, nauczyciel, sala, rozwinięciaOddziałów):
                potrzebniNauczyciele.add((sala["url"], dzień, numer))
                nauczyciel = zwróćPustySłownik()

            lekcje.append({
                "standard": True,
                "przedmiot": przedmiot,
                "grupa": grupa,
                "nauczyciel": nauczyciel,
                "sala": sala,
                "oddzialy": oddziały
            })
            aktywnaLekcja = lekcje[-1]

        return lekcje

    def wyczyśćKomórkę(
        td: Tag,
        dzień: str,
        numer: int,
        nazwa: str | None
    ) -> list[Lekcja]:
        """
        Czyści, interpretuje i strukturyzuje zawartość pojedynczej komórki tabeli planu lekcji.

        Args:
            td (Tag): Znacznik `<td>` reprezentujący pojedynczą komórkę planu lekcji.
            dzień (str): Dzień tygodnia, dla którego przetwarzana jest komórka.
            numer (int): Numer lekcji w danym dniu tygodnia.
            nazwa (str | None): Nazwa aktualnie przetwarzanego planu lekcji.

        Returns:
            list[Lekcja]: Lista słowników opisujących lekcje znajdujące się w danej komórce tabeli.
        """

        lekcje: list[Lekcja] = []
        bloki = podzielKomórkę(td)

        if not bloki:
            tekst = td.get_text(" ", strip=True)

            if tekst:
                return [{
                    "standard": False,
                    "tekst": tekst
                }]

            return []

        for blok in bloki:
            fragment = BeautifulSoup("".join(map(str, blok)), "html.parser")

            niestandardowa = rozpoznajLekcję(fragment)
            if niestandardowa:
                lekcje.append(niestandardowa)
                continue

            lekcje.extend(sparsujLekcje(fragment, dzień, numer, nazwa, rozwinięciaOddziałów, potrzebniNauczyciele, grupy, przedmiotyDodatkowe))

        return lekcje

    if zawartośćStrony is None:
        logowanie.warning(
            "Brak treści pobranej ze strony. Zwracanie pustej zawartości."
        )
        return None

    if not isinstance(listaOddziałów, dict):
        logowanie.warning(
            "Nieprawidłowy typ danych listy oddziałów. Zwracanie pustej zawartości."
        )
        return None

    if not isinstance(url, str) or not url.startswith(("http://", "https://")):
        logowanie.warning(
            "Nieprawidłowy URL wejściowy. Zwracanie pustej zawartości."
        )
        return None

    try:
        potrzebniNauczyciele: set[tuple[str | None, str, int]] = set()
        rozwinięciaOddziałów: set[str] = set()

        etykietaPlanu = zawartośćStrony.select_one(".tytulnapis")
        tabela = zawartośćStrony.select_one("table.tabela")

        nazwa = None
        wygenerowano = None
        data = {
            "od": None,
            "do": None
        }
        wyniki = []

        for dane in listaOddziałów.values():
            rozwinięcie = dane.get("rozwiniecie")

            if isinstance(rozwinięcie, str) and rozwinięcie:
                rozwinięciaOddziałów.add(rozwinięcie)

        if etykietaPlanu:
            nazwa = etykietaPlanu.get_text(strip=True)

            części = nazwa.split()
            if len(części) >= 2 and części[0] == części[1]:
                nazwa = " ".join([części[0]] + części[2:])

        for td in zawartośćStrony.find_all("td"):
            tekst = (
                td.get_text(" ", strip=True)
                .replace(":", "")
                .replace("r.", "")
            )

            if tekst.startswith("Obowiązuje"):
                if "od" in tekst:
                    data["od"] = tekst.split("od", 1)[1].split("do", 1)[0].strip()

                if "do" in tekst:
                    data["do"] = tekst.split("do", 1)[1].strip()

                break

        for td in zawartośćStrony.find_all("td"):
            tekst = td.get_text(" ", strip=True).lower()

            if tekst.startswith("wygenerowano"):
                wygenerowano = tekst.replace("wygenerowano", "").strip().split()[0]
                break

        if not tabela:
            return None

        rozkładSkrócony = konfiguracja.get("skrocone", {})
        schematSkróconych: dict[int, str] = {
            int(numer): zakres
            for numer, zakres in rozkładSkrócony.items()
        }

        dniTygodnia = wydobądźDniTygodnia(tabela)
        wiersze = tabela.find_all("tr")[1:]
        plan = {dzień: [] for dzień in dniTygodnia}

        for wiersz in wiersze:
            komórki = wiersz.find_all("td")

            if len(komórki) < 7:
                continue

            numer = int(komórki[0].get_text(strip=True))

            for indeks, dzień in enumerate(dniTygodnia):
                td = komórki[indeks + 2]

                if dzieńSkróconych is not None and dzień == dzieńSkróconych:
                    godziny = schematSkróconych.get(numer)
                else:
                    godziny = None

                if not godziny:
                    godziny = komórki[1].get_text(strip=True).replace(" ", "")

                od, do = godziny.split("-", 1)

                lekcje = wyczyśćKomórkę(td, dzień, numer, nazwa)
                if not lekcje:
                    continue

                plan[dzień].append({
                    "numer": numer,
                    "od": od,
                    "do": do,
                    "lekcje": lekcje
                })

        listaPotrzebnychNauczycieli = list(potrzebniNauczyciele)

        for indeks in range(0, len(listaPotrzebnychNauczycieli), 20):
            paczka = listaPotrzebnychNauczycieli[indeks:indeks + 20]

            wyniki.extend(
                await asyncio.gather(*[
                    uzupełnijNauczyciela(atom, url, dniTygodnia, dzień, numer)
                    for url, dzień, numer in paczka
                ])
            )

        słownikNauczycieli: dict[tuple[str, str, int], EncjaPlanu] = {
            (url, dzień, numer): nauczyciel
            for (url, dzień, numer), nauczyciel in zip(listaPotrzebnychNauczycieli, wyniki)
        }

        for dzień, wpisy in plan.items():
            for wpis in wpisy:
                numer = wpis["numer"]

                for lekcja in wpis["lekcje"]:
                    if (
                        lekcja["standard"]
                        and lekcja["nauczyciel"]["tekst"] is None
                        and lekcja["sala"]["url"] is not None
                    ):
                        klucz = (lekcja["sala"]["url"], dzień, numer)
                        if klucz in słownikNauczycieli:
                            lekcja["nauczyciel"] = słownikNauczycieli[klucz]

        identyfikator = wydobądźIdentyfikator(url)

        if isinstance(identyfikator, str):
            if identyfikator.startswith("o"):
                kategoria = "oddział"
            elif identyfikator.startswith("n"):
                kategoria = "nauczyciel"
            elif identyfikator.startswith("s"):
                kategoria = "sala"
            else:
                kategoria = None
        else:
            kategoria = None

        return {
            "nazwa": nazwa,
            "kategoria": kategoria,
            "url": url,
            "identyfikator": identyfikator,
            "wygenerowano": wygenerowano,
            "data": data,
            "plan": plan
        }
    except Exception as e:
        logowanie.exception(
            f"Wystąpił błąd podczas przetwarzania HTML planu lekcji ({url}). Więcej informacji: {e}"
        )
        return None

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
import asyncio
import re
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
from src.classes.types.lists import ElementListy
from src.classes.types.timetables import (
    ElementPlanu,
    Lekcja,
    PlanLekcji
)
from src.handlers.configuration import konfiguracja
from src.handlers.helpers import sprawdźGrupę
from src.handlers.logging import logowanie
from src.handlers.timetables.helpers import (
    wyodrębnijIdentyfikator,
    zwróćPustySłownik
)
from src.handlers.timetables.resolver import uzupełnijNauczyciela

async def wyodrębnijPlanLekcji(
    atom: aiohttp.ClientSession,
    zawartośćStrony: BeautifulSoup,
    listaOddziałów: list[ElementListy] | None,
    grupy: list[str] | None,
    przedmiotyDodatkowe: dict[str, bool] | None,
    zastępstwa: bool,
    url: str | None
) -> PlanLekcji:
    """
    Wyodrębnia, przetwarza i strukturyzuje dane planu lekcji z pliku strony internetowej.

    Args:
        atom (aiohttp.ClientSession): Aktywna sesja HTTP używana do wykonania zapytania.
        zawartośćStrony (BeautifulSoup): Obiekt BeautifulSoup reprezentujący stronę HTML.
        listaOddziałów (list[ElementListy] | None): Lista wszystkich oddziałów.
        grupy (list[str] | None): Lista oznaczeń określających grupę przedmiotów.
        przedmiotyDodatkowe (dict[str, bool] | None): Słownik przedmiotów dodatkowych przeznaczonych do filtracji.
        zastępstwa (bool): Flaga informująca, czy uwzględniać zastępstwa w planie lekcji.
        url (str | None): Adres strony internetowej planu lekcji użyty do pobrania jej zawartości.

    Returns:
        PlanLekcji: Słownik zawierający ustrukturyzowany plan lekcji.
    """
    def zwróćPustyPlanLekcji() -> PlanLekcji:
        """
        Zwraca pustą strukturę planu lekcji w standardowym formacie.

        Returns:
            PlanLekcji: Pusta struktura planu lekcji.
        """

        return {
            "nazwa": "",
            "kategoria": None,
            "url": "",
            "identyfikator": None,
            "wygenerowano": None,
            "data": {
                "obowiazuje": None,
                "wygasa": None
            },
            "zastepstwa": False,
            "plan": None
        }

    def wyodrębnijDniTygodnia(tabela: Tag) -> list[str]:
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

    def wyodrębnijGrupę(tekst: str) -> str | None:
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

    def normalizujElementy(etykieta: Tag) -> str:
        """
        Normalizuje nazwę elementu dołączając ewentualny dopisek, który jej dotyczy.

        Args:
            etykieta (Tag): Znacznik HTML reprezentujący nazwę przedmiotu lub oddziału.

        Returns:
            str: Znormalizowana nazwa elementu.
        """

        element = etykieta.get_text(strip=True)

        dopisek = etykieta.next_sibling
        if isinstance(dopisek, str) and dopisek.strip().startswith(("-", "/")):
            element += dopisek.strip()

        return element

    def wyodrębnijElementy(
        fragment: BeautifulSoup,
        url: str | None
    ) -> tuple[ElementPlanu, ElementPlanu, list[ElementPlanu]]:
        """
        Wyodrębnia informacje o nauczycielu, sali oraz oddziałach z fragmentu HTML.

        Args:
            fragment (BeautifulSoup): Fragment obiektu BeautifulSoup reprezentującego strukturę HTML zawierający dane pojedynczej lekcji.
            url (str | None): Adres strony internetowej planu lekcji użyty do pobrania jej zawartości.

        Returns:
            tuple[ElementPlanu, ElementPlanu, list[ElementPlanu]]: Krotka słowników nauczyciela, sali i oddziałów.
        """

        katalog = konfiguracja.get("plany", {}).get("url")
        nauczyciel = zwróćPustySłownik()
        sala = zwróćPustySłownik()
        oddziały: list[ElementPlanu] = []

        if not katalog or not url or urlparse(url).netloc != urlparse(katalog).netloc:
            logowanie.warning(
                "Otrzymany URL nie zgadza się z wartością URL znajdującego się w pliku konfiguracyjnym. Zwracanie nieuzupełnionych elementów."
            )
            return nauczyciel, sala, oddziały

        for etykietaOddziału in fragment.select(".o"):
            hrefOddziału = etykietaOddziału.get("href")
            urlOddziału = urljoin(katalog, hrefOddziału) if katalog and hrefOddziału else None

            oddziały.append({
                "tekst": normalizujElementy(etykietaOddziału),
                "url": urlOddziału,
                "identyfikator": wyodrębnijIdentyfikator(urlOddziału)
            })

        etykietaNauczyciela = fragment.select_one(".n")
        if etykietaNauczyciela:
            hrefNauczyciela = etykietaNauczyciela.get("href")
            urlNauczyciela = urljoin(katalog, hrefNauczyciela) if katalog and hrefNauczyciela else None

            nauczyciel = {
                "tekst": etykietaNauczyciela.get_text(strip=True),
                "url": urlNauczyciela,
                "identyfikator": wyodrębnijIdentyfikator(urlNauczyciela)
            }

        etykietaSali = fragment.select_one(".s")
        if etykietaSali:
            hrefSali = etykietaSali.get("href")
            urlSali = urljoin(katalog, hrefSali) if katalog and hrefSali else None

            sala = {
                "tekst": etykietaSali.get_text(strip=True),
                "url": urlSali,
                "identyfikator": wyodrębnijIdentyfikator(urlSali)
            }

        return nauczyciel, sala, oddziały

    def podzielKomórkę(td: Tag) -> list[list[Tag | str]]:
        """
        Dzieli zawartość komórki tabeli na logiczne bloki oddzielone znacznikami `<br>`.

        Args:
            td (Tag): Znacznik `<td>` reprezentujący pojedynczą komórkę planu lekcji.

        Returns:
            list[list[Tag | str]]: Lista bloków, gdzie każdy blok jest listą elementów HTML lub tekstu.
        """

        bloki: list[list[Tag | str]] = []
        aktualny: list[Tag | str] = []

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

    def rozpoznajLekcję(fragment: BeautifulSoup) -> Lekcja | None:
        """
        Rozpoznaje niestandardową lekcję, która nie zawiera oznaczeń przedmiotu.

        Args:
            fragment (BeautifulSoup): Fragment obiektu BeautifulSoup reprezentującego strukturę HTML zawierający dane pojedynczego bloku komórki.

        Returns:
            Lekcja | None: Słownik opisujący lekcję niestandardową, jeśli fragment ją reprezentuje.
        """

        etykietyPrzedmiotu = fragment.select(".p")
        if etykietyPrzedmiotu:
            return None

        tekst = fragment.get_text(" ", strip=True)
        if not tekst:
            return None

        return {
            "przedmiot": tekst,
            "grupa": None,
            "nauczyciel": None,
            "sala": None,
            "oddzialy": None,
            "zastepstwo": None
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
            nazwa = normalizujElementy(etykieta)

            if nazwa:
                przedmioty.append(nazwa)

        return przedmioty

    def sprawdźNauczyciela(
        nazwa: str | None,
        nauczyciel: ElementPlanu,
        sala: ElementPlanu,
        rozwinięciaOddziałów: set[str]
    ) -> bool:
        """
        Sprawdza, czy dla lekcji należy później uzupełnić dane nauczyciela.

        Args:
            nazwa (str | None): Nazwa aktualnie przetwarzanego planu lekcji.
            nauczyciel (ElementPlanu): Dane nauczyciela.
            sala (ElementPlanu): Dane sali.
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
        przedmiotyDodatkowe: dict[str, bool] | None,
        url: str | None
    ) -> list[Lekcja]:
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
            url (str | None): Adres strony internetowej planu lekcji użyty do pobrania jej zawartości.

        Returns:
            list[Lekcja]: Lista słowników opisujących lekcje standardowe.
        """

        lekcje: list[Lekcja] = []
        nauczyciel, sala, oddziały = wyodrębnijElementy(fragment, url)
        przedmioty = pobierzPrzedmioty(fragment)
        aktywnaLekcja: Lekcja | None = None

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

            grupa = wyodrębnijGrupę(przedmiot)
            if not sprawdźGrupę(grupa, grupy):
                continue

            if sprawdźNauczyciela(nazwa, nauczyciel, sala, rozwinięciaOddziałów):
                potrzebniNauczyciele.add((sala["url"], dzień, numer))
                nauczyciel = zwróćPustySłownik()

            lekcje.append({
                "przedmiot": przedmiot,
                "grupa": grupa,
                "nauczyciel": nauczyciel,
                "sala": sala,
                "oddzialy": oddziały,
                "zastepstwo": None
            })
            aktywnaLekcja = lekcje[-1]

        return lekcje

    def wyczyśćKomórkę(
        td: Tag,
        dzień: str,
        numer: int,
        nazwa: str | None,
        rozwinięciaOddziałów: set[str],
        potrzebniNauczyciele: set[tuple[str | None, str, int]],
        grupy: list[str] | None,
        przedmiotyDodatkowe: dict[str, bool] | None,
        url: str | None
    ) -> list[Lekcja]:
        """
        Czyści, interpretuje i strukturyzuje zawartość pojedynczej komórki tabeli planu lekcji.

        Args:
            td (Tag): Znacznik `<td>` reprezentujący pojedynczą komórkę planu lekcji.
            dzień (str): Dzień tygodnia, dla którego przetwarzana jest komórka.
            numer (int): Numer lekcji w danym dniu tygodnia.
            nazwa (str | None): Nazwa aktualnie przetwarzanego planu lekcji.
            rozwinięciaOddziałów (set[str]): Zbiór rozwiniętych nazw oddziałów.
            potrzebniNauczyciele (set[tuple[str | None, str, int]]): Zbiór lekcji, dla których należy uzupełnić dane nauczyciela.
            grupy (list[str] | None): Lista oznaczeń określających grupę przedmiotów.
            przedmiotyDodatkowe (dict[str, bool] | None): Słownik przedmiotów dodatkowych przeznaczonych do filtracji.
            url (str | None): Adres strony internetowej planu lekcji użyty do pobrania jej zawartości.

        Returns:
            list[Lekcja]: Lista słowników opisujących lekcje znajdujące się w danej komórce tabeli.
        """

        lekcje: list[Lekcja] = []
        bloki = podzielKomórkę(td)

        if not bloki:
            tekst = td.get_text(" ", strip=True)

            if tekst:
                return [{
                    "przedmiot": tekst,
                    "grupa": None,
                    "nauczyciel": None,
                    "sala": None,
                    "oddzialy": None,
                    "zastepstwo": None
                }]

            return []

        for blok in bloki:
            fragment = BeautifulSoup("".join(map(str, blok)), "html.parser")

            niestandardowa = rozpoznajLekcję(fragment)
            if niestandardowa:
                lekcje.append(niestandardowa)
                continue

            lekcje.extend(sparsujLekcje(fragment, dzień, numer, nazwa, rozwinięciaOddziałów, potrzebniNauczyciele, grupy, przedmiotyDodatkowe, url))

        return lekcje

    if listaOddziałów is None:
        logowanie.warning(
            "Brak listy oddziałów. Zwracanie pustej zawartości."
        )
        return zwróćPustyPlanLekcji()

    if not isinstance(url, str) or not url.startswith(("http://", "https://")):
        logowanie.warning(
            "Nieprawidłowy URL wejściowy. Zwracanie pustej zawartości."
        )
        return zwróćPustyPlanLekcji()

    try:
        potrzebniNauczyciele: set[tuple[str | None, str, int]] = set()
        rozwinięciaOddziałów: set[str] = set()

        etykietaPlanu = zawartośćStrony.select_one(".tytulnapis")
        tabela = zawartośćStrony.select_one("table.tabela")

        nazwa = None
        wygenerowano = None
        data = {
            "obowiazuje": None,
            "wygasa": None
        }
        wyniki = []

        for dane in listaOddziałów:
            rozwinięcie = dane.get("rozwiniecie") if isinstance(dane, dict) else None

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
                .lower()
            )

            if tekst.startswith("obowiązuje"):
                daty = re.findall(r"\d{1,2}[.\-]\d{1,2}[.\-]\d{4}", tekst)

                if daty:
                    data["obowiazuje"] = daty[0]

                if len(daty) >= 2:
                    data["wygasa"] = daty[1]
                elif "-" in tekst:
                    dopasowanie = re.search(r"\d{1,2}[.\-]\d{1,2}[.\-]\d{4}\s*-\s*(.+)", tekst)

                    if dopasowanie:
                        data["wygasa"] = dopasowanie.group(1).strip()

            if tekst.startswith("wygenerowano"):
                wygenerowano = tekst.replace("wygenerowano", "").strip().split()[0]

            if data["obowiazuje"] is not None and wygenerowano is not None:
                break

        if not tabela:
            return zwróćPustyPlanLekcji()

        dniTygodnia = wyodrębnijDniTygodnia(tabela)
        wiersze = tabela.find_all("tr")[1:]
        plan = {dzień: [] for dzień in dniTygodnia}

        for wiersz in wiersze:
            komórki = wiersz.find_all("td")

            if len(komórki) < 7:
                continue

            numer = int(komórki[0].get_text(strip=True))

            for indeks, dzień in enumerate(dniTygodnia):
                td = komórki[indeks + 2]

                godziny = komórki[1].get_text(strip=True).replace(" ", "")
                surowyPoczątek, surowyKoniec = godziny.split("-", 1)

                godzinaPoczątku, minutaPoczątku = surowyPoczątek.split(":", 1)
                godzinaKońca, minutaKońca = surowyKoniec.split(":", 1)

                początek = f"{int(godzinaPoczątku):02d}:{minutaPoczątku}"
                koniec = f"{int(godzinaKońca):02d}:{minutaKońca}"

                lekcje = wyczyśćKomórkę(td, dzień, numer, nazwa, rozwinięciaOddziałów, potrzebniNauczyciele, grupy, przedmiotyDodatkowe, url)
                if not lekcje and not zastępstwa:
                    continue

                plan[dzień].append({
                    "numer": numer,
                    "poczatek": początek,
                    "koniec": koniec,
                    "lekcje": lekcje if lekcje else []
                })

        listaPotrzebnychNauczycieli = list(potrzebniNauczyciele)

        for indeks in range(0, len(listaPotrzebnychNauczycieli), 20):
            paczka = listaPotrzebnychNauczycieli[indeks:indeks + 20]

            wyniki.extend(
                await asyncio.gather(*[
                    uzupełnijNauczyciela(atom, urlSali, dniTygodnia, dzień, numer)
                    for urlSali, dzień, numer in paczka
                ])
            )

        if len(wyniki) != len(listaPotrzebnychNauczycieli):
            logowanie.error(
                f"Wystąpiła niezgodność w liczbie wyników uzupełniania nauczycieli (oczekiwano: {len(listaPotrzebnychNauczycieli)}, lecz otrzymano: {len(wyniki)})."
            )

        słownikNauczycieli: dict[tuple[str, str, int], ElementPlanu] = {}

        for indeks, klucz in enumerate(listaPotrzebnychNauczycieli):
            if indeks >= len(wyniki):
                break

            urlSali, dzieńLekcji, numerLekcji = klucz
            nauczyciel = wyniki[indeks]

            słownikNauczycieli[(urlSali, dzieńLekcji, numerLekcji)] = nauczyciel

        for dzień, wpisy in plan.items():
            for wpis in wpisy:
                numer = wpis["numer"]

                for lekcja in wpis["lekcje"]:
                    if (
                        (lekcja.get("nauczyciel") or {}).get("tekst") is None
                        and (lekcja.get("sala") or {}).get("url") is not None
                    ):
                        klucz = ((lekcja.get("sala") or {}).get("url"), dzień, numer)
                        if klucz in słownikNauczycieli:
                            lekcja["nauczyciel"] = słownikNauczycieli[klucz]

        identyfikator = wyodrębnijIdentyfikator(url)

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
            "zastepstwa": zastępstwa,
            "plan": plan
        }
    except Exception as e:
        logowanie.exception(
            f"Wystąpił błąd podczas przetwarzania HTML planu lekcji ({url}). Więcej informacji: {e}"
        )
        return zwróćPustyPlanLekcji()

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
from datetime import datetime
import re
from typing import Iterable

# Zewnętrzne biblioteki
import aiohttp
from bs4 import (
    BeautifulSoup,
    NavigableString,
    Tag
)

# Wewnętrzne importy
from src.handlers.helpers import (
    posortujNauczycieli,
    wyczyśćTekst as wyczyśćTekstZastępstw
)
from src.handlers.logging import logowanie
from src.handlers.substitutions.helpers import (
    normalizujTekst,
    zwróćNazwyKluczy
)
from src.handlers.substitutions.resolver import uzupełnijZastępstwa
from src.schemas.lists import ElementListy
from src.schemas.substitutions import (
    Zastępstwa,
    Zastępstwo
)

async def wyodrębnijZastępstwa(
    klientAtom: aiohttp.ClientSession,
    zawartośćStrony: BeautifulSoup,
    listaOddziałów: list[ElementListy] | None,
    listaNauczycieli: list[ElementListy] | None,
    wybranyOddział: str | None,
    wybranyNauczyciel: str | None,
    grupy: list[str] | None,
    przedmiotyDodatkowe: dict[str, bool] | None
) -> Zastępstwa:
    """
    Wyodrębnia, przetwarza i filtruje dane zastępstw z pliku strony internetowej.

    Args:
        klientAtom (aiohttp.ClientSession): Aktywna sesja HTTP używana do wykonania zapytania.
        zawartośćStrony (BeautifulSoup): Obiekt BeautifulSoup reprezentujący stronę HTML.
        listaOddziałów (list[ElementListy] | None): Lista wszystkich oddziałów.
        listaNauczycieli (list[ElementListy] | None): Lista wszystkich nauczycieli.
        wybranyOddział (str | None): Oddział przeznaczony do filtracji.
        wybranyNauczyciel (str | None): Nauczyciel przeznaczony do filtracji.
        grupy (list[str] | None): Lista oznaczeń określających grupę przedmiotów.
        przedmiotyDodatkowe (dict[str, bool] | None): Słownik przedmiotów dodatkowych przeznaczonych do filtracji.

    Returns:
        Zastępstwa: Słownik zawierający informacje o zastępstwach.
    """

    def zwróćPusteZastępstwa() -> Zastępstwa:
        """
        Zwraca pustą strukturę zastępstw w standardowym formacie.

        Returns:
            Zastępstwa: Pusta struktura zastępstw.
        """
        return {
            "identyfikator": None,
            "dni": [],
            "informacje": "",
            "skrocone": None,
            "zastepstwa": []
        }

    def sprawdźKlasyKomórki(
        komórka: Tag,
        nazwy: Iterable[str]
    ) -> bool:
        """
        Sprawdza, czy dana komórka HTML zawiera przynajmniej jedną z podanych klas CSS `(np. "st0", "st1")`.

        Args:
            komórka (Tag): Element HTML (np. <td>) do sprawdzenia.
            nazwy (Iterable[str]): Kolekcja nazw klas (lista, zbiór itp.) do dopasowania.

        Returns:
            bool: True, jeśli komórka zawiera którąkolwiek z klas, False w przeciwnym razie.
        """

        klasy = komórka.get("class", [])

        if isinstance(klasy, str):
            klasy = [klasy]

        return any(klasa in nazwy for klasa in klasy)

    def wyczyśćTekst(węzeł: Tag | str | None) -> str:
        """
        Czyści i normalizuje tekst.

        Args:
            węzeł (Tag | str | None): Element strony internetowej do przetworzenia.

        Returns:
            str: Oczyszczony i znormalizowany tekst.
        """
        return wyczyśćTekstZastępstw(węzeł, separator="", rozpakujTagi=True, usuńSuroweNoweLinie=True)

    def wyodrębnijInformacje(
        wiersze: list[Tag],
        nazwaKlasy: str
    ) -> str:
        """
        Wyodrębnia informacje z pierwszej niepustej komórki `<td>` o podanej klasie, przetwarza jej zawartość i zwraca oczyszczony tekst.

        Args:
            wiersze (list[Tag]): Lista wierszy (<tr>) pobranych z obiektu BeautifulSoup.
            nazwaKlasy (str): Nazwa klasy CSS do wyszukania (np. "st0", "st1").

        Returns:
            str: Przetworzony i oczyszczony tekst.
        """

        for wiersz in wiersze:
            for komórka in wiersz.find_all("td"):
                if not sprawdźKlasyKomórki(komórka, {nazwaKlasy}):
                    continue

                surowyTekst = wyczyśćTekst(komórka).strip()
                if not surowyTekst or surowyTekst == "&nbsp;":
                    continue

                link = komórka.find("a")
                if link and link.get("href"):
                    tekstLinku = wyczyśćTekst(link)
                    urlLinku = link.get("href")
                    link.replace_with(NavigableString(f"[{tekstLinku}]({urlLinku})"))

                tekst = wyczyśćTekst(komórka)
                tekst = re.sub(r"[ \t]+", " ", tekst)
                tekst = re.sub(r"\n+\[", " [", tekst)

                return tekst

        return ""

    def dodajUnikalnyElement(
        lista: list[str],
        wartość: str | None
    ) -> None:
        """
        Dodaje element do listy, jeżeli nie jest pusty i nie został wcześniej dodany.

        Args:
            lista (list[str]): Lista docelowa.
            wartość (str | None): Wartość do dodania.
        """

        if wartość is not None and wartość not in lista:
            lista.append(wartość)

    def wyodrębnijDni(tekst: str | None) -> list[str]:
        """
        Wyodrębnia nazwy dni tygodnia z tekstu zastępstw.

        Args:
            tekst (str | None): Tekst zawierający informacje dodatkowe zastępstw.

        Returns:
            list[str]: Nazwy dni tygodnia w kolejności wystąpienia.
        """

        if not tekst:
            return []

        listaDniTygodnia: list[str] = []
        dniTygodnia = {
            "poniedziałek": "Poniedziałek",
            "poniedzialek": "Poniedziałek",
            "wtorek": "Wtorek",
            "środa": "Środa",
            "sroda": "Środa",
            "czwartek": "Czwartek",
            "piątek": "Piątek",
            "piatek": "Piątek",
            "sobota": "Sobota",
            "niedziela": "Niedziela"
        }
        mapaDniTygodnia = {
            0: "Poniedziałek",
            1: "Wtorek",
            2: "Środa",
            3: "Czwartek",
            4: "Piątek",
            5: "Sobota",
            6: "Niedziela"
        }

        tekst = tekst.strip().split("\n")[0].lower().replace("\xa0", " ")
        wzórDni = "|".join(re.escape(dzień) for dzień in dniTygodnia)

        for dopasowanie in re.finditer(r"\b(\d{1,2}\.\d{1,2}\.\d{4})\b", tekst):
            try:
                data = datetime.strptime(dopasowanie.group(1), "%d.%m.%Y")
            except ValueError:
                continue

            dodajUnikalnyElement(listaDniTygodnia, mapaDniTygodnia.get(data.weekday()))

        for dopasowanie in re.finditer(rf"\b({wzórDni})\b", tekst):
            dodajUnikalnyElement(listaDniTygodnia, dniTygodnia[dopasowanie.group(1)])

        return listaDniTygodnia

    def wyodrębnijDzień(tekst: str | None) -> str | None:
        """
        Wyodrębnia pierwszą nazwę dnia tygodnia z tekstu zastępstw.

        Args:
            tekst (str | None): Tekst zawierający informacje dodatkowe zastępstw.

        Returns:
            str | None: Nazwa dnia tygodnia, jeżeli udało się ją ustalić.
        """

        dni = wyodrębnijDni(tekst)
        return dni[0] if dni else None

    def sprawdźSkrócone(tekst: str) -> bool:
        """
        Sprawdza, czy przekazany tekst wskazuje na skrócone lekcje.

        Args:
            tekst (str): Tekst informacji dodatkowych zastępstw.

        Returns:
            bool: True, jeśli tekst sugeruje skrócone lekcje, False w przeciwnym razie.
        """

        tekst = tekst.lower()
        return "rzs.pdf" in tekst or "skrócon" in tekst

    def sprawdźPrzydatne(
        wartość: str | None,
        etykieta: str
    ) -> bool:
        """
        Sprawdza, czy dana wartość w wierszu tabeli jest przydatna, w celu jej wyświetlenia.

        Args:
            wartość (str | None): Tekst zawarty w polu wiersza (np. lekcja, opis, zastępca, uwagi).
            etykieta (str): Nagłówek odpowiadający wartości (np. "Lekcja", "Opis", "Zastępca", "Uwagi").

        Returns:
            bool: True, jeśli wartość jest niepusta i różna od etykiety, False w przeciwnym razie.
        """

        if not isinstance(wartość, str):
            return False

        wartość = wartość.strip()
        return bool(wartość and wartość.lower() != etykieta.lower())

    def sprawdźOddział(
        komórkiWiersza: list[str],
        wybranyOddział: str | None
    ) -> bool:
        """
        Sprawdza, czy wiersz HTML (lista wartości z wiersza tabeli) odpowiada wybranemu oddziałowi.

        Args:
            komórkiWiersza (list[str]): Lista wartości z wiersza tabeli (np. lekcja, opis, zastępca, uwagi).
            wybranyOddział (str): Wybrany oddział przeznaczony do dopasowania.

        Returns:
            bool: True, jeśli wiersz pasuje do wybranego oddziału, False w przeciwnym razie.
        """

        komórki = komórkiWiersza[:]

        if not wybranyOddział:
            return False

        if len(komórki) > 1 and komórki[1]:
            komórki[1] = komórki[1].split("-", 1)[0]

        tekst = " ".join(komórka for komórka in komórki[:-1])
        tekst = normalizujTekst(tekst)
        tekst = re.sub(r"[\(\)]", " ", tekst)
        tekst = re.sub(r"\s+", " ", tekst)

        znormalizowanyOddział = normalizujTekst(wybranyOddział)
        części = znormalizowanyOddział.split()
        wzór = r"\b" + r"\s*".join(map(re.escape, części)) + r"\b"

        if re.search(wzór, tekst):
            return True

        return False

    def wyodrębnijNauczycieli(
        nazwaNagłówka: str | None,
        komórkaZastępcy: str | None
    ) -> set[str]:
        """
        Wyodrębnia nazwiska nauczycieli z nagłówka i treści komórki zastępcy.

        Args:
            nazwaNagłówka (str | None): Tekst nagłówka zawierający nazwisko nauczyciela.
            komórkaZastępcy (str | None): Tekst komórki z informacją o zastępcy.

        Returns:
            set[str]: Zbiór unikalnych nazwisk nauczycieli.
        """

        wyodrębnieniNauczyciele = set()

        if nazwaNagłówka and nazwaNagłówka.strip():
            wyodrębnieniNauczyciele.add(nazwaNagłówka.strip())

        if komórkaZastępcy and komórkaZastępcy.strip():
            części = re.split(r"[,\n;/&]| i | I ", komórkaZastępcy)

            for nauczyciel in części:
                nauczyciel = nauczyciel.strip()

                if nauczyciel and nauczyciel != "&nbsp;":
                    wyodrębnieniNauczyciele.add(nauczyciel)

        return wyodrębnieniNauczyciele

    if listaOddziałów is None or listaNauczycieli is None:
        logowanie.warning(
            "Brak listy oddziałów lub listy nauczycieli. Zwracanie pustej zawartości."
        )
        return zwróćPusteZastępstwa()

    def sprawdźNauczyciela(
        wyodrębnieniNauczyciele: set[str],
        wybranyNauczyciel: str | None
    ) -> bool:
        """
        Sprawdza, czy którykolwiek z wyodrębnionych nauczycieli zgadza się z wybranym nauczycielem.

        Args:
            wyodrębnieniNauczyciele (set[str]): Zbiór nazwisk nauczycieli wyodrębnionych z wiersza zastępstwa.
            wybranyNauczyciel (str | None): Nauczyciel przeznaczony do dopasowania.

        Returns:
            bool: True, jeśli jakikolwiek wyodrębniony nauczyciel pasuje do wybranego, False w przeciwnym razie.
        """

        zbiórKluczy = set()
        kluczeWybranychNauczycieli = set()

        if not wybranyNauczyciel:
            return False

        for dopasowanie in wyodrębnieniNauczyciele:
            zbiórKluczy |= zwróćNazwyKluczy(dopasowanie)

        kluczeWybranychNauczycieli |= zwróćNazwyKluczy(wybranyNauczyciel)

        return bool(zbiórKluczy & kluczeWybranychNauczycieli)

    def sprawdźIstnienieZastępstw(wiersze: list[Tag]) -> bool:
        """
        Sprawdza, czy w tabeli HTML istnieje przynajmniej jeden wiersz z realnym zastępstwem.

        Args:
            wiersze (list[Tag]): Lista wierszy (<tr>) pobranych z obiektu BeautifulSoup.

        Returns:
            bool: True, jeśli przynajmniej jeden wiersz zawiera dane zastępstwo, False w przeciwnym razie.
        """

        nagłówki = {"lekcja", "opis", "zastępca", "uwagi"}

        for wiersz in wiersze:
            komórki = wiersz.find_all("td")

            if len(komórki) >= 4:
                teksty = [wyczyśćTekst(td).lower() for td in komórki[:4]]
                jestPuste = all(tekst == "" or tekst == "&nbsp;" for tekst in teksty)
                jestNagłówek = set(tekst.strip().lower() for tekst in teksty) <= nagłówki

                if not jestPuste and not jestNagłówek:
                    return True

        return False

    try:
        identyfikator: str | None = None
        wiersze = zawartośćStrony.find_all("tr")
        wpisyZastępstw: list[Zastępstwo] = []
        dni: list[str] = []

        mapaOddziałów: dict[str, ElementListy] = {
            element["nazwa"]: element
            for element in (listaOddziałów or [])
            if element.get("nazwa")
        }

        mapaNauczycieli: dict[str, ElementListy] = {
            element["nazwa"]: element
            for element in (listaNauczycieli or [])
            if element.get("nazwa")
        }

        if wybranyOddział:
            dane = mapaOddziałów.get(wybranyOddział)
            identyfikator = dane.get("identyfikator") if dane else None

        elif wybranyNauczyciel:
            dane = mapaNauczycieli.get(wybranyNauczyciel)
            identyfikator = dane.get("identyfikator") if dane else None

        informacjeDodatkowe = wyodrębnijInformacje(wiersze, "st0")
        for dzieńInformacji in wyodrębnijDni(informacjeDodatkowe):
            dodajUnikalnyElement(dni, dzieńInformacji)

        domyślnyDzień = dni[0] if dni else None
        skrócone = sprawdźSkrócone(informacjeDodatkowe)

        indeksST0: int | None = None
        for indeksWiersza, wiersz in enumerate(wiersze):
            komórki = wiersz.find_all("td")

            if komórki and sprawdźKlasyKomórki(komórki[0], {"st0"}):
                indeksST0 = indeksWiersza

        aktualnyNauczyciel: str | None = None
        aktualnyDzień: str | None = domyślnyDzień

        for indeks, wiersz in enumerate(wiersze):
            if indeksST0 is not None and indeks <= indeksST0:
                continue

            komórki = wiersz.find_all("td")
            if len(komórki) == 1:
                nagłówek = wyczyśćTekst(komórki[0])
                aktualnyDzień = wyodrębnijDzień(nagłówek) or domyślnyDzień
                dodajUnikalnyElement(dni, aktualnyDzień)
                aktualnyNauczyciel = nagłówek.split("/", 1)[0].strip() or nagłówek
                continue

            if len(komórki) >= 4:
                teksty = [wyczyśćTekst(komórka) for komórka in komórki[:4]]
                lekcja, opis, zastępca, uwagi = teksty
                pola = [lekcja, opis, zastępca, uwagi]
                etykiety = ["Lekcja", "Opis", "Zastępca", "Uwagi"]

                if not any(sprawdźPrzydatne(wartość, etykieta) for wartość, etykieta in zip(pola, etykiety)):
                    continue

                komórkiWiersza = [lekcja, opis, zastępca, uwagi]
                dopasowaneDoOddziału = sprawdźOddział(
                    komórkiWiersza,
                    wybranyOddział
                )
                wyodrębnieniNauczyciele = wyodrębnijNauczycieli(aktualnyNauczyciel, zastępca)
                dopasowaneDoNauczyciela = sprawdźNauczyciela(
                    wyodrębnieniNauczyciele,
                    wybranyNauczyciel
                )
                zidentyfikowane: bool = True
                pełnyTekst = " ".join(komórkiWiersza)

                if mapaOddziałów:
                    znalezionoOddziały = any(
                        re.search(
                            r"\b" + re.escape(normalizujTekst(oddział)) + r"\b",
                            normalizujTekst(pełnyTekst)
                        )
                        for oddział in mapaOddziałów.keys()
                    )
                    zidentyfikowane = znalezionoOddziały
                else:
                    if not re.search(r"\d", pełnyTekst):
                        zidentyfikowane = False

                if (
                    (not wybranyOddział and not wybranyNauczyciel)
                    or (wybranyOddział and (dopasowaneDoOddziału or not zidentyfikowane))
                    or (wybranyNauczyciel and dopasowaneDoNauczyciela)
                ):
                    dzieńWpisu = aktualnyDzień or domyślnyDzień
                    dodajUnikalnyElement(dni, dzieńWpisu)
                    wpisyZastępstw.append({
                        "zidentyfikowane": zidentyfikowane,
                        "dzien": dzieńWpisu,
                        "grupa": None,
                        "nauczyciel": aktualnyNauczyciel or ", ".join(wyodrębnieniNauczyciele) or "Nieznany",
                        "lekcja": int(lekcja) if sprawdźPrzydatne(lekcja, "Lekcja") and lekcja.isdigit() else None,
                        "opis": opis if sprawdźPrzydatne(opis, "Opis") else None,
                        "zastepca": zastępca if sprawdźPrzydatne(zastępca, "Zastępca") else None,
                        "uwagi": uwagi if sprawdźPrzydatne(uwagi, "Uwagi") else None
                    })

        if not informacjeDodatkowe and not sprawdźIstnienieZastępstw(wiersze):
            informacjeDodatkowe = wyodrębnijInformacje(wiersze, "st1")
            for dzieńInformacji in wyodrębnijDni(informacjeDodatkowe):
                dodajUnikalnyElement(dni, dzieńInformacji)

            skrócone = sprawdźSkrócone(informacjeDodatkowe)

        if wybranyOddział and wpisyZastępstw and identyfikator:
            uzupełnioneWpisy: list[Zastępstwo] = []
            for dzień in dni:
                wpisyDnia = [
                    wpis
                    for wpis in wpisyZastępstw
                    if wpis.get("dzien") == dzień
                ]

                if wpisyDnia:
                    uzupełnioneWpisy.extend(
                        await uzupełnijZastępstwa(klientAtom, wpisyDnia, identyfikator, dzień, listaOddziałów, grupy, przedmiotyDodatkowe)
                    )

            uzupełnioneWpisy.extend(
                wpis
                for wpis in wpisyZastępstw
                if wpis.get("dzien") not in dni
            )
            wpisyZastępstw = uzupełnioneWpisy

        indeksyDni = {
            dzień: indeks
            for indeks, dzień in enumerate(dni)
        }
        wpisyZastępstw.sort(
            key=lambda wpis: (
                indeksyDni.get(wpis.get("dzien"), len(indeksyDni)),
                posortujNauczycieli(wpis),
            )
        )

        return {
            "identyfikator": identyfikator,
            "dni": dni,
            "informacje": informacjeDodatkowe,
            "skrocone": skrócone,
            "zastepstwa": wpisyZastępstw
        }
    except Exception as e:
        logowanie.exception(
            f"Wystąpił błąd podczas przetwarzania HTML zastępstw. Więcej informacji: {e}"
        )
        return zwróćPusteZastępstwa()

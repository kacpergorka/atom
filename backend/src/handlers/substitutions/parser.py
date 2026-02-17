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
from typing import Iterable
from datetime import datetime

# Zewnętrzne biblioteki
import aiohttp
from bs4 import (
    BeautifulSoup,
    NavigableString,
    Tag
)

# Wewnętrzne importy
from src.classes.types import (
    ListaNauczycieli,
    ListaOddziałów,
    Zastępstwa,
    Zastępstwo
)
from src.handlers.substitutions.helpers import (
    normalizujTekst,
    zwróćNazwyKluczy
)
from src.handlers.substitutions.resolver import uzupełnijZastępstwa
from src.handlers.logging import logowanie

async def wyodrębnijZastępstwa(
    atom: aiohttp.ClientSession,
    zawartośćStrony: BeautifulSoup | None,
    listaOddziałów: ListaOddziałów | None,
    listaNauczycieli: ListaNauczycieli | None,
    wybranyOddział: str | None,
    wybranyNauczyciel: str | None,
    grupy: list[str] | None,
    przedmiotyDodatkowe: dict[str, bool] | None
) -> Zastępstwa:
    """
    Wyodrębnia, przetwarza i filtruje dane zastępstw z pliku strony internetowej.

    Args:
        atom (aiohttp.ClientSession): Aktywna sesja HTTP używana do wykonania zapytania.
        zawartośćStrony (BeautifulSoup | None): Obiekt BeautifulSoup reprezentujący stronę HTML.
        listaOddziałów (ListaOddziałów | None): Słownik wszystkich oddziałów.
        listaNauczycieli (ListaNauczycieli | None): Słownik wszystkich nauczycieli.
        wybranyOddział (str | None): Oddział przeznaczony do filtracji.
        wybranyNauczyciel (str | None): Nauczyciel przeznaczony do filtracji.
        grupy (list[str] | None): Lista oznaczeń określających grupę przedmiotów.
        przedmiotyDodatkowe (dict[str, bool] | None): Słownik przedmiotów dodatkowych przeznaczonych do filtracji.

    Returns:
        Zastępstwa: Słownik zawierający informacje o zastępstwach.
    """

    def wyczyśćTekst(węzeł: Tag | str | None) -> str:
        """
        Czyści i normalizuje zawartość tekstu.

        Args:
            węzeł (Tag | str | None): Element strony internetowej do przetworzenia.

        Returns:
            str: Oczyszczony i znormalizowany tekst.
        """

        if not węzeł:
            return ""

        tymczasowy = BeautifulSoup(str(węzeł), "html.parser")

        try:
            for br in tymczasowy.find_all("br"):
                br.replace_with(NavigableString("\n"))

            for tag in tymczasowy.find_all(True):
                tag.unwrap()
        except Exception as e:
            logowanie.exception(
                f"Wystąpił błąd podczas rozpakowywania tagów. Więcej informacji: {e}"
            )

        tekst = tymczasowy.get_text(separator="")
        tekst = tekst.replace("\r\n", "\n").replace("\r", "\n")
        tekst = tekst.replace("\xa0", " ")
        tekst = re.sub(r"[ \t]*\n[ \t]*", "\n", tekst)
        tekst = re.sub(r"[ \t]{2,}", " ", tekst)
        tekst = re.sub(r"\n\n", "\n", tekst)
        tekst = re.sub(r"\n{3,}", "\n\n", tekst)

        return tekst.strip("\n ")

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

    def wyodrębnijDzień(tekst: str | None) -> str | None:
        """
        Wyodrębnia nazwę dnia tygodnia na podstawie informacji dodatkowych zastępstw.

        Args:
            tekst (str | None): Tekst zawierający informacje dodatkowe zastępstw.

        Returns:
            str | None: Nazwa dnia tygodnia, jeżeli udało się ją ustalić.
        """

        if not tekst:
            return None

        linia = tekst.splitlines()[0].lower() if tekst.splitlines() else ""
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

        for klucz, nazwa in dniTygodnia.items():
            if klucz in linia:
                return nazwa

        dopasowanie = re.search(r"(\d{2}\.\d{2}\.\d{4})", linia)
        if dopasowanie:
            try:
                data = datetime.strptime(dopasowanie.group(1), "%d.%m.%Y")
                mapaDniTygodnia = {
                    0: "Poniedziałek",
                    1: "Wtorek",
                    2: "Środa",
                    3: "Czwartek",
                    4: "Piątek",
                    5: "Sobota",
                    6: "Niedziela"
                }
                return mapaDniTygodnia.get(data.weekday())
            except ValueError:
                return None

        return None

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

    if zawartośćStrony is None:
        logowanie.warning(
            "Brak treści pobranej ze strony. Zwracanie pustej zawartości."
        )
        return {
            "identyfikator": None,
            "dzien": None,
            "informacje": "",
            "zastepstwa": []
        }

    if not isinstance(listaOddziałów, dict) or not isinstance(listaNauczycieli, dict):
        logowanie.warning(
            "Brak listy oddziałów lub listy nauczycieli. Zwracanie pustej zawartości."
        )
        return {
            "identyfikator": None,
            "dzien": None,
            "informacje": "",
            "zastepstwa": []
        }

    try:
        identyfikator: str | None = None
        wiersze = zawartośćStrony.find_all("tr")
        wpisyZastępstw: list[Zastępstwo] = []

        if wybranyOddział and listaOddziałów:
            dane = listaOddziałów.get(wybranyOddział)
            identyfikator = dane.get("identyfikator") if dane else None

        elif wybranyNauczyciel and listaNauczycieli:
            dane = listaNauczycieli.get(wybranyNauczyciel)
            identyfikator = dane.get("identyfikator") if dane else None

        informacjeDodatkowe = wyodrębnijInformacje(wiersze, "st0")
        dzień = wyodrębnijDzień(informacjeDodatkowe) if informacjeDodatkowe else None

        indeksST0: int | None = None
        for indeksWiersza, wiersz in enumerate(wiersze):
            komórki = wiersz.find_all("td")

            if komórki and sprawdźKlasyKomórki(komórki[0], {"st0"}):
                indeksST0 = indeksWiersza

        aktualnyNauczyciel: str | None = None
        for indeks, wiersz in enumerate(wiersze):
            if indeksST0 is not None and indeks <= indeksST0:
                continue

            komórki = wiersz.find_all("td")
            if len(komórki) == 1:
                aktualnyNauczyciel = wyczyśćTekst(komórki[0])
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

                if listaOddziałów:
                    znalezionoOddziały = any(
                        re.search(
                            r"\b" + re.escape(normalizujTekst(oddział)) + r"\b",
                            normalizujTekst(pełnyTekst)
                        )
                        for oddział in listaOddziałów.keys()
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
                    nazwaNauczyciela = aktualnyNauczyciel or ", ".join(wyodrębnieniNauczyciele) or "Nieznany"
                    wpisyZastępstw.append({
                        "zidentyfikowane": zidentyfikowane,
                        "nauczyciel": nazwaNauczyciela,
                        "lekcja": int(lekcja) if sprawdźPrzydatne(lekcja, "Lekcja") else None,
                        "opis": (
                            opis.split("-", 1)[1].strip() if sprawdźPrzydatne(opis, "Opis") and "-" in opis and (wybranyOddział or wybranyNauczyciel)
                            else opis if sprawdźPrzydatne(opis, "Opis") else None
                        ),
                        "zastepca": zastępca if sprawdźPrzydatne(zastępca, "Zastępca") else None,
                        "uwagi": uwagi if sprawdźPrzydatne(uwagi, "Uwagi") else None
                    })

        if not informacjeDodatkowe and not sprawdźIstnienieZastępstw(wiersze):
            informacjeDodatkowe = wyodrębnijInformacje(wiersze, "st1")
            dzień = None

        if wybranyOddział and wpisyZastępstw and identyfikator and dzień:
            wpisyZastępstw = await uzupełnijZastępstwa(atom, wpisyZastępstw, identyfikator, dzień, listaOddziałów, grupy, przedmiotyDodatkowe)

        return {
            "identyfikator": identyfikator,
            "dzien": dzień,
            "informacje": informacjeDodatkowe,
            "zastepstwa": wpisyZastępstw
        }
    except Exception as e:
        logowanie.exception(
            f"Wystąpił błąd podczas przetwarzania HTML zastępstw. Więcej informacji: {e}"
        )
        return {
            "identyfikator": None,
            "dzien": None,
            "informacje": "",
            "zastepstwa": []
        }

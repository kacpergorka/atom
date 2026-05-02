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
import re
from urllib.parse import urljoin

# Zewnętrzne biblioteki
from bs4 import (
    BeautifulSoup,
    Tag
)

# Wewnętrzne importy
from src.classes.types.announcements import (
    Ogłoszenia,
    Ogłoszenie
)
from src.handlers.helpers import wyczyśćTekst
from src.handlers.logging import logowanie

def wyodrębnijOgłoszenia(
    zawartośćStrony: BeautifulSoup,
    url: str
) -> Ogłoszenia:
    """
    Parsuje ogłoszenia z pliku strony internetowej.

    Args:
        zawartośćStrony: Obiekt BeautifulSoup reprezentujący stronę HTML.
        url: Adres strony internetowej listy aktualności użyty do pobrania jej zawartości.

    Returns:
        Ogłoszenia: Słownik zawierający listę ogłoszeń z paginacją.
    """

    def zwróćPusteOgłoszenia() -> Ogłoszenia:
        """
        Zwraca pustą strukturę ogłoszeń w standardowym formacie.

        Returns:
            Zastępstwa: Pusta struktura ogłoszeń.
        """
        return {
            "aktualnaStrona": 1,
            "ostatniaStrona": 1,
            "poprzedniaStrona": None,
            "nastepnaStrona": None,
            "ogloszenia": []
        }

    def zbudujPełnyUrl(
        bazowyUrl: str,
        url: str | None
    ) -> str | None:
        """
        Buduje pełny adres strony internetowej na podstawie bazowego adresu i względnej ścieżki.

        Args:
            bazowyUrl: Bazowy adres strony internetowej.
            url: Względny lub absolutny adres strony internetowej.

        Returns:
            str | None: Pełny URL lub None, jeśli brak wejściowego URL.
        """
        if not url:
            return None

        return urljoin(bazowyUrl, url.strip())

    def znajdźLinkOgłoszenia(wiersz: Tag) -> Tag | None:
        """
        Znajduje link prowadzący do szczegółów ogłoszenia w wierszu.

        Args:
            wiersz: Element HTML reprezentujący ogłoszenie.

        Returns:
            Tag | None: Link prowadzący do szczegółów ogłoszenia w wierszu albo `None`, jeśli nie uda się znaleść linku.
        """
        wzórLinkuOgłoszenia = re.compile(r"-w\d+,\d+,\d+\.html(?:$|\?)")
        przycisk = wiersz.find("a", class_=lambda klasa: klasa and "btn" in klasa)

        if isinstance(przycisk, Tag) and wzórLinkuOgłoszenia.search(przycisk.get("href", "")):
            return przycisk

        for link in wiersz.find_all("a", href=True):
            if wzórLinkuOgłoszenia.search(link.get("href", "")):
                return link

        return None

    def wyodrębnijIdentyfikator(url: str | None) -> str:
        """
        Wyodrębnia identyfikator ogłoszenia z URL.

        Args:
            url: Adres strony internetowej ogłoszenia.

        Returns:
            str: Wyodrębniony identyfikator.
        """
        wzórIdentyfikatora = re.compile(r"w\d+,\d+,(\d+)\.html(?:$|\?)")

        if not url:
            return ""

        dopasowanie = wzórIdentyfikatora.search(url)
        return dopasowanie.group(1) if dopasowanie else ""

    def wyodrębnijPaginację(
        zawartośćStrony: BeautifulSoup,
        url: str
    ) -> tuple[int, int, str | None, str | None]:
        """
        Wyodrębnia informacje o paginacji ze strony internetowej.

        Args:
            zawartośćStrony: Obiekt BeautifulSoup reprezentujący stronę HTML.
            url: Adres strony internetowej.

        Returns:
            tuple[int, int, str | None, str | None]: (aktualnaStrona, ostatniaStrona, poprzedniaStrona, następnaStrona)
        """
        paginacja = zawartośćStrony.select_one(".pagination")
        if not paginacja:
            return 1, 1, None, None

        aktywna = wyczyśćTekst(paginacja.select_one(".page-item.active .page-link"))
        aktualnaStrona = int(aktywna) if aktywna.isdigit() else 1
        ostatniaStrona = aktualnaStrona
        poprzedniaStrona: str | None = None
        następnaStrona: str | None = None

        for element in paginacja.select(".page-item"):
            link = element.find("a", href=True)
            tekst = wyczyśćTekst(link or element)

            if tekst.isdigit():
                ostatniaStrona = max(ostatniaStrona or 0, int(tekst))

            if "disabled" in element.get("class", []):
                continue

            if link and tekst == "«":
                poprzedniaStrona = zbudujPełnyUrl(url, link.get("href"))
            elif link and tekst == "»":
                następnaStrona = zbudujPełnyUrl(url, link.get("href"))

        return aktualnaStrona, ostatniaStrona, poprzedniaStrona, następnaStrona

    try:
        kontener = zawartośćStrony.select_one(".main-content")
        if not isinstance(kontener, Tag):
            return zwróćPusteOgłoszenia()

        ogłoszenia: list[Ogłoszenie] = []

        for wiersz in kontener.find_all("div", class_="row", recursive=False):
            if not isinstance(wiersz, Tag):
                continue

            link = znajdźLinkOgłoszenia(wiersz)
            nagłówek = wiersz.find(["h1", "h2", "h3", "h4"])

            if not link or not isinstance(nagłówek, Tag):
                continue

            urlOgłoszenia = zbudujPełnyUrl(url, link.get("href"))
            tytuł = wyczyśćTekst(nagłówek)

            if not urlOgłoszenia or not tytuł:
                continue

            obrazek = wiersz.find("img", src=True)
            obraz = zbudujPełnyUrl(url, obrazek.get("src")) if isinstance(obrazek, Tag) else None
            identyfikator = wyodrębnijIdentyfikator(urlOgłoszenia)

            if not identyfikator:
                continue

            ogłoszenia.append({
                "identyfikator": identyfikator,
                "tytul": tytuł,
                "stopka": wyczyśćTekst(wiersz.find("p")) or None,
                "url": urlOgłoszenia,
                "obraz": obraz
            })

        aktualnaStrona, ostatniaStrona, poprzedniaStrona, następnaStrona = wyodrębnijPaginację(zawartośćStrony, url)

        return {
            "aktualnaStrona": aktualnaStrona,
            "ostatniaStrona": ostatniaStrona,
            "poprzedniaStrona": poprzedniaStrona,
            "nastepnaStrona": następnaStrona,
            "ogloszenia": ogłoszenia
        }
    except Exception as e:
        logowanie.exception(
            f"Wystąpił błąd podczas przetwarzania HTML ogłoszeń. Więcej informacji: {e}"
        )
        return zwróćPusteOgłoszenia()

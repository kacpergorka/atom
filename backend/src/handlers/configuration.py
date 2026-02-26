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
from datetime import datetime
import json
from pathlib import Path
from typing import Any

# Wewnętrzne importy
from src.classes.types import Konfiguracja
from src.handlers.logging import logowanie

def wczytajKonfiguracje() -> Konfiguracja:
    """
    Wczytuje, tworzy, zapisuje i uporządkowuje plik konfiguracyjny zapisany w formacie `JSON`.

    Returns:
        Konfiguracja: Słownik zawartości pliku konfiguracyjnego.
    """

    def uporządkuj(
        dane: dict[str, Any],
        wzorzec: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Uporządkowuje i uzupełnia słownik `dane` według kolejności i wartości kluczy w `wzorzec`, zachowując wszystkie dodatkowe klucze na końcu.

        Args:
            dane (dict[str, Any]): Słownik do uporządkowania.
            wzorzec (dict[str, Any]): Słownik określający domyślną kolejność kluczy.

        Returns:
            dict[str, Any]: Nowy słownik z uporządkowanymi kluczami.

        Raises:
            ValueError: Gdy struktura `dane` jest niezgodna z `wzorzec`.
        """

        wynik: dict[str, Any] = {}

        for klucz, wartośćWzorca in wzorzec.items():
            if klucz not in dane:
                wynik[klucz] = wartośćWzorca
                continue

            wartość = dane[klucz]

            if isinstance(wartośćWzorca, dict):
                if isinstance(wartość, dict):
                    wynik[klucz] = uporządkuj(wartość, wartośćWzorca)
                else:
                    raise ValueError(
                        f"Wystąpił konflikt typów w konfiguracji. W kluczu ({klucz}) oczekiwano obiektu, lecz otrzymano {type(wartość).__name__}."
                    )
            else:
                if isinstance(wartość, dict):
                    raise ValueError(
                        f"Wystąpił konflikt typów w konfiguracji. W kluczu ({klucz}) oczekiwano typu prostego, lecz otrzymano obiekt."
                    )
                wynik[klucz] = wartość

        for klucz, wartość in dane.items():
            if klucz not in wynik:
                wynik[klucz] = wartość

        return wynik

    def zapisz(dane: Konfiguracja) -> None:
        """
        Uporządkowuje i zapisuje dane w pliku konfiguracyjnym o formacie `JSON`

        Args:
            dane (Konfiguracja): Słownik danych przeznaczonych do zapisania w pliku konfiguracyjnym.
        """

        dane = uporządkuj(dane, domyślne)
        ścieżka.write_text(
            json.dumps(dane, ensure_ascii=False, indent=4),
            encoding="utf-8"
        )

    domyślne = {
        "wersja": "0.2.2-custom",
        "plany": {
            "url": "https://plan.zse.bydgoszcz.pl/plany/",
            "kodowanie": "utf-8"
        },
        "lista": {
            "url": "https://plan.zse.bydgoszcz.pl/lista.html",
            "kodowanie": "utf-8"
        },
        "zastepstwa": {
            "url": "https://zastepstwa.zse.bydgoszcz.pl",
            "kodowanie": "iso-8859-2"
        },
        "grupy": [
            "1/3", "2/3", "3/3", "1/2", "2/2", "1/1", "j1", "j2"
        ],
        "skrocone": {
            "0": "7:05-7:35",
            "1": "7:40-8:10",
            "2": "8:15-8:45",
            "3": "8:50-9:20",
            "4": "9:30-10:00",
            "5": "10:05-10:35",
            "6": "10:40-11:10",
            "7": "11:15-11:45",
            "8": "11:50-12:20",
            "9": "12:30-13:00",
            "10": "13:05-13:35",
            "11": "13:40-14:10",
            "12": "14:15-14:45",
            "13": "14:50-15:20",
            "14": "15:25-15:55"
        }
    }

    ścieżka = Path(__file__).resolve().parents[1] / "config.json"

    if not ścieżka.exists():
        zapisz(domyślne)
        logowanie.info(
            "Utworzono plik konfiguracyjny z domyślną zawartością. Uzupełnij brakujące i/lub skoryguj domyślnie uzupełnione dane."
        )
        return domyślne

    try:
        dane = json.loads(ścieżka.read_text(encoding="utf-8"))
        dane = uporządkuj(dane, domyślne)

        if dane.get("wersja", "") != domyślne["wersja"]:
            logowanie.warning(
                f"Aktualizuję wersję API z {dane.get('wersja', 'Brak danych')} na {domyślne['wersja']}."
            )
            dane["wersja"] = domyślne["wersja"]

        zapisz(dane)
        return dane
    except Exception as e:
        logowanie.exception(
            f"Wystąpił błąd podczas wczytywania pliku konfiguracyjnego. Więcej informacji: {e}"
        )
        if ścieżka.exists():
            czas = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
            kopia = ścieżka.with_name(f"config-{czas}.json.old")
            ścieżka.replace(kopia)
            logowanie.warning(
                f"Zachowano plik konfiguracyjny z uszkodzoną/niepoprawną zawartością jako {kopia}."
            )

        zapisz(domyślne)
        logowanie.info(
            "Utworzono plik konfiguracyjny z domyślną zawartością. Uzupełnij brakujące i/lub skoryguj domyślnie uzupełnione dane."
        )
        return domyślne

konfiguracja: Konfiguracja = wczytajKonfiguracje()

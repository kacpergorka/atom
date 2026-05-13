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
import hashlib

# Wewnętrzne importy
from src.api.endpoints.atom.timetables.schemas import (
    AtomowaLekcja,
    AtomowyPlanLekcji
)
from src.schemas.timetables import (
    ElementPlanu as SurowyElementPlanu,
    PlanLekcji as SurowyPlanLekcji
)

def mapujPlanLekcji(dane: SurowyPlanLekcji) -> AtomowyPlanLekcji:
    """
    Mapuje surową strukturę planu lekcji do modelu API Atomu.

    Args:
        dane (SurowyPlanLekcji): Surowy plan lekcji zwrócony przez parser lub assembler.

    Returns:
        AtomowyPlanLekcji: Spłaszczony model planu lekcji.
    """

    def wyodrębnijTekst(element: SurowyElementPlanu | None) -> str | None:
        """
        Zwraca wartość pola `tekst` z przekazanego elementu planu.

        Args:
            element (SurowyElementPlanu | None): Element planu lub `None`.

        Returns:
            str | None: Tekst elementu albo `None`, jeśli element nie istnieje.
        """

        if element is None:
            return None

        return element.get("tekst")

    def połączOddziały(oddziały: list[SurowyElementPlanu] | None) -> str | None:
        """
        Łączy nazwy oddziałów w pojedynczy ciąg znaków oddzielony przecinkami.

        Args:
            oddziały (list[SurowyElementPlanu] | None): Lista elementów opisujących oddziały.

        Returns:
            str | None: Połączona lista nazw oddziałów albo `None`, jeśli brak danych.
        """

        if not oddziały:
            return None

        przetworzoneOddziały = []

        for oddział in oddziały:
            tekst = oddział.get("tekst")

            if not tekst:
                continue

            oczyszczonyTekst = tekst.strip().rstrip(",")
            if oczyszczonyTekst:
                przetworzoneOddziały.append(oczyszczonyTekst)

        return ", ".join(przetworzoneOddziały) or None

    def wygenerujIdentyfikator(
        dzień: str,
        numer: int,
        przedmiot: str,
        nauczyciel: str | None,
        sala: str | None,
        oddzialy: str | None,
        zastepca: str | None,
        opis: str | None,
        uwagi: str | None,
        początek: str,
        koniec: str
    ) -> str:
        """
        Generuje stabilny identyfikator lekcji na podstawie jej cech opisowych.

        Args:
            dzień (str): Dzień tygodnia, w którym odbywa się lekcja.
            numer (int): Numer lekcji w planie dnia.
            przedmiot (str): Nazwa przedmiotu.
            nauczyciel (str | None): Nazwa nauczyciela.
            sala (str | None): Nazwa sali.
            oddzialy (str | None): Połączona lista nazw oddziałów.
            zastepca (str | None): Nazwa nauczyciela prowadzącego zastępstwo.
            opis (str | None): Opis zastępstwa.
            uwagi (str | None): Dodatkowe uwagi do zastępstwa.
            początek (str): Godzina rozpoczęcia lekcji.
            koniec (str): Godzina zakończenia lekcji.

        Returns:
            str: Skrót SHA-256 identyfikujący lekcję.
        """

        surowyIdentyfikator = (
            f"{dzień}|{numer}|{początek}|{koniec}|{przedmiot}|{nauczyciel or 'brak'}|{sala or 'brak'}|{oddzialy or 'brak'}|{zastepca or 'brak'}|{opis or 'brak'}|{uwagi or 'brak'}"
        )
        skrót = hashlib.sha256(surowyIdentyfikator.encode("utf-8"))
        return skrót.hexdigest()

    lekcjeZmapowane: list[AtomowaLekcja] = []

    surowyPlan = dane.get("plan")
    plan = surowyPlan if isinstance(surowyPlan, dict) else {}

    surowaData = dane.get("data")
    data = surowaData if isinstance(surowaData, dict) else {}

    for dzień, wpisy in plan.items():
        for wpis in wpisy:
            numer = wpis["numer"]
            początek = wpis["poczatek"]
            koniec = wpis["koniec"]

            for lekcja in wpis.get("lekcje", []):
                nauczyciel = wyodrębnijTekst(lekcja.get("nauczyciel"))
                sala = wyodrębnijTekst(lekcja.get("sala"))
                oddzialy = połączOddziały(lekcja.get("oddzialy"))
                daneZastępstwa = lekcja.get("zastepstwo")
                zastepca = daneZastępstwa.get("nauczyciel") if daneZastępstwa else None
                opis = daneZastępstwa.get("opis") if daneZastępstwa else None
                uwagi = daneZastępstwa.get("uwagi") if daneZastępstwa else None

                model = AtomowaLekcja(
                    id=wygenerujIdentyfikator(dzień, numer, lekcja["przedmiot"], nauczyciel, sala, oddzialy, zastepca, opis, uwagi, początek, koniec),
                    dzien=dzień,
                    numer=numer,
                    poczatek=początek,
                    koniec=koniec,
                    przedmiot=lekcja["przedmiot"],
                    nauczyciel=nauczyciel,
                    sala=sala,
                    oddzialy=oddzialy,
                    zastepstwo=(f"{zastepca or ''}{f' ({uwagi})' if uwagi else ''}{f' {opis}' if opis else ''}".strip() if daneZastępstwa else None),
                )
                lekcjeZmapowane.append(model)

    return AtomowyPlanLekcji(
        wygenerowano=dane.get("wygenerowano"),
        obowiazuje=data.get("obowiazuje"),
        wygasa=data.get("wygasa"),
        wolne=dane.get("wolne", False),
        zastepstwa=dane["zastepstwa"],
        lekcje=(lekcjeZmapowane if surowyPlan is not None else None)
    )

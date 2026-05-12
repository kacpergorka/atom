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
import hashlib
import json

# Wewnętrzne importy
from src.api.endpoints.atom.notifications.service import wyślijPowiadomienieDoUżytkownika
from src.api.endpoints.universal.numbers.service import pobierzSzczęśliweNumerki
from src.api.endpoints.universal.substitutions.service import pobierzZastępstwa
from src.handlers.logging import logowanie
from src.handlers.notifications import database
from src.classes.types.notifications import PreferencjePowiadomień

def utwórzOdcisk(dane: object) -> str:
    """
    Tworzy stabilny odcisk danych używany do wykrywania zmian.

    Args:
        dane (object): Dane, dla których ma zostać utworzony odcisk.

    Returns:
        str: Szesnastkowy odcisk SHA-256 utworzony z danych.
    """

    tekst = json.dumps(dane, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(tekst.encode("utf-8")).hexdigest()


async def monitorujNumerki(preferencje: list[PreferencjePowiadomień]) -> None:
    """
    Wykrywa zmianę szczęśliwego numerka i wysyła powiadomienia do dopasowanych użytkowników.

    Args:
        preferencje (list[PreferencjePowiadomień]): Lista preferencji powiadomień użytkowników.
    """

    numerki = await pobierzSzczęśliweNumerki()
    dane = numerki.model_dump()
    nowyOdcisk = utwórzOdcisk(dane)
    klucz = f"powiadomienia:monitor:numerki:{dane.get('data')}"
    poprzedniOdcisk = await database.pobierzStanMonitora(klucz)

    if poprzedniOdcisk == nowyOdcisk:
        return

    if poprzedniOdcisk is None:
        await database.zapiszStanMonitora(klucz, nowyOdcisk)
        return

    szczęśliweNumerki = set(numerki.numerki or [])
    if not szczęśliweNumerki:
        await database.zapiszStanMonitora(klucz, nowyOdcisk)
        return

    for preferencja in preferencje:
        if preferencja.numerekUcznia in szczęśliweNumerki:
            await wyślijPowiadomienieDoUżytkownika(
                preferencja.identyfikatorUżytkownika,
                "Szczęśliwy numerek",
                f"Dzisiaj jest Twój szczęśliwy dzień, masz szczęśliwy numerek.",
            )

    await database.zapiszStanMonitora(klucz, nowyOdcisk)


async def monitorujZastępstwa(preferencje: list[PreferencjePowiadomień]) -> None:
    """
    Wykrywa zmianę zastępstw oraz informacji dodatkowych i wysyła powiadomienia do dopasowanych użytkowników.

    Args:
        preferencje: Lista preferencji powiadomień użytkowników.
    """

    preferencjeWedługZastępstw = {}
    for preferencja in preferencje:
        if preferencja.identyfikatorOddziału:
            kluczPreferencji = (
                preferencja.identyfikatorOddziału,
                preferencja.grupy,
                preferencja.religia,
                preferencja.edukacjaZdrowotna,
            )
            preferencjeWedługZastępstw.setdefault(kluczPreferencji, []).append(preferencja)

    for (identyfikator, grupy, religia, edukacjaZdrowotna), dopasowanePreferencje in preferencjeWedługZastępstw.items():
        zastępstwa = await pobierzZastępstwa(
            identyfikator,
            list(grupy) or None,
            religia,
            edukacjaZdrowotna,
            pomińCache=True,
        )
        dane = zastępstwa.model_dump()
        odciskPreferencji = utwórzOdcisk((identyfikator, grupy, religia, edukacjaZdrowotna))
        kluczZastępstw = f"powiadomienia:monitor:zastepstwa:{odciskPreferencji}:wpisy"
        kluczInformacji = f"powiadomienia:monitor:zastepstwa:{odciskPreferencji}:informacje"
        nowyOdciskZastępstw = utwórzOdcisk(dane.get("zastepstwa") or [])
        nowyOdciskInformacji = utwórzOdcisk(dane.get("informacje") or "")
        poprzedniOdciskZastępstw = await database.pobierzStanMonitora(kluczZastępstw)
        poprzedniOdciskInformacji = await database.pobierzStanMonitora(kluczInformacji)

        if poprzedniOdciskZastępstw == nowyOdciskZastępstw and poprzedniOdciskInformacji == nowyOdciskInformacji:
            continue

        if poprzedniOdciskZastępstw is None or poprzedniOdciskInformacji is None:
            await database.zapiszStanMonitora(kluczZastępstw, nowyOdciskZastępstw)
            await database.zapiszStanMonitora(kluczInformacji, nowyOdciskInformacji)
            continue

        if poprzedniOdciskZastępstw != nowyOdciskZastępstw:
            for preferencja in dopasowanePreferencje:
                await wyślijPowiadomienieDoUżytkownika(
                    preferencja.identyfikatorUżytkownika,
                    "Nowe zastępstwa",
                    "Pojawiły się nowe wpisy zastępstw przypisane do Twojego planu lekcji.",
                )
        elif poprzedniOdciskInformacji != nowyOdciskInformacji:
            for preferencja in dopasowanePreferencje:
                await wyślijPowiadomienieDoUżytkownika(
                    preferencja.identyfikatorUżytkownika,
                    "Informacje dodatkowe",
                    "Zmieniły się informacje dodatkowe załączone do wpisów zastępstw.",
                )

        await database.zapiszStanMonitora(kluczZastępstw, nowyOdciskZastępstw)
        await database.zapiszStanMonitora(kluczInformacji, nowyOdciskInformacji)


async def uruchomMonitorPowiadomień() -> None:
    """
    Uruchamia cykliczny monitor powiadomień.
    """

    while True:
        try:
            preferencje = await database.pobierzPreferencje()
            if preferencje:
                await monitorujNumerki(preferencje)
                await monitorujZastępstwa(preferencje)
        except asyncio.CancelledError:
            raise
        except Exception as e:
            logowanie.exception(
                f"Wystąpił bład podczas monitorowania zmian dla powiadomień. Więcej informacji: {e}"
            )

        await asyncio.sleep(300)

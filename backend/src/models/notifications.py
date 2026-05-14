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
from dataclasses import dataclass
from enum import StrEnum
import os
from pathlib import Path

środowiskaProdukcyjne = {"production", "release"}
katalogKluczy = Path(__file__).resolve().parents[2] / "keys"

@dataclass(frozen=True)
class KonfiguracjaAPNs:
    """
    Model konfiguracji połączenia z APNs.
    """

    identyfikatorKlucza: str
    identyfikatorZespołu: str
    temat: str
    kluczPrywatny: str
    adresSerwera: str

    @staticmethod
    def odczytajKluczPrywatny(ścieżka: str) -> str:
        """
        Odczytuje klucz prywatny APNs z pliku.

        Args:
            ścieżka (str): Ścieżka albo nazwa pliku klucza prywatnego APNs.

        Returns:
            str: Zawartość klucza prywatnego APNs.
        """

        plik = katalogKluczy / Path(ścieżka).name

        try:
            return plik.read_text(encoding="utf-8")
        except OSError as e:
            raise RuntimeError(f"Nie można odczytać pliku klucza prywatnego APNs: {ścieżka}") from e

    @classmethod
    def zbudujZeZmiennychŚrodowiskowych(cls) -> "KonfiguracjaAPNs":
        """
        Buduje konfigurację APNs ze zmiennych środowiskowych.

        Returns:
            KonfiguracjaAPNs: Kompletna konfiguracja APNs gotowa do wysyłki powiadomień.
        """

        brakujące = [
            nazwa for nazwa in ("APNS_KEY_ID", "APNS_TEAM_ID", "APNS_BUNDLE_ID")
            if not os.getenv(nazwa)
        ]

        kluczPrywatny = os.getenv("APNS_PRIVATE_KEY")
        if kluczPrywatny:
            kluczPrywatny = cls.odczytajKluczPrywatny(kluczPrywatny)
        else:
            brakujące.append("APNS_PRIVATE_KEY")

        if brakujące:
            raise RuntimeError(f"Brakuje konfiguracji APNs: {', '.join(brakujące)}")

        środowisko = os.getenv("APNS_ENV") or "development"
        adresSerwera = "api.push.apple.com" if środowisko.lower() in środowiskaProdukcyjne else "api.sandbox.push.apple.com"

        return cls(
            identyfikatorKlucza=os.environ["APNS_KEY_ID"],
            identyfikatorZespołu=os.environ["APNS_TEAM_ID"],
            temat=os.environ["APNS_BUNDLE_ID"],
            kluczPrywatny=kluczPrywatny or "",
            adresSerwera=adresSerwera,
        )


@dataclass(frozen=True)
class PreferencjePowiadomień:
    """
    Model preferencji powiadomień użytkownika.
    """

    identyfikatorUżytkownika: str
    oddział: str | None
    identyfikatorOddziału: str | None
    nauczyciel: str | None
    identyfikatorNauczyciela: str | None
    grupaZajęćLekcyjnych: str | None
    grupaZajęćPraktycznych: str | None
    grupaWychowaniaFizycznego: str | None
    religia: bool
    edukacjaZdrowotna: bool
    numerekUcznia: int | None

    @property
    def grupy(self) -> tuple[str, ...]:
        """
        Zwraca grupy używane przy pobieraniu planu i zastępstw.

        Returns:
            tuple[str, ...]: Lista ustawionych grup.
        """

        return tuple(
            grupa
            for grupa in (
                self.grupaZajęćLekcyjnych,
                self.grupaZajęćPraktycznych,
                self.grupaWychowaniaFizycznego,
            )
            if grupa
        )


class AkcjaPowiadomieniaPush(StrEnum):
    """
    Dodatkowe akcje wykonywane po otwarciu ekranu z powiadomienia.
    """

    pokażInformacjeDodatkowe = "pokaz_informacje_dodatkowe"


class EkranPowiadomieniaPush(StrEnum):
    """
    Docelowe ekrany aplikacji mobilnej Atom obsługiwane przez payload powiadomień.
    """

    dashboard = "dashboard"
    planLekcji = "plan_lekcji"
    zastępstwa = "zastepstwa"


class TypPowiadomieniaPush(StrEnum):
    """
    Typy powiadomień wysyłanych do aplikacji mobilnej Atom.
    """

    zastępstwa = "zastępstwa"
    informacjeDodatkowe = "informacje_dodatkowe"
    szczęśliwyNumerek = "szczęśliwy_numerek"


@dataclass(frozen=True)
class TreśćPowiadomieniaPush:
    """
    Konfiguracja treści i nawigacji pojedynczego typu powiadomienia.
    """

    tytuł: str
    treść: str
    ekran: EkranPowiadomieniaPush
    akcja: AkcjaPowiadomieniaPush | None = None


treściPowiadomieńPush: dict[TypPowiadomieniaPush, TreśćPowiadomieniaPush] = {
    TypPowiadomieniaPush.zastępstwa: TreśćPowiadomieniaPush(
        tytuł="Nowe zastępstwa",
        treść="Pojawiły się nowe wpisy zastępstw przypisane do Twojego planu lekcji.",
        ekran=EkranPowiadomieniaPush.planLekcji,
    ),
    TypPowiadomieniaPush.informacjeDodatkowe: TreśćPowiadomieniaPush(
        tytuł="Informacje dodatkowe",
        treść="Zmieniły się informacje dodatkowe załączone do wpisów zastępstw.",
        ekran=EkranPowiadomieniaPush.zastępstwa,
        akcja=AkcjaPowiadomieniaPush.pokażInformacjeDodatkowe,
    ),
    TypPowiadomieniaPush.szczęśliwyNumerek: TreśćPowiadomieniaPush(
        tytuł="Szczęśliwy numerek",
        treść="Dzisiaj jest Twój szczęśliwy dzień, masz szczęśliwy numerek.",
        ekran=EkranPowiadomieniaPush.dashboard,
    ),
}


@dataclass(frozen=True)
class PowiadomieniePush:
    """
    Model powiadomienia APNs z ujednoliconym payloadem dla aplikacji mobilnej.
    """

    typ: TypPowiadomieniaPush
    dzień: str | None = None

    @property
    def konfiguracja(self) -> TreśćPowiadomieniaPush:
        return treściPowiadomieńPush[self.typ]

    @property
    def tytuł(self) -> str:
        return self.konfiguracja.tytuł

    @property
    def treść(self) -> str:
        return self.konfiguracja.treść

    @property
    def ekran(self) -> EkranPowiadomieniaPush:
        return self.konfiguracja.ekran

    @property
    def akcja(self) -> AkcjaPowiadomieniaPush | None:
        return self.konfiguracja.akcja

    def zbudujPayload(self) -> dict[str, object]:
        """
        Buduje payload APNs z polami systemowymi i nawigacją aplikacji.

        Returns:
            dict[str, object]: Payload wysyłany do APNs.
        """

        payload: dict[str, object] = {
            "aps": {
                "alert": {
                    "title": self.tytuł,
                    "body": self.treść,
                },
                "badge": 1,
                "sound": "default",
                "thread-id": self.typ.value,
            },
            "typ": self.typ.value,
            "ekran": self.ekran.value,
        }

        if self.akcja is not None:
            payload["akcja"] = self.akcja.value

        if self.dzień is not None:
            payload["dzien"] = self.dzień

        return payload


@dataclass(frozen=True)
class WynikAPNs:
    """
    Model wyniku wysyłki powiadomienia APNs.
    """

    sukces: bool
    kodStanu: int
    powód: str | None
    identyfikatorPowiadomienia: str | None

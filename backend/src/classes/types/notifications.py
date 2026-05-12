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
import os
from pathlib import Path

środowiskaProdukcyjne = {"production", "release"}
katalogKluczy = Path(__file__).resolve().parents[3] / "keys"

@dataclass(frozen=True)
class KonfiguracjaAPNs:
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


@dataclass(frozen=True)
class WynikAPNs:
    sukces: bool
    kodStanu: int
    powód: str | None
    identyfikatorPowiadomienia: str | None

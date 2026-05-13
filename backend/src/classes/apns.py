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
import time
import uuid

# Zewnętrzne biblioteki
import httpx
import jwt

# Wewnętrzne importy
from src.types.notifications import (
    KonfiguracjaAPNs,
    WynikAPNs
)
from src.handlers.logging import logowanie

class APNs:
    """
    Odpowiada za komunikację z Apple Push Notification service.
    """

    maksymalnyWiekTokenu = 50 * 60

    def __init__(self) -> None:
        """
        Inicjalizuje obiekt, ustawiając początkowy stan bez aktywnej sesji HTTP.
        """

        self.konfiguracja: KonfiguracjaAPNs | None = None
        self.klient: httpx.AsyncClient | None = None
        self.wartośćTokenuDostawcy: str | None = None
        self.utworzonoTokenDostawcy = 0

    @staticmethod
    def odczytajPowódOdrzucenia(odpowiedź: httpx.Response) -> str:
        """
        Odczytuje powód odrzucenia odpowiedzi APNs.

        Args:
            odpowiedź (httpx.Response): Odpowiedź zwrócona przez APNs.

        Returns:
            str: Powód odrzucenia zwrócony przez APNs albo wartość domyślna.
        """

        if not odpowiedź.content:
            return "Nieznany"

        try:
            return odpowiedź.json().get("reason", "Nieznany")
        except ValueError:
            return "Nieznany"

    def pobierzKonfigurację(self) -> KonfiguracjaAPNs:
        """
        Zwraca aktywną konfigurację APNs.

        Returns:
            KonfiguracjaAPNs: Skonfigurowane dane uwierzytelnienia i adres APNs.
        """

        if self.konfiguracja is None:
            self.konfiguracja = KonfiguracjaAPNs.zbudujZeZmiennychŚrodowiskowych()

        return self.konfiguracja

    def pobierzTokenDostawcy(self) -> str:
        """
        Zwraca aktualny token dostawcy APNs.

        Returns:
            str: Token JWT dostawcy używany w autoryzacji APNs.
        """

        teraz = int(time.time())
        if self.wartośćTokenuDostawcy and teraz - self.utworzonoTokenDostawcy < self.maksymalnyWiekTokenu:
            return self.wartośćTokenuDostawcy

        konfiguracja = self.pobierzKonfigurację()
        self.utworzonoTokenDostawcy = teraz
        self.wartośćTokenuDostawcy = jwt.encode(
            {"iss": konfiguracja.identyfikatorZespołu, "iat": teraz},
            konfiguracja.kluczPrywatny,
            algorithm="ES256",
            headers={"kid": konfiguracja.identyfikatorKlucza},
        )
        return self.wartośćTokenuDostawcy

    async def zamknij(self) -> None:
        """
        Zamyka aktywnego klienta HTTP APNs utworzonego przy uruchomieniu Atom API.
        """

        if self.klient is not None:
            try:
                await self.klient.aclose()
            except Exception as e:
                logowanie.exception(
                    f"Wystąpił błąd podczas zamykania klienta HTTP APNs. Więcej informacji: {e}"
                )
            finally:
                self.klient = None

    async def wyślijPowiadomienie(
        self,
        tokenUrządzenia: str,
        tytuł: str,
        treść: str
    ) -> WynikAPNs:
        """
        Wysyła pojedyncze powiadomienie APNs na token urządzenia.

        Args:
            tokenUrządzenia (str): Token APNs urządzenia odbiorcy.
            tytuł (str): Tytuł powiadomienia.
            treść (str): Treść powiadomienia.

        Returns:
            WynikAPNs: Wynik próby wysłania powiadomienia.
        """

        konfiguracja = self.pobierzKonfigurację()
        identyfikatorPowiadomienia = str(uuid.uuid4())
        dane: dict[str, object] = {
            "aps": {
                "alert": {
                    "title": tytuł,
                    "body": treść,
                },
                "sound": "default",
            }
        }

        if self.klient is None:
            self.klient = httpx.AsyncClient(
                http2=True,
                timeout=httpx.Timeout(10, connect=5),
            )

        odpowiedź = await self.klient.post(
            f"https://{konfiguracja.adresSerwera}/3/device/{tokenUrządzenia}",
            headers={
                "authorization": f"bearer {self.pobierzTokenDostawcy()}",
                "apns-topic": konfiguracja.temat,
                "apns-push-type": "alert",
                "apns-priority": "10",
                "apns-expiration": "0",
                "apns-id": identyfikatorPowiadomienia,
            },
            json=dane,
        )
        identyfikatorOdpowiedzi = odpowiedź.headers.get("apns-id") or odpowiedź.headers.get("apns-request-id")
        if odpowiedź.status_code == 200:
            return WynikAPNs(True, odpowiedź.status_code, None, identyfikatorOdpowiedzi or identyfikatorPowiadomienia)

        powód = self.odczytajPowódOdrzucenia(odpowiedź)
        if powód == "ExpiredProviderToken":
            self.wartośćTokenuDostawcy = None

        return WynikAPNs(False, odpowiedź.status_code, powód, identyfikatorOdpowiedzi or identyfikatorPowiadomienia)

klientAPNs = APNs()

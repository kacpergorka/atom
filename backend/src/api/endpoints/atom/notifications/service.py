#
#     ▄▄     ▄▄▄▄▄▄▄▄    ▄▄▄▄    ▄▄▄  ▄▄▄               ▄▄     ▄▄▄▄▄▄     ▄▄▄▄▄▄
#    ████    ▀▀▀██▀▀▀   ██▀▀██   ███  ███              ████    ██▀▀▀▀█▄   ▀▀██▀▀
#    ████       ██     ██    ██  ████████              ████    ██    ██     ██
#   ██  ██      ██     ██    ██  ██ ██ ██             ██  ██   ██████▀      ██
#   ██████      ██     ██    ██  ██ ▀▀ ██             ██████   ██           ██
#  ▄██  ██▄     ██      ██▄▄██   ██    ██            ▄██  ██▄  ██         ▄▄██▄▄
#  ▀▀    ▀▀     ▀▀       ▀▀▀▀    ▀▀    ▀▀            ▀▀    ▀▀  ▀▀         ▀▀▀▀▀▀
#

# Zewnętrzne biblioteki
import httpx

# Wewnętrzne importy
from src.classes.apns import klientAPNs
from src.handlers.logging import logowanie
from src.handlers.notifications import database

async def wyślijPowiadomienieDoUżytkownika(
    identyfikatorUżytkownika: str,
    tytuł: str,
    treść: str
) -> None:
    """
    Wysyła powiadomienie APNs do wszystkich urządzeń użytkownika.

    Args:
        identyfikatorUżytkownika (str): Identyfikator użytkownika, do którego należą urządzenia.
        tytuł (str): Tytuł powiadomienia.
        treść (str): Treść powiadomienia.
    """

    tokenyUrządzeń = await database.pobierzTokenyUżytkownika(identyfikatorUżytkownika)
    powodyNieważnegoTokenu = {"BadDeviceToken", "DeviceTokenNotForTopic", "ExpiredToken", "Unregistered"}
    wysłane = nieudane = 0

    if not tokenyUrządzeń:
        return

    for tokenUrządzenia in tokenyUrządzeń:
        try:
            wynik = await klientAPNs.wyślijPowiadomienie(tokenUrządzenia, tytuł, treść)
        except (RuntimeError, httpx.HTTPError) as e:
            nieudane += 1
            logowanie.exception(
                f"Wystąpił błąd podczas wysyłania powiadomienia APNs. Więcej informacji: {e}"
            )
            continue

        if wynik.sukces:
            wysłane += 1
            continue

        nieudane += 1
        if wynik.powód in powodyNieważnegoTokenu:
            await database.usuńToken(tokenUrządzenia)
        elif wynik.powód == "TooManyRequests" or wynik.kodStanu == 429:
            logowanie.warning(
                f"APNs ograniczyło wysyłanie powiadomień ({wynik.kodStanu}, {wynik.powód}, {wynik.identyfikatorPowiadomienia})."
            )
        logowanie.warning(
            f"APNs odrzuciło powiadomienie ({wynik.kodStanu}, {wynik.powód}, {wynik.identyfikatorPowiadomienia})."
        )

    if nieudane > 0:
        logowanie.error(
            f"Wystąpił błąd podczas dostarczania powiadomień do użytkownika ({identyfikatorUżytkownika}), "
            f"z liczbą urządzeń: {len(tokenyUrządzeń)}. "
            f"Wysłano {wysłane} powiadomienie/ń, "
            f"nie udało się dostarczyć {nieudane} powiadomienie/ń."
        )

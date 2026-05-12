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
import os

# Zewnętrzne biblioteki
from fastapi import (
    HTTPException,
    status
)
import httpx

# Wewnętrzne importy
from src.handlers.accounts import database as bazaDanychKont
from src.handlers.logging import logowanie
from src.handlers.notifications import database as bazaDanychPowiadomień

def pobierzKonfiguracjęSupabase() -> tuple[str, str]:
    """
    Pobiera konfigurację Supabase Admin API.

    Returns:
        tuple[str, str]: Adres Supabase oraz klucz service-role.
    """

    adresSupabase = os.getenv("SUPABASE_URL", "").rstrip("/")
    kluczServiceRole = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")

    if not adresSupabase or not kluczServiceRole:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Obsługa konta nie jest skonfigurowana.",
        )

    return adresSupabase, kluczServiceRole


async def pobierzKontoSupabase(identyfikatorUżytkownika: str) -> dict:
    """
    Pobiera konto użytkownika z Supabase Auth.

    Args:
        identyfikatorUżytkownika (str): Identyfikator użytkownika z JWT.

    Returns:
        dict: Dane użytkownika Supabase.
    """

    adresSupabase, kluczServiceRole = pobierzKonfiguracjęSupabase()
    try:
        async with httpx.AsyncClient(timeout=10) as klient:
            odpowiedź = await klient.get(
                f"{adresSupabase}/auth/v1/admin/users/{identyfikatorUżytkownika}",
                headers={
                    "apikey": kluczServiceRole,
                    "authorization": f"Bearer {kluczServiceRole}",
                },
            )
    except httpx.HTTPError as e:
        logowanie.exception(
            f"Wystąpił błąd podczas łączenia z Supabase w celu pobrania konta. Więcej informacji: {e}"
        )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Nie udało się pobrać konta.",
        ) from e

    if odpowiedź.status_code != 200:
        logowanie.warning(
            f"Supabase odrzuciło pobranie konta ({odpowiedź.status_code})."
        )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Nie udało się pobrać konta.",
        )

    try:
        dane = odpowiedź.json()
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Nie udało się pobrać konta.",
        ) from e

    if not isinstance(dane, dict):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Nie udało się pobrać konta.",
        )

    return dane


async def usuńKontoSupabase(identyfikatorUżytkownika: str) -> None:
    """
    Usuwa konto użytkownika z Supabase Auth.

    Args:
        identyfikatorUżytkownika (str): Identyfikator użytkownika z JWT.
    """

    adresSupabase, kluczServiceRole = pobierzKonfiguracjęSupabase()
    try:
        async with httpx.AsyncClient(timeout=10) as klient:
            odpowiedź = await klient.delete(
                f"{adresSupabase}/auth/v1/admin/users/{identyfikatorUżytkownika}",
                headers={
                    "apikey": kluczServiceRole,
                    "authorization": f"Bearer {kluczServiceRole}",
                },
            )
    except httpx.HTTPError as e:
        logowanie.exception(
            f"Wystąpił błąd podczas łączenia z Supabase w celu usuwania konta. Więcej informacji: {e}"
        )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Nie udało się usunąć konta.",
        ) from e

    if odpowiedź.status_code not in {200, 204}:
        logowanie.warning(
            f"Supabase odrzuciło usunięcie konta ({odpowiedź.status_code}, {odpowiedź.text[:200]})."
        )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Nie udało się usunąć konta.",
        )


def znajdźIdentyfikatorApple(daneUżytkownika: dict) -> str | None:
    """
    Wyszukuje stabilny identyfikator Apple w danych użytkownika Supabase.

    Args:
        daneUżytkownika (dict): Dane użytkownika zwrócone przez Supabase Admin API.

    Returns:
        str | None: Identyfikator Apple albo None.
    """

    tożsamości = daneUżytkownika.get("identities")
    if not isinstance(tożsamości, list):
        return None

    for tożsamość in tożsamości:
        if not isinstance(tożsamość, dict) or tożsamość.get("provider") != "apple":
            continue

        identyfikator = tożsamość.get("provider_id")
        if isinstance(identyfikator, str) and identyfikator:
            return identyfikator

        daneTożsamości = tożsamość.get("identity_data")
        if isinstance(daneTożsamości, dict):
            identyfikator = daneTożsamości.get("sub")

            if isinstance(identyfikator, str) and identyfikator:
                return identyfikator

    return None


async def pobierzIdentyfikatorApple(identyfikatorUżytkownika: str) -> str:
    """
    Pobiera identyfikator Apple aktualnego konta Supabase.

    Args:
        identyfikatorUżytkownika (str): Identyfikator użytkownika z JWT.

    Returns:
        str: Stabilny identyfikator Apple.
    """

    identyfikatorApple = znajdźIdentyfikatorApple(await pobierzKontoSupabase(identyfikatorUżytkownika))
    if identyfikatorApple is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Konto nie jest powiązane z Apple.",
        )

    return identyfikatorApple


def znajdźNazwęApple(daneUżytkownika: dict) -> str | None:
    """
    Wyszukuje nazwę użytkownika Apple w danych Supabase.

    Args:
        daneUżytkownika (dict): Dane użytkownika zwrócone przez Supabase Admin API.

    Returns:
        str | None: Nazwa użytkownika albo None.
    """

    def odczytajNazwę(dane: object) -> str | None:
        if not isinstance(dane, dict):
            return None

        for klucz in ("full_name", "name"):
            wartość = dane.get(klucz)
            if not isinstance(wartość, str):
                continue

            nazwa = wartość.strip()
            if nazwa:
                return nazwa

        imię = ""
        for klucz in ("given_name", "first_name"):
            wartość = dane.get(klucz)
            if isinstance(wartość, str) and wartość.strip():
                imię = wartość.strip()
                break

        nazwisko = ""
        for klucz in ("last_name", "family_name"):
            wartość = dane.get(klucz)
            if isinstance(wartość, str) and wartość.strip():
                nazwisko = wartość.strip()
                break

        nazwa = f"{imię} {nazwisko}".strip()
        return nazwa or None

    nazwa = odczytajNazwę(daneUżytkownika.get("user_metadata"))
    if nazwa:
        return nazwa

    tożsamości = daneUżytkownika.get("identities")
    if not isinstance(tożsamości, list):
        return None

    for tożsamość in tożsamości:
        if not isinstance(tożsamość, dict) or tożsamość.get("provider") != "apple":
            continue

        nazwa = odczytajNazwę(tożsamość.get("identity_data"))
        if nazwa:
            return nazwa

    return None


async def zachowajProfilApple(identyfikatorUżytkownika: str) -> None:
    """
    Zachowuje wymagany do prawidłowego działania aplikacji profil Apple użytkownika.

    Args:
        identyfikatorUżytkownika (str): Identyfikator użytkownika z JWT.
    """

    try:
        daneUżytkownika = await pobierzKontoSupabase(identyfikatorUżytkownika)
    except HTTPException as e:
        logowanie.exception(
            f"Wystąpił błąd podczas zachowywania profilu Apple przed usunięciem konta. Więcej informacji: {e.detail}"
        )
        return

    identyfikatorApple = znajdźIdentyfikatorApple(daneUżytkownika)
    nazwa = znajdźNazwęApple(daneUżytkownika)
    if not identyfikatorApple or not nazwa:
        return

    await bazaDanychKont.zapiszProfilApple(
        identyfikatorUżytkownika,
        identyfikatorApple,
        nazwa,
    )


async def usuńKontoUżytkownika(identyfikatorUżytkownika: str) -> None:
    """
    Usuwa konto użytkownika oraz jego lokalne dane.

    Args:
        identyfikatorUżytkownika (str): Identyfikator użytkownika z JWT.
    """

    await zachowajProfilApple(identyfikatorUżytkownika)
    await usuńKontoSupabase(identyfikatorUżytkownika)
    await bazaDanychKont.odłączUżytkownikaOdProfiluApple(identyfikatorUżytkownika)
    await bazaDanychPowiadomień.usuńDaneUżytkownika(identyfikatorUżytkownika)

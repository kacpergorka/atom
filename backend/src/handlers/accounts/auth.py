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
from asyncio import to_thread
import os

# Zewnętrzne biblioteki
from fastapi import (
    Depends,
    HTTPException,
    status
)
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer
)
import jwt
from jwt import (
    PyJWKClient,
    ExpiredSignatureError,
    InvalidAlgorithmError,
    InvalidAudienceError,
    InvalidIssuerError,
    InvalidSignatureError,
    InvalidTokenError
)
from jwt.exceptions import (
    MissingCryptographyError,
    PyJWKClientError
)

# Wewnętrzne importy
from src.types.accounts import AktualnyUżytkownik
from src.handlers.logging import logowanie

maksymalnaDługośćIdentyfikatoraUżytkownika = 128
minimalnaDługośćSekretuHmac = 32

schematBearer = HTTPBearer(auto_error=False)
klientKluczyJwks: PyJWKClient | None = None

def pobierzZmiennąŚrodowiskową(nazwa: str) -> str | None:
    """
    Pobiera niepustą wartość zmiennej środowiskowej.

    Args:
        nazwa (str): Nazwa zmiennej środowiskowej.

    Returns:
        str | None: Oczyszczona wartość zmiennej albo None.
    """

    wartość = os.getenv(nazwa)
    if wartość is None:
        return None

    wartość = wartość.strip()
    return wartość or None


def pobierzKlientaJwks() -> PyJWKClient | None:
    """
    Zwraca współdzielonego klienta JWKS, jeśli został skonfigurowany.

    Returns:
        PyJWKClient | None: Klient JWKS albo None, jeśli adres JWKS nie został ustawiony.
    """

    global klientKluczyJwks

    adresJwks = pobierzZmiennąŚrodowiskową("JWT_JWKS_URL")
    if not adresJwks:
        return None

    if klientKluczyJwks is None:
        klientKluczyJwks = PyJWKClient(adresJwks)

    return klientKluczyJwks


async def pobierzKluczJwt(
    token: str,
    algorytm: str
) -> str:
    """
    Zwraca klucz używany do weryfikacji podpisu JWT.

    Args:
        token (str): Token JWT przekazany w nagłówku Authorization.
        algorytm (str): Algorytm podpisu odczytany z nagłówka JWT.

    Returns:
        str: Klucz do weryfikacji podpisu JWT.
    """

    klient = pobierzKlientaJwks()
    if klient is not None:
        klucz = await to_thread(klient.get_signing_key_from_jwt, token)
        return klucz.key

    if algorytm.startswith("HS"):
        sekret = pobierzZmiennąŚrodowiskową("JWT_SECRET")
        if sekret and len(sekret.encode("utf-8")) >= minimalnaDługośćSekretuHmac:
            return sekret

        raise RuntimeError("JWT_SECRET musi mieć co najmniej 32 bajty dla walidacji JWT HMAC.")

    raise RuntimeError("JWT_JWKS_URL jest wymagane do walidacji JWT z algorytmem asymetrycznym.")


def utwórzBłądBrakuAutoryzacji() -> HTTPException:
    """
    Buduje odpowiedź błędu dla braku poprawnej autoryzacji.

    Returns:
        HTTPException: Wyjątek HTTP 401 z nagłówkiem Bearer.
    """

    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Wymagana autoryzacja.",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def pobierzAktualnegoUżytkownika(daneAutoryzacji: HTTPAuthorizationCredentials | None = Depends(schematBearer)) -> AktualnyUżytkownik:
    """
    Weryfikuje token Bearer i zwraca aktualnego użytkownika.

    Args:
        daneAutoryzacji (HTTPAuthorizationCredentials | None): Dane nagłówka Authorization odczytane przez FastAPI.

    Returns:
        AktualnyUżytkownik: Użytkownik zidentyfikowany na podstawie zweryfikowanego JWT.
    """

    if daneAutoryzacji is None or daneAutoryzacji.scheme.lower() != "bearer":
        logowanie.warning(
            "Odrzucono żądanie powiadomień (brak nagłówka Authorization Bearer)."
        )
        raise utwórzBłądBrakuAutoryzacji()

    algorytmJwt = pobierzZmiennąŚrodowiskową("JWT_ALGORITHM")
    if not algorytmJwt:
        raise RuntimeError("JWT_ALGORITHM jest wymagane do walidacji JWT.")

    wystawca = pobierzZmiennąŚrodowiskową("JWT_ISSUER")
    odbiorca = pobierzZmiennąŚrodowiskową("JWT_AUDIENCE")
    otrzymanyWystawca = "brak"
    otrzymanyOdbiorca = "brak"

    try:
        nagłówek = jwt.get_unverified_header(daneAutoryzacji.credentials)
        algorytm = nagłówek.get("alg")
        if not isinstance(algorytm, str) or algorytm != algorytmJwt:
            raise InvalidAlgorithmError(f"{algorytm} nie jest dozwolonym algorytmem JWT.")

        daneBezWeryfikacji = jwt.decode(
            daneAutoryzacji.credentials,
            options={
                "verify_signature": False,
                "verify_aud": False,
                "verify_iss": False,
            },
        )
        otrzymanyWystawca = str(daneBezWeryfikacji.get("iss", "brak"))
        otrzymanyOdbiorca = str(daneBezWeryfikacji.get("aud", "brak"))

        dane = jwt.decode(
            daneAutoryzacji.credentials,
            await pobierzKluczJwt(daneAutoryzacji.credentials, algorytm),
            algorithms=[algorytmJwt],
            audience=odbiorca,
            issuer=wystawca,
            leeway=30,
            options={
                "require": ["sub"],
                "verify_aud": odbiorca is not None,
                "verify_iss": wystawca is not None,
            },
        )
    except ExpiredSignatureError:
        logowanie.warning(
            "Odrzucono żądanie powiadomień (JWT wygasł).")
        raise utwórzBłądBrakuAutoryzacji()
    except InvalidAudienceError:
        logowanie.warning(
            f"Odrzucono żądanie powiadomień (JWT ma nieprawidłowe audience (otrzymano: {otrzymanyOdbiorca}, oczekiwano: {odbiorca}))."
        )
        raise utwórzBłądBrakuAutoryzacji()
    except InvalidIssuerError:
        logowanie.warning(
            f"Odrzucono żądanie powiadomień (JWT ma nieprawidłowego wystawcę (otrzymano: {otrzymanyWystawca}, oczekiwano: {wystawca}))."
        )
        raise utwórzBłądBrakuAutoryzacji()
    except InvalidAlgorithmError as e:
        logowanie.warning(
            f"Odrzucono żądanie powiadomień (algorytm JWT jest niedozwolony ({e}))."
        )
        raise utwórzBłądBrakuAutoryzacji()
    except InvalidSignatureError:
        logowanie.warning(
            "Odrzucono żądanie powiadomień (podpis JWT jest nieprawidłowy)."
        )
        raise utwórzBłądBrakuAutoryzacji()
    except MissingCryptographyError:
        logowanie.warning(
            "Odrzucono żądanie powiadomień (algorytm JWT wymaga pakietu cryptography)."
        )
        raise utwórzBłądBrakuAutoryzacji()
    except PyJWKClientError as e:
        logowanie.warning(
            f"Odrzucono żądanie powiadomień (nie udało się pobrać klucza JWKS ({e.__class__.__name__})).")
        raise utwórzBłądBrakuAutoryzacji()
    except RuntimeError as e:
        logowanie.warning(
            f"Odrzucono żądanie powiadomień (nie skonfigurowano walidacji JWT ({e}))."
        )
        raise utwórzBłądBrakuAutoryzacji()
    except InvalidTokenError as e:
        logowanie.warning(
            f"Odrzucono żądanie powiadomień (JWT jest nieprawidłowy ({e.__class__.__name__}))."
        )
        raise utwórzBłądBrakuAutoryzacji()
    except Exception as e:
        logowanie.exception(
            f"Wystąpił nieoczekiwany błąd podczas walidacji JWT. Więcej informacji {e}"
        )
        raise utwórzBłądBrakuAutoryzacji()

    identyfikatorUżytkownika = dane.get("sub")
    if (
        not isinstance(identyfikatorUżytkownika, str)
        or not identyfikatorUżytkownika
        or len(identyfikatorUżytkownika) > maksymalnaDługośćIdentyfikatoraUżytkownika
    ):
        logowanie.warning(
            "Odrzucono żądanie powiadomień (JWT nie zawiera prawidłowego sub)."
        )
        raise utwórzBłądBrakuAutoryzacji()

    return AktualnyUżytkownik(identyfikator=identyfikatorUżytkownika)

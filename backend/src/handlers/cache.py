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
from typing import TypeVar

# Zewnętrzne biblioteki
from pydantic import BaseModel
from redis.exceptions import RedisError

# Wewnętrzne importy
from src.classes.atom import klientAtom
from src.handlers.logging import logowanie

ModelCache = TypeVar("ModelCache", bound=BaseModel)

def normalizujStanOpcji(wartość: bool) -> str:
    """
    Normalizuje stan opcji logicznej do fragmentu klucza cache.

    Args:
        wartość (bool): Wartość logiczna.

    Returns:
        str: `"1"` gdy wartość to True, `"0"` gdy False
    """

    return "1" if wartość else "0"


async def pobierzModel(
    klucz: str,
    model: type[ModelCache]
) -> ModelCache | None:
    """
    Pobiera zapisany model z Redis i zamienia go na podany model Pydantic.

    Args:
        klucz (str): Klucz pod którym dane są zapisane w Redis.
        model (type[ModelCache]): Model Pydantic, do którego zostaną zamienione zapisane dane JSON.

    Returns:
        ModelCache | None: Obiekt modelu Pydantic lub `None`, jeśli wpis nie istnieje, Redis jest niedostępny lub dane w cache są uszkodzone.
    """

    if klientAtom.redis is None:
        return None

    try:
        dane = await klientAtom.redis.get(klucz)
    except RedisError as e:
        logowanie.warning(
            f"Nie udało się odczytać wpisu cache Redis ({klucz}). Więcej informacji: {e}"
        )
        return None

    if dane is None:
        return None

    try:
        return model.model_validate_json(dane)
    except ValueError as e:
        logowanie.warning(
            f"Wpis cache Redis ({klucz}) ma nieprawidłowy format. Więcej informacji: {e}"
        )
        try:
            await klientAtom.redis.delete(klucz)
        except RedisError:
            pass

        return None


async def zapiszModel(
    klucz: str,
    model: BaseModel,
    czas: int = 300
) -> None:
    """
    Zapisuje model Pydantic w Redis jako JSON.

    Args:
        klucz (str): Klucz pod którym dane zostaną zapisane w Redis.
        model (BaseModel): Model Pydantic który zostanie zapisany w Redis w formacie JSON.
        czas (int, optional): Czas życia wpisu w cache (TTL) w sekundach.
    """

    if klientAtom.redis is None:
        return

    try:
        await klientAtom.redis.set(klucz, model.model_dump_json(), ex=czas)
    except RedisError as e:
        logowanie.warning(
            f"Nie udało się zapisać wpisu cache Redis ({klucz}). Więcej informacji: {e}"
        )


def zbudujFragmentKluczaCache(wartości: list[str] | None) -> str:
    """
    Zwraca stabilny fragment klucza cache dla listy tekstów.

    Args:
        wartości (list[str] | None): Lista tekstów używana do budowy fragmentu klucza cache.

    Returns:
        str: Posortowany i połączony przecinkami ciąg znaków reprezentujący listę.
    """

    if not wartości:
        return "wszystkie"

    wynik = sorted({
        wartość.strip()
        for wartość in wartości
        if isinstance(wartość, str) and wartość.strip()
    })

    return ",".join(wynik or ["wszystkie"])

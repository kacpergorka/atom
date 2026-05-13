#
#     ▄▄     ▄▄▄▄▄▄▄▄    ▄▄▄▄    ▄▄▄  ▄▄▄               ▄▄     ▄▄▄▄▄▄     ▄▄▄▄▄▄
#    ████    ▀▀▀██▀▀▀   ██▀▀██   ███  ███              ████    ██▀▀▀▀█▄   ▀▀██▀▀
#    ████       ██     ██    ██  ████████              ████    ██    ██     ██
#   ██  ██      ██     ██    ██  ██ ██ ██             ██  ██   ██████▀      ██
#   ██████      ██     ██    ██  ██ ▀▀ ██             ██████   ██           ██
#  ▄██  ██▄     ██      ██▄▄██   ██    ██            ▄██  ██▄  ██         ▄▄██▄▄
#  ▀▀    ▀▀     ▀▀       ▀▀▀▀    ▀▀    ▀▀            ▀▀    ▀▀  ▀▀         ▀▀▀▀▀▀
#

class BłądAPI(Exception):
    """
    Bazowy wyjątek błędów obsługiwanych przez Atom API.
    """


class BłądWewnętrzny(BłądAPI):
    """
    Błąd przetwarzania danych po stronie backendu.
    """


class BrakWymaganychDanych(BłądAPI):
    """
    Błąd brakujących danych konfiguracyjnych backendu.
    """


class NieprawidłowyIdentyfikator(BłądAPI):
    """
    Błąd nieprawidłowego identyfikatora przekazanego do API.
    """


class ŹródłoNiedostępne(BłądAPI):
    """
    Błąd niedostępnego źródła danych zewnętrznych.
    """

# Nowoczesna aplikacja mobilna Atom dla uczniów i nauczycieli Zespołu Szkół Elektronicznych w Bydgoszczy
[![](https://img.shields.io/badge/Atom%20Development-Dołącz%20do%20serwera-5865F2?logo=discord&logoColor=white)](https://discord.gg/5KjkvbGQWj) [![](https://img.shields.io/badge/Atom%20API-Zapoznaj%20się%20z%20dokumentacją-009688?logo=fastapi&logoColor=white)](https://api.kacpergorka.com/docs)

<p align="left">
  <img src="https://raw.githubusercontent.com/kacpergorka/atom/develop/assets/1.png" width="24%">
  <img src="https://raw.githubusercontent.com/kacpergorka/atom/develop/assets/2.png" width="24%">
  <img src="https://raw.githubusercontent.com/kacpergorka/atom/develop/assets/3.png" width="24%">
  <img src="https://raw.githubusercontent.com/kacpergorka/atom/develop/assets/4.png" width="24%">
</p>

> [!NOTE]
> Aplikacja mobilna Atom jest oprogramowaniem przeznaczonym dla uczniów i nauczycieli [Zespołu Szkół Elektronicznych im. Wojska Polskiego w Bydgoszczy](https://zse.bydgoszcz.pl). 

Na ten moment aplikacja jest w zamkniętych beta testach na systemach firmy [Apple](https://www.apple.com), takich jak [iOS](https://www.apple.com/pl/os/ios/) w wersji 26.0 lub nowszej, [iPadOS](https://www.apple.com/pl/os/ipados/) w wersji 26.0 lub nowszej i [macOS](https://www.apple.com/pl/os/macos/) w wersji Tahoe lub nowszej. W przyszłości planowane jest udostępnienie aplikacji na urządzenia z systemem [Android](https://www.android.com).

# Informacje techniczne API
Atom API wykorzystywane przez aplikacje mobilną jest przeznaczone dla deweloperów i pasjonatów należących do [Zespołu Szkół Elektronicznych im. Wojska Polskiego w Bydgoszczy](https://zse.bydgoszcz.pl) i zawiera ogólnodostępne endpointy dla osób chcących stworzyć własne projekty z jego wykorzystaniem. Jeżeli jesteś zainteresowany, zapoznaj się z [dokumentacją Atom API](https://api.kacpergorka.com/docs). Jeżeli masz taką potrzebę [skontaktuj się ze mną](mailto:kontakt@kacpergorka.com), a w miarę możliwości odpowiem w wolnej chwili.

> [!IMPORTANT]
> W przypadku wystąpienia jakiegokolwiek błędu z zakresu poprawnego funkcjonowania API lub prawidłowego zwracania danych utwórz issue z dokładnym opisem błędu, a w miarę możliwości odpowiednio szybko zostanie on usunięty.

# Najprzydatniejsze funkcje aplikacji mobilnej Atom

<img align="left" src="https://raw.githubusercontent.com/kacpergorka/atom/develop/assets/1.png" width="25%" />

### 1️⃣ Dashboard wyświetlający najważniejsze informacje
Szybki podgląd najistotniejszych danych po uruchomieniu aplikacji, takich jak zbliżające się lekcje, szczęśliwe numerki czy inne szkolne materiały dostępne w jednym miejscu.

### 2️⃣ Plan lekcji z nanoszonymi zastępstwami
Czytelny plan lekcji z automatycznie uwzględnianymi zastępstwami i zmianami, dzięki czemu zawsze widzisz aktualne zajęcia bez potrzeby sprawdzania wielu źródeł.

### 3️⃣ Ogłoszenia i aktualności szkolne
Dostęp do najnowszych komunikatów, wydarzeń oraz informacji publikowanych przez szkołę w przejrzystej i wygodnej formie.

### 4️⃣ Powiadomienia o bieżących zmianach
Natychmiastowe powiadomienia o nowych zmianach w planie lekcji, zastępstwach i dołączonych do nich informacji dodatkowych, szczęśliwych numerkach oraz innych ważnych wydarzeniach szkolnych sprawiają, że zawsze jesteś na bieżąco.

# Instalacja i uruchamianie API
> [!NOTE]
> Do instalacji i uruchomienia Atom API wymagany jest Docker w najnowszej wersji.

	git clone https://github.com/kacpergorka/atom/
	cd atom/backend
	docker compose up --build

#
Projekt licencjonowany na podstawie licencji [Apache-2.0](./LICENSE). Stworzone z ❤️ przez Kacpra Górkę!

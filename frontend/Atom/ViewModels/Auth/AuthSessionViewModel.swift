//
//     ▄▄     ▄▄▄▄▄▄▄▄    ▄▄▄▄    ▄▄▄  ▄▄▄
//    ████    ▀▀▀██▀▀▀   ██▀▀██   ███  ███
//    ████       ██     ██    ██  ████████
//   ██  ██      ██     ██    ██  ██ ██ ██
//   ██████      ██     ██    ██  ██ ▀▀ ██
//  ▄██  ██▄     ██      ██▄▄██   ██    ██
//  ▀▀    ▀▀     ▀▀       ▀▀▀▀    ▀▀    ▀▀
//

import Combine
import Foundation
import Supabase
import Observation

@MainActor
@Observable
final class AuthSessionViewModel {
    // MARK: - Stan

    private(set) var sesja: Session?
    private(set) var błąd: String?
    private(set) var czyŁaduje = false
    private(set) var czyŁadowanieSesji = true

    // MARK: - Zależności

    private let klient: SupabaseClient?
    private let managerPowiadomień: PushNotificationsManager
    private var zadanieNasłuchiwania: Task<Void, Never>?
    private var zadanieSynchronizacjiKonta: Task<Void, Never>?

    // MARK: - Inicjalizacja

    init(
        klient: SupabaseClient? = nil,
        managerPowiadomień: PushNotificationsManager? = nil
    ) {
        self.klient = klient ?? SupabaseManager.współdzielony
        self.managerPowiadomień = managerPowiadomień ?? .współdzielony
        Task {
            await załadujSesję()
        }
    }

    // MARK: - Właściwości obliczeniowe

    var czySupabaseSkonfigurowany: Bool {
        klient != nil
    }

    var emailUżytkownika: String {
        sesja?.user.email ?? "Zalogowano"
    }

    var czyZalogowano: Bool {
        sesja != nil
    }

    // MARK: - Akcje

    func rozpocznijNasłuchiwanie() {
        guard zadanieNasłuchiwania == nil, let klient else { return }

        zadanieNasłuchiwania = Task { [weak self, klient] in
            for await zmiana in await klient.auth.authStateChanges {
                guard let self else {
                    return
                }

                if zmiana.session == nil {
                    self.ustawSesję(nil)
                    continue
                }

                await self.sprawdźCzySesjaJestPrawidłowa()
            }
        }
    }

    func zalogujZApple(idToken: String, nonce: String, nazwa: String?) async {
        await wykonajAkcję {
            let sesja = try await self.klient?.auth.signInWithIdToken(
                credentials: OpenIDConnectCredentials(
                    provider: .apple,
                    idToken: idToken,
                    nonce: nonce
                )
            )

            let nazwaDoZapisu = self.nazwaDoZapisuPoLogowaniu(nazwa)
            self.zapiszNazwęJeśliDostępna(nazwaDoZapisu)
            self.ustawSesję(sesja, nazwaPreferowana: nazwaDoZapisu)
        }
    }

    func wyloguj() async {
        await wykonajAkcję {
            await self.managerPowiadomień.usuńTokenPrzedWylogowaniem(sesja: self.sesja)
            try await self.klient?.auth.signOut()
            self.ustawSesję(nil)
        }
    }

    func usuńKonto() async {
        await wykonajAkcję {
            guard let tokenJWT = self.sesja?.accessToken else {
                throw URLError(.userAuthenticationRequired)
            }

            await self.managerPowiadomień.usuńTokenPrzedWylogowaniem(sesja: self.sesja)
            try await APIClient.współdzielony.usuńKonto(tokenJWT: tokenJWT)
            try? await self.klient?.auth.signOut()
            self.wyczyśćLokalneUstawienia()
            self.ustawSesję(nil)
        }
    }

    func wyczyśćBłąd() {
        błąd = nil
    }

    func zsynchronizujKontoAktualnejSesji() {
        Task {
            await sprawdźCzySesjaJestPrawidłowa()
        }
    }

    func ustawBłąd(_ komunikat: String) {
        błąd = komunikat
    }

    func sprawdźCzySesjaJestPrawidłowa() async {
        guard let klient else {
            ustawSesję(nil)
            return
        }

        do {
            _ = try await klient.auth.user()

            let aktualnaSesja = try await klient.auth.session
            ustawSesję(aktualnaSesja)
        } catch {
            await wyczyśćNieprawidłowąSesję()
        }
    }

    func wyczyśćNieprawidłowąSesję() async {
        try? await klient?.auth.signOut()
        ustawSesję(nil)
    }

    // MARK: - Prywatne

    private func ustawSesję(_ nowaSesja: Session?, nazwaPreferowana: String? = nil) {
        sesja = nowaSesja

        Task {
            await managerPowiadomień.zsynchronizuj(sesja: nowaSesja)
        }

        if let nowaSesja {
            uruchomSynchronizacjęKonta(sesja: nowaSesja, nazwaPreferowana: nazwaPreferowana)
        } else {
            zadanieSynchronizacjiKonta?.cancel()
            zadanieSynchronizacjiKonta = nil
        }
    }

    // MARK: - Zarządzanie nazwą

    @discardableResult
    private func zapiszNazwęJeśliDostępna(_ nazwa: String?) -> Bool {
        guard let nazwa = nazwa?.trimmingCharacters(in: .whitespacesAndNewlines), !nazwa.isEmpty else {
            return false
        }

        UserDefaults.standard.set(nazwa, forKey: KluczeUstawień.nazwa)
        return true
    }

    private func nazwaDoZapisuPoLogowaniu(_ nazwaApple: String?) -> String? {
        if let nazwa = nazwaApple?.trimmingCharacters(in: .whitespacesAndNewlines), !nazwa.isEmpty {
            return nazwa
        }

        return UserDefaults.standard.string(forKey: KluczeUstawień.nazwa)
    }

    // MARK: - Synchronizacja konta

    private func uruchomSynchronizacjęKonta(sesja: Session, nazwaPreferowana: String? = nil) {
        zadanieSynchronizacjiKonta?.cancel()

        let tokenJWT = sesja.accessToken
        let nazwaDoZapisu = nazwaDoZapisuPoLogowaniu(nazwaPreferowana)
        let opóźnieniaPonowień: [UInt64] = [0, 5, 15, 60, 300]

        zadanieSynchronizacjiKonta = Task { [weak self] in
            for opóźnienie in opóźnieniaPonowień {
                guard !Task.isCancelled else {
                    return
                }

                if opóźnienie > 0 {
                    try? await Task.sleep(nanoseconds: opóźnienie * 1_000_000_000)
                }

                guard !Task.isCancelled else {
                    return
                }

                if await self?.zsynchronizujKonto(tokenJWT: tokenJWT, nazwa: nazwaDoZapisu) == true {
                    return
                }
            }
        }
    }

    private func zsynchronizujKonto(tokenJWT: String, nazwa: String?) async -> Bool {
        do {
            let konto = try await APIClient.współdzielony.synchronizujKonto(
                tokenJWT: tokenJWT,
                nazwa: nazwa
            )
            zapiszNazwęJeśliDostępna(konto.nazwa)
            return true
        } catch {
            return false
        }
    }

    private func wyczyśćLokalneUstawienia() {
        let ustawienia = UserDefaults.standard
        [
            KluczeUstawień.czyKonfiguracjaZakończona,
            KluczeUstawień.oddział,
            KluczeUstawień.identyfikatorOddziału,
            KluczeUstawień.nauczyciel,
            KluczeUstawień.identyfikatorNauczyciela,
            KluczeUstawień.numerekUcznia,
            KluczeUstawień.nazwa,
            KluczeUstawień.grupaZajęćLekcyjnych,
            KluczeUstawień.grupaZajęćPraktycznych,
            KluczeUstawień.grupaWychowaniaFizycznego,
            KluczeUstawień.religia,
            KluczeUstawień.edukacjaZdrowotna
        ].forEach(ustawienia.removeObject)
    }

    // MARK: - Zarządzanie sesją

    private func załadujSesję() async {
        defer {
            czyŁadowanieSesji = false
        }

        guard let klient else {
            return
        }

        do {
            let sesja = try await klient.auth.session
            ustawSesję(sesja)

            await sprawdźCzySesjaJestPrawidłowa()
        } catch {
            await wyczyśćNieprawidłowąSesję()
        }
    }

    // MARK: - Obsługa błędów

    private func wykonajAkcję(_ akcja: @MainActor @escaping () async throws -> Void) async {
        błąd = nil
        czyŁaduje = true
        defer { czyŁaduje = false }

        do {
            try await akcja()
        } catch {

            let komunikat = error.localizedDescription

            if komunikat.contains("JWT") ||
                komunikat.contains("refresh") ||
                komunikat.contains("session") ||
                komunikat.contains("User from sub claim in JWT does not exist") {
                await wyczyśćNieprawidłowąSesję()
            }

            błąd = error.komunikatDlaUżytkownika
        }
    }
}

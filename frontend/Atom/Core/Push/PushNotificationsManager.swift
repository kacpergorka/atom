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
import UIKit
import UserNotifications
import Observation

// MARK: - Typy powiadomień push

enum TypPowiadomieniaPush: String, Sendable {
    case zastępstwa = "zastępstwa"
    case informacjeDodatkowe = "informacje_dodatkowe"
    case szczęśliwyNumerek = "szczęśliwy_numerek"
}

// MARK: - Docelowe ekrany powiadomień

enum DocelowyEkranPowiadomieniaPush: String, Sendable {
    case dashboard
    case planLekcji = "plan_lekcji"
    case zastępstwa = "zastepstwa"
}

// MARK: - Akcje powiadomień

enum AkcjaPowiadomieniaPush: String, Sendable {
    case pokażInformacjeDodatkowe = "pokaz_informacje_dodatkowe"
}

// MARK: - Miejsce docelowe powiadomienia

struct MiejsceDocelowePowiadomieniaPush: Equatable, Sendable {
    let typ: TypPowiadomieniaPush
    let ekran: DocelowyEkranPowiadomieniaPush
    let dzień: Dzien?
    let akcja: AkcjaPowiadomieniaPush?

    nonisolated init?(userInfo: [AnyHashable: Any]) {
        guard let typPowiadomienia = userInfo["typ"] as? String,
              let ekranPowiadomienia = userInfo["ekran"] as? String,
              let typ = TypPowiadomieniaPush(rawValue: typPowiadomienia),
              let ekran = DocelowyEkranPowiadomieniaPush(rawValue: ekranPowiadomienia) else {
            return nil
        }

        self.typ = typ
        self.ekran = ekran
        self.dzień = (userInfo["dzien"] as? String).flatMap(Dzien.init(rawValue:))
        self.akcja = (userInfo["akcja"] as? String).flatMap(AkcjaPowiadomieniaPush.init(rawValue:))
    }

    nonisolated init(
        typ: TypPowiadomieniaPush,
        ekran: DocelowyEkranPowiadomieniaPush,
        dzień: Dzien? = nil,
        akcja: AkcjaPowiadomieniaPush? = nil
    ) {
        self.typ = typ
        self.ekran = ekran
        self.dzień = dzień
        self.akcja = akcja
    }
}

// MARK: - Manager powiadomień push

@MainActor
@Observable
final class PushNotificationsManager: NSObject {
    // MARK: - Stan

    static let współdzielony = PushNotificationsManager()

    private(set) var czyAutoryzowano = false
    private(set) var oczekiwaneMiejsceDocelowe: MiejsceDocelowePowiadomieniaPush?

    // MARK: - Zależności

    private let klientAPI: APIClient
    private var tokenUrządzenia: String?
    private var tokenJWT: String?
    private var czyPoproszonoORejestracjęAPNs = false
    private var trwającaRejestracja: DaneRejestracjiPush?
    private var ostatniaUdanaRejestracja: DaneRejestracjiPush?

    // MARK: - Inicjalizacja

    init(klientAPI: APIClient? = nil) {
        self.klientAPI = klientAPI ?? .współdzielony
        super.init()
    }

    // MARK: - Publiczne API

    func skonfiguruj() {
        UNUserNotificationCenter.current().delegate = self
    }

    func pobierzOczekiwaneMiejsceDocelowe() -> MiejsceDocelowePowiadomieniaPush? {
        defer {
            oczekiwaneMiejsceDocelowe = nil
        }

        return oczekiwaneMiejsceDocelowe
    }

    func wyczyśćLokalnyBadge() {
        Task {
            try? await UNUserNotificationCenter.current().setBadgeCount(0)
        }
    }

    func poprośOZgodę() async {
        do {
            let centrum = UNUserNotificationCenter.current()
            let zgoda = try await centrum.requestAuthorization(options: [.alert, .badge, .sound])
            czyAutoryzowano = zgoda

            guard zgoda, !czyPoproszonoORejestracjęAPNs else {
                return
            }

            czyPoproszonoORejestracjęAPNs = true
            UIApplication.shared.registerForRemoteNotifications()
        } catch {
            czyAutoryzowano = false
        }
    }

    func zsynchronizuj(sesja: Session?) async {
        tokenJWT = sesja?.accessToken

        guard tokenJWT != nil else {
            return
        }

        await zsynchronizujPreferencjeKontaPoLogowaniu()
        await poprośOZgodę()
        await zarejestrujJeśliMożna()
    }

    func ustawTokenUrządzenia(_ dane: Data) {
        let nowyTokenUrządzenia = dane.map { String(format: "%02x", $0) }.joined()
        guard tokenUrządzenia != nowyTokenUrządzenia else {
            return
        }

        tokenUrządzenia = nowyTokenUrządzenia

        Task {
            await zarejestrujJeśliMożna()
        }
    }

    func usuńTokenPrzedWylogowaniem(sesja: Session?) async {
        defer {
            self.tokenJWT = nil
            ostatniaUdanaRejestracja = nil
            trwającaRejestracja = nil
        }

        guard let tokenJWT = sesja?.accessToken, let tokenUrządzenia else {
            return
        }

        try? await klientAPI.usuńTokenPush(
            tokenUrządzenia: tokenUrządzenia,
            tokenJWT: tokenJWT
        )
    }

    func zsynchronizujPreferencje() async {
        await zapiszPreferencjeKonta()
        await zarejestrujJeśliMożna()
    }

    // MARK: - Synchronizacja preferencji

    private func zsynchronizujPreferencjeKontaPoLogowaniu() async {
        guard let tokenJWT else {
            return
        }

        do {
            if let preferencje = try await klientAPI.pobierzPreferencjePush(tokenJWT: tokenJWT) {
                zastosujPreferencjeKonta(preferencje)
            } else if czyLokalnePreferencjeSąKompletne {
                await zapiszPreferencjeKonta()
            }
        } catch {
            return
        }
    }

    private func zapiszPreferencjeKonta() async {
        guard let tokenJWT, czyLokalnePreferencjeSąKompletne else {
            return
        }

        try? await klientAPI.zapiszPreferencjePush(
            tokenJWT: tokenJWT,
            preferencje: preferencje
        )
    }

    // MARK: - Rejestracja push

    private func zarejestrujJeśliMożna() async {
        guard czyAutoryzowano, let tokenUrządzenia, let tokenJWT else {
            return
        }

        let daneRejestracji = DaneRejestracjiPush(
            tokenUrządzenia: tokenUrządzenia,
            tokenJWT: tokenJWT
        )

        guard daneRejestracji != ostatniaUdanaRejestracja,
              daneRejestracji != trwającaRejestracja else {
            return
        }

        trwającaRejestracja = daneRejestracji
        defer {
            if trwającaRejestracja == daneRejestracji {
                trwającaRejestracja = nil
            }
        }

        do {
            try await klientAPI.zarejestrujTokenPush(
                tokenUrządzenia: daneRejestracji.tokenUrządzenia,
                tokenJWT: daneRejestracji.tokenJWT
            )
            ostatniaUdanaRejestracja = daneRejestracji
        } catch {
            return
        }
    }

    // MARK: - Modele prywatne

    private struct DaneRejestracjiPush: Equatable {
        let tokenUrządzenia: String
        let tokenJWT: String
    }

    // MARK: - Właściwości obliczeniowe

    private var preferencje: PreferencjeKontaPush {
        let ustawienia = UserDefaults.standard
        let oddział = wartośćUstawienia(KluczeUstawień.oddział, ustawienia: ustawienia)
        let identyfikatorOddziału = wartośćUstawienia(KluczeUstawień.identyfikatorOddziału, ustawienia: ustawienia)
        let nauczyciel = wartośćUstawienia(KluczeUstawień.nauczyciel, ustawienia: ustawienia)
        let identyfikatorNauczyciela = wartośćUstawienia(KluczeUstawień.identyfikatorNauczyciela, ustawienia: ustawienia)
        let grupaZajęćLekcyjnych = wartośćUstawienia(KluczeUstawień.grupaZajęćLekcyjnych, ustawienia: ustawienia)
        let grupaZajęćPraktycznych = wartośćUstawienia(KluczeUstawień.grupaZajęćPraktycznych, ustawienia: ustawienia)
        let grupaWychowaniaFizycznego = wartośćUstawienia(KluczeUstawień.grupaWychowaniaFizycznego, ustawienia: ustawienia)
        let religia = ustawienia.object(forKey: KluczeUstawień.religia) as? Bool ?? true
        let edukacjaZdrowotna = ustawienia.object(forKey: KluczeUstawień.edukacjaZdrowotna) as? Bool ?? true
        let numerekUcznia = ustawienia.string(forKey: KluczeUstawień.numerekUcznia)
            .flatMap { Int($0) }

        return PreferencjeKontaPush(
            oddzial: oddział,
            identyfikatorOddzialu: identyfikatorOddziału,
            nauczyciel: nauczyciel,
            identyfikatorNauczyciela: identyfikatorNauczyciela,
            grupaZajecLekcyjnych: grupaZajęćLekcyjnych,
            grupaZajecPraktycznych: grupaZajęćPraktycznych,
            grupaWychowaniaFizycznego: grupaWychowaniaFizycznego,
            religia: religia,
            edukacjaZdrowotna: edukacjaZdrowotna,
            numerekUcznia: numerekUcznia
        )
    }

    private var czyLokalnePreferencjeSąKompletne: Bool {
        let ustawienia = UserDefaults.standard
        let identyfikatorOddziału = wartośćUstawienia(KluczeUstawień.identyfikatorOddziału, ustawienia: ustawienia)
        let identyfikatorNauczyciela = wartośćUstawienia(KluczeUstawień.identyfikatorNauczyciela, ustawienia: ustawienia)

        return identyfikatorOddziału != nil || identyfikatorNauczyciela != nil
    }

    // MARK: - Zarządzanie ustawieniami

    private func wartośćUstawienia(_ klucz: String, ustawienia: UserDefaults) -> String? {
        ustawienia.string(forKey: klucz).flatMap { $0.isEmpty ? nil : $0 }
    }

    private func ustawWartość(_ wartość: String?, dla klucz: String, ustawienia: UserDefaults) {
        ustawienia.set(wartość ?? "", forKey: klucz)
    }

    // MARK: - Nawigacja powiadomień

    private func ustawOczekiwaneMiejsceDocelowe(_ miejsceDocelowe: MiejsceDocelowePowiadomieniaPush) {
        oczekiwaneMiejsceDocelowe = miejsceDocelowe
    }

    private func zastosujPreferencjeKonta(_ preferencje: PreferencjeKontaPush) {
        let ustawienia = UserDefaults.standard

        ustawWartość(preferencje.oddzial, dla: KluczeUstawień.oddział, ustawienia: ustawienia)
        ustawWartość(preferencje.identyfikatorOddzialu, dla: KluczeUstawień.identyfikatorOddziału, ustawienia: ustawienia)
        ustawWartość(preferencje.nauczyciel, dla: KluczeUstawień.nauczyciel, ustawienia: ustawienia)
        ustawWartość(preferencje.identyfikatorNauczyciela, dla: KluczeUstawień.identyfikatorNauczyciela, ustawienia: ustawienia)
        ustawWartość(preferencje.numerekUcznia.map(String.init), dla: KluczeUstawień.numerekUcznia, ustawienia: ustawienia)
        ustawWartość(preferencje.grupaZajecLekcyjnych, dla: KluczeUstawień.grupaZajęćLekcyjnych, ustawienia: ustawienia)
        ustawWartość(preferencje.grupaZajecPraktycznych, dla: KluczeUstawień.grupaZajęćPraktycznych, ustawienia: ustawienia)
        ustawWartość(preferencje.grupaWychowaniaFizycznego, dla: KluczeUstawień.grupaWychowaniaFizycznego, ustawienia: ustawienia)
        ustawienia.set(preferencje.religia, forKey: KluczeUstawień.religia)
        ustawienia.set(preferencje.edukacjaZdrowotna, forKey: KluczeUstawień.edukacjaZdrowotna)
        ustawienia.set(czyLokalnePreferencjeSąKompletne, forKey: KluczeUstawień.czyKonfiguracjaZakończona)
    }
}

// MARK: - UNUserNotificationCenterDelegate

extension PushNotificationsManager: UNUserNotificationCenterDelegate {
    nonisolated func userNotificationCenter(
        _ center: UNUserNotificationCenter,
        willPresent notification: UNNotification
    ) async -> UNNotificationPresentationOptions {
        [.banner, .list, .sound, .badge]
    }

    nonisolated func userNotificationCenter(
        _ center: UNUserNotificationCenter,
        didReceive response: UNNotificationResponse,
        withCompletionHandler completionHandler: @escaping () -> Void
    ) {
        guard response.actionIdentifier == UNNotificationDefaultActionIdentifier else {
            completionHandler()
            return
        }

        guard let miejsceDocelowe = MiejsceDocelowePowiadomieniaPush(
            userInfo: response.notification.request.content.userInfo
        ) else {
            completionHandler()
            return
        }

        Task { @MainActor in
            self.ustawOczekiwaneMiejsceDocelowe(miejsceDocelowe)
        }

        completionHandler()
    }
}

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
import Observation

struct LekcjaWidoku: Identifiable, Equatable {
    let id: String
    let numer: Int
    let poczatek: String
    let koniec: String
    let przedmiot: String
    let nauczyciel: String
    let sala: String
    let oddzialy: String
    let zastepstwo: String?

    init(lekcja: Lekcja) {
        id = lekcja.id
        numer = lekcja.numer
        poczatek = lekcja.poczatek
        koniec = lekcja.koniec
        przedmiot = lekcja.przedmiot
        nauczyciel = lekcja.nauczyciel ?? ""
        sala = lekcja.sala ?? ""
        oddzialy = lekcja.oddzialy ?? ""
        zastepstwo = lekcja.zastepstwo
    }
}

@MainActor
@Observable
final class TimetableViewModel {
    // MARK: - Zależności

    private let klientAPI: APIClient

    // MARK: - Stan

    private(set) var lekcje: [LekcjaWidoku] = []
    private(set) var błąd: String?
    private(set) var czyŁaduje = false
    private(set) var czyWolne = false
    private(set) var czyDaneZastępstwDostępne = true
    private(set) var wygenerowano: String?
    private(set) var obowiazujeOd: String?
    private(set) var wygasa: String?

    private var identyfikatorŁadowania: UUID?

    // MARK: - Inicjalizacja

    init(klientAPI: APIClient? = nil) {
        self.klientAPI = klientAPI ?? .współdzielony
    }

    // MARK: - Właściwości obliczeniowe

    var grupyLekcji: [GrupaLekcjiWidoku] {
        GrupaLekcjiWidoku.utwórz(z: lekcje)
    }

    var czyMaInformacjePlanu: Bool {
        obowiazujeOd != nil || wygasa != nil || wygenerowano != nil
    }

    // MARK: - Akcje

    func załaduj(
        identyfikator: String?,
        grupy: [String]? = nil,
        zastepstwa: Bool? = true,
        dzien: Dzien,
        religia: Bool? = nil,
        edukacjaZdrowotna: Bool? = nil,
        pomińCache: Bool = false
    ) async {
        guard let identyfikator, !identyfikator.isEmpty else {
            identyfikatorŁadowania = nil
            wyczyśćPlan()
            return
        }

        let identyfikatorŁadowania = UUID()
        self.identyfikatorŁadowania = identyfikatorŁadowania

        błąd = nil
        czyŁaduje = true
        defer {
            zakończŁadowanie(identyfikator: identyfikatorŁadowania)
        }

        do {
            let planLekcji = try await klientAPI.pobierzPlanLekcji(
                identyfikator: identyfikator,
                grupy: grupy,
                zastepstwa: zastepstwa,
                religia: religia,
                edukacjaZdrowotna: edukacjaZdrowotna,
                pomińCache: pomińCache
            )

            guard czyAktualneŁadowanie(identyfikatorŁadowania) else {
                return
            }

            czyDaneZastępstwDostępne = planLekcji.zastepstwa
            czyWolne = planLekcji.wolne
            wygenerowano = planLekcji.wygenerowano
            obowiazujeOd = planLekcji.obowiazuje
            wygasa = planLekcji.wygasa
            lekcje = planLekcji.lekcje
                .filter { $0.dzien == dzien }
                .map(LekcjaWidoku.init)
        } catch {
            guard !error.czyAnulowany, czyAktualneŁadowanie(identyfikatorŁadowania) else {
                return
            }

            błąd = error.komunikatDlaUżytkownika
            wyczyśćPlan(zachowajBłąd: true)
        }
    }

    func wyczyśćBłąd() {
        błąd = nil
    }

    private func czyAktualneŁadowanie(_ identyfikator: UUID) -> Bool {
        identyfikatorŁadowania == identyfikator && !Task.isCancelled
    }

    private func zakończŁadowanie(identyfikator: UUID) {
        guard identyfikatorŁadowania == identyfikator else {
            return
        }

        czyŁaduje = false
        identyfikatorŁadowania = nil
    }

    private func wyczyśćPlan(zachowajBłąd: Bool = false) {
        lekcje = []
        if !zachowajBłąd {
            błąd = nil
        }
        czyŁaduje = false
        czyWolne = false
        czyDaneZastępstwDostępne = true
        wygenerowano = nil
        obowiazujeOd = nil
        wygasa = nil
    }
}

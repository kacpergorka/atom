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

@MainActor
@Observable
final class NumbersViewModel {
    // MARK: - Zależności

    private let klientAPI: APIClient

    // MARK: - Stan

    private(set) var numerki: [Int] = []
    private(set) var błąd: String?
    private(set) var czyŁaduje = false

    private var identyfikatorŁadowania: UUID?

    // MARK: - Inicjalizacja

    init(klientAPI: APIClient? = nil) {
        self.klientAPI = klientAPI ?? .współdzielony
    }

    // MARK: - Właściwości obliczeniowe

    var opisNumerków: String {
        guard !numerki.isEmpty else {
            return "Brak"
        }

        return numerki
            .sorted()
            .map(String.init)
            .joined(separator: ", ")
    }

    // MARK: - Akcje

    func załaduj(pomińCache: Bool = false) async {
        let identyfikatorŁadowania = UUID()
        self.identyfikatorŁadowania = identyfikatorŁadowania

        błąd = nil
        czyŁaduje = true
        defer {
            zakończŁadowanie(identyfikator: identyfikatorŁadowania)
        }

        do {
            let wynik = try await klientAPI.pobierzNumerki(pomińCache: pomińCache).numerki ?? []

            guard czyAktualneŁadowanie(identyfikatorŁadowania) else {
                return
            }

            numerki = wynik
        } catch {
            guard !error.czyAnulowany, czyAktualneŁadowanie(identyfikatorŁadowania) else {
                return
            }

            błąd = error.komunikatDlaUżytkownika
            numerki = []
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
}

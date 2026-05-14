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
final class PersonalizationViewModel {
    // MARK: - Typy

    struct OpcjaListy: Identifiable, Equatable {
        let id: String
        let nazwa: String
    }

    // MARK: - Zależności

    private let klientAPI: APIClient

    // MARK: - Stałe

    private let opcjaBrak = OpcjaListy(id: "", nazwa: "Brak")
    private let opcjaBrakDanych = OpcjaListy(id: "", nazwa: "Brak danych")

    // MARK: - Stan

    private(set) var listaOddziałów: [OpcjaListy] = []
    private(set) var listaNauczycieli: [OpcjaListy] = []
    private(set) var błąd: String?
    private(set) var czyŁaduje = false

    // MARK: - Inicjalizacja

    init(klientAPI: APIClient? = nil) {
        self.klientAPI = klientAPI ?? .współdzielony
    }

    // MARK: - Właściwości obliczeniowe

    var dostępneOddziały: [OpcjaListy] {
        listaOddziałów.isEmpty ? [opcjaBrakDanych] : listaOddziałów
    }

    var dostępniNauczyciele: [OpcjaListy] {
        listaNauczycieli.isEmpty ? [opcjaBrakDanych] : listaNauczycieli
    }

    var czyListaOddziałówJestZaładowana: Bool {
        !listaOddziałów.isEmpty
    }

    var czyListaNauczycieliJestZaładowana: Bool {
        !listaNauczycieli.isEmpty
    }

    // MARK: - Akcje

    func załaduj() async {
        błąd = nil
        czyŁaduje = true
        defer { czyŁaduje = false }

        do {
            let listy = try await klientAPI.pobierzListy()
            listaOddziałów = przygotujOpcje(z: listy.oddzialy)
            listaNauczycieli = przygotujOpcje(z: listy.nauczyciele)
        } catch {
            błąd = error.komunikatDlaUżytkownika
        }
    }

    func wyczyśćBłąd() {
        błąd = nil
    }

    func opcjaNauczyciela(oId identyfikator: String) -> OpcjaListy? {
        opcja(oId: identyfikator, w: listaNauczycieli)
    }

    func opcjaOddziału(oId identyfikator: String) -> OpcjaListy? {
        opcja(oId: identyfikator, w: listaOddziałów)
    }

    // MARK: - Prywatne

    private func opcja(oId identyfikator: String, w lista: [OpcjaListy]) -> OpcjaListy? {
        guard !identyfikator.isEmpty else {
            return opcjaBrak
        }

        return lista.first { $0.id == identyfikator }
    }

    private func przygotujOpcje(z lista: [ElementListy]?) -> [OpcjaListy] {
        let opcje = (lista ?? []).map { wartość in
            OpcjaListy(id: wartość.identyfikator, nazwa: wartość.nazwa)
        }

        return [opcjaBrak] + opcje
    }
}

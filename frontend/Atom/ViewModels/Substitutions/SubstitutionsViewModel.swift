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

struct InformacjaDodatkowaWidoku: Identifiable, Equatable {
    let id: Int
    let tekst: AttributedString
    let czyPusta: Bool
}

struct GrupaZastępstwWidoku: Identifiable {
    let dzień: String?
    let nauczyciel: String
    var zastępstwa: [Zastepstwo]

    var id: String {
        "\(dzień ?? "")|\(nauczyciel)"
    }
}

@MainActor
@Observable
final class SubstitutionsViewModel {
    // MARK: - Zależności

    private let klientAPI: APIClient

    // MARK: - Stan

    private(set) var zastępstwa: Zastepstwa?
    private(set) var błąd: String?
    private(set) var czyŁaduje = false

    private var identyfikatorŁadowania: UUID?

    // MARK: - Inicjalizacja

    init(klientAPI: APIClient? = nil) {
        self.klientAPI = klientAPI ?? .współdzielony
    }

    // MARK: - Właściwości obliczeniowe

    var dni: String {
        zastępstwa?.dni.joined(separator: " / ") ?? ""
    }

    var grupyZastępstw: [GrupaZastępstwWidoku] {
        let wpisy = zastępstwa?.zastepstwa ?? []

        var wynik: [GrupaZastępstwWidoku] = []
        var indeksy: [String: Int] = [:]

        for wpis in wpisy {
            let klucz = "\(wpis.dzien ?? "")|\(wpis.nauczyciel)"

            if let indeks = indeksy[klucz] {
                wynik[indeks].zastępstwa.append(wpis)
            } else {
                indeksy[klucz] = wynik.count
                wynik.append(
                    GrupaZastępstwWidoku(
                        dzień: wpis.dzien,
                        nauczyciel: wpis.nauczyciel,
                        zastępstwa: [wpis]
                    )
                )
            }
        }

        return wynik
    }

    var informacjeDodatkowe: [InformacjaDodatkowaWidoku] {
        (zastępstwa?.informacje ?? []).enumerated().map { indeks, linia in
            InformacjaDodatkowaWidoku(
                id: indeks,
                tekst: sformatujInformację(linia),
                czyPusta: linia.isEmpty
            )
        }
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
            let wynik = try await klientAPI.pobierzZastępstwa(pomińCache: pomińCache)

            guard czyAktualneŁadowanie(identyfikatorŁadowania) else {
                return
            }

            zastępstwa = wynik
        } catch {
            guard !error.czyAnulowany, czyAktualneŁadowanie(identyfikatorŁadowania) else {
                return
            }

            błąd = error.komunikatDlaUżytkownika
            zastępstwa = nil
        }
    }

    func wyczyśćBłąd() {
        błąd = nil
    }

    // MARK: - Prywatne

    private func sformatujInformację(_ linia: String) -> AttributedString {
        (try? AttributedString(
            markdown: linia,
            options: AttributedString.MarkdownParsingOptions(
                interpretedSyntax: .inlineOnlyPreservingWhitespace
            )
        )) ?? AttributedString(linia)
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

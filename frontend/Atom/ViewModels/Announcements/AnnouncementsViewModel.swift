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

struct OgloszenieWidoku: Identifiable, Hashable {
    let ogloszenie: Ogloszenie

    var id: String {
        ogloszenie.url
    }

    var tytul: String {
        ogloszenie.tytul
    }

    var stopka: String {
        ogloszenie.stopka?.trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
    }

    var miniaturaURL: URL? {
        guard let ścieżka = ogloszenie.obraz, let url = URL(string: ścieżka) else {
            return nil
        }

        return url
    }
}

@MainActor
@Observable
final class AnnouncementsViewModel {
    // MARK: - Zależności

    private let klientAPI: APIClient

    // MARK: - Stan

    private(set) var ogloszenia: [OgloszenieWidoku] = []
    private(set) var błąd: String?
    private(set) var czyŁaduje = false
    private(set) var czyŁadujeWięcej = false

    private var aktualnaStrona = 0
    private var ostatniaStrona = 1
    private var identyfikatorOdświeżania: UUID?
    private var identyfikatorDoładowania: UUID?

    // MARK: - Inicjalizacja

    init(klientAPI: APIClient? = nil) {
        self.klientAPI = klientAPI ?? .współdzielony
    }

    // MARK: - Właściwości obliczeniowe

    var podtytul: String {
        guard !ogloszenia.isEmpty else {
            return "Aktualności"
        }

        if czyMożnaZaładowaćWięcej {
            return "Strona \(aktualnaStrona) z \(ostatniaStrona)"
        }

        return "Aktualności"
    }

    var czyMożnaZaładowaćWięcej: Bool {
        aktualnaStrona < ostatniaStrona
    }

    // MARK: - Akcje

    func załadujPonownieJeśliPotrzeba() async {
        guard ogloszenia.isEmpty, !czyŁaduje else {
            return
        }

        await odśwież(pomińCache: false)
    }

    func odśwież(pomińCache: Bool = true) async {
        let identyfikatorOdświeżania = UUID()
        self.identyfikatorOdświeżania = identyfikatorOdświeżania

        błąd = nil
        czyŁaduje = true
        defer {
            zakończOdświeżanie(identyfikator: identyfikatorOdświeżania)
        }

        do {
            let odpowiedź = try await klientAPI.pobierzOgłoszenia(strona: 1, pomińCache: pomińCache)

            guard czyAktualneOdświeżanie(identyfikatorOdświeżania) else {
                return
            }

            aktualizujStan(odpowiedź, zastąp: true)
        } catch {
            guard !error.czyAnulowany, czyAktualneOdświeżanie(identyfikatorOdświeżania) else {
                return
            }

            błąd = error.komunikatDlaUżytkownika
            ogloszenia = []
            aktualnaStrona = 0
            ostatniaStrona = 1
        }
    }

    func załadujWięcej() async {
        guard czyMożnaZaładowaćWięcej, !czyŁadujeWięcej else {
            return
        }

        błąd = nil
        czyŁadujeWięcej = true

        let następnaStrona = aktualnaStrona + 1
        let identyfikatorDoładowania = UUID()
        self.identyfikatorDoładowania = identyfikatorDoładowania
        defer {
            zakończDoładowanie(identyfikator: identyfikatorDoładowania)
        }

        do {
            let odpowiedź = try await klientAPI.pobierzOgłoszenia(strona: następnaStrona)

            guard czyAktualneDoładowanie(identyfikatorDoładowania) else {
                return
            }

            aktualizujStan(odpowiedź, zastąp: false)
        } catch {
            guard !error.czyAnulowany, czyAktualneDoładowanie(identyfikatorDoładowania) else {
                return
            }

            błąd = error.komunikatDlaUżytkownika
        }
    }

    // MARK: - Prywatne

    private func czyAktualneOdświeżanie(_ identyfikator: UUID) -> Bool {
        identyfikatorOdświeżania == identyfikator && !Task.isCancelled
    }

    private func czyAktualneDoładowanie(_ identyfikator: UUID) -> Bool {
        identyfikatorDoładowania == identyfikator && !Task.isCancelled
    }

    private func zakończOdświeżanie(identyfikator: UUID) {
        guard identyfikatorOdświeżania == identyfikator else {
            return
        }

        czyŁaduje = false
        identyfikatorOdświeżania = nil
    }

    private func zakończDoładowanie(identyfikator: UUID) {
        guard identyfikatorDoładowania == identyfikator else {
            return
        }

        czyŁadujeWięcej = false
        identyfikatorDoładowania = nil
    }

    private func aktualizujStan(_ odpowiedź: Ogloszenia, zastąp: Bool) {
        let noweOgłoszenia = odpowiedź.ogloszenia.map(OgloszenieWidoku.init)

        if zastąp {
            ogloszenia = noweOgłoszenia
        } else {
            let istniejąceURL = Set(ogloszenia.map(\.ogloszenie.url))
            ogloszenia.append(contentsOf: noweOgłoszenia.filter { !istniejąceURL.contains($0.ogloszenie.url) })
        }

        aktualnaStrona = max(1, odpowiedź.aktualnaStrona)
        ostatniaStrona = max(aktualnaStrona, odpowiedź.ostatniaStrona)
    }
}

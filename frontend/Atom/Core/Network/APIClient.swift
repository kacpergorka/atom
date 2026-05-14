//
//     ▄▄     ▄▄▄▄▄▄▄▄    ▄▄▄▄    ▄▄▄  ▄▄▄
//    ████    ▀▀▀██▀▀▀   ██▀▀██   ███  ███
//    ████       ██     ██    ██  ████████
//   ██  ██      ██     ██    ██  ██ ██ ██
//   ██████      ██     ██    ██  ██ ▀▀ ██
//  ▄██  ██▄     ██      ██▄▄██   ██    ██
//  ▀▀    ▀▀     ▀▀       ▀▀▀▀    ▀▀    ▀▀
//

import Foundation

// MARK: - Błąd API

enum APIBłąd: Error {
    case niepoprawnyAdres
    case niepoprawnaOdpowiedź
    case niepoprawnyStatusHTTP(Int)
}

// MARK: - Lokalizacja błędów API

extension APIBłąd: LocalizedError {
    var errorDescription: String? {
        switch self {
        case .niepoprawnyAdres:
            return "Adres serwera jest nieprawidłowy."
        case .niepoprawnaOdpowiedź:
            return "Serwer zwrócił nieprawidłową odpowiedź."
        case .niepoprawnyStatusHTTP:
            return "Nie udało się pobrać danych z serwera."
        }
    }
}

// MARK: - Rozszerzenia błędów

extension Error {
    var czyAnulowany: Bool {
        if self is CancellationError {
            return true
        }

        if let błądURL = self as? URLError, błądURL.code == .cancelled {
            return true
        }

        let błąd = self as NSError
        return błąd.domain == NSURLErrorDomain && błąd.code == NSURLErrorCancelled
    }

    var komunikatDlaUżytkownika: String {
        if let błądAPI = self as? APIBłąd,
           let opis = błądAPI.errorDescription {
            return opis
        }

        if let błądURL = self as? URLError {
            switch błądURL.code {
            case .notConnectedToInternet:
                return "Brak połączenia z internetem."
            case .timedOut:
                return "Przekroczono czas oczekiwania na odpowiedź serwera."
            default:
                return "Nie udało się połączyć z serwerem."
            }
        }

        if self is DecodingError {
            return "Nie udało się odczytać danych z serwera."
        }

        let opis = (self as NSError).localizedDescription
        return opis.isEmpty ? "Wystąpił nieoczekiwany błąd." : opis
    }
}

// MARK: - Klient API

final class APIClient {
    static let współdzielony = APIClient()
    private let adresAPI: URL
    private let sesjaURL: URLSession
    private let cache = NSCache<NSString, CacheEntry>()

    private enum PolitykaCache {
        case czasŻycia(TimeInterval)
        case wygasa(Date)
    }

    private final class CacheEntry {
        let dane: Data
        let dataWażności: Date

        init(dane: Data, dataWażności: Date) {
            self.dane = dane
            self.dataWażności = dataWażności
        }

        var czyWażny: Bool {
            Date() < dataWażności
        }
    }

    private init() {
        guard let url = URL(string: LinkiStatyczne.api) else {
            preconditionFailure("Nieprawidłowy adres API w konfiguracji aplikacji.")
        }
        self.adresAPI = url

        let konfiguracja = URLSessionConfiguration.default
        konfiguracja.waitsForConnectivity = true
        konfiguracja.timeoutIntervalForRequest = 15
        konfiguracja.timeoutIntervalForResource = 30
        self.sesjaURL = URLSession(configuration: konfiguracja)
    }

    private enum Endpoint {
        static let listy = "v1/atom/listy"
        static let numerki = "v1/atom/numerki"
        static let planLekcji = "v1/atom/planlekcji"
        static let zastepstwa = "v1/atom/zastepstwa"
        static let ogloszenia = "v1/atom/ogloszenia"

        static let pobieraniePreferencji = "preferencje/pobierz"
        static let zapisywaniePreferencji = "preferencje/zapisz"

        static let synchronizacjaKonta = "konto/synchronizuj"
        static let usuwanieKonta = "konto/usun"

        static let rejestracjaPush = "powiadomienia/zarejestruj"
        static let usuwaniePush = "powiadomienia/wyrejestruj"
    }

    private func adresURL(
        path: String,
        parametry: [URLQueryItem] = []
    ) throws -> URL {
        guard var komponentyURL = URLComponents(
            url: adresAPI.appendingPathComponent(path),
            resolvingAgainstBaseURL: false
        ) else {
            throw APIBłąd.niepoprawnyAdres
        }

        komponentyURL.queryItems = parametry.isEmpty ? nil : parametry

        guard let adresURL = komponentyURL.url else {
            throw APIBłąd.niepoprawnyAdres
        }

        return adresURL
    }

    private func dodajParametry(
        nazwa: String,
        wartości: [String]?,
        do parametry: inout [URLQueryItem]
    ) {
        for wartość in wartości ?? [] where !wartość.isEmpty {
            parametry.append(URLQueryItem(name: nazwa, value: wartość))
        }
    }

    private func dodajParametr(
        nazwa: String,
        wartość: Bool?,
        do parametry: inout [URLQueryItem]
    ) {
        guard let wartość else { return }
        parametry.append(URLQueryItem(name: nazwa, value: wartość ? "true" : "false"))
    }

    private func kluczCache(adresURL: URL) -> NSString {
        NSString(string: adresURL.absoluteString)
    }

    private func dataWażności(politykaCache: PolitykaCache) -> Date {
        switch politykaCache {
        case .czasŻycia(let czasŻycia):
            return Date().addingTimeInterval(czasŻycia)
        case .wygasa(let data):
            return data
        }
    }

    private func najbliższaPółnoc(
        względem data: Date = Date(),
        kalendarz: Calendar = .current
    ) -> Date {
        let początekDnia = kalendarz.startOfDay(for: data)
        return kalendarz.date(byAdding: .day, value: 1, to: początekDnia) ?? data.addingTimeInterval(60 * 60 * 24)
    }

    private func wykonajŻądanie<ModelOdpowiedzi: Decodable>(
        path: String,
        parametry: [URLQueryItem] = [],
        politykaCache: PolitykaCache? = nil,
        pomińCache: Bool = false
    ) async throws -> ModelOdpowiedzi {
        let adresURL = try adresURL(path: path, parametry: parametry)
        let kluczCache = kluczCache(adresURL: adresURL)

        if !pomińCache,
           politykaCache != nil,
           let wpisCache = cache.object(forKey: kluczCache),
           wpisCache.czyWażny {
            return try JSONDecoder().decode(ModelOdpowiedzi.self, from: wpisCache.dane)
        }

        let (dane, odpowiedź) = try await sesjaURL.data(from: adresURL)

        guard let odpowiedźHTTP = odpowiedź as? HTTPURLResponse else {
            throw APIBłąd.niepoprawnaOdpowiedź
        }

        guard (200..<300).contains(odpowiedźHTTP.statusCode) else {
            throw APIBłąd.niepoprawnyStatusHTTP(odpowiedźHTTP.statusCode)
        }

        if let politykaCache {
            cache.setObject(
                CacheEntry(dane: dane, dataWażności: dataWażności(politykaCache: politykaCache)),
                forKey: kluczCache
            )
        }

        return try JSONDecoder().decode(ModelOdpowiedzi.self, from: dane)
    }

    private func wykonajŻądanieAutoryzowane<ModelŻądania: Encodable>(
        path: String,
        metodaHTTP: String,
        tokenJWT: String,
        daneŻądania: ModelŻądania
    ) async throws {
        let adresURL = try adresURL(path: path)
        var żądanie = URLRequest(url: adresURL)
        żądanie.httpMethod = metodaHTTP
        żądanie.setValue("Bearer \(tokenJWT)", forHTTPHeaderField: "Authorization")
        żądanie.setValue("application/json", forHTTPHeaderField: "Content-Type")
        żądanie.httpBody = try JSONEncoder().encode(daneŻądania)

        let (_, odpowiedź) = try await sesjaURL.data(for: żądanie)

        guard let odpowiedźHTTP = odpowiedź as? HTTPURLResponse else {
            throw APIBłąd.niepoprawnaOdpowiedź
        }

        guard (200..<300).contains(odpowiedźHTTP.statusCode) else {
            throw APIBłąd.niepoprawnyStatusHTTP(odpowiedźHTTP.statusCode)
        }
    }

    private func wykonajŻądanieAutoryzowane<ModelŻądania: Encodable, ModelOdpowiedzi: Decodable>(
        path: String,
        metodaHTTP: String,
        tokenJWT: String,
        daneŻądania: ModelŻądania
    ) async throws -> ModelOdpowiedzi {
        let adresURL = try adresURL(path: path)
        var żądanie = URLRequest(url: adresURL)
        żądanie.httpMethod = metodaHTTP
        żądanie.setValue("Bearer \(tokenJWT)", forHTTPHeaderField: "Authorization")
        żądanie.setValue("application/json", forHTTPHeaderField: "Content-Type")
        żądanie.httpBody = try JSONEncoder().encode(daneŻądania)

        let (dane, odpowiedź) = try await sesjaURL.data(for: żądanie)

        guard let odpowiedźHTTP = odpowiedź as? HTTPURLResponse else {
            throw APIBłąd.niepoprawnaOdpowiedź
        }

        guard (200..<300).contains(odpowiedźHTTP.statusCode) else {
            throw APIBłąd.niepoprawnyStatusHTTP(odpowiedźHTTP.statusCode)
        }

        return try JSONDecoder().decode(ModelOdpowiedzi.self, from: dane)
    }

    private func wykonajŻądanieAutoryzowane<ModelOdpowiedzi: Decodable>(
        path: String,
        parametry: [URLQueryItem] = [],
        tokenJWT: String
    ) async throws -> ModelOdpowiedzi {
        let adresURL = try adresURL(path: path, parametry: parametry)
        var żądanie = URLRequest(url: adresURL)
        żądanie.httpMethod = "GET"
        żądanie.setValue("Bearer \(tokenJWT)", forHTTPHeaderField: "Authorization")

        let (dane, odpowiedź) = try await sesjaURL.data(for: żądanie)

        guard let odpowiedźHTTP = odpowiedź as? HTTPURLResponse else {
            throw APIBłąd.niepoprawnaOdpowiedź
        }

        guard (200..<300).contains(odpowiedźHTTP.statusCode) else {
            throw APIBłąd.niepoprawnyStatusHTTP(odpowiedźHTTP.statusCode)
        }

        return try JSONDecoder().decode(ModelOdpowiedzi.self, from: dane)
    }

    private func wykonajŻądanieAutoryzowane(
        path: String,
        metodaHTTP: String,
        tokenJWT: String
    ) async throws {
        let adresURL = try adresURL(path: path)
        var żądanie = URLRequest(url: adresURL)
        żądanie.httpMethod = metodaHTTP
        żądanie.setValue("Bearer \(tokenJWT)", forHTTPHeaderField: "Authorization")

        let (_, odpowiedź) = try await sesjaURL.data(for: żądanie)

        guard let odpowiedźHTTP = odpowiedź as? HTTPURLResponse else {
            throw APIBłąd.niepoprawnaOdpowiedź
        }

        guard (200..<300).contains(odpowiedźHTTP.statusCode) else {
            throw APIBłąd.niepoprawnyStatusHTTP(odpowiedźHTTP.statusCode)
        }
    }

    // MARK: - Publiczne API

    func pobierzListy(pomińCache: Bool = false) async throws -> Listy {
        return try await wykonajŻądanie(
            path: Endpoint.listy,
            politykaCache: .czasŻycia(60 * 60 * 24),
            pomińCache: pomińCache
        )
    }

    func pobierzNumerki(pomińCache: Bool = false) async throws -> SzczesliweNumerki {
        return try await wykonajŻądanie(
            path: Endpoint.numerki,
            politykaCache: .wygasa(najbliższaPółnoc()),
            pomińCache: pomińCache
        )
    }

    func pobierzPlanLekcji(
        identyfikator: String,
        grupy: [String]? = nil,
        zastepstwa: Bool? = nil,
        religia: Bool? = nil,
        edukacjaZdrowotna: Bool? = nil,
        pomińCache: Bool = false
    ) async throws -> PlanLekcji {
        guard !identyfikator.isEmpty else {
            throw URLError(.userAuthenticationRequired)
        }

        var parametry: [URLQueryItem] = [
            URLQueryItem(
                name: "identyfikator",
                value: identyfikator
            )
        ]

        dodajParametry(nazwa: "grupy", wartości: grupy, do: &parametry)
        dodajParametr(nazwa: "zastepstwa", wartość: zastepstwa, do: &parametry)
        dodajParametr(nazwa: "religia", wartość: religia, do: &parametry)
        dodajParametr(nazwa: "edukacjaZdrowotna", wartość: edukacjaZdrowotna, do: &parametry)

        return try await wykonajŻądanie(
            path: Endpoint.planLekcji,
            parametry: parametry,
            politykaCache: .wygasa(najbliższaPółnoc()),
            pomińCache: pomińCache
        )
    }

    func pobierzZastępstwa(pomińCache: Bool = false) async throws -> Zastepstwa {
        return try await wykonajŻądanie(
            path: Endpoint.zastepstwa,
            politykaCache: .czasŻycia(60),
            pomińCache: pomińCache
        )
    }

    func pobierzOgłoszenia(
        strona: Int = 1,
        pomińCache: Bool = false
    ) async throws -> Ogloszenia {
        let parametry = [
            URLQueryItem(name: "strona", value: String(max(1, strona)))
        ]

        return try await wykonajŻądanie(
            path: Endpoint.ogloszenia,
            parametry: parametry,
            politykaCache: .czasŻycia(60),
            pomińCache: pomińCache
        )
    }

    func zarejestrujTokenPush(
        tokenUrządzenia: String,
        tokenJWT: String
    ) async throws {
        try await wykonajŻądanieAutoryzowane(
            path: Endpoint.rejestracjaPush,
            metodaHTTP: "POST",
            tokenJWT: tokenJWT,
            daneŻądania: ZadanieRejestracjiPush(
                tokenUrzadzenia: tokenUrządzenia
            )
        )
    }

    func usuńTokenPush(
        tokenUrządzenia: String,
        tokenJWT: String
    ) async throws {
        try await wykonajŻądanieAutoryzowane(
            path: Endpoint.usuwaniePush,
            metodaHTTP: "DELETE",
            tokenJWT: tokenJWT,
            daneŻądania: ZadanieUsunieciaPush(tokenUrzadzenia: tokenUrządzenia)
        )
    }

    func pobierzPreferencjePush(tokenJWT: String) async throws -> PreferencjeKontaPush? {
        try await wykonajŻądanieAutoryzowane(
            path: Endpoint.pobieraniePreferencji,
            tokenJWT: tokenJWT
        )
    }

    func zapiszPreferencjePush(
        tokenJWT: String,
        preferencje: PreferencjeKontaPush
    ) async throws {
        try await wykonajŻądanieAutoryzowane(
            path: Endpoint.zapisywaniePreferencji,
            metodaHTTP: "PUT",
            tokenJWT: tokenJWT,
            daneŻądania: preferencje
        )
    }

    func usuńKonto(tokenJWT: String) async throws {
        try await wykonajŻądanieAutoryzowane(
            path: Endpoint.usuwanieKonta,
            metodaHTTP: "DELETE",
            tokenJWT: tokenJWT
        )
    }

    func synchronizujKonto(
        tokenJWT: String,
        nazwa: String?
    ) async throws -> Konto {
        try await wykonajŻądanieAutoryzowane(
            path: Endpoint.synchronizacjaKonta,
            metodaHTTP: "PUT",
            tokenJWT: tokenJWT,
            daneŻądania: ZadanieKonta(nazwa: nazwa)
        )
    }
}

private struct ZadanieRejestracjiPush: Encodable {
    let tokenUrzadzenia: String
}

private struct ZadanieUsunieciaPush: Encodable {
    let tokenUrzadzenia: String
}

// MARK: - Modele API

struct PreferencjeKontaPush: Codable, Equatable {
    let oddzial: String?
    let identyfikatorOddzialu: String?
    let nauczyciel: String?
    let identyfikatorNauczyciela: String?
    let grupaZajecLekcyjnych: String?
    let grupaZajecPraktycznych: String?
    let grupaWychowaniaFizycznego: String?
    let religia: Bool
    let edukacjaZdrowotna: Bool
    let numerekUcznia: Int?

    enum CodingKeys: String, CodingKey {
        case oddzial = "oddzial"
        case identyfikatorOddzialu = "identyfikatorOddzialu"
        case nauczyciel = "nauczyciel"
        case identyfikatorNauczyciela = "identyfikatorNauczyciela"
        case grupaZajecLekcyjnych = "grupaZajecLekcyjnych"
        case grupaZajecPraktycznych = "grupaZajecPraktycznych"
        case grupaWychowaniaFizycznego = "grupaWychowaniaFizycznego"
        case religia = "religia"
        case edukacjaZdrowotna = "edukacjaZdrowotna"
        case numerekUcznia = "numerekUcznia"
    }
}

struct Konto: Decodable {
    let nazwa: String?

    enum CodingKeys: String, CodingKey {
        case nazwa = "nazwa"
    }
}

private struct ZadanieKonta: Encodable {
    let nazwa: String?

    enum CodingKeys: String, CodingKey {
        case nazwa = "nazwa"
    }
}
